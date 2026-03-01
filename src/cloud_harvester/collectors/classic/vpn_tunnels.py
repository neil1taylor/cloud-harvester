"""Collect IBM Cloud Classic VPN Tunnels (IPSec)."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,name,customerPeerIpAddress,internalPeerIpAddress,"
    "phaseOneAuthentication,phaseOneEncryption,"
    "phaseTwoAuthentication,phaseTwoEncryption,"
    "addressTranslations,customerSubnets,internalSubnets]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_vpn_tunnels(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all VPN tunnel contexts."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        tunnels = account.getNetworkTunnelContexts(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for tunnel in tunnels:
        # Format address translations
        addr_trans = tunnel.get("addressTranslations", [])
        if isinstance(addr_trans, list):
            address_translations = safe_string(addr_trans)
        else:
            address_translations = str(addr_trans)

        # Format customer subnets
        cust_subnets = tunnel.get("customerSubnets", [])
        if isinstance(cust_subnets, list):
            customer_subnets = safe_string(cust_subnets)
        else:
            customer_subnets = str(cust_subnets)

        # Format internal subnets
        int_subnets = tunnel.get("internalSubnets", [])
        if isinstance(int_subnets, list):
            internal_subnets = safe_string(int_subnets)
        else:
            internal_subnets = str(int_subnets)

        results.append({
            "id": tunnel.get("id"),
            "name": tunnel.get("name", "") or "",
            "customerPeerIpAddress": tunnel.get("customerPeerIpAddress", ""),
            "internalPeerIpAddress": tunnel.get("internalPeerIpAddress", ""),
            "phaseOneAuthentication": tunnel.get("phaseOneAuthentication", ""),
            "phaseOneEncryption": tunnel.get("phaseOneEncryption", ""),
            "phaseTwoAuthentication": tunnel.get("phaseTwoAuthentication", ""),
            "phaseTwoEncryption": tunnel.get("phaseTwoEncryption", ""),
            "addressTranslations": address_translations,
            "customerSubnets": customer_subnets,
            "internalSubnets": internal_subnets,
        })

    return results
