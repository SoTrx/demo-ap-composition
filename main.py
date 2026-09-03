import asyncio
import json
from pathlib import Path

import httpx
import streamlit as st
from kiota_abstractions.api_error import APIError

from api import (
    AP_EXECUTOR_EXECUTE_URL,
    EXECUTION_ENABLED,
    compose_aps,
    execute_ap,
    plan_ap,
    seed_aps_to_moma,
)
from generated.ap_management.models.error_response import ErrorResponse
from utils import (
    ap_to_graphviz,
    extract_operator_output,
    format_type,
    list_ap_files,
    load_ap_json,
    operator_execution_order,
    operator_input_sources,
    operator_output_targets,
)

TITLE = "Analytical Pattern Explorer"


@st.cache_resource
def _warmup_moma() -> None:
    asyncio.run(seed_aps_to_moma())


_warmup_moma()

st.set_page_config(page_title=TITLE, layout="wide")
st.title(TITLE)

ap_files = list_ap_files()

# Group by category, preserving insertion order
_grouped: dict[str, list[tuple[str, str]]] = {}
for name, path, category in ap_files:
    _grouped.setdefault(category, []).append((name, path))

path_by_name = {name: path for name, path, _ in ap_files}
_prefix_to_name = {Path(path).stem[:2]: name for name, path, _ in ap_files}

_PLACEHOLDER = "Select an AP…"
_grouped_options: list[str] = [_PLACEHOLDER]
_headers: set[str] = set()
for _cat, _aps in _grouped.items():
    _header = f"── {_cat} ──"
    _grouped_options.append(_header)
    _headers.add(_header)
    _grouped_options.extend(name for name, _ in _aps)


def _format_option(opt: str) -> str:
    if opt in _headers:
        return opt
    if opt == _PLACEHOLDER:
        return opt
    return f"  {opt}"


_PRESET_PLACEHOLDER = "— Select a preset —"
_PRESETS: list[tuple[str, str | None, str | None, str]] = [
    (_PRESET_PLACEHOLDER, None, None, ""),
    ("One input to one output", "01", "02",
     "The simplest composition: AP1 produces a single output that feeds directly into AP2's single input."),
    ("Multiple outputs to one input", "03", "02",
     "AP1 exposes several outputs; the composer selects the right one to wire into AP2's input."),
    ("Object output to string input", "04", "02",
     "AP1 returns a structured object, requiring the composer to extract the correct field and convert it to the string expected by AP2."),
    ("Ambiguous array to string", "05", "02",
     "AP1 outputs an array of strings, forcing the composer to resolve the ambiguity before passing a single value to AP2."),
    ("Cross operator sourcing", "06", "07",
     "AP1 chains two operators internally; AP2 relies on a cross-operator source, exercising more complex dependency resolution."),
]
_PRESET_LABELS = [label for label, _, _, _ in _PRESETS]
_PRESET_MAP = {label: (p1, p2, desc)
               for label, p1, p2, desc in _PRESETS if p1 and p2}


def _apply_preset() -> None:
    label = st.session_state.get("preset")
    entry = _PRESET_MAP.get(label)
    if not entry:
        return
    p1, p2, _ = entry
    name1 = _prefix_to_name.get(p1)
    name2 = _prefix_to_name.get(p2)
    if name1 and name1 in _grouped_options:
        st.session_state["ap1"] = name1
    if name2 and name2 in _grouped_options:
        st.session_state["ap2"] = name2


def _is_valid_ap(sel: str) -> bool:
    return sel != _PLACEHOLDER and sel not in _headers


