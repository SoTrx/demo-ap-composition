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


def _format_type(param: dict) -> str:
    t = param.get("type", "?")
    if t == "object":
        fields = param.get("properties", {})
        inner = ", ".join(f"{k}: {v.get('type', '?')}" for k, v in fields.items())
        return "{" + inner + "}" if inner else "object"
    if t == "array":
        item_type = param.get("items", {}).get("type", "any")
        return f"{item_type}[]"
    return t


def ap_to_graphviz(ap_data: dict) -> str:
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

        escaped_name = name.replace('"', '\\"')
        escaped_primary = primary.replace('"', '\\"')
        label = f"{escaped_name}\\n({escaped_primary})"

        if "Operator" in labels:
            inputs = props.get("inputs", [])
            outputs = props.get("outputs", [])
            in_sig = ", ".join(f"{p['name']}: {_format_type(p)}" for p in inputs)
            out_sig = ", ".join(f"{p['name']}: {_format_type(p)}" for p in outputs)
            signature = f"({in_sig}) -> ({out_sig})".replace('"', '\\"')
            label = f"{label}\\n{signature}"
        elif "ResultType" in labels:
            # The type is encoded as a second label alongside ResultType
            result_type = next((lbl for lbl in labels if lbl != "ResultType"), None)
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
