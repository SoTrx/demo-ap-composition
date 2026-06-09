import logging
from os import getenv

from kiota_abstractions.authentication.anonymous_authentication_provider import (
    AnonymousAuthenticationProvider,
)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_serialization_json.json_serialization_writer import JsonSerializationWriter

from generated.ap_management.ap_management_client import ApManagementClient
from generated.ap_management.models.compose_payload import ComposePayload
from generated.ap_management.models.compose_payload_ap1 import ComposePayload_ap1
from generated.ap_management.models.compose_payload_ap2 import ComposePayload_ap2
from generated.ap_management.models.error_response import ErrorResponse

AP_MANAGEMENT_SERVICE_URL = getenv(
    "AP_MANAGEMENT_SERVICE_URL", "http://ap-management:5000")


def _create_adapter(base_url: str) -> HttpxRequestAdapter:
    adapter = HttpxRequestAdapter(AnonymousAuthenticationProvider())
    adapter.base_url = base_url
    return adapter


_log = logging.getLogger(__name__)


async def compose_aps(ap1_data: dict, ap2_data: dict) -> dict:
    client = ApManagementClient(_create_adapter(AP_MANAGEMENT_SERVICE_URL))
    payload = ComposePayload()
    payload.ap1 = ComposePayload_ap1()
    payload.ap1.additional_data = ap1_data
    payload.ap2 = ComposePayload_ap2()
    payload.ap2.additional_data = ap2_data
    try:
        response = await client.analytical_patterns.compose.post(body=payload)
    except Exception as e:
        _log.exception("ap-management /compose call failed")
        raise
    return response.additional_data if response else {}


def serialize(model) -> dict:
    writer = JsonSerializationWriter()
    model.serialize(writer)
    return writer.get_serialized_content().decode("utf-8")
