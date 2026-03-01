"""Collect VCF for Classic vCenter instances."""
from cloud_harvester.collectors.vmware.client import VMwareClient


def collect_vmware_instances(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VMware vCenter instances."""
    client = VMwareClient(token)

    try:
        instances = client.get_vcenter_instances()
    except Exception:
        return []

    results = []
    for inst in instances:
        detail = {}
        instance_id = inst.get("id", "")
        if instance_id:
            try:
                detail = client.get_vcenter_detail(instance_id)
            except Exception:
                pass

        clusters = detail.get("clusters", inst.get("clusters", []))

        results.append({
            "id": inst.get("id", ""),
            "name": inst.get("name", ""),
            "location": inst.get("location", inst.get("datacenter", "")),
            "status": inst.get("status", ""),
            "deployType": inst.get("deploy_type", inst.get("deployType", "")),
            "domainType": inst.get("domain_type", inst.get("domainType", "")),
            "nsxType": inst.get("nsx_type", inst.get("nsxType", "")),
            "version": inst.get("version", detail.get("version", "")),
            "clusterCount": len(clusters) if isinstance(clusters, list) else 0,
            "creator": inst.get("creator", detail.get("creator", "")),
            "crn": inst.get("crn", detail.get("crn", "")),
        })

    return results
