"""Collect IBM Cloud Classic Object Storage."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,username,storageType,capacityGb,bytesUsed,"
    "billingItem[recurringFee],createDate]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(api_key=api_key)


def collect_object_storage(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all object storage accounts."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        items = account.getHubNetworkStorage(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for item in items:
        billing = item.get("billingItem", {})

        storage_type = item.get("storageType", {})
        if isinstance(storage_type, dict):
            storage_type_str = storage_type.get("keyName", "")
        else:
            storage_type_str = str(storage_type)

        results.append({
            "id": item.get("id"),
            "username": item.get("username", ""),
            "storageType": storage_type_str,
            "capacityGb": item.get("capacityGb", 0),
            "bytesUsed": item.get("bytesUsed", 0),
            "recurringFee": billing.get("recurringFee", "") if billing else "",
            "createDate": item.get("createDate", ""),
        })

    return results
