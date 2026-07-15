import logging
from os import getenv

import httpx
from kiota_abstractions.authentication.anonymous_authentication_provider import (
    AnonymousAuthenticationProvider,
)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter

from generated.ap_management.ap_management_client import ApManagementClient
from generated.ap_management.models.analytical_pattern import AnalyticalPattern
from generated.ap_management.models.compose_payload import ComposePayload
from generated.ap_management.models.plan_payload import PlanPayload
from generated.ap_management.models.suggested_parameter import SuggestedParameter
from utils import list_ap_files, load_ap_json

AP_MANAGEMENT_SERVICE_URL = getenv(
    "AP_MANAGEMENT_SERVICE_URL", "http://ap-management:5000")
MOMA_MANAGEMENT_SERVICE_URL = getenv(
    "MOMA_MANAGEMENT_SERVICE_URL", "http://moma-management:5000")

_log = logging.getLogger(__name__)


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


def _suggested_parameters_to_list(params: list[SuggestedParameter] | None) -> list[dict]:
    return [
        {"name": p.name, "type": p.type, "required": p.required, **(p.additional_data or {})}
        for p in (params or [])
    ]


async def plan_ap(task: str) -> dict:
    client = ApManagementClient(_create_adapter(AP_MANAGEMENT_SERVICE_URL))
    try:
        response = await client.api.v1.aps.plan.post(PlanPayload(task=task))
    except Exception:
        _log.exception("ap-management /plan call failed")
        raise
    if not response:
        return {}
    result = _ap_model_to_dict(response.ap) if response.ap else {}
    result["instantiation_parameters"] = _suggested_parameters_to_list(
        response.instantiation_parameters)
    return result


async def seed_aps_to_moma() -> None:
    base = MOMA_MANAGEMENT_SERVICE_URL.rstrip("/")
    async with httpx.AsyncClient() as client:
        for _, path, _ in list_ap_files():
            if path.split("/")[-1][:2] not in ("01", "02", "08"):
                continue
            data = load_ap_json(path)
            ap_id = next(
                (n["id"] for n in data.get("nodes", [])
                 if "Analytical_Pattern" in n.get("labels", [])),
                None,
            )
            if not ap_id:
                continue
            resp = await client.get(f"{base}/api/v1/aps/{ap_id}")
            if resp.status_code != 404:
                if resp.status_code != 200:
                    _log.warning("moma GET /aps/%s returned %s",
                                 ap_id, resp.status_code)
                continue
            body = {k: v for k, v in data.items() if k != "$schema"}
            try:
                resp = await client.post(f"{base}/api/v1/aps/", json=body)
                resp.raise_for_status()
                _log.info("Seeded AP %s into moma-management", ap_id)
            except httpx.HTTPStatusError:
                _log.exception("Failed to seed AP %s into moma-management: %s %s",
                               ap_id, resp.status_code, resp.text)
