"""VPC infrastructure collectors."""


def get_collectors():
    """Return list of (resource_type, collector_fn) tuples."""
    from .instances import collect_vpc_instances
    from .bare_metal import collect_vpc_bare_metal
    from .dedicated_hosts import collect_vpc_dedicated_hosts
    from .placement_groups import collect_vpc_placement_groups
    from .vpcs import collect_vpcs
    from .subnets import collect_vpc_subnets
    from .security_groups import collect_vpc_security_groups
    from .floating_ips import collect_vpc_floating_ips
    from .public_gateways import collect_vpc_public_gateways
    from .network_acls import collect_vpc_network_acls
    from .load_balancers import collect_vpc_load_balancers
    from .vpn_gateways import collect_vpc_vpn_gateways
    from .transit_gateways import collect_transit_gateways, collect_transit_gateway_connections
    from .direct_links import collect_direct_link_gateways, collect_direct_link_virtual_connections
    from .endpoint_gateways import collect_vpc_endpoint_gateways
    from .routing_tables import collect_vpc_routing_tables
    from .volumes import collect_vpc_volumes
    from .ssh_keys import collect_vpc_ssh_keys
    from .images import collect_vpc_images
    from .flow_logs import collect_vpc_flow_logs
    from .vpn_gateway_connections import collect_vpn_gateway_connections

    return [
        ("vpcInstances", collect_vpc_instances),
        ("vpcBareMetalServers", collect_vpc_bare_metal),
        ("vpcDedicatedHosts", collect_vpc_dedicated_hosts),
        ("vpcPlacementGroups", collect_vpc_placement_groups),
        ("vpcs", collect_vpcs),
        ("vpcSubnets", collect_vpc_subnets),
        ("vpcSecurityGroups", collect_vpc_security_groups),
        ("vpcFloatingIps", collect_vpc_floating_ips),
        ("vpcPublicGateways", collect_vpc_public_gateways),
        ("vpcNetworkAcls", collect_vpc_network_acls),
        ("vpcLoadBalancers", collect_vpc_load_balancers),
        ("vpcVpnGateways", collect_vpc_vpn_gateways),
        ("transitGateways", collect_transit_gateways),
        ("transitGatewayConnections", collect_transit_gateway_connections),
        ("directLinkGateways", collect_direct_link_gateways),
        ("directLinkVirtualConnections", collect_direct_link_virtual_connections),
        ("vpcEndpointGateways", collect_vpc_endpoint_gateways),
        ("vpcRoutingTables", collect_vpc_routing_tables),
        ("vpcVolumes", collect_vpc_volumes),
        ("vpcSshKeys", collect_vpc_ssh_keys),
        ("vpcImages", collect_vpc_images),
        ("vpcFlowLogCollectors", collect_vpc_flow_logs),
        ("vpnGatewayConnections", collect_vpn_gateway_connections),
    ]
