import copy
import json
import logging
from os import getenv

from kiota_abstractions.api_error import APIError
from kiota_abstractions.authentication.anonymous_authentication_provider import (
    AnonymousAuthenticationProvider,
)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter

from generated.ap_management.ap_management_client import ApManagementClient
from generated.ap_management.models.analytical_pattern import AnalyticalPattern
from generated.ap_management.models.compose_payload import ComposePayload
from generated.ap_management.models.plan_payload import PlanPayload
from generated.moma_management.models.analytical_pattern_input import (
    AnalyticalPatternInput,
)
from generated.moma_management.moma_management_client import MomaManagementClient
from utils import list_ap_files, load_ap_json

AP_MANAGEMENT_SERVICE_URL = getenv(
    "AP_MANAGEMENT_SERVICE_URL", "http://ap-management:5000")
MOMA_MANAGEMENT_SERVICE_URL = getenv(
    "MOMA_MANAGEMENT_SERVICE_URL", "http://moma-management:5000")

_log = logging.getLogger(__name__)


def _neo4j_safe(data: dict) -> dict:
    """Serialize node properties that are objects/arrays-of-objects to JSON strings.

    Neo4j only accepts primitive types and arrays of primitives as property values.
    Operator nodes carry `inputs`/`outputs` as arrays of objects, which must be
    stringified before the graph repository writes them.
    """
    data = copy.deepcopy(data)
    for node in data.get("nodes", []):
        props = node.get("properties", {})
        for key, value in props.items():
            if isinstance(value, dict):
                props[key] = json.dumps(value)
            elif isinstance(value, list) and any(isinstance(v, (dict, list)) for v in value):
                props[key] = json.dumps(value)
    return data


def _create_adapter(base_url: str) -> HttpxRequestAdapter:
    adapter = HttpxRequestAdapter(AnonymousAuthenticationProvider())
    adapter.base_url = base_url
    return adapter


def _ap_model_to_dict(ap: AnalyticalPattern) -> dict:
    nodes = []
    for n in (ap.nodes or []):
        nodes.append({
            "id": str(n.id) if n.id else "",
            "labels": n.labels or [],
            "properties": (n.properties.additional_data if n.properties else {}),
        })
    edges = []
    for e in (ap.edges or []):
        d = dict(e.additional_data)
        for key in ("from", "to"):
            if key in d:
                d[key] = str(d[key])
        edges.append(d)
    return {"nodes": nodes, "edges": edges}


async def compose_aps(ap1_data: dict, ap2_data: dict) -> dict:
    client = ApManagementClient(_create_adapter(AP_MANAGEMENT_SERVICE_URL))
    payload = ComposePayload()
    payload.ap1 = AnalyticalPattern(ap1_data)
    payload.ap2 = AnalyticalPattern(ap2_data)
    try:
        response = await client.api.v1.aps.compose.post(body=payload)
    except Exception:
        _log.exception("ap-management /compose call failed")
        raise
    return _ap_model_to_dict(response) if response else {}


async def plan_ap(task: str) -> dict:
    client = ApManagementClient(_create_adapter(AP_MANAGEMENT_SERVICE_URL))
    try:
        response = await client.api.v1.aps.plan.post(PlanPayload(task=task))
    except Exception:
        _log.exception("ap-management /compose call failed")
        raise
    return _ap_model_to_dict(response) if response else {}


async def seed_aps_to_moma() -> None:
    client = MomaManagementClient(_create_adapter(MOMA_MANAGEMENT_SERVICE_URL))
    for _, path, _ in list_ap_files():
        data = load_ap_json(path)
        ap_id = next(
            (n["id"] for n in data.get("nodes", [])
             if "Analytical_Pattern" in n.get("labels", [])),
            None,
        )
        if not ap_id:
            continue
        try:
            await client.api.v1.aps.by_id(ap_id).get()
            continue
        except APIError as exc:
            if exc.response_status_code != 404:
                _log.warning("moma GET /aps/%s failed with %s",
                             ap_id, exc.response_status_code)
                continue
        payload = AnalyticalPatternInput()
        payload.additional_data = _neo4j_safe(data)
        try:
            await client.api.v1.aps.empty_path_segment.post(payload)
            _log.info("Seeded AP %s into moma-management", ap_id)
        except Exception:
            _log.exception("Failed to seed AP %s into moma-management", ap_id)
