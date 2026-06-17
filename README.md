# MG iSmart India

Home Assistant custom integration for MG iSmart India connected vehicles.

This is a read-only integration. It authenticates against the India MG iSmart
cloud, lists vehicles, and decodes the India-specific TAP protocol 513 vehicle
status response.

## Current Entities

- Model
- Series
- Model year
- Platform
- Supported feature count
- Last update
- Vehicle status time
- Last vehicle activity
- Activation status
- AC support
- Battery level
- Remaining range
- Odometer
- Auxiliary battery voltage
- Interior and exterior temperature
- Lock state
- Door, boot, bonnet, and window state
- Remote climate and CAN bus activity

## Installation

Copy `custom_components/mg_ismart_india` into your Home Assistant
`custom_components` directory, restart Home Assistant, then add the integration
from **Settings > Devices & services**.

## Notes

- Use the 10-digit India mobile number associated with the MG iSmart account.
- Controls and vehicle location are intentionally not exposed.
- Tyre pressure and charging details remain unavailable until their separate
  India encodings are validated.
- This project is independent from the generic MG SAIC integration because the
  India cloud uses a different TAP login and gateway signing flow.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for ASN.1 schema
attribution.