_PLAN_PRESET_PLACEHOLDER = "— Select a preset —"
_PLAN_PRESETS: list[tuple[str, str, str]] = [
    (_PLAN_PRESET_PLACEHOLDER, "", ""),
    ("NL To SQL + Explain (OK Scenario)", "Convert \"Find my stuff\"  into SQL and compute the provenance of the result",
     "Selects and wires the patterns needed to translate a natural-language question into SQL and produce a human-readable explanation."),
    ("NL To SQL + Explain + Report (OK Scenario)",
     "Translate \"Find my stuff\" to SQL, explain the query with provenance information, and produce a structured provenance report", "3 Steps workflow"),
    ("Impossible request (KO Scenario)", "Make a chocolate cake",
     "There are no chocolate cake info"),
    ("Partial request (KO Scenario)", "Convert \"Find my stuff\" into SQL and then convert the SQL to JSON",
     "The query-to-SQL pattern is available, but the SQL-to-JSON pattern is missing, so the plan cannot be completed. This is expected to FAIL"),
]
_PLAN_PRESET_LABELS = [label for label, _, _ in _PLAN_PRESETS]
_PLAN_PRESET_MAP = {label: (task, desc)
                    for label, task, desc in _PLAN_PRESETS if task}


def _apply_plan_preset() -> None:
    label = st.session_state.get("plan_preset")
    entry = _PLAN_PRESET_MAP.get(label)
    if not entry:
        return
    task, _ = entry
    st.session_state["plan_task"] = task


_EXEC_PRESET_PLACEHOLDER = "— Select a preset —"
_EXEC_PRESETS: list[dict] = json.loads(
    (Path(__file__).parent / "presets" / "execute_presets.json").read_text()
)
_EXEC_PRESET_LABELS = [_EXEC_PRESET_PLACEHOLDER] + [p["label"] for p in _EXEC_PRESETS]
_EXEC_PRESET_MAP = {p["label"]: p for p in _EXEC_PRESETS}


def _apply_exec_preset() -> None:
    preset = _EXEC_PRESET_MAP.get(st.session_state.get("exec_preset"))
    if preset:
        st.session_state["exec_ap_json"] = json.dumps(preset["instance"], indent=2)


def _apply_planexec_preset() -> None:
    preset = _EXEC_PRESET_MAP.get(st.session_state.get("planexec_preset"))
    if preset:
        st.session_state["planexec_task"] = preset["nl"]


def _seed_state_from_params(ap_data: dict | None, params: list | None) -> dict:
    """Best-effort ``state`` (``{operator_id: {input_name: value}}``) built by
    matching each suggested parameter's ``name`` to an operator input of the
    same name."""
    state: dict[str, dict] = {}
    if not ap_data or not params:
        return state
    op_nodes = [n for n in ap_data.get("nodes", []) if "Operator" in n.get("labels", [])]
    for param in params:
        name, value = param.get("name"), param.get("suggested_value")
        if name is None or value is None:
            continue
        for node in op_nodes:
            inputs = node.get("properties", {}).get("inputs") or []
            if any(i.get("name") == name for i in inputs):
                state.setdefault(node.get("id"), {})[name] = value
    return state


def _split_instance(data) -> tuple[dict | None, dict]:
    """Accept an AP *instance* (``{"ap": {...}, "state": {...}}``) — the shape
    ap-executor's ``/execute`` takes — or, for convenience, a bare AP template
    (``{"nodes": [...], "edges": [...]}``). Returns ``(ap, state)`` or
    ``(None, {})`` if it is neither."""
    if isinstance(data, dict) and isinstance(data.get("ap"), dict):
        return data["ap"], (data.get("state") or {})
    if isinstance(data, dict) and data.get("nodes"):
        return data, {}
    return None, {}


def _err_detail(exc: ErrorResponse) -> str:
    """A useful message even when the service returned an empty body (e.g. a bare
    502 from a gateway in front of ap-management), where ``detail`` is ``None``."""
    return exc.detail or (
        f"upstream service returned HTTP {getattr(exc, 'response_status_code', '?')} "
        "with no detail (it is likely down or its own upstream — e.g. the LLM at "
        "LLM_API_BASE — failed)")


def _short(value) -> str:
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True)
    return text if len(text) <= 200 else text[:197] + "…"


