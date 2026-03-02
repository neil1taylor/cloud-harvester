"""Collect IBM Cloud Classic Images (Block Device Template Groups)."""
import SoftLayer

OBJECT_MASK = (
    "mask[id,name,globalIdentifier,note,createDate,status[name],"
    "datacenter[name],parentId]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_images(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all image templates."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        images = account.getBlockDeviceTemplateGroups(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for img in images:
        dc = img.get("datacenter", {}).get("name", "") if img.get("datacenter") else ""
        if regions and dc and not any(r in dc for r in regions):
            continue

        results.append({
            "id": img.get("id"),
            "name": img.get("name", ""),
            "globalIdentifier": img.get("globalIdentifier", ""),
            "note": img.get("note", "") or "",
            "createDate": img.get("createDate", ""),
            "status": img.get("status", {}).get("name", "") if img.get("status") else "",
            "datacenter": dc,
            "parentId": img.get("parentId") or 0,
        })

    return results
