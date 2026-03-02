"""Collect IBM Cloud Classic SSH Keys."""
import SoftLayer

OBJECT_MASK = (
    "mask[id,label,fingerprint,createDate,modifyDate,notes]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_ssh_keys(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all SSH keys."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        keys = account.getSshKeys(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for key in keys:
        results.append({
            "id": key.get("id"),
            "label": key.get("label", ""),
            "fingerprint": key.get("fingerprint", ""),
            "createDate": key.get("createDate", ""),
            "modifyDate": key.get("modifyDate", ""),
            "notes": key.get("notes", "") or "",
        })

    return results
