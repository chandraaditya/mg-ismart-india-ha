"""Tests for India TAP protocol 513 status handling."""

from mg_ismart_india.client import parse_vehicle_status
from mg_ismart_india.tap_codec import (
    TAP_RESERVED_SIZE,
    _codec,
    decode_status_response,
    encode_status_request,
)


def test_encode_status_request() -> None:
    raw = encode_status_request("1" * 50, "2" * 40, "3" * 17, 42)
    payload = bytes.fromhex(raw[5:])
    dispatcher_end = TAP_RESERVED_SIZE + payload[1]
    dispatcher = _codec().decode("MPDispatcherBody", payload[19:dispatcher_end])
    app = _codec().decode("OTARVMVehicleStatusReq", payload[dispatcher_end:])

    assert raw.startswith("1")
    assert dispatcher["applicationID"] == "511"
    assert dispatcher["applicationDataProtocolVersion"] == 513
    assert dispatcher["eventID"] == 42
    assert app == {"vehStatusReqType": 2}


def test_decode_and_normalize_status_response() -> None:
    status = {
        "statusTime": 1_700_000_000,
        "gpsPosition": {
            "wayPoint": {
                "position": {"latitude": 0, "longitude": 0, "altitude": 0},
                "heading": 0,
                "speed": 0,
                "hdop": 0,
                "satellites": 0,
            },
            "timestamp4Short": {"seconds": 1_700_000_000},
            "gpsStatus": "noGpsSignal",
        },
        "basicVehicleStatus": {
            "driverDoor": False,
            "passengerDoor": False,
            "rearLeftDoor": False,
            "rearRightDoor": False,
            "bootStatus": False,
            "bonnetStatus": False,
            "lockStatus": True,
            "driverWindow": False,
            "passengerWindow": False,
            "rearLeftWindow": False,
            "rearRightWindow": False,
            "sideLightStatus": False,
            "dippedBeamStatus": False,
            "mainBeamStatus": False,
            "engineStatus": 0,
            "powerMode": 0,
            "lastKeySeen": 0,
            "currentJourneyDistance": 0,
            "currentJourneyID": 1,
            "interiorTemperature": 30,
            "exteriorTemperature": 26,
            "fuelLevelPrc": 94,
            "fuelRange": 4040,
            "remoteClimateStatus": 0,
            "canBusActive": False,
            "timeOfLastCANBUSActivity": 1_699_999_999,
            "clstrDspdFuelLvlSgmt": 0,
            "mileage": 49353,
            "batteryVoltage": 140,
            "extendedData1": 47,
            "extendedData2": 0,
            "handBrake": False,
        },
    }
    app = _codec().encode("OTARVMVehicleStatusResp513", status)
    dispatcher = _codec().encode(
        "MPDispatcherBody",
        {
            "applicationID": "511",
            "messageID": 1,
            "eventCreationTime": 1_700_000_000,
            "eventID": 42,
            "applicationDataLength": len(app),
            "applicationDataEncoding": "perUnaligned",
            "applicationDataProtocolVersion": 513,
            "result": 0,
        },
    )
    payload = bytes((33, len(dispatcher) + 3, 0)) + bytes(16) + dispatcher + app
    raw = "1" + f"{len(payload) + 3:04X}" + payload.hex().upper()

    decoded_dispatcher, decoded_status = decode_status_response(raw)
    normalized = parse_vehicle_status(decoded_status or {})

    assert decoded_dispatcher["eventID"] == 42
    assert normalized.battery_percent == 94
    assert normalized.range_km == 404.0
    assert normalized.odometer_km == 4935.3
    assert normalized.auxiliary_battery_voltage == 14.0
    assert normalized.locked is True
    assert normalized.driver_door_open is False
