"""Collect IBM Cloud Classic Billing Items."""
import SoftLayer

OBJECT_MASK = (
    "mask[id,description,categoryCode,recurringFee,"
    "createDate,cancellationDate,notes]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_billing(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all billing items."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        items = account.getAllBillingItems(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for item in items:
        results.append({
            "id": item.get("id"),
            "description": item.get("description", ""),
            "categoryCode": item.get("categoryCode", ""),
            "recurringFee": item.get("recurringFee", ""),
            "createDate": item.get("createDate", ""),
            "cancellationDate": item.get("cancellationDate", ""),
            "notes": item.get("notes", "") or "",
        })

    return results
