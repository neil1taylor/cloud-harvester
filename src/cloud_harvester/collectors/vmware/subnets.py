"""Collect VCF for Classic subnets (nested within VLANs)."""
from cloud_harvester.collectors.vmware.client import VMwareClient


def collect_vmware_subnets(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VMware subnets from all cluster VLANs."""
    client = VMwareClient(token)

    try:
        instances = client.get_vcenter_instances()
    except Exception:
        return []

    results = []
    for inst in instances:
        instance_id = inst.get("id", "")
        if not instance_id:
            continue

        try:
            detail = client.get_vcenter_detail(instance_id)
        except Exception:
            continue

        location = inst.get("location", inst.get("datacenter", ""))
        clusters = detail.get("clusters", [])

        for cluster in clusters:
            cluster_id = cluster.get("id", cluster.get("cluster_id", ""))
            cluster_name = cluster.get("name", "")

            if not cluster_id:
                continue

            try:
                vlans = client.get_cluster_vlans(instance_id, cluster_id)
            except Exception:
                continue

            for vlan in vlans:
                vlan_number = vlan.get("vlan_number", vlan.get("vlanNumber", 0))
                vlan_name = vlan.get("name", "")

                # Subnets are nested within each VLAN
                subnets = vlan.get("subnets", [])
                for subnet in subnets:
                    results.append({
                        "cidr": subnet.get("cidr", ""),
                        "netmask": subnet.get("netmask", subnet.get("net_mask", "")),
                        "gateway": subnet.get("gateway", ""),
                        "type": subnet.get("type", ""),
                        "purpose": subnet.get("purpose", ""),
                        "vlanNumber": vlan_number,
                        "vlanName": vlan_name,
                        "clusterName": cluster_name,
                        "location": location,
                        "instanceId": instance_id,
                    })

    return results
