"""Collect IBM Cloud Classic Load Balancers."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,name,ipAddress,loadBalancerType,connectionLimit,"
    "virtualServers,billingItem]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(api_key=api_key)


def collect_load_balancers(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all load balancers."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        lbs = account.getAdcLoadBalancers(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for lb in lbs:
        billing = lb.get("billingItem", {})

        # Format virtual servers
        vs_list = lb.get("virtualServers", [])
        if isinstance(vs_list, list):
            virtual_servers = safe_string(vs_list)
        else:
            virtual_servers = str(vs_list)

        results.append({
            "id": lb.get("id"),
            "name": lb.get("name", "") or "",
            "ipAddress": lb.get("ipAddress", {}).get("ipAddress", "") if isinstance(lb.get("ipAddress"), dict) else lb.get("ipAddress", ""),
            "loadBalancerType": lb.get("loadBalancerType", ""),
            "connectionLimit": lb.get("connectionLimit", 0),
            "recurringFee": billing.get("recurringFee", "") if billing else "",
            "virtualServers": virtual_servers,
        })

    return results
