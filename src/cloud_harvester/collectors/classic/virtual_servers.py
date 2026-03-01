"""Collect IBM Cloud Classic Virtual Servers."""
import SoftLayer
from cloud_harvester.utils.formatting import bool_to_yesno, safe_string

OBJECT_MASK = (
    "mask[id,hostname,domain,fullyQualifiedDomainName,primaryIpAddress,"
    "primaryBackendIpAddress,maxCpu,maxMemory,startCpus,status,powerState,"
    "datacenter,operatingSystem[softwareDescription],hourlyBillingFlag,"
    "createDate,modifyDate,billingItem[recurringFee,hourlyRecurringFee,"
    "children[categoryCode,hourlyRecurringFee],orderItem],"
    "networkVlans[id,vlanNumber,name,networkSpace],"
    "blockDevices[diskImage[capacity,units]],tagReferences[tag],notes,"
    "dedicatedAccountHostOnlyFlag,placementGroupId,privateNetworkOnlyFlag,"
    "localDiskFlag]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(api_key=api_key)


def collect_virtual_servers(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all virtual server instances."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        vsis = account.getVirtualGuests(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for vsi in vsis:
        dc = vsi.get("datacenter", {}).get("name", "")
        if regions and dc and not any(r in dc for r in regions):
            continue

        os_desc = vsi.get("operatingSystem", {}).get("softwareDescription", {})
        os_name = os_desc.get("name", "")
        os_version = os_desc.get("version", "")
        os_str = f"{os_name} {os_version}".strip()

        # Calculate monthly fee
        billing = vsi.get("billingItem", {})
        recurring_fee = billing.get("recurringFee", "")
        cost_basis = "Monthly"
        if vsi.get("hourlyBillingFlag") and not recurring_fee:
            hourly = float(billing.get("hourlyRecurringFee", 0) or 0)
            for child in billing.get("children", []):
                hourly += float(child.get("hourlyRecurringFee", 0) or 0)
            recurring_fee = f"{hourly * 730:.2f}"
            cost_basis = "Estimated"

        # Calculate disk
        disk_gb = sum(
            bd.get("diskImage", {}).get("capacity", 0) or 0
            for bd in vsi.get("blockDevices", [])
        )

        # Format VLANs
        vlans = ", ".join(
            str(v.get("vlanNumber", ""))
            for v in vsi.get("networkVlans", [])
        )

        # Format tags
        tags = ", ".join(
            t.get("tag", {}).get("name", "")
            for t in vsi.get("tagReferences", [])
        )

        results.append({
            "id": vsi.get("id"),
            "hostname": vsi.get("hostname", ""),
            "domain": vsi.get("domain", ""),
            "fqdn": vsi.get("fullyQualifiedDomainName", ""),
            "primaryIp": vsi.get("primaryIpAddress", ""),
            "backendIp": vsi.get("primaryBackendIpAddress", ""),
            "maxCpu": vsi.get("maxCpu", 0),
            "maxMemory": vsi.get("maxMemory", 0),
            "status": vsi.get("status", {}).get("keyName", ""),
            "powerState": vsi.get("powerState", {}).get("keyName", ""),
            "datacenter": dc,
            "os": os_str,
            "hourlyBilling": bool_to_yesno(vsi.get("hourlyBillingFlag", False)),
            "createDate": vsi.get("createDate", ""),
            "recurringFee": recurring_fee,
            "costBasis": cost_basis,
            "notes": vsi.get("notes", "") or "",
            "privateNetworkOnly": bool_to_yesno(vsi.get("privateNetworkOnlyFlag", False)),
            "localDisk": bool_to_yesno(vsi.get("localDiskFlag", False)),
            "startCpus": vsi.get("startCpus", 0),
            "modifyDate": vsi.get("modifyDate", ""),
            "dedicated": bool_to_yesno(vsi.get("dedicatedAccountHostOnlyFlag", False)),
            "placementGroupId": vsi.get("placementGroupId") or 0,
            "tags": tags,
            "diskGb": disk_gb,
            "networkVlans": vlans,
        })

    return results
