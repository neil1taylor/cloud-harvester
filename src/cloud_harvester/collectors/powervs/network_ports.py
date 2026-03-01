"""Collect PowerVS network ports."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_network_ports(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect network ports across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])

        # First get all networks, then get ports for each
        try:
            net_data = client.get("networks")
        except Exception:
            continue

        networks = net_data.get("networks", [])
        for network in networks:
            network_id = network.get("networkID", "")
            network_name = network.get("name", "")

            try:
                port_data = client.get(f"networks/{network_id}/ports")
            except Exception:
                continue

            ports = port_data.get("ports", [])
            for port in ports:
                pvm_instance = port.get("pvmInstance", {})
                results.append({
                    "portID": port.get("portID", ""),
                    "ipAddress": port.get("ipAddress", ""),
                    "macAddress": port.get("macAddress", ""),
                    "status": port.get("status", ""),
                    "networkName": network_name,
                    "pvmInstanceName": pvm_instance.get("pvmInstanceID", "") if pvm_instance else "",
                    "workspace": ws["name"],
                    "zone": ws["zone"],
                })

    return results
