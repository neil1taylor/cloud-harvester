# VMware Resources

11 resource types collected from IBM Cloud for VMware Solutions via VCD and VCF APIs.

## VMware as a Service

### Instances (`vVMwareInstances`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Location | location | string |
| Status | status | string |
| Deploy Type | deployType | string |
| Domain Type | domainType | string |
| NSX Type | nsxType | string |
| Version | version | string |
| Clusters | clusterCount | number |
| Creator | creator | string |
| CRN | crn | string |

### Clusters (`vVMwareClusters`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Location | location | string |
| Status | status | string |
| Host Count | hostCount | number |
| Storage Type | storageType | string |
| Instance ID | instanceId | string |

### Hosts (`vVMwareHosts`)

| Column | Field | Type |
|--------|-------|------|
| Hostname | hostname | string |
| Public IP | publicIp | string |
| Private IP | privateIp | string |
| Status | status | string |
| Server ID | serverId | string |
| Version | version | string |
| Memory (GB) | memory | number |
| CPUs | cpus | number |
| Cluster | clusterName | string |
| Location | location | string |
| Instance ID | instanceId | string |
| Cluster ID | clusterId | string |

### VLANs (`vVMwareVlans`)

| Column | Field | Type |
|--------|-------|------|
| VLAN Number | vlanNumber | number |
| Name | name | string |
| Purpose | purpose | string |
| Primary Router | primaryRouter | string |
| Cluster | clusterName | string |
| Location | location | string |
| Instance ID | instanceId | string |
| Cluster ID | clusterId | string |

### Subnets (`vVMwareSubnets`)

| Column | Field | Type |
|--------|-------|------|
| CIDR | cidr | string |
| Netmask | netmask | string |
| Gateway | gateway | string |
| Type | type | string |
| Purpose | purpose | string |
| VLAN | vlanNumber | number |
| VLAN Name | vlanName | string |
| Cluster | clusterName | string |
| Location | location | string |
| Instance ID | instanceId | string |

## Cloud Director

### Director Sites (`vDirectorSites`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Region | region | string |
| PVDCs | pvdcCount | number |
| Created | createdAt | date |

### PVDCs (`vPVDCs`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Datacenter | datacenter | string |
| Status | status | string |
| Provider Type | providerType | string |
| Clusters | clusterCount | number |
| Director Site ID | directorSiteId | string |

### VCF Clusters (`vVCFClusters`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Host Count | hostCount | number |
| Status | status | string |
| Datacenter | datacenter | string |
| Host Profile | hostProfile | string |
| Storage Type | storageType | string |
| PVDC ID | pvdcId | string |

### VDCs (`vVDCs`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Director Site | directorSiteName | string |
| CPU | cpu | string |
| RAM | ram | string |
| Disk | disk | string |
| Region | region | string |
| Type | type | string |
| Created | createdAt | date |

### Multitenant Sites (`vMultitenantSites`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Region | region | string |
| PVDCs | pvdcCount | number |

## Cross-References

### VMware Cross References (`vVMwareCrossReferences`)

| Column | Field | Type |
|--------|-------|------|
| Classic Resource Type | classicResourceType | string |
| Classic Resource ID | classicResourceId | string |
| Classic Resource Name | classicResourceName | string |
| VMware Role | vmwareRole | string |
| VMware Resource Type | vmwareResourceType | string |
| VMware Resource ID | vmwareResourceId | string |
| VMware Resource Name | vmwareResourceName | string |
