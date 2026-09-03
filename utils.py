import json
import re
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "assets"


def _ap_category(nodes: list) -> str:
    op_labels = [
        lbl
        for n in nodes
        if "Operator" in n.get("labels", [])
        for lbl in n.get("labels", [])
        if lbl != "Operator"
    ]
    unique = list(dict.fromkeys(op_labels))
    if len(unique) > 1:
        return "Composed"
    if not unique:
        return "Other"
    label = unique[0].replace("_Operator", "").replace("_", " ")
    return label.replace("Sql", "SQL").replace("Nl", "NL")


def list_ap_files() -> list[tuple[str, str, str]]:
    results = []
    for path in sorted(ASSETS_DIR.glob("*.json")):
        try:
            with open(path) as f:
                data = json.load(f)
            nodes = data.get("nodes", [])
            name = next(
                (
                    n["properties"]["name"]
                    for n in nodes
                    if "Analytical_Pattern" in n.get("labels", []) and n.get("properties", {}).get("name")
                ),
                path.stem,
            )
            category = _ap_category(nodes)
        except Exception:
            name = path.stem
            category = "Other"
        results.append((name, str(path), category))
    return results


def load_ap_json(file_path: str) -> dict:
    with open(file_path) as f:
        return json.load(f)


def _param_name(expr: str) -> str:
    keys = re.findall(r"\['([^']+)'\]", expr)
    return ".".join(keys) if keys else expr


def format_type(param: dict) -> str:
    t = param.get("type", "?")
    if t == "object":
        fields = param.get("properties", {})
        inner = ", ".join(
            f"{k}: {v.get('type', '?')}" for k, v in fields.items())
        return "{" + inner + "}" if inner else "object"
    if t == "array":
        item_type = param.get("items", {}).get("type", "any")
        return f"{item_type}[]"
    return t


def _node_name(node: dict) -> str:
    props = node.get("properties", {}) or {}
    return props.get("name") or (node.get("labels") or ["?"])[0]


def operator_execution_order(ap_data: dict) -> list[dict]:
    """Operator nodes in the order ap-executor walks them.

    Order is derived from data dependencies — an ``output`` edge feeds a
    ``ResultType`` node which an ``input`` edge feeds into the next operator — so
    an operator only runs once everything it consumes has produced. A
    ``properties.step`` value (when present) and the original document order break
    ties between operators that are otherwise independent.
    """
    nodes = ap_data.get("nodes", [])
    edges = ap_data.get("edges", [])
    labels_by_id = {n["id"]: n.get("labels", []) for n in nodes}
    ops = [n for n in nodes if "Operator" in n.get("labels", [])]
    op_ids = {n["id"] for n in ops}
    node_by_id = {n["id"]: n for n in ops}
    hint = {n["id"]: i for i, n in enumerate(ops)}

    # Which operator produces each ResultType node.
    produced_by: dict[str, list[str]] = {}
    for e in edges:
        if "output" not in (e.get("labels") or []):
            continue
        frm, to = str(e.get("from")), str(e.get("to"))
        if frm in op_ids and "ResultType" in labels_by_id.get(to, []):
            produced_by.setdefault(to, []).append(frm)

    deps: dict[str, set[str]] = {oid: set() for oid in op_ids}
    for e in edges:
        if not ({"input", "output"} & set(e.get("labels") or [])):
            continue
        frm, to = str(e.get("from")), str(e.get("to"))
        if to not in op_ids:
            continue
        if frm in op_ids:
            deps[to].add(frm)
        elif frm in produced_by:
            deps[to].update(p for p in produced_by[frm] if p != to)

    def sort_key(oid: str) -> tuple:
        step = (node_by_id[oid].get("properties", {}) or {}).get("step")
        return (step is None, step if step is not None else 0, hint[oid])

    ordered: list[str] = []
    done: set[str] = set()
    ready = [oid for oid in op_ids if not deps[oid]]
    while ready:
        ready.sort(key=sort_key)
        cur = ready.pop(0)
        ordered.append(cur)
        done.add(cur)
        for oid in op_ids:
            if oid not in done and oid not in ready and deps[oid] <= done:
                ready.append(oid)
    # Anything left is part of a dependency cycle — append in document order.
    for oid in sorted(op_ids - set(ordered), key=lambda o: hint[o]):
        ordered.append(oid)
    return [node_by_id[oid] for oid in ordered]


def _param_after_inputs(dest_expr: str) -> str | None:
    keys = re.findall(r"\['([^']+)'\]", dest_expr or "")
    for i, k in enumerate(keys):
        if i and keys[i - 1] == "inputs":
            return k
    return keys[-1] if keys else None


