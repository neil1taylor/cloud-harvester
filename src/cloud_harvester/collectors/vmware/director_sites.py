"""Collect VCFaaS director sites."""
from cloud_harvester.collectors.vmware.client import VMwareClient, VCFAAS_REGIONS


def collect_director_sites(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VCFaaS director sites across all regions."""
    client = VMwareClient(token)
    target_regions = [r for r in VCFAAS_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            sites = client.get_vcfaas_director_sites(region)
        except Exception:
            continue

        for site in sites:
            pvdcs = site.get("pvdcs", [])
            results.append({
                "id": site.get("id", ""),
                "name": site.get("name", ""),
                "status": site.get("status", ""),
                "region": region,
                "pvdcCount": len(pvdcs) if isinstance(pvdcs, list) else 0,
                "createdAt": site.get("created_at", site.get("createdAt", "")),
            })

    return results
