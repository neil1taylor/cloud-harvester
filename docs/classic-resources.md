# Classic Infrastructure Resources

25 resource types collected from IBM Cloud Classic Infrastructure via the SoftLayer API.

## Compute

### Virtual Servers (`vVirtualServers`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Hostname | hostname | string |
| Domain | domain | string |
| FQDN | fqdn | string |
| Primary IP | primaryIp | string |
| Backend IP | backendIp | string |
| CPU | maxCpu | number |
| Memory (MB) | maxMemory | number |
| Status | status | string |
| Power State | powerState | string |
| Datacenter | datacenter | string |
| OS | os | string |
| Hourly Billing | hourlyBilling | string |
| Create Date | createDate | date |
| Classic Monthly Fee | recurringFee | currency |
| Cost Basis | costBasis | string |
| Notes | notes | string |
| Private Only | privateNetworkOnly | string |
| Local Disk | localDisk | string |
| Start CPUs | startCpus | number |
| Modified | modifyDate | date |
| Dedicated | dedicated | string |
| Placement Group | placementGroupId | number |
| Tags | tags | string |
| Disk (GB) | diskGb | number |
| VLANs | networkVlans | string |
| Local Storage (GB) | localStorageGb | number |
| Portable Storage (GB) | portableStorageGb | number |
| Portable Storage Details | portableStorageDetails | string |
| Block Device Details | blockDeviceDetails | string |
| Attached Block Storage (GB) | attachedBlockStorageGb | number |
| Attached File Storage (GB) | attachedFileStorageGb | number |
| Volume Count | volumeCount | number |

### Bare Metal Servers (`vBareMetal`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Hostname | hostname | string |
| Domain | domain | string |
| FQDN | fqdn | string |
| Serial Number | serialNumber | string |
| Primary IP | primaryIp | string |
| Backend IP | backendIp | string |
| Cores | cores | number |
| Memory (GB) | memory | number |
| Datacenter | datacenter | string |
| OS | os | string |
| Classic Monthly Fee | recurringFee | currency |
| Provision Date | provisionDate | date |
| Power Supplies | powerSupplyCount | number |
| Gateway Member | gatewayMember | string |
| VMware Role | vmwareRole | string |
| Notes | notes | string |
| Hard Drives | hardDrives | string |
| Drive Details | hardDriveDetails | string |
| Attached Block Storage (GB) | attachedBlockStorageGb | number |
| Attached File Storage (GB) | attachedFileStorageGb | number |
| Volume Count | volumeCount | number |
| Network Components | networkComponents | string |
| VLANs | networkVlans | string |
| Tags | tags | string |

### Dedicated Hosts (`vDedicatedHosts`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Name | name | string |
| Created | createDate | date |
| Datacenter | datacenter | string |
| CPU Count | cpuCount | number |
| Memory (GB) | memoryCapacity | number |
| Disk (GB) | diskCapacity | number |
| Guest Count | guestCount | number |

### Placement Groups (`vPlacementGroups`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Name | name | string |
| Created | createDate | date |
| Rule | rule | string |
| Backend Router | backendRouter | string |
| Guest Count | guestCount | number |

### Reserved Capacity (`vReservedCapacity`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Name | name | string |
| Created | createDate | date |
| Backend Router | backendRouter | string |
| Instances | instanceCount | number |

### Images (`vImages`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Name | name | string |
| Global ID | globalIdentifier | string |
| Note | note | string |
| Created | createDate | date |
| Status | status | string |
| Datacenter | datacenter | string |
| Parent ID | parentId | number |

## Networking

### VLANs (`vVLANs`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| VLAN Number | vlanNumber | number |
| Name | name | string |
| Network Space | networkSpace | string |
| Primary Router | primaryRouter | string |
| Datacenter | datacenter | string |
| Subnet Count | subnetCount | number |
| Firewall Components | firewallComponents | number |
| Gateway | gateway | string |

### Subnets (`vSubnets`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Network | networkIdentifier | string |
| CIDR | cidr | number |
| Type | subnetType | string |
| Gateway | gateway | string |
| Broadcast | broadcastAddress | string |
| Usable IPs | usableIpAddressCount | number |
| Total IPs | totalIpAddresses | number |
| VLAN | vlanNumber | number |
| Datacenter | datacenter | string |

### Gateways (`vGateways`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Name | name | string |
| Network Space | networkSpace | string |
| Status | status | string |
| Public IP | publicIp | string |
| Private IP | privateIp | string |
| Members | memberCount | number |
| Inside VLANs | insideVlanCount | number |

### Firewalls (`vFirewalls`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Primary IP | primaryIpAddress | string |
| Type | firewallType | string |
| VLAN | vlanNumber | number |
| Datacenter | datacenter | string |
| Classic Monthly Fee | recurringFee | currency |
| Rules | ruleCount | number |

### Security Groups (`vSecurityGroups`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Name | name | string |
| Description | description | string |
| Created | createDate | date |
| Modified | modifyDate | date |
| Rules | ruleCount | number |
| Bindings | bindingCount | number |

### Security Group Rules (`vSecurityGroupRules`)

| Column | Field | Type |
|--------|-------|------|
| Security Group ID | securityGroupId | number |
| Security Group Name | securityGroupName | string |
| Rule ID | id | number |
| Direction | direction | string |
| Protocol | protocol | string |
| Port Min | portRangeMin | number |
| Port Max | portRangeMax | number |
| Remote IP | remoteIp | string |
| Remote Group ID | remoteGroupId | number |