_STATUS_ICON = {
    "success": "✅", "error": "❌", "skipped": "⏭️",
    "running": "⏳", "pending": "⏳",
}


def _render_exec_plan(
    ap_data: dict,
    state: dict,
    *,
    results_by_id: dict | None = None,
    status_by_id: dict | None = None,
    errors_by_id: dict | None = None,
) -> None:
    """The operator sequence ap-executor walks, and — per step — where each input
    comes from and where each output goes.

    Before a run (``results_by_id``/``status_by_id`` are ``None``) it is a preview
    of what **Execute** will do; after a run it is filled in with the real
    per-operator status and output values.
    """
    ops = operator_execution_order(ap_data)
    if not ops:
        st.info("This Analytical Pattern has no operators to execute.")
        return

    ran = results_by_id is not None or status_by_id is not None
    st.caption(
        f"ap-executor {'ran' if ran else 'will run'} these {len(ops)} operator(s) "
        "in dependency order, feeding each one's outputs into the operators "
        "downstream:")

    for pos, op in enumerate(ops, 1):
        oid = op["id"]
        props = op.get("properties", {}) or {}
        title = props.get("name") or (op.get("labels") or ["Operator"])[0]
        step = props.get("step")
        bits = [f"**{pos}. {title}**"]
        if step is not None:
            bits.append(f"· step {step}")
        if status_by_id and status_by_id.get(oid):
            s = status_by_id[oid]
            bits.append(f"· {_STATUS_ICON.get(s, '')} `{s}`")
        st.markdown(" ".join(bits))
        if props.get("description"):
            st.caption(props["description"])

        op_state = (state or {}).get(oid, {}) or {}
        wired, extras = operator_input_sources(ap_data, oid)
        pending = "produced at run time"

        inputs = props.get("inputs") or []
        if inputs:
            st.markdown("_Inputs_")
            in_rows = []
            for p in inputs:
                nm = p.get("name")
                src = wired.get(nm)
                if nm in op_state:
                    source_cell, value_cell = "caller `state`", _short(op_state[nm])
                elif src:
                    source_cell = src["label"]
                    resolved = None
                    if (results_by_id and src["output_name"]
                            and src["producer_id"] in results_by_id):
                        resolved = extract_operator_output(
                            results_by_id[src["producer_id"]], src["output_name"])
                    value_cell = (
                        _short(resolved) if resolved is not None
                        else "—" if ran
                        else pending
                    )
                else:
                    source_cell, value_cell = "—", "— not set —"
                in_rows.append({
                    "Parameter": nm,
                    "Type": format_type(p),
                    "Required": p.get("required"),
                    "Source": source_cell,
                    "Value": value_cell,
                })
            st.table(in_rows)
        if extras:
            st.caption("Also wired in: " + ", ".join(f"`{e}`" for e in extras))

        outputs = props.get("outputs") or []
        targets = operator_output_targets(ap_data, oid)
        if outputs:
            st.markdown("_Outputs_")
            out_rows = []
            for p in outputs:
                nm = p.get("name")
                if results_by_id and oid in results_by_id:
                    value_cell = _short(extract_operator_output(results_by_id[oid], nm))
                elif errors_by_id and oid in errors_by_id:
                    value_cell = f"⚠️ {_short(errors_by_id[oid])}"
                else:
                    value_cell = "—" if ran else pending
                out_rows.append({
                    "Parameter": nm,
                    "Type": format_type(p),
                    "Value": value_cell,
                    "Flows to": targets.get(nm) or "final result",
                })
            st.table(out_rows)

        if pos < len(ops):
            st.markdown(
                "<div style='text-align:center;color:#888;font-size:1.3rem;"
                "line-height:1'>&#8595;</div>",
                unsafe_allow_html=True,
            )