def operator_input_sources(ap_data: dict, op_id: str) -> tuple[dict[str, dict], list[str]]:
    """``({input_name: source}, [unmapped feeder names])`` for one operator,
    tracing ``input`` edges back through their ``ResultType`` node to the operator
    that produced them.

    Each ``source`` is ``{"label", "producer_id", "output_name"}`` — ``label`` is
    the human ``"Producer → out_param"`` string; ``producer_id`` /
    ``output_name`` (``None`` when the feeder is not an operator) let the caller
    look up the real value in an execution result once the AP has run.
    """
    nodes = ap_data.get("nodes", [])
    edges = ap_data.get("edges", [])
    labels_by_id = {n["id"]: n.get("labels", []) for n in nodes}
    name_by_id = {n["id"]: _node_name(n) for n in nodes}
    op_ids = {n["id"] for n in nodes if "Operator" in n.get("labels", [])}

    # {result_type_id: {result_type_prop: {"producer_id", "producer_name", "output_name"}}}
    rt_source: dict[str, dict[str, dict]] = {}
    for e in edges:
        if "output" not in (e.get("labels") or []):
            continue
        to = str(e.get("to"))
        if "ResultType" not in labels_by_id.get(to, []):
            continue
        producer_id = str(e.get("from"))
        producer = name_by_id.get(producer_id, "?")
        mapping = (e.get("properties") or {}).get("mapping") or {}
        if not mapping:
            rt_source.setdefault(to, {})[name_by_id.get(to, "")] = {
                "producer_id": producer_id, "producer_name": producer,
                "output_name": None}
        for dest_expr, src_expr in mapping.items():
            dk = re.findall(r"\['([^']+)'\]", dest_expr)
            sk = re.findall(r"\['([^']+)'\]", src_expr)
            rt_prop = dk[-1] if dk else name_by_id.get(to, "")
            out_name = sk[-1] if sk else None
            rt_source.setdefault(to, {})[rt_prop] = {
                "producer_id": producer_id, "producer_name": producer,
                "output_name": out_name}

    def _src(producer_id: str | None, producer_name: str, output_name: str | None) -> dict:
        label = f"{producer_name} → {output_name}" if output_name else producer_name
        return {"label": label, "producer_id": producer_id, "output_name": output_name}

    wired: dict[str, dict] = {}
    extras: list[str] = []
    for e in edges:
        if str(e.get("to")) != str(op_id) or "input" not in (e.get("labels") or []):
            continue
        frm = str(e.get("from"))
        mapping = (e.get("properties") or {}).get("mapping") or {}
        if not mapping:
            extras.append(name_by_id.get(frm, "?"))
            continue
        for dest_expr, src_expr in mapping.items():
            param = _param_after_inputs(dest_expr)
            if not param:
                continue
            sk = re.findall(r"\['([^']+)'\]", src_expr)
            if "ResultType" in labels_by_id.get(frm, []):
                rt_prop = sk[-1] if sk else name_by_id.get(frm, "")
                info = rt_source.get(frm, {}).get(rt_prop)
                wired[param] = _src(
                    info["producer_id"], info["producer_name"], info["output_name"]
                ) if info else _src(None, name_by_id.get(frm, "?"), None)
            elif frm in op_ids:
                wired[param] = _src(
                    frm, name_by_id.get(frm, "?"), sk[-1] if sk else None)
            else:
                wired[param] = _src(None, name_by_id.get(frm, "?"), None)
    return wired, list(dict.fromkeys(extras))


def operator_output_targets(ap_data: dict, op_id: str) -> dict[str, str]:
    """``{output_name: "Consumer → in_param, …"}`` for one operator, tracing
    ``output`` edges forward through their ``ResultType`` node to every consumer."""
    nodes = ap_data.get("nodes", [])
    edges = ap_data.get("edges", [])
    labels_by_id = {n["id"]: n.get("labels", []) for n in nodes}
    name_by_id = {n["id"]: _node_name(n) for n in nodes}

    # {result_type_id: [(consumer_name, input_param|None)]}
    rt_consumers: dict[str, list[tuple[str, str | None]]] = {}
    for e in edges:
        if "input" not in (e.get("labels") or []):
            continue
        frm = str(e.get("from"))
        if "ResultType" not in labels_by_id.get(frm, []):
            continue
        consumer = name_by_id.get(str(e.get("to")), "?")
        mapping = (e.get("properties") or {}).get("mapping") or {}
        if not mapping:
            rt_consumers.setdefault(frm, []).append((consumer, None))
        for dest_expr in mapping:
            rt_consumers.setdefault(frm, []).append(
                (consumer, _param_after_inputs(dest_expr)))

    targets: dict[str, list[str]] = {}
    for e in edges:
        if str(e.get("from")) != str(op_id) or "output" not in (e.get("labels") or []):
            continue
        to = str(e.get("to"))
        mapping = (e.get("properties") or {}).get("mapping") or {}
        out_names = [re.findall(r"\['([^']+)'\]", src)[-1]
                     for src in mapping.values()
                     if re.findall(r"\['([^']+)'\]", src)] or [None]
        for out_name in out_names:
            for consumer, inp in rt_consumers.get(to, [(name_by_id.get(to, "?"), None)]):
                label = f"{consumer} → {inp}" if inp else consumer
                targets.setdefault(out_name, [])
                if label not in targets[out_name]:
                    targets[out_name].append(label)
    return {k: ", ".join(v) for k, v in targets.items()}


