"""Collect IBM Cloud Classic VLANs."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,vlanNumber,name,networkSpace,"
    "primaryRouter[hostname,datacenter[name]],"
    "subnets[id],firewallGuestNetworkComponents[id],"
    "attachedNetworkGateway[id,name]]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(api_key=api_key)


def collect_vlans(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all VLANs."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        vlans = account.getNetworkVlans(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for vlan in vlans:
        router = vlan.get("primaryRouter", {})
        dc = router.get("datacenter", {}).get("name", "") if router.get("datacenter") else ""
        if regions and dc and not any(r in dc for r in regions):
            continue

        gateway = vlan.get("attachedNetworkGateway", {})
        gateway_name = gateway.get("name", "") if gateway else ""

        results.append({
            "id": vlan.get("id"),
            "vlanNumber": vlan.get("vlanNumber", 0),
            "name": vlan.get("name", "") or "",
            "networkSpace": vlan.get("networkSpace", ""),
            "primaryRouter": router.get("hostname", ""),
            "datacenter": dc,
            "subnetCount": len(vlan.get("subnets", [])),
            "firewallComponents": len(vlan.get("firewallGuestNetworkComponents", [])),
            "gateway": gateway_name,
        })

    return results
