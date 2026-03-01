"""Collect IBM Cloud Classic Subnets."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,networkIdentifier,cidr,subnetType,gateway,broadcastAddress,"
    "usableIpAddressCount,totalIpAddresses,"
    "networkVlan[id,vlanNumber,name],datacenter]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(api_key=api_key)


def collect_subnets(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all subnets."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        subnets = account.getSubnets(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for subnet in subnets:
        dc = subnet.get("datacenter", {}).get("name", "") if subnet.get("datacenter") else ""
        if regions and dc and not any(r in dc for r in regions):
            continue

        vlan = subnet.get("networkVlan", {})

        results.append({
            "id": subnet.get("id"),
            "networkIdentifier": subnet.get("networkIdentifier", ""),
            "cidr": subnet.get("cidr", 0),
            "subnetType": subnet.get("subnetType", ""),
            "gateway": subnet.get("gateway", ""),
            "broadcastAddress": subnet.get("broadcastAddress", ""),
            "usableIpAddressCount": subnet.get("usableIpAddressCount", 0),
            "totalIpAddresses": subnet.get("totalIpAddresses", 0),
            "vlanNumber": vlan.get("vlanNumber", 0) if vlan else 0,
            "datacenter": dc,
        })

    return results
