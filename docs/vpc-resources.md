# VPC Resources

24 resource types collected from IBM Cloud VPC Infrastructure via the VPC API.

## Compute

### Instances (`vVpcInstances`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Profile | profile | string |
| vCPUs | vcpu | number |
| Memory (GB) | memory | number |
| Zone | zone | string |
| VPC | vpcName | string |
| Primary IP | primaryIp | string |
| Region | region | string |
| Created | created_at | date |
| Resource Group | resourceGroup | string |

### Bare Metal Servers (`vVpcBareMetal`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Profile | profile | string |
| Zone | zone | string |
| VPC | vpcName | string |
| Region | region | string |
| Created | created_at | date |
| Resource Group | resourceGroup | string |

### Dedicated Hosts (`vVpcDedicatedHosts`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| State | state | string |
| Profile | profile | string |
| Zone | zone | string |
| vCPUs | vcpu | number |
| Memory (GB) | memory | number |
| Instances | instanceCount | number |
| Region | region | string |
| Created | created_at | date |

### Placement Groups (`vVpcPlacementGroups`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Strategy | strategy | string |
| Region | region | string |
| Created | created_at | date |
| Resource Group | resourceGroup | string |

### Images (`vVpcImages`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| OS | os | string |
| Architecture | architecture | string |
| Region | region | string |
| Created | created_at | date |

### SSH Keys (`vVpcSshKeys`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Type | type | string |
| Fingerprint | fingerprint | string |
| Length | length | number |
| Region | region | string |
| Created | created_at | date |

## Networking

### VPCs (`vVpcs`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Classic Access | classicAccess | boolean |
| Region | region | string |
| Created | created_at | date |
| Resource Group | resourceGroup | string |

### Subnets (`vVpcSubnets`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| CIDR | cidr | string |
| Available IPs | availableIps | number |
| Total IPs | totalIps | number |
| Zone | zone | string |
| VPC | vpcName | string |
| Region | region | string |
| Created | created_at | date |

### Security Groups (`vVpcSecurityGroups`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| VPC | vpcName | string |
| Rules | ruleCount | number |
| Targets | targetCount | number |
| Region | region | string |
| Created | created_at | date |

### Floating IPs (`vVpcFloatingIps`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Address | address | string |
| Status | status | string |
| Target | target | string |
| Zone | zone | string |
| Region | region | string |
| Created | created_at | date |

### Public Gateways (`vVpcPublicGateways`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| VPC | vpcName | string |
| Floating IP | floatingIp | string |
| Zone | zone | string |
| Region | region | string |
| Created | created_at | date |

### Network ACLs (`vVpcNetworkAcls`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| VPC | vpcName | string |
| Rules | ruleCount | number |
| Subnets | subnetCount | number |
| Region | region | string |
| Created | created_at | date |

### Load Balancers (`vVpcLoadBalancers`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Hostname | hostname | string |
| Public | isPublic | boolean |
| Operating Status | operatingStatus | string |
| Provisioning Status | provisioningStatus | string |
| Region | region | string |
| Created | created_at | date |

### VPN Gateways (`vVpcVpnGateways`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Mode | mode | string |
| Subnet | subnet | string |
| Region | region | string |
| Created | created_at | date |

### VPN Gateway Connections (`vVpnGwConns`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Mode | mode | string |
| VPN Gateway | vpnGatewayName | string |
| Peer Address | peerAddress | string |
| Local CIDRs | localCidrs | string |
| Peer CIDRs | peerCidrs | string |
| Region | region | string |
| Created | created_at | date |

### Endpoint Gateways (`vVpcEndpointGateways`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Lifecycle State | lifecycleState | string |
| Health State | healthState | string |
| Target | target | string |
| VPC | vpcName | string |
| Region | region | string |
| Created | created_at | date |

### Routing Tables (`vVpcRoutingTables`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| VPC | vpcName | string |
| Default | isDefault | boolean |
| Status | lifecycleState | string |
| Routes | routeCount | number |
| Subnets | subnets | string |
| Region | region | string |
| Created | created_at | date |

### Routes (`vVpcRoutes`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Routing Table | routingTableName | string |
| VPC | vpcName | string |
| Destination CIDR | destination | string |
| Action | action | string |
| Next Hop Type | nextHopType | string |
| Next Hop Target | nextHopTarget | string |
| Zone | zone | string |
| Priority | priority | number |
| Origin | origin | string |
| Region | region | string |
| Created | created_at | date |

### Transit Gateways (`vTransitGateways`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Location | location | string |
| Routing Scope | routingScope | string |
| Resource Group | resourceGroup | string |
| Created | created_at | date |

### Transit Gateway Connections (`vTGConnections`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Network Type | networkType | string |
| Transit Gateway | transitGatewayName | string |
| Network ID | networkId | string |
| Ownership | ownershipType | string |
| Created | created_at | date |

### Direct Link Gateways (`vDirectLinkGateways`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Type | type | string |
| Speed (Mbps) | speedMbps | number |
| Location | locationName | string |
| BGP Status | bgpStatus | string |
| Operational Status | operationalStatus | string |
| Global | global | boolean |
| Resource Group | resourceGroup | string |
| Created | created_at | date |

### Direct Link Virtual Connections (`vDLVirtualConns`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Type | type | string |
| Gateway | gatewayName | string |
| Network ID | networkId | string |
| Network Account | networkAccountId | string |
| Created | created_at | date |

## Storage

### Volumes (`vVpcVolumes`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Status | status | string |
| Capacity (GB) | capacity | number |
| IOPS | iops | number |
| Profile | profile | string |
| Encryption | encryption | string |
| Zone | zone | string |
| Region | region | string |
| Created | created_at | date |

## Observability

### Flow Log Collectors (`vVpcFlowLogs`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | string |
| Name | name | string |
| Active | active | boolean |
| Lifecycle State | lifecycleState | string |
| Target | target | string |
| Storage Bucket | storageBucket | string |
| Region | region | string |
| Created | created_at | date |
