"""Collect IBM Cloud Classic File Storage."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,username,capacityGb,iops,storageType,storageTierLevel,"
    "serviceResourceBackendIpAddress,fileNetworkMountAddress,"
    "allowedVirtualGuests[id,hostname],allowedHardware[id,hostname],"
    "snapshotCapacityGb,replicationPartners,"
    "billingItem[recurringFee],createDate,notes]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_file_storage(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all file storage volumes."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        items = account.getNasNetworkStorage(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for item in items:
        billing = item.get("billingItem", {})

        # Format allowed virtual guests
        allowed_vsis = ", ".join(
            f"{v.get('id')}:{v.get('hostname', '')}"
            for v in item.get("allowedVirtualGuests", [])
        )

        # Format allowed hardware
        allowed_hw = ", ".join(
            f"{h.get('id')}:{h.get('hostname', '')}"
            for h in item.get("allowedHardware", [])
        )

        # Format replication partners
        repl_list = item.get("replicationPartners", [])
        if isinstance(repl_list, list):
            repl_partners = safe_string(repl_list)
        else:
            repl_partners = str(repl_list)

        storage_type = item.get("storageType", {})
        if isinstance(storage_type, dict):
            storage_type_str = storage_type.get("keyName", "")
        else:
            storage_type_str = str(storage_type)

        results.append({
            "id": item.get("id"),
            "username": item.get("username", ""),
            "capacityGb": item.get("capacityGb", 0),
            "iops": item.get("iops", ""),
            "storageType": storage_type_str,
            "storageTierLevel": item.get("storageTierLevel", ""),
            "targetIp": item.get("serviceResourceBackendIpAddress", ""),
            "mountAddress": item.get("fileNetworkMountAddress", ""),
            "snapshotCapacityGb": item.get("snapshotCapacityGb", 0),
            "recurringFee": billing.get("recurringFee", "") if billing else "",
            "createDate": item.get("createDate", ""),
            "notes": item.get("notes", "") or "",
            "allowedVirtualGuests": allowed_vsis,
            "allowedHardware": allowed_hw,
            "replicationPartners": repl_partners,
        })

    return results