def _render_execution_result(ap_data: dict, exec_result: dict, state: dict | None = None) -> None:
    operators = exec_result.get("operators") or []
    status_by_id = {o.get("operator_id"): o.get("status") for o in operators}
    results_by_id = {
        o.get("operator_id"): o.get("result")
        for o in operators if o.get("status") == "success"
    }
    errors_by_id = {
        o.get("operator_id"): o.get("error")
        for o in operators if o.get("status") != "success" and o.get("error") is not None
    }

    overall = exec_result.get("status", "?")
    st.subheader("Execution result")
    _banner = {"success": st.success, "error": st.error, "failed": st.error}.get(
        overall, st.info)
    _banner(f"{_STATUS_ICON.get(overall, '')} **Overall status:** `{overall}`")

    _render_exec_plan(
        ap_data, state or {},
        results_by_id=results_by_id,
        status_by_id=status_by_id,
        errors_by_id=errors_by_id,
    )

    terminals = [
        o for o in operator_execution_order(ap_data)
        if not operator_output_targets(ap_data, o["id"])
        and o["id"] in results_by_id
    ]
    if terminals:
        st.markdown("**Final result**")
        for o in terminals:
            res = results_by_id[o["id"]]
            (st.json if isinstance(res, (dict, list)) else st.write)(res)

    if operators:
        st.table([
            {
                "Operator": o.get("operator_name"),
                "Status": o.get("status"),
                "Mode": o.get("execution_mode") or "—",
                "Service": o.get("service_instance") or "—",
                "Result / error": _short(
                    o.get("result") if o.get("status") == "success" else o.get("error")),
            }
            for o in operators
        ])
    with st.expander("Raw executor response (JSON)"):
        st.json(exec_result)


tab_compose, tab_plan, tab_execute, tab_planexec = st.tabs(
    ["⚡ Compose", "📋 Plan", "▶️ Execute", "📋▶️ Plan + Execute"])

with tab_compose:
    st.markdown(
        "Select two Analytical Patterns below, inspect their graphs, then click **Compose** "
        "to call the `/compose` endpoint and see the resulting combined pattern."
    )

    st.selectbox(
        "Preset",
        _PRESET_LABELS,
        key="preset",
        on_change=_apply_preset,
        help="Pre-select a pair of Analytical Patterns to compose.",
    )

    _active_preset = st.session_state.get("preset", _PRESET_PLACEHOLDER)
    _active_entry = _PRESET_MAP.get(_active_preset)
    if _active_entry:
        st.caption(_active_entry[2])

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Analytical Pattern 1")
        sel1 = st.selectbox("Choose AP 1", _grouped_options,
                            format_func=_format_option, key="ap1")
        if _is_valid_ap(sel1):
            ap1_data = load_ap_json(path_by_name[sel1])
            st.graphviz_chart(ap_to_graphviz(ap1_data), width='stretch')
        else:
            ap1_data = None
            st.info("Pick a pattern to see its graph.")

    with col2:
        st.subheader("Analytical Pattern 2")
        sel2 = st.selectbox("Choose AP 2", _grouped_options,
                            format_func=_format_option, key="ap2")
        if _is_valid_ap(sel2):
            ap2_data = load_ap_json(path_by_name[sel2])
            st.graphviz_chart(ap_to_graphviz(ap2_data), width='stretch')
        else:
            ap2_data = None
            st.info("Pick a pattern to see its graph.")

    st.divider()

    if ap1_data and ap2_data:
        if st.button("⚡ Compose", type="primary", width='stretch'):
            try:
                with st.spinner("Composing analytical patterns…"):
                    result = asyncio.run(compose_aps(ap1_data, ap2_data))
                st.subheader("Composed Analytical Pattern")
                if result.get("nodes"):
                    st.graphviz_chart(ap_to_graphviz(result), width='stretch')
                else:
                    st.json(result)
                with st.expander("Raw composer response (JSON)"):
                    st.json(result)
            except ErrorResponse as exc:
                st.warning(f"Composition impossible: {_err_detail(exc)}")
            except APIError as exc:
                st.error(
                    f"Compose request failed with status {exc.response_status_code}")
    else:
        st.info("Select two analytical patterns above to enable composition.")

