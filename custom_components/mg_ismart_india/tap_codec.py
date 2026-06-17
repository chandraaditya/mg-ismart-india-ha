"""TAP v2.1 protocol codec for the India application protocol 513."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import time
from typing import Any

import asn1tools

TAP_PROTOCOL_VERSION = 33
TAP_RESERVED_SIZE = 16
STATUS_APPLICATION_ID = "511"
STATUS_APPLICATION_PROTOCOL = 513


class TapCodecError(ValueError):
    """Raised when a TAP status message cannot be encoded or decoded."""


@lru_cache(maxsize=1)
def _codec() -> Any:
    return asn1tools.compile_files(
        str(Path(__file__).with_name("tap_v21_513.asn1")), "uper"
    )


def encode_status_request(uid: str, token: str, vin: str, event_id: int) -> str:
    """Encode a read-only vehicle status request."""

    app = _codec().encode("OTARVMVehicleStatusReq", {"vehStatusReqType": 2})
    body = _codec().encode(
        "MPDispatcherBody",
        {
            "uid": uid,
            "token": token,
            "applicationID": STATUS_APPLICATION_ID,
            "vin": vin,
            "messageID": 1,
            "eventCreationTime": int(time.time()),
            "eventID": event_id,
            "ulMessageCounter": 0,
            "dlMessageCounter": 0,
            "ackMessageCounter": 0,
            "ackRequired": False,
            "applicationDataLength": len(app),
            "applicationDataEncoding": "perUnaligned",
            "applicationDataProtocolVersion": STATUS_APPLICATION_PROTOCOL,
            "testFlag": 2,
            "result": 0,
        },
    )
    dispatcher_length = len(body) + 3
    if dispatcher_length > 255:
        raise TapCodecError("TAP dispatcher is too large")
    payload = (
        bytes((TAP_PROTOCOL_VERSION, dispatcher_length, 0))
        + bytes(TAP_RESERVED_SIZE)
        + body
        + app
    )
    return "1" + f"{len(payload) + 3:04X}" + payload.hex().upper()


def decode_status_response(raw: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Decode the dispatcher and optional vehicle status application data."""

    if len(raw) < 5 or raw[0] != "1":
        raise TapCodecError("Unexpected TAP status response framing")
    try:
        payload = bytes.fromhex(raw[5:])
    except ValueError as err:
        raise TapCodecError("TAP status response is not hexadecimal") from err
    if len(payload) < 19:
        raise TapCodecError("TAP status response is too short")

    dispatcher_length = payload[1]
    dispatcher_end = TAP_RESERVED_SIZE + dispatcher_length
    if dispatcher_length < 3 or dispatcher_end > len(payload):
        raise TapCodecError("Invalid TAP dispatcher length")
    try:
        dispatcher = _codec().decode("MPDispatcherBody", payload[19:dispatcher_end])
    except Exception as err:
        raise TapCodecError("Unable to decode TAP status dispatcher") from err

    app_length = dispatcher.get("applicationDataLength", 0)
    if not app_length:
        return dispatcher, None
    app = payload[dispatcher_end : dispatcher_end + app_length]
    if len(app) != app_length:
        raise TapCodecError("Truncated TAP status application data")
    try:
        status = _codec().decode("OTARVMVehicleStatusResp513", app)
    except Exception as err:
        raise TapCodecError("Unable to decode TAP vehicle status") from err
    return dispatcher, status
