"""Collect IBM Cloud Classic Block Storage."""
import SoftLayer

OBJECT_MASK = (
    "mask[id,username,capacityGb,iops,storageType,storageTierLevel,"
    "serviceResourceBackendIpAddress,lunId,"
    "allowedVirtualGuests[id,hostname],allowedHardware[id,hostname],"
    "snapshotCapacityGb,replicationPartners[id,username,"
    "serviceResourceBackendIpAddress],"
    "billingItem[recurringFee],createDate,notes]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_block_storage(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all block storage volumes (deduplicated from two API calls)."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    all_items = []
    seen_ids = set()

    # Collect from iSCSI network storage
    try:
        iscsi = account.getIscsiNetworkStorage(mask=OBJECT_MASK)
        for item in iscsi:
            item_id = item.get("id")
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                all_items.append(item)
    except Exception:
        pass

    # Collect from general network storage (block type)
    try:
        storage = account.getNetworkStorage(mask=OBJECT_MASK)
        for item in storage:
            item_id = item.get("id")
            if item_id and item_id not in seen_ids:
                storage_type = item.get("storageType", {})
                type_key = storage_type.get("keyName", "") if isinstance(storage_type, dict) else str(storage_type)
                if "BLOCK" in type_key.upper() or "ISCSI" in type_key.upper():
                    seen_ids.add(item_id)
                    all_items.append(item)
    except Exception:
        pass

    results = []
    for item in all_items:
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
        repl_partners = ", ".join(
            f"{r.get('id')}:{r.get('username', '')}"
            for r in item.get("replicationPartners", [])
        )

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
            "lunId": item.get("lunId", ""),
            "snapshotCapacityGb": item.get("snapshotCapacityGb", 0),
            "recurringFee": billing.get("recurringFee", "") if billing else "",
            "createDate": item.get("createDate", ""),
            "notes": item.get("notes", "") or "",
            "allowedVirtualGuests": allowed_vsis,
            "allowedHardware": allowed_hw,
            "replicationPartners": repl_partners,
        })

    return results
