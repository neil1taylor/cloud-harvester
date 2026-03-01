"""Collect IBM Cloud Classic Event Log."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[eventName,eventCreateDate,userType,userId,"
    "username,objectName,objectId,traceId]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(api_key=api_key)


def collect_event_log(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect event log entries."""
    client = _create_sl_client(api_key)

    try:
        event_log_service = client["SoftLayer_Event_Log"]
        events = event_log_service.getAllObjects(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for event in events:
        results.append({
            "eventName": event.get("eventName", ""),
            "eventCreateDate": event.get("eventCreateDate", ""),
            "userType": event.get("userType", ""),
            "userId": event.get("userId"),
            "username": event.get("username", ""),
            "objectName": event.get("objectName", ""),
            "objectId": event.get("objectId"),
            "traceId": event.get("traceId", ""),
        })

    return results
