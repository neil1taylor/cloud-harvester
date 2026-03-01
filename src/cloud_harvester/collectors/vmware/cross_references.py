"""Build VMware cross-references with classic bare metal resources."""


def collect_vmware_cross_references(api_key: str, token: str, regions: list[str], context: dict | None = None) -> list[dict]:
    """Build cross-references between classic bare metal servers and VMware hosts.

    The context dict should contain previously collected data keyed by resource type,
    specifically "bareMetal" (classic bare metal servers) and "vmwareHosts".
    """
    if not context:
        return []

    bare_metals = context.get("bareMetal", [])
    vmware_hosts = context.get("vmwareHosts", [])

    if not bare_metals or not vmware_hosts:
        return []

    results = []

    # Build lookup of VMware hosts by private IP and hostname for matching
    vmware_by_ip = {}
    vmware_by_hostname = {}
    for host in vmware_hosts:
        private_ip = host.get("privateIp", "")
        if private_ip:
            vmware_by_ip[private_ip] = host

        hostname = host.get("hostname", "").lower()
        if hostname:
            vmware_by_hostname[hostname] = host

    for bm in bare_metals:
        vmware_role = bm.get("vmwareRole", "")
        if not vmware_role:
            continue

        backend_ip = bm.get("backendIp", "")
        bm_hostname = bm.get("hostname", "").lower()

        # Try to match by private/backend IP first, then by hostname
        matched_host = vmware_by_ip.get(backend_ip)
        if not matched_host:
            matched_host = vmware_by_hostname.get(bm_hostname)

        if matched_host:
            results.append({
                "classicResourceType": "bareMetal",
                "classicResourceId": str(bm.get("id", "")),
                "classicResourceName": bm.get("hostname", ""),
                "vmwareRole": vmware_role,
                "vmwareResourceType": "vmwareHost",
                "vmwareResourceId": matched_host.get("clusterId", ""),
                "vmwareResourceName": matched_host.get("hostname", ""),
            })
        else:
            # Still record the bare metal server with VMware role even without a match
            results.append({
                "classicResourceType": "bareMetal",
                "classicResourceId": str(bm.get("id", "")),
                "classicResourceName": bm.get("hostname", ""),
                "vmwareRole": vmware_role,
                "vmwareResourceType": "",
                "vmwareResourceId": "",
                "vmwareResourceName": "",
            })

    return results
