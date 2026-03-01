# cloud-harvester

IBM Cloud Infrastructure Data Collector

Collects infrastructure data from IBM Cloud Classic, VPC, PowerVS, and VMware
environments, producing XLSX files compatible with
[classic_analyser](https://github.com/IBM/classic_analyser). All four domains
are collected in parallel, and results are written to a single workbook with
one worksheet per resource type.

## Installation

```bash
pip install cloud-harvester
```

Or from source:

```bash
git clone <repo>
cd classic_analyser_tools
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Requires Python 3.11 or later.

## Quick Start

```bash
# Set your IBM Cloud API key
export IBMCLOUD_API_KEY=<your-api-key>
cloud-harvester

# Or pass it directly
cloud-harvester --api-key <your-api-key>
```

## Authentication

cloud-harvester authenticates via an IBM Cloud API key. Both personal API keys
and Service ID API keys are supported.

### Creating a read-only API key

1. Log in to the [IBM Cloud console](https://cloud.ibm.com).
2. Navigate to **Manage > Access (IAM) > API keys**.
3. Click **Create an IBM Cloud API key**.
4. Assign the **Viewer** role on all infrastructure services to the key (or
   to the Service ID it belongs to).

The Viewer role is the minimum permission needed. No write access is required.

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--api-key` | `$IBMCLOUD_API_KEY` | IBM Cloud API key |
| `--domains` | `classic,vpc,powervs,vmware` | Comma-separated domains to collect |
| `--skip` | *(none)* | Comma-separated resource types to skip |
| `--account` | *(none)* | Comma-separated account IDs to limit collection |
| `--region` | *(none)* | Comma-separated regions or datacenters to filter |
| `--output` | `.` | Output directory for XLSX files |
| `--concurrency` | `5` | Parallel threads per domain |
| `--resume / --no-resume` | `--no-resume` | Resume an interrupted collection |
| `--no-cache` | off | Force fresh collection, ignore cache |
| `--version` | | Show version and exit |

### Examples

Collect only VPC and PowerVS resources:

```bash
cloud-harvester --domains vpc,powervs
```

Skip billing and event log collection:

```bash
cloud-harvester --skip billing,eventLog
```

Collect with higher parallelism and write to a specific directory:

```bash
cloud-harvester --concurrency 10 --output ./reports
```

## Supported Resource Types

82 resource types across four domains.

### Classic (25 types)

| Resource Type | Worksheet |
|---------------|-----------|
| virtualServers | vVirtualServers |
| bareMetal | vBareMetal |
| vlans | vVLANs |
| subnets | vSubnets |
| gateways | vGateways |
| firewalls | vFirewalls |
| securityGroups | vSecurityGroups |
| securityGroupRules | vSecurityGroupRules |
| loadBalancers | vLoadBalancers |
| blockStorage | vBlockStorage |
| fileStorage | vFileStorage |
| objectStorage | vObjectStorage |
| sslCertificates | vSSLCertificates |
| sshKeys | vSSHKeys |
| dnsDomains | vDNSDomains |
| dnsRecords | vDNSRecords |
| images | vImages |
| dedicatedHosts | vDedicatedHosts |
| placementGroups | vPlacementGroups |
| reservedCapacity | vReservedCapacity |
| vpnTunnels | vVPNTunnels |
| billing | vBilling |
| users | vUsers |
| eventLog | vEventLog |
| relationships | vRelationships |

### VPC (24 types)

| Resource Type | Worksheet |
|---------------|-----------|
| vpcInstances | vVpcInstances |
| vpcBareMetalServers | vVpcBareMetal |
| vpcDedicatedHosts | vVpcDedicatedHosts |
| vpcPlacementGroups | vVpcPlacementGroups |
| vpcs | vVpcs |
| vpcSubnets | vVpcSubnets |
| vpcSecurityGroups | vVpcSecurityGroups |
| vpcFloatingIps | vVpcFloatingIps |
| vpcPublicGateways | vVpcPublicGateways |
| vpcNetworkAcls | vVpcNetworkAcls |
| vpcLoadBalancers | vVpcLoadBalancers |
| vpcVpnGateways | vVpcVpnGateways |
| transitGateways | vTransitGateways |
| transitGatewayConnections | vTGConnections |
| directLinkGateways | vDirectLinkGateways |
| directLinkVirtualConnections | vDLVirtualConns |
| vpnGatewayConnections | vVpnGwConns |
| vpcEndpointGateways | vVpcEndpointGateways |
| vpcRoutingTables | vVpcRoutingTables |
| vpcRoutes | vVpcRoutes |
| vpcVolumes | vVpcVolumes |
| vpcSshKeys | vVpcSshKeys |
| vpcImages | vVpcImages |
| vpcFlowLogCollectors | vVpcFlowLogs |

### PowerVS (22 types)

| Resource Type | Worksheet |
|---------------|-----------|
| pvsInstances | pPvsInstances |
| pvsSharedProcessorPools | pPvsSPPools |
| pvsPlacementGroups | pPvsPlacementGrps |
| pvsHostGroups | pPvsHostGroups |
| pvsNetworks | pPvsNetworks |
| pvsNetworkPorts | pPvsNetPorts |
| pvsNetworkSecurityGroups | pPvsNSGs |
| pvsCloudConnections | pPvsCloudConns |
| pvsDhcpServers | pPvsDhcp |
| pvsVpnConnections | pPvsVpnConns |
| pvsIkePolicies | pPvsIkePolicies |
| pvsIpsecPolicies | pPvsIpsecPolicies |
| pvsVolumes | pPvsVolumes |
| pvsVolumeGroups | pPvsVolGroups |
| pvsSnapshots | pPvsSnapshots |
| pvsSshKeys | pPvsSshKeys |
| pvsWorkspaces | pPvsWorkspaces |
| pvsSystemPools | pPvsSystemPools |
| pvsSapProfiles | pPvsSapProfiles |
| pvsImages | pPvsImages |
| pvsStockImages | pPvsStockImages |
| pvsEvents | pPvsEvents |

### VMware (11 types)

| Resource Type | Worksheet |
|---------------|-----------|
| vmwareInstances | vVMwareInstances |
| vmwareClusters | vVMwareClusters |
| vmwareHosts | vVMwareHosts |
| vmwareVlans | vVMwareVlans |
| vmwareSubnets | vVMwareSubnets |
| directorSites | vDirectorSites |
| pvdcs | vPVDCs |
| vcfClusters | vVCFClusters |
| vdcs | vVDCs |
| multitenantSites | vMultitenantSites |
| vmwareCrossReferences | vVMwareCrossReferences |

## Output Format

cloud-harvester writes a single XLSX file per account, named:

```
<account_name>_<account_id>_<YYYYMMDD_HHMMSS>.xlsx
```

The workbook contains:

- **Summary** sheet -- account metadata and resource counts for every type.
- One worksheet per resource type, named as shown in the tables above.
- IBM Carbon-styled headers (blue `#0F62FE` background, white bold text).
- Auto-sized columns, capped at 60 characters width.

The output is directly compatible with classic_analyser for analysis and
reporting.

## Development

Install in development mode:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/ -v --cov=cloud_harvester
```

Lint:

```bash
ruff check src/ tests/
```

## License

See [LICENSE](LICENSE) for details.
