# PowerVS Resources

22 resource types collected from IBM Power Virtual Server via the PowerVS API.

## Compute

### Instances (`pPvsInstances`)

| Column | Field | Type |
|--------|-------|------|
| ID | pvmInstanceID | string |
| Name | serverName | string |
| Status | status | string |
| System Type | sysType | string |
| Processors | processors | number |
| Proc Type | procType | string |
| Memory (GB) | memory | number |
| OS Type | osType | string |
| Primary IP | primaryIp | string |
| Storage Type | storageType | string |
| Workspace | workspace | string |
| Zone | zone | string |
| Created | creationDate | date |

### Shared Processor Pools (`pPvsSPPools`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Host Group | hostGroup | string |
| Reserved Cores | reservedCores | number |
| Allocated Cores | allocatedCores | number |
| Available Cores | availableCores | number |
| Instances | instanceCount | number |
| Workspace | workspace | string |
| Zone | zone | string |

### Placement Groups (`pPvsPlacementGrps`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Policy | policy | string |
| Members | memberCount | number |
| Workspace | workspace | string |
| Zone | zone | string |

### Host Groups (`pPvsHostGroups`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Hosts | hostCount | number |
| Secondaries | secondaryCount | number |
| Workspace | workspace | string |
| Zone | zone | string |

### System Pools (`pPvsSystemPools`)

| Column | Field | Type |
|--------|-------|------|
| System Type | type | string |
| Shared Core Ratio | sharedCoreRatio | string |
| Max Available Cores | maxAvailable | number |
| Max Available Memory (GB) | maxMemory | number |
| Core:Memory Ratio | coreMemoryRatio | number |
| Workspace | workspace | string |
| Zone | zone | string |

### SAP Profiles (`pPvsSapProfiles`)

| Column | Field | Type |
|--------|-------|------|
| Profile ID | profileID | string |
| Type | type | string |
| Cores | cores | number |
| Memory (GB) | memory | number |
| SAPS | saps | number |
| Certified | certified | boolean |
| Workspace | workspace | string |
| Zone | zone | string |

### Images (`pPvsImages`)

| Column | Field | Type |
|--------|-------|------|
| ID | imageID | string |
| Name | name | string |
| State | state | string |
| OS | operatingSystem | string |
| Architecture | architecture | string |
| Size (GB) | size | number |
| Storage Type | storageType | string |
| Workspace | workspace | string |
| Zone | zone | string |
| Created | creationDate | date |

### Stock Images (`pPvsStockImages`)

| Column | Field | Type |
|--------|-------|------|
| ID | imageID | string |
| Name | name | string |
| State | state | string |
| OS | operatingSystem | string |
| Architecture | architecture | string |
| Storage Type | storageType | string |
| Workspace | workspace | string |
| Zone | zone | string |

## Networking

### Networks (`pPvsNetworks`)

| Column | Field | Type |
|--------|-------|------|
| ID | networkID | string |
| Name | name | string |
| Type | type | string |
| VLAN ID | vlanID | number |
| CIDR | cidr | string |
| Gateway | gateway | string |
| MTU | mtu | number |
| Workspace | workspace | string |
| Zone | zone | string |

### Network Ports (`pPvsNetPorts`)

| Column | Field | Type |
|--------|-------|------|
| Port ID | portID | string |
| IP Address | ipAddress | string |
| MAC Address | macAddress | string |
| Status | status | string |
| Network | networkName | string |
| Instance | pvmInstanceName | string |
| Workspace | workspace | string |
| Zone | zone | string |

### Network Security Groups (`pPvsNSGs`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Rules | ruleCount | number |
| Members | memberCount | number |
| Workspace | workspace | string |
| Zone | zone | string |

### Cloud Connections (`pPvsCloudConns`)

| Column | Field | Type |
|--------|-------|------|
| ID | cloudConnectionID | string |
| Name | name | string |
| Speed (Mbps) | speed | number |
| Global Routing | globalRouting | boolean |
| GRE Tunnel | greEnabled | boolean |
| Transit Enabled | transitEnabled | boolean |
| Networks | networkCount | number |
| Workspace | workspace | string |
| Zone | zone | string |

### DHCP Servers (`pPvsDhcp`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Status | status | string |
| Network ID | networkId | string |
| Network | networkName | string |
| Workspace | workspace | string |
| Zone | zone | string |

### VPN Connections (`pPvsVpnConns`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Mode | mode | string |
| Peer Address | peerAddress | string |
| Local Subnets | localSubnets | string |
| Peer Subnets | peerSubnets | string |
| Workspace | workspace | string |
| Zone | zone | string |

### IKE Policies (`pPvsIkePolicies`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| IKE Version | version | number |
| Encryption | encryption | string |
| DH Group | dhGroup | number |
| Authentication | authentication | string |
| Workspace | workspace | string |
| Zone | zone | string |

### IPsec Policies (`pPvsIpsecPolicies`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Encryption | encryption | string |
| DH Group | dhGroup | number |
| Authentication | authentication | string |
| PFS | pfs | boolean |
| Workspace | workspace | string |
| Zone | zone | string |

## Storage

### Volumes (`pPvsVolumes`)

| Column | Field | Type |
|--------|-------|------|
| ID | volumeID | string |
| Name | name | string |
| State | state | string |
| Size (GB) | size | number |
| Disk Type | diskType | string |
| Bootable | bootable | boolean |
| Shareable | shareable | boolean |
| Attached To | pvmInstanceName | string |
| Workspace | workspace | string |
| Zone | zone | string |
| Created | creationDate | date |

### Volume Groups (`pPvsVolGroups`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Consistency Group | consistencyGroupName | string |
| Volumes | volumeCount | number |
| Replication | replicationEnabled | boolean |
| Workspace | workspace | string |
| Zone | zone | string |

### Snapshots (`pPvsSnapshots`)

| Column | Field | Type |
|--------|-------|------|
| ID | snapshotID | string |
| Name | name | string |
| Status | status | string |
| % Complete | percentComplete | number |
| Instance | pvmInstanceName | string |
| Volumes | volumeCount | number |
| Workspace | workspace | string |
| Zone | zone | string |
| Created | creationDate | date |

## Security

### SSH Keys (`pPvsSshKeys`)

| Column | Field | Type |
|--------|-------|------|
| Name | name | string |
| Key (truncated) | sshKey | string |
| Created | creationDate | date |
| Workspace | workspace | string |
| Zone | zone | string |

## Management

### Workspaces (`pPvsWorkspaces`)

| Column | Field | Type |
|--------|-------|------|
| GUID | guid | string |
| Name | name | string |
| Zone | zone | string |
| Region | region | string |
| Resource Group | resourceGroupName | string |
| State | state | string |
| Created | createdAt | date |

### Events (`pPvsEvents`)

| Column | Field | Type |
|--------|-------|------|
| Event ID | eventID | string |
| Action | action | string |
| Level | level | string |
| Message | message | string |
| Resource | resource | string |
| User | user | string |
| Timestamp | timestamp | date |
| Workspace | workspace | string |
| Zone | zone | string |