### Load Balancers (`vLoadBalancers`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Name | name | string |
| IP Address | ipAddress | string |
| Type | loadBalancerType | string |
| Connection Limit | connectionLimit | number |
| Classic Monthly Fee | recurringFee | currency |
| Virtual Servers | virtualServers | string |

### VPN Tunnels (`vVPNTunnels`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Name | name | string |
| Customer Peer IP | customerPeerIpAddress | string |
| Internal Peer IP | internalPeerIpAddress | string |
| P1 Auth | phaseOneAuthentication | string |
| P1 Encryption | phaseOneEncryption | string |
| P2 Auth | phaseTwoAuthentication | string |
| P2 Encryption | phaseTwoEncryption | string |
| Address Translations | addressTranslations | string |
| Customer Subnets | customerSubnets | string |
| Internal Subnets | internalSubnets | string |

## Storage

### Block Storage (`vBlockStorage`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Username | username | string |
| Capacity (GB) | capacityGb | number |
| IOPS | iops | string |
| Storage Type | storageType | string |
| Tier | storageTierLevel | string |
| Target IP | targetIp | string |
| LUN ID | lunId | string |
| Datacenter | datacenter | string |
| Encrypted | encrypted | boolean |
| Snapshot (GB) | snapshotCapacityGb | number |
| Snapshot Used (Bytes) | snapshotSizeBytes | number |
| Replication Status | replicationStatus | string |
| Classic Monthly Fee | recurringFee | currency |
| Create Date | createDate | date |
| Notes | notes | string |
| Allowed VSIs | allowedVirtualGuests | string |
| Allowed Hardware | allowedHardware | string |
| Allowed Subnets | allowedSubnets | string |
| Replication Partners | replicationPartners | string |

### File Storage (`vFileStorage`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Username | username | string |
| Capacity (GB) | capacityGb | number |
| IOPS | iops | string |
| Storage Type | storageType | string |
| Tier | storageTierLevel | string |
| Target IP | targetIp | string |
| Mount Address | mountAddress | string |
| Datacenter | datacenter | string |
| Encrypted | encrypted | boolean |
| Bytes Used | bytesUsed | number |
| Snapshot (GB) | snapshotCapacityGb | number |
| Snapshot Used (Bytes) | snapshotSizeBytes | number |
| Replication Status | replicationStatus | string |
| Classic Monthly Fee | recurringFee | currency |
| Create Date | createDate | date |
| Notes | notes | string |
| Allowed VSIs | allowedVirtualGuests | string |
| Allowed Hardware | allowedHardware | string |
| Allowed Subnets | allowedSubnets | string |
| Replication Partners | replicationPartners | string |

### Object Storage (`vObjectStorage`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Username | username | string |
| Storage Type | storageType | string |
| Capacity (GB) | capacityGb | number |
| Bytes Used | bytesUsed | number |
| Classic Monthly Fee | recurringFee | currency |
| Create Date | createDate | date |

## Security & Identity

### SSL Certificates (`vSSLCertificates`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Common Name | commonName | string |
| Organization | organizationName | string |
| Valid From | validityBegin | date |
| Validity (Days) | validityDays | number |
| Valid Until | validityEnd | date |
| Create Date | createDate | date |
| Notes | notes | string |

### SSH Keys (`vSSHKeys`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Label | label | string |
| Fingerprint | fingerprint | string |
| Create Date | createDate | date |
| Modify Date | modifyDate | date |
| Notes | notes | string |

### Users (`vUsers`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Username | username | string |
| Email | email | string |
| First Name | firstName | string |
| Last Name | lastName | string |
| Create Date | createDate | date |
| Status Date | statusDate | date |
| Status | userStatus | string |
| Roles | roles | string |
| Permissions | permissions | string |

## DNS

### DNS Domains (`vDNSDomains`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Name | name | string |
| Serial | serial | number |
| Update Date | updateDate | date |
| Record Count | recordCount | number |

### DNS Records (`vDNSRecords`)

| Column | Field | Type |
|--------|-------|------|
| Domain ID | domainId | number |
| Domain | domainName | string |
| ID | id | number |
| Host | host | string |
| Type | type | string |
| Data | data | string |
| TTL | ttl | number |
| Priority | priority | number |

## Account

### Billing (`vBilling`)

| Column | Field | Type |
|--------|-------|------|
| ID | id | number |
| Description | description | string |
| Category | categoryCode | string |
| Classic Monthly Fee | recurringFee | currency |
| Create Date | createDate | date |
| Cancel Date | cancellationDate | date |
| Notes | notes | string |

### Event Log (`vEventLog`)

| Column | Field | Type |
|--------|-------|------|
| Event | eventName | string |
| Date | eventCreateDate | date |
| User Type | userType | string |
| User ID | userId | number |
| Username | username | string |
| Object | objectName | string |
| Object ID | objectId | number |
| Trace ID | traceId | string |

### Relationships (`vRelationships`)

| Column | Field | Type |
|--------|-------|------|
| Parent Type | parentType | string |
| Parent ID | parentId | number |
| Parent Name | parentName | string |
| Child Type | childType | string |
| Child ID | childId | number |
| Child Name | childName | string |
| Relationship Field | relationshipField | string |
