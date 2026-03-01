"""Classic infrastructure collectors."""


def get_collectors():
    """Return list of (resource_type, collector_fn) tuples."""
    from .virtual_servers import collect_virtual_servers
    from .bare_metal import collect_bare_metal
    from .dedicated_hosts import collect_dedicated_hosts
    from .images import collect_images
    from .placement_groups import collect_placement_groups
    from .reserved_capacity import collect_reserved_capacity
    from .vlans import collect_vlans
    from .subnets import collect_subnets
    from .gateways import collect_gateways
    from .firewalls import collect_firewalls
    from .security_groups import collect_security_groups, collect_security_group_rules
    from .load_balancers import collect_load_balancers
    from .vpn_tunnels import collect_vpn_tunnels
    from .block_storage import collect_block_storage
    from .file_storage import collect_file_storage
    from .object_storage import collect_object_storage
    from .ssl_certificates import collect_ssl_certificates
    from .ssh_keys import collect_ssh_keys
    from .dns import collect_dns_domains, collect_dns_records
    from .billing import collect_billing
    from .users import collect_users
    from .event_log import collect_event_log
    from .transit_gateways import collect_transit_gateways
    from .direct_links import collect_direct_links
    from .relationships import collect_relationships

    return [
        ("virtualServers", collect_virtual_servers),
        ("bareMetal", collect_bare_metal),
        ("dedicatedHosts", collect_dedicated_hosts),
        ("images", collect_images),
        ("placementGroups", collect_placement_groups),
        ("reservedCapacity", collect_reserved_capacity),
        ("vlans", collect_vlans),
        ("subnets", collect_subnets),
        ("gateways", collect_gateways),
        ("firewalls", collect_firewalls),
        ("securityGroups", collect_security_groups),
        ("securityGroupRules", collect_security_group_rules),
        ("loadBalancers", collect_load_balancers),
        ("vpnTunnels", collect_vpn_tunnels),
        ("blockStorage", collect_block_storage),
        ("fileStorage", collect_file_storage),
        ("objectStorage", collect_object_storage),
        ("sslCertificates", collect_ssl_certificates),
        ("sshKeys", collect_ssh_keys),
        ("dnsDomains", collect_dns_domains),
        ("dnsRecords", collect_dns_records),
        ("billing", collect_billing),
        ("users", collect_users),
        ("eventLog", collect_event_log),
        ("transitGateways", collect_transit_gateways),
        ("directLinks", collect_direct_links),
        ("relationships", collect_relationships),
    ]
