import asyncio
import json
import logging
import time
from os import getenv

import httpx
from kiota_abstractions.api_error import APIError
from kiota_abstractions.authentication.anonymous_authentication_provider import (
    AnonymousAuthenticationProvider,
)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_serialization_json.json_serialization_writer import JsonSerializationWriter

from generated.ap_executor.ap_executor_client import ApExecutorClient
from generated.ap_executor.models.analytical_pattern import (
    AnalyticalPattern as ExecutorAnalyticalPattern,
)
from generated.ap_executor.models.ap_instance import ApInstance as ExecutorApInstance
from generated.ap_management.ap_management_client import ApManagementClient
from generated.ap_management.models.analytical_pattern import AnalyticalPattern
from generated.ap_management.models.compose_payload import ComposePayload
from generated.ap_management.models.plan_payload import PlanPayload
from generated.ap_management.models.suggested_parameter import SuggestedParameter
from utils import (
    DATASET_ROOT_LABEL,
    list_ap_files,
    list_dataset_files,
    load_ap_json,
)

AP_MANAGEMENT_SERVICE_URL = getenv(
    "AP_MANAGEMENT_SERVICE_URL", "http://ap-management:5000")
MOMA_MANAGEMENT_SERVICE_URL = getenv(
    "MOMA_MANAGEMENT_SERVICE_URL", "http://moma-management:5000")
AP_EXECUTOR_SERVICE_URL = getenv(
    "AP_EXECUTOR_SERVICE_URL", "http://ap-executor:5000")
# Full URL of the synchronous execute endpoint. Override this directly when the
# executor sits behind a gateway with a non-default path prefix, e.g.
#   http://datagems.127.0.0.1.sslip.io:8080/moma2/v1/api/aps/execute
# Otherwise it is derived from AP_EXECUTOR_SERVICE_URL + the stock route.
AP_EXECUTOR_EXECUTE_URL = getenv("AP_EXECUTOR_EXECUTE_URL") or (
    AP_EXECUTOR_SERVICE_URL.rstrip("/") + "/api/v1/aps/execute")

# Execution is only offered when the deployer has explicitly pointed the demo at
# a reachable executor via AP_EXECUTOR_EXECUTE_URL. Without it, the Execute and
# Plan + Execute tabs disable their run buttons.
EXECUTION_ENABLED = bool(getenv("AP_EXECUTOR_EXECUTE_URL"))

# How long to keep polling the async execution endpoint after a sync 504.
_ASYNC_POLL_TIMEOUT_SECONDS = 180
_ASYNC_POLL_INTERVAL_SECONDS = 2

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
    """``operator_id`` / ``operator_name`` are spelled out rather than left to the
    ``additional_data`` spread: they are typed properties on the model, so they never
    land in ``additional_data``. ``operator_id`` is what keys the executor's ``state``
    (see ``main._seed_state_from_params``) — a parameter's ``name`` alone is ambiguous
    as soon as an AP has more than one operator declaring an input of that name."""
    return [
        {
            "name": p.name,
            "type": p.type,
            "required": p.required,
            "operator_id": p.operator_id,
            "operator_name": p.operator_name,
            **(p.additional_data or {}),
        }
        for p in (params or [])
    ]


async def plan_ap(
    task: str,
    dataset_ids: list[str] | None = None,
    allow_magic_operator: bool = False,
) -> dict:
    """Plan an AP for *task*.

    ``dataset_ids`` grounds the plan on datasets held by moma-management: their kinds
    constrain which operators may apply (a SQL operator needs a relational/tabular
    dataset) and their table/column names ground the suggested parameter values. When
    none of them is compatible with the planned AP, ap-management fails the request with
    a 422 rather than letting the executor fail later.

    ``allow_magic_operator`` lets a step no catalogued AP covers be filled by a generic
    LLM-backed "magic" operator instead of failing with a 404.

    Returns ``{"ap", "instantiation_parameters", "datasets", "used_magic_operator"}`` —
    the AP stays nested under ``ap`` so it can be handed to the executor (or the graph
    renderer) without having to strip the plan metadata off it.
    """
    client = ApManagementClient(_create_adapter(AP_MANAGEMENT_SERVICE_URL))
    payload = PlanPayload(
        task=task,
        dataset_ids=list(dataset_ids or []),
        allow_magic_operator=allow_magic_operator,
    )
    try:
        response = await client.api.v1.aps.plan.post(payload)
    except Exception:
        _log.exception("ap-management /plan call failed")
        raise
    if not response:
        return {}
    return {
        "ap": _ap_model_to_dict(response.ap) if response.ap else {},
        "instantiation_parameters": _suggested_parameters_to_list(
            response.instantiation_parameters),
        "datasets": [
            {"id": d.id, "name": d.name, "kinds": d.kinds or []}
            for d in (response.datasets or [])
        ],
        "used_magic_operator": bool(response.used_magic_operator),
    }


def _kiota_model_to_dict(model) -> dict:
    """Re-serialize a Kiota response model to the plain JSON dict it came from.

    Going back through the JSON writer collapses the ``anyOf: [T, null]``
    composed-type wrappers Kiota generates (``OperatorResult_error`` &c.) without
    any per-field unwrapping.
    """
    if model is None:
        return {}
    writer = JsonSerializationWriter()
    writer.write_object_value(None, model)
    return json.loads(writer.get_serialized_content() or "{}")


