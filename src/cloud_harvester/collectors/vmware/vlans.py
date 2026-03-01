"""Collect VCF for Classic VLANs."""
from cloud_harvester.collectors.vmware.client import VMwareClient


def collect_vmware_vlans(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VMware VLANs from all clusters."""
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
                results.append({
                    "vlanNumber": vlan.get("vlan_number", vlan.get("vlanNumber", 0)),
                    "name": vlan.get("name", ""),
                    "purpose": vlan.get("purpose", vlan.get("type", "")),
                    "primaryRouter": vlan.get("primary_router", vlan.get("primaryRouter", "")),
                    "clusterName": cluster_name,
                    "location": location,
                    "instanceId": instance_id,
                    "clusterId": cluster_id,
                })

    return results