with tab_plan:
    st.markdown(
        "Describe a task and click **Plan** to call the `/plan` endpoint, "
        "which selects and wires the Analytical Patterns needed to fulfil it."
    )

    st.selectbox(
        "Preset",
        _PLAN_PRESET_LABELS,
        key="plan_preset",
        on_change=_apply_plan_preset,
        help="Pre-fill the task with a predefined example.",
    )

    _active_plan_preset = st.session_state.get(
        "plan_preset", _PLAN_PRESET_PLACEHOLDER)
    _active_plan_entry = _PLAN_PRESET_MAP.get(_active_plan_preset)
    if _active_plan_entry:
        st.caption(_active_plan_entry[1])

    st.divider()

    task = st.text_input("Task", key="plan_task",
                         placeholder="Describe the task…")

    if st.button("📋 Plan", type="primary", width='stretch', disabled=not task):
        try:
            with st.spinner("Planning…"):
                result = asyncio.run(plan_ap(task))
            st.subheader("Planned Analytical Pattern")
            if result.get("nodes"):
                st.graphviz_chart(ap_to_graphviz(result), width='stretch')
            else:
                st.json(result)

            params = result.get("instantiation_parameters") or []
            if params:
                st.subheader("Suggested Instantiation Parameters")
                st.table([
                    {
                        "Name": p.get("name"),
                        "Type": p.get("type"),
                        "Required": p.get("required"),
                        "Suggested value": p.get("suggested_value"),
                    }
                    for p in params
                ])

            with st.expander("Raw planner response (JSON)"):
                st.json(result)
        except ErrorResponse as exc:
            st.warning(f"Plan impossible: {_err_detail(exc)}")
        except APIError as exc:
            st.error(
                f"Plan request failed with status {exc.response_status_code}")

def _executor_disabled_notice() -> None:
    st.warning(
        "`AP_EXECUTOR_EXECUTE_URL` is not provided, execution is disabled on this instance.")


with tab_execute:
    st.markdown(
        "Load an **Analytical Pattern instance** — `{ \"ap\": { … }, \"state\": { … } }`, "
        "the template plus the per-operator parameter values to run it with — then click "
        "**Execute**. Execution walks the operators in dependency order on the configured "
        "[`ap-executor`](https://github.com/SoTrx/ap-executor), feeding each operator's "
        "output into the next."
    )

    st.selectbox(
        "Preset",
        _EXEC_PRESET_LABELS,
        key="exec_preset",
        on_change=_apply_exec_preset,
        help="Load a ready-made Analytical Pattern instance into the editor below.",
    )

    _active_exec_preset = _EXEC_PRESET_MAP.get(st.session_state.get("exec_preset"))
    if _active_exec_preset and _active_exec_preset.get("description"):
        st.caption(_active_exec_preset["description"])

    st.divider()

    st.session_state.setdefault("exec_ap_json", "")

    ap_text = st.text_area(
        "Analytical Pattern instance (JSON)", key="exec_ap_json", height=360,
        placeholder='Pick a preset above, or paste {"ap": {"nodes": …}, "state": {…}} here…',
    )

    parsed = None
    if ap_text.strip():
        try:
            parsed = json.loads(ap_text)
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")

    exec_ap_data, exec_state = _split_instance(parsed) if parsed is not None else (None, {})

    if not EXECUTION_ENABLED:
        _executor_disabled_notice()

    if parsed is None:
        st.info("Choose a preset above or paste an Analytical Pattern instance to run.")
    elif exec_ap_data is None:
        st.warning(
            'Expected an AP instance `{ "ap": { "nodes": … }, "state": { … } }` '
            '(a bare `{ "nodes": … }` template is also accepted).')
    else:
        st.subheader("What Execute will do")
        _render_exec_plan(exec_ap_data, exec_state)
        if not exec_state:
            st.caption("`state` is empty — operators will run without caller parameters.")

        if st.button("▶️ Execute", type="primary", width='stretch',
                     disabled=not EXECUTION_ENABLED):
            try:
                with st.spinner("Executing on ap-executor…"):
                    exec_result = asyncio.run(execute_ap(exec_ap_data, exec_state))
                _render_execution_result(exec_ap_data, exec_result, exec_state)
            except ErrorResponse as exc:
                st.warning(f"Execution impossible: {_err_detail(exc)}")
            except (httpx.HTTPError, ConnectionError, OSError):
                st.error(
                    f"Couldn't reach ap-executor at `{AP_EXECUTOR_EXECUTE_URL}`. "
                    "Check `AP_EXECUTOR_EXECUTE_URL`.")
            except APIError as exc:
                st.error(
                    f"Execute request failed with status {exc.response_status_code}")
            except Exception as exc:  # noqa: BLE001 — surface unexpected errors
                st.error(f"Execution error: {exc}")