def _build_ap_instance(ap_data: dict, state: dict) -> ExecutorApInstance:
    payload = {k: v for k, v in ap_data.items() if k != "$schema"}
    instance = ExecutorApInstance()
    instance.ap = ExecutorAnalyticalPattern(payload)
    instance.additional_data = {"state": state or {}}
    return instance


async def execute_ap(ap_data: dict, state: dict) -> dict:
    """Run an AP on the real ap-executor service.

    Tries the synchronous endpoint first; on its 504 ("still running") falls back
    to dispatching an async task and polling until it settles. Returns an
    ``ExecutionResult``-shaped dict.
    """
    client = ApExecutorClient(_create_adapter(AP_EXECUTOR_SERVICE_URL))
    instance = _build_ap_instance(ap_data, state)

    # Pin every call to AP_EXECUTOR_EXECUTE_URL (and paths derived from it) rather
    # than Kiota's built-in route template, so a gateway path prefix Just Works.
    execute_url = AP_EXECUTOR_EXECUTE_URL.rstrip("/")
    async_url = f"{execute_url}/async"

    try:
        response = await client.api.v1.aps.execute.with_url(execute_url).post(body=instance)
        return _kiota_model_to_dict(response)
    except APIError as exc:
        if getattr(exc, "response_status_code", None) != 504:
            _log.exception("ap-executor /execute call failed")
            raise

    task = await client.api.v1.aps.execute.async_.with_url(async_url).post(body=instance)
    task_id = getattr(task, "task_id", None)
    if not task_id:
        raise RuntimeError("ap-executor async dispatch returned no task_id")

    deadline = time.monotonic() + _ASYNC_POLL_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        await asyncio.sleep(_ASYNC_POLL_INTERVAL_SECONDS)
        poll = _kiota_model_to_dict(
            await client.api.v1.aps.execute.async_.by_task_id(task_id)
            .with_url(f"{async_url}/{task_id}").get())
        status = poll.get("status")
        if status == "success":
            return poll.get("result") or {}
        if status in ("error", "not_found"):
            raise RuntimeError(
                f"ap-executor execution {status}: {poll.get('error') or 'no detail'}")
    raise TimeoutError("ap-executor execution did not finish in time")


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


async def seed_datasets_to_moma() -> None:
    """Seed the demo datasets in ``assets/datasets/`` into moma-management.

    The planner's ``dataset_ids`` are resolved through moma, so without these the
    dataset picker in the Plan tabs would have nothing to offer on a fresh stack. Same
    idempotency rule as :func:`seed_aps_to_moma`: only POST what is not already there.
    """
    base = MOMA_MANAGEMENT_SERVICE_URL.rstrip("/")
    async with httpx.AsyncClient() as client:
        for path in list_dataset_files():
            data = load_ap_json(path)
            dataset_id = next(
                (n["id"] for n in data.get("nodes", [])
                 if DATASET_ROOT_LABEL in n.get("labels", [])),
                None,
            )
            if not dataset_id:
                continue
            resp = await client.get(f"{base}/api/v1/datasets/{dataset_id}")
            if resp.status_code != 404:
                if resp.status_code != 200:
                    _log.warning("moma GET /datasets/%s returned %s",
                                 dataset_id, resp.status_code)
                continue
            body = {k: v for k, v in data.items() if k != "$schema"}
            try:
                resp = await client.post(f"{base}/api/v1/datasets/", json=body)
                resp.raise_for_status()
                _log.info("Seeded dataset %s into moma-management", dataset_id)
            except httpx.HTTPStatusError:
                _log.exception("Failed to seed dataset %s into moma-management: %s %s",
                               dataset_id, resp.status_code, resp.text)


async def list_datasets() -> list[dict]:
    """``[{"id", "name", "kinds"}]`` for every dataset moma-management holds.

    Plain httpx rather than the generated client: moma types this response as a bare
    ``additionalProperties: true`` object, so Kiota hands back an untyped blob anyway.

    moma returns each dataset as a whole PG-JSON graph, so the name comes off the
    ``sc:Dataset`` root node and ``kinds`` is the set of the other nodes' labels — the
    same projection ap-management makes internally to decide which operators can run
    against a dataset (``RelationalDatabase``/``Table`` for SQL, ``PdfSet`` for PDF …).
    """
    base = MOMA_MANAGEMENT_SERVICE_URL.rstrip("/")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{base}/api/v1/datasets/",
                                    params={"pageSize": 100})
            resp.raise_for_status()
        except httpx.HTTPError:
            _log.exception("moma GET /datasets/ failed")
            return []

    datasets = []
    for graph in (resp.json().get("datasets") or []):
        nodes = graph.get("nodes") or []
        root = next(
            (n for n in nodes if DATASET_ROOT_LABEL in (n.get("labels") or [])), None)
        if not root:
            continue
        datasets.append({
            "id": str(root.get("id")),
            "name": (root.get("properties") or {}).get("name") or str(root.get("id")),
            "kinds": list(dict.fromkeys(
                label
                for node in nodes
                for label in (node.get("labels") or [])
                if label != DATASET_ROOT_LABEL
            )),
        })
    return datasets
