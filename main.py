import asyncio
from pathlib import Path

import streamlit as st
from kiota_abstractions.api_error import APIError

from api import compose_aps, plan_ap, seed_aps_to_moma
from generated.ap_management.models.error_response import ErrorResponse
from utils import ap_to_graphviz, list_ap_files, load_ap_json

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


tab_compose, tab_plan = st.tabs(["⚡ Compose", "📋 Plan"])

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
                st.warning(f"Composition impossible: {exc.detail}")
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
            st.warning(f"Plan impossible: {exc.detail}")
        except APIError as exc:
            st.error(
                f"Plan request failed with status {exc.response_status_code}")
