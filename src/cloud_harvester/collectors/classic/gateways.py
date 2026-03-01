"""Collect IBM Cloud Classic Network Gateways."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,name,networkSpace,status[keyName],"
    "members[hardware[id,hostname]],"
    "insideVlans[id,networkVlan[id,vlanNumber,name]],"
    "publicIpAddress[ipAddress],privateIpAddress[ipAddress]]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(api_key=api_key)


def collect_gateways(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all network gateways."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        gateways = account.getNetworkGateways(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for gw in gateways:
        pub_ip = gw.get("publicIpAddress", {})
        priv_ip = gw.get("privateIpAddress", {})

        results.append({
            "id": gw.get("id"),
            "name": gw.get("name", ""),
            "networkSpace": gw.get("networkSpace", ""),
            "status": gw.get("status", {}).get("keyName", "") if gw.get("status") else "",
            "publicIp": pub_ip.get("ipAddress", "") if pub_ip else "",
            "privateIp": priv_ip.get("ipAddress", "") if priv_ip else "",
            "memberCount": len(gw.get("members", [])),
            "insideVlanCount": len(gw.get("insideVlans", [])),
        })

    return results
