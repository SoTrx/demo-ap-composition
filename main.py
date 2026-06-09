import asyncio

import streamlit as st
from kiota_abstractions.api_error import APIError

from api import compose_aps
from generated.ap_management.models.error_response import ErrorResponse
from utils import ap_to_graphviz, list_ap_files, load_ap_json

TITLE = "Analytical Pattern Composer"

st.set_page_config(page_title=TITLE, layout="wide")
st.title(TITLE)
st.markdown(
    "Select two Analytical Patterns below, inspect their graphs, then click **Compose** "
    "to call the `/compose` endpoint and see the resulting combined pattern."
)

ap_files = list_ap_files()

# Group by category, preserving insertion order
_grouped: dict[str, list[tuple[str, str]]] = {}
for name, path, category in ap_files:
    _grouped.setdefault(category, []).append((name, path))

path_by_name = {name: path for name, path, _ in ap_files}

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

st.divider()

col1, col2 = st.columns(2)

def _is_valid_ap(sel: str) -> bool:
    return sel != _PLACEHOLDER and sel not in _headers


with col1:
    st.subheader("Analytical Pattern 1")
    sel1 = st.selectbox("Choose AP 1", _grouped_options, format_func=_format_option, key="ap1")
    if _is_valid_ap(sel1):
        ap1_data = load_ap_json(path_by_name[sel1])
        st.graphviz_chart(ap_to_graphviz(ap1_data), width='stretch')
    else:
        ap1_data = None
        st.info("Pick a pattern to see its graph.")

with col2:
    st.subheader("Analytical Pattern 2")
    sel2 = st.selectbox("Choose AP 2", _grouped_options, format_func=_format_option, key="ap2")
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
        except ErrorResponse as exc:
            st.warning(f"Composition impossible: {exc.detail}")
        except APIError as exc:
            st.error(
                f"Compose request failed with status {exc.response_status_code}")
else:
    st.info("Select two analytical patterns above to enable composition.")
