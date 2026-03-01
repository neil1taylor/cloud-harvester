"""Collect IBM Cloud Classic Firewalls."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,primaryIpAddress,firewallType,"
    "networkVlan[id,vlanNumber,name],"
    "billingItem[recurringFee],datacenter,rules]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_firewalls(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all firewalls."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        firewalls = account.getNetworkVlanFirewalls(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for fw in firewalls:
        dc = fw.get("datacenter", {}).get("name", "") if fw.get("datacenter") else ""
        if regions and dc and not any(r in dc for r in regions):
            continue

        vlan = fw.get("networkVlan", {})
        billing = fw.get("billingItem", {})

        results.append({
            "id": fw.get("id"),
            "primaryIpAddress": fw.get("primaryIpAddress", ""),
            "firewallType": fw.get("firewallType", ""),
            "vlanNumber": vlan.get("vlanNumber", 0) if vlan else 0,
            "datacenter": dc,
            "recurringFee": billing.get("recurringFee", "") if billing else "",
            "ruleCount": len(fw.get("rules", [])),
        })

    return results