with tab_planexec:
    st.markdown(
        "Describe a task, then click **Plan + Execute**: `/plan` selects and wires the "
        "Analytical Patterns for it, its suggested instantiation parameters seed the "
        "`state`, and the resulting instance is run on the configured "
        "[`ap-executor`](https://github.com/SoTrx/ap-executor) — Plan and Execute in one go."
    )

    st.selectbox(
        "Preset",
        _EXEC_PRESET_LABELS,
        key="planexec_preset",
        on_change=_apply_planexec_preset,
        help="Pre-fill the task with a predefined example.",
    )

    _active_planexec_preset = _EXEC_PRESET_MAP.get(st.session_state.get("planexec_preset"))
    if _active_planexec_preset and _active_planexec_preset.get("description"):
        st.caption(_active_planexec_preset["description"])

    st.divider()

    if not EXECUTION_ENABLED:
        _executor_disabled_notice()

    pe_task = st.text_input("Task", key="planexec_task",
                            placeholder="Describe the task…")

    if st.button("📋▶️ Plan + Execute", type="primary", width='stretch',
                 disabled=not (pe_task and EXECUTION_ENABLED)):
        try:
            with st.spinner("Planning…"):
                plan_result = asyncio.run(plan_ap(pe_task))

            if not plan_result.get("nodes"):
                st.warning("Planning produced no Analytical Pattern.")
                st.json(plan_result)
            else:
                pe_ap_data = {k: v for k, v in plan_result.items()
                              if k != "instantiation_parameters"}
                pe_params = plan_result.get("instantiation_parameters") or []
                pe_state = _seed_state_from_params(pe_ap_data, pe_params)

                st.subheader("Planned Analytical Pattern")
                st.graphviz_chart(ap_to_graphviz(pe_ap_data), width='stretch')
                if pe_params:
                    st.subheader("Suggested Instantiation Parameters")
                    st.table([
                        {
                            "Name": p.get("name"),
                            "Type": p.get("type"),
                            "Required": p.get("required"),
                            "Suggested value": p.get("suggested_value"),
                        }
                        for p in pe_params
                    ])

                with st.spinner("Executing on ap-executor…"):
                    pe_result = asyncio.run(execute_ap(pe_ap_data, pe_state))
                _render_execution_result(pe_ap_data, pe_result, pe_state)
        except ErrorResponse as exc:
            st.warning(f"Plan + execute impossible: {_err_detail(exc)}")
        except (httpx.HTTPError, ConnectionError, OSError):
            st.error(
                f"Couldn't reach ap-executor at `{AP_EXECUTOR_EXECUTE_URL}`. "
                "Check `AP_EXECUTOR_EXECUTE_URL`.")
        except APIError as exc:
            st.error(f"Request failed with status {exc.response_status_code}")
        except Exception as exc:  # noqa: BLE001 — surface unexpected errors
            st.error(f"Plan + execute error: {exc}")
