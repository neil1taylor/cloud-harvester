"""PowerVS infrastructure collectors."""


def get_collectors():
    """Return list of (resource_type, collector_fn) tuples."""
    from .workspaces import collect_workspaces
    from .instances import collect_instances
    from .volumes import collect_volumes
    from .volume_groups import collect_volume_groups
    from .snapshots import collect_snapshots
    from .networks import collect_networks
    from .network_ports import collect_network_ports
    from .network_security_groups import collect_network_security_groups
    from .cloud_connections import collect_cloud_connections
    from .dhcp import collect_dhcp_servers
    from .vpn_connections import collect_vpn_connections
    from .ike_policies import collect_ike_policies
    from .ipsec_policies import collect_ipsec_policies
    from .ssh_keys import collect_ssh_keys
    from .images import collect_images
    from .stock_images import collect_stock_images
    from .system_pools import collect_system_pools
    from .sap_profiles import collect_sap_profiles
    from .placement_groups import collect_placement_groups
    from .host_groups import collect_host_groups
    from .events import collect_events

    return [
        ("pvsWorkspaces", collect_workspaces),
        ("pvsInstances", collect_instances),
        ("pvsVolumes", collect_volumes),
        ("pvsVolumeGroups", collect_volume_groups),
        ("pvsSnapshots", collect_snapshots),
        ("pvsNetworks", collect_networks),
        ("pvsNetworkPorts", collect_network_ports),
        ("pvsNetworkSecurityGroups", collect_network_security_groups),
        ("pvsCloudConnections", collect_cloud_connections),
        ("pvsDhcpServers", collect_dhcp_servers),
        ("pvsVpnConnections", collect_vpn_connections),
        ("pvsIkePolicies", collect_ike_policies),
        ("pvsIpsecPolicies", collect_ipsec_policies),
        ("pvsSshKeys", collect_ssh_keys),
        ("pvsImages", collect_images),
        ("pvsStockImages", collect_stock_images),
        ("pvsSystemPools", collect_system_pools),
        ("pvsSapProfiles", collect_sap_profiles),
        ("pvsPlacementGroups", collect_placement_groups),
        ("pvsHostGroups", collect_host_groups),
        ("pvsEvents", collect_events),
    ]
