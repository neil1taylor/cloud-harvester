"""Collect VPC Routing Tables and Routes."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def _collect_routing_data(token: str, regions: list[str]):
    """Collect routing tables and routes data (shared helper)."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    rt_results = []
    route_results = []

    for region in target_regions:
        try:
            vpcs = client.list_resources(region, "vpcs", "vpcs")
        except Exception:
            continue

        for vpc in vpcs:
            vpc_id = vpc.get("id", "")
            vpc_name = vpc.get("name", "")

            try:
                tables = client.list_resources(
                    region, f"vpcs/{vpc_id}/routing_tables", "routing_tables"
                )
            except Exception:
                continue

            for rt in tables:
                rt_id = rt.get("id", "")
                rt_name = rt.get("name", "")
                subnets = ", ".join(
                    s.get("name", "") for s in rt.get("subnets", [])
                )

                rt_results.append({
                    "id": rt_id,
                    "name": rt_name,
                    "vpcName": vpc_name,
                    "isDefault": rt.get("is_default", False),
                    "lifecycleState": rt.get("lifecycle_state", ""),
                    "routeCount": len(rt.get("routes", [])),
                    "subnets": subnets,
                    "region": region,
                    "created_at": rt.get("created_at", ""),
                })

                # Collect routes for this routing table
                try:
                    routes = client.list_resources(
                        region,
                        f"vpcs/{vpc_id}/routing_tables/{rt_id}/routes",
                        "routes",
                    )
                except Exception:
                    continue

                for route in routes:
                    next_hop = route.get("next_hop", {})
                    if isinstance(next_hop, dict):
                        next_hop_target = next_hop.get("address", "") or next_hop.get("id", "")
                        next_hop_type = "ip" if next_hop.get("address") else "connection"
                    else:
                        next_hop_target = str(next_hop)
                        next_hop_type = ""

                    route_results.append({
                        "id": route.get("id", ""),
                        "name": route.get("name", ""),
                        "routingTableName": rt_name,
                        "vpcName": vpc_name,
                        "destination": route.get("destination", ""),
                        "action": route.get("action", ""),
                        "nextHopType": next_hop_type,
                        "nextHopTarget": next_hop_target,
                        "zone": route.get("zone", {}).get("name", ""),
                        "priority": route.get("priority", 0),
                        "origin": route.get("origin", ""),
                        "region": region,
                        "created_at": route.get("created_at", ""),
                    })

    return rt_results, route_results


def collect_vpc_routing_tables(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC routing tables across all regions."""
    rt_results, _ = _collect_routing_data(token, regions)
    return rt_results


def collect_vpc_routes(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC routes across all regions."""
    _, route_results = _collect_routing_data(token, regions)
    return route_results