def extract_operator_output(result, name: str):
    """Best-effort pluck of a single named output from an operator's ``result``
    payload, whatever shape it arrived in."""
    if isinstance(result, dict):
        if name in result:
            return result[name]
        outs = result.get("outputs")
        if isinstance(outs, dict) and name in outs:
            return outs[name]
    return result


# Fill colours applied to operator nodes once an execution result is available,
# keyed by the per-operator ``status`` reported by ap-executor.
_STATUS_FILLCOLOR = {
    "success": "#8ae08a",
    "error": "#ff9999",
    "skipped": "#d9d9d9",
    "running": "#ffe08a",
    "pending": "#ffe08a",
}


def ap_to_graphviz(ap_data: dict, status_by_id: dict[str, str] | None = None) -> str:
    """Render an AP graph as Graphviz DOT.

    When ``status_by_id`` (``{node_id: status}``) is given, operator nodes are
    recoloured by execution status instead of their label-derived colour. Every
    other caller passes it as ``None`` and the output is unchanged.
    """
    nodes = ap_data.get("nodes", [])
    edges = ap_data.get("edges", [])

    id_map: dict[str, str] = {}
    lines = [
        "digraph AP {",
        '  rankdir=LR;',
        '  node [fontname="Arial" style=filled];',
        '  edge [fontname="Arial" fontsize=10];',
    ]

    for i, node in enumerate(nodes):
        safe = f"n{i}"
        id_map[node["id"]] = safe
        labels = node.get("labels", [])
        props = node.get("properties", {})
        name = props.get("name") or (labels[0] if labels else "?")
        primary = labels[0] if labels else "Unknown"

        if "Analytical_Pattern" in labels:
            color, shape = "lightblue", "ellipse"
        elif "Operator" in labels:
            color, shape = "lightsalmon", "box"
        elif "ResultType" in labels:
            color, shape = "lightyellow", "note"
        elif "Data" in labels:
            color, shape = "lightgreen", "box3d"
        else:
            color, shape = "lightgray", "diamond"

        if status_by_id:
            status = status_by_id.get(node["id"])
            if status in _STATUS_FILLCOLOR:
                color = _STATUS_FILLCOLOR[status]

        escaped_name = name.replace('"', '\\"')
        escaped_primary = primary.replace('"', '\\"')
        label = f"{escaped_name}\\n({escaped_primary})"

        if "Operator" in labels:
            inputs = props.get("inputs", [])
            outputs = props.get("outputs", [])
            in_sig = ", ".join(
                f"{p['name']}: {format_type(p)}" for p in inputs)
            out_sig = ", ".join(
                f"{p['name']}: {format_type(p)}" for p in outputs)
            signature = f"({in_sig}) -> ({out_sig})".replace('"', '\\"')
            label = f"{label}\\n{signature}"
        elif "ResultType" in labels:
            # The type is encoded as a second label alongside ResultType
            result_type = next(
                (lbl for lbl in labels if lbl != "ResultType"), None)
            if result_type:
                label = f"{escaped_name}: {result_type}"
        lines.append(
            f'  {safe} [label="{label}" fillcolor="{color}" shape={shape}];')

    for edge in edges:
        src = id_map.get(edge.get("from", ""))
        dst = id_map.get(edge.get("to", ""))
        edge_label = (edge.get("labels") or [""])[0].replace('"', '\\"')
        mapping = (edge.get("properties") or {}).get("mapping", {})
        if mapping:
            mapping_lines = "\\n".join(
                f"{_param_name(src_expr)} -> {_param_name(dst_expr)}"
                for src_expr, dst_expr in mapping.items()
            )
            edge_label = f"{edge_label}\\n{mapping_lines}" if edge_label else mapping_lines
        if src and dst:
            lines.append(f'  {src} -> {dst} [label="{edge_label}"];')

    lines.append("}")
    return "\n".join(lines)
