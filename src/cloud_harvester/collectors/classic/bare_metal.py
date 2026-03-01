"""Collect IBM Cloud Classic Bare Metal Servers."""
import SoftLayer
from cloud_harvester.utils.formatting import bool_to_yesno, safe_string

OBJECT_MASK = (
    "mask[id,hostname,domain,fullyQualifiedDomainName,manufacturerSerialNumber,"
    "primaryIpAddress,primaryBackendIpAddress,processorPhysicalCoreAmount,"
    "memoryCapacity,hardDrives[capacity,hardwareComponentModel"
    "[hardwareGenericComponentModel[hardwareComponentType]]],"
    "datacenter,operatingSystem[softwareDescription],"
    "networkComponents[primaryIpAddress,port,speed,status,macAddress],"
    "billingItem[recurringFee],provisionDate,powerSupplyCount,"
    "networkGatewayMemberFlag,networkVlans,tagReferences,notes]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_bare_metal(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all bare metal servers."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        servers = account.getHardware(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for srv in servers:
        dc = srv.get("datacenter", {}).get("name", "")
        if regions and dc and not any(r in dc for r in regions):
            continue

        os_desc = srv.get("operatingSystem", {}).get("softwareDescription", {})
        os_name = os_desc.get("name", "")
        os_version = os_desc.get("version", "")
        os_str = f"{os_name} {os_version}".strip()

        billing = srv.get("billingItem", {})
        recurring_fee = billing.get("recurringFee", "")

        # Format hard drives
        drives = []
        for hd in srv.get("hardDrives", []):
            cap = hd.get("capacity", "")
            drives.append(str(cap))
        hard_drives = ", ".join(drives)

        # Format network components
        net_comps = []
        for nc in srv.get("networkComponents", []):
            speed = nc.get("speed", "")
            status = nc.get("status", "")
            net_comps.append(f"{speed}Mbps ({status})")
        network_components = ", ".join(net_comps)

        # Format VLANs
        vlans = ", ".join(
            str(v.get("vlanNumber", ""))
            for v in srv.get("networkVlans", [])
        )

        # Format tags
        tags = ", ".join(
            t.get("tag", {}).get("name", "")
            for t in srv.get("tagReferences", [])
        )

        # Determine VMware role based on hostname pattern
        hostname = srv.get("hostname", "")
        vmware_role = ""
        hn_lower = hostname.lower()
        if "esx" in hn_lower or "esxi" in hn_lower:
            vmware_role = "ESXi Host"
        elif "vcenter" in hn_lower or "vcsa" in hn_lower:
            vmware_role = "vCenter"
        elif "nsx" in hn_lower:
            vmware_role = "NSX"

        results.append({
            "id": srv.get("id"),
            "hostname": hostname,
            "domain": srv.get("domain", ""),
            "fqdn": srv.get("fullyQualifiedDomainName", ""),
            "serialNumber": srv.get("manufacturerSerialNumber", ""),
            "primaryIp": srv.get("primaryIpAddress", ""),
            "backendIp": srv.get("primaryBackendIpAddress", ""),
            "cores": srv.get("processorPhysicalCoreAmount", 0),
            "memory": srv.get("memoryCapacity", 0),
            "datacenter": dc,
            "os": os_str,
            "recurringFee": recurring_fee,
            "provisionDate": srv.get("provisionDate", ""),
            "powerSupplyCount": srv.get("powerSupplyCount", 0),
            "gatewayMember": bool_to_yesno(srv.get("networkGatewayMemberFlag", False)),
            "vmwareRole": vmware_role,
            "notes": srv.get("notes", "") or "",
            "hardDrives": hard_drives,
            "networkComponents": network_components,
            "networkVlans": vlans,
            "tags": tags,
        })

    return results
