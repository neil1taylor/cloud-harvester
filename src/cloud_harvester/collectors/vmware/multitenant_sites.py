"""Collect VCFaaS multitenant director sites."""
from cloud_harvester.collectors.vmware.client import VMwareClient, VCFAAS_REGIONS


def collect_multitenant_sites(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VCFaaS multitenant director sites across all regions."""
    client = VMwareClient(token)
    target_regions = [r for r in VCFAAS_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            sites = client.get_vcfaas_multitenant_sites(region)
        except Exception:
            continue

        for site in sites:
            pvdcs = site.get("pvdcs", [])
            results.append({
                "id": site.get("id", ""),
                "name": site.get("name", ""),
                "region": region,
                "pvdcCount": len(pvdcs) if isinstance(pvdcs, list) else 0,
            })

    return results
