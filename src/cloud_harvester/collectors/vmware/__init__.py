"""VMware/VCF infrastructure collectors."""


def get_collectors():
    """Return list of (resource_type, collector_fn) tuples."""
    from .instances import collect_vmware_instances
    from .clusters import collect_vmware_clusters
    from .hosts import collect_vmware_hosts
    from .vlans import collect_vmware_vlans
    from .subnets import collect_vmware_subnets
    from .director_sites import collect_director_sites
    from .pvdcs import collect_pvdcs
    from .vcf_clusters import collect_vcf_clusters
    from .vdcs import collect_vdcs
    from .multitenant_sites import collect_multitenant_sites
    from .cross_references import collect_vmware_cross_references

    return [
        ("vmwareInstances", collect_vmware_instances),
        ("vmwareClusters", collect_vmware_clusters),
        ("vmwareHosts", collect_vmware_hosts),
        ("vmwareVlans", collect_vmware_vlans),
        ("vmwareSubnets", collect_vmware_subnets),
        ("directorSites", collect_director_sites),
        ("pvdcs", collect_pvdcs),
        ("vcfClusters", collect_vcf_clusters),
        ("vdcs", collect_vdcs),
        ("multitenantSites", collect_multitenant_sites),
        ("vmwareCrossReferences", collect_vmware_cross_references),
    ]
