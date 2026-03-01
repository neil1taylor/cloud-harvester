"""Collect PowerVS system pools."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_system_pools(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect system pools across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("system-pools")
        except Exception:
            continue

        # system-pools returns a list directly (or a dict of system types)
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = []
            for sys_type, pool_info in data.items():
                if isinstance(pool_info, dict):
                    pool_info["type"] = sys_type
                    items.append(pool_info)
                elif isinstance(pool_info, list):
                    for p in pool_info:
                        p["type"] = sys_type
                        items.append(p)
        else:
            continue

        for item in items:
            results.append({
                "type": item.get("type", ""),
                "sharedCoreRatio": str(item.get("sharedCoreRatio", "")),
                "maxAvailable": item.get("maxAvailable", 0),
                "maxMemory": item.get("maxMemory", 0),
                "coreMemoryRatio": item.get("coreMemoryRatio", 0),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
