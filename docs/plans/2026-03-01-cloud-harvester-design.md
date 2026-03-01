# cloud-harvester Design Document

**Date:** 2026-03-01
**Status:** Approved

## Overview

cloud-harvester is a Python CLI tool that collects IBM Cloud infrastructure data across all domains (Classic, VPC, PowerVS, VMware) using read-only API access and produces XLSX files compatible with the classic_analyser app.

Analogous to RVTools for VMware - easy to run, read-only, produces a comprehensive infrastructure snapshot.

## CLI Interface

```bash
# Basic - collects all accessible accounts
cloud-harvester --api-key <key>

# Via environment variable
export IBMCLOUD_API_KEY=<key>
cloud-harvester

# Filters
cloud-harvester --domains classic,vpc       # limit to specific domains
cloud-harvester --skip vlans,subnets        # skip specific resource types
cloud-harvester --account 1234567           # limit to specific account(s)
cloud-harvester --region dal,wdc            # limit to specific regions/DCs

# Output control
cloud-harvester --output ./exports/         # custom output directory
cloud-harvester --concurrency 10            # parallel threads per domain

# Resume
cloud-harvester --resume                    # resume interrupted collection
cloud-harvester --no-cache                  # force fresh collection
```

**Output filename pattern:** `<account_name>_<account_id>_<YYYYMMDD_HHMMSS>.xlsx`

## Technology Stack

- **Language:** Python 3.11+
- **CLI framework:** click
- **Classic API:** softlayer (softlayer-python SDK)
- **IAM/Account:** ibm-cloud-sdk-core, ibm-platform-services
- **VPC API:** ibm-vpc SDK
- **PowerVS API:** ibm-cloud-networking-services or REST via ibm-cloud-sdk-core
- **VMware API:** REST via ibm-cloud-sdk-core
- **XLSX:** openpyxl
- **Progress UI:** rich
- **Distribution:** PyPI (pip install cloud-harvester)

## Architecture

Plugin-based collectors with a standard interface. One file per resource type.

### Project Structure

```
cloud-harvester/
├── pyproject.toml
├── README.md
├── src/
│   └── cloud_harvester/
│       ├── __init__.py
│       ├── cli.py              # Click CLI entry point
│       ├── auth.py             # IAM auth, account discovery
│       ├── xlsx_writer.py      # XLSX generation (openpyxl)
│       ├── schema.py           # Column defs matching classic_analyser
│       ├── collectors/
│       │   ├── __init__.py
│       │   ├── base.py         # BaseCollector ABC
│       │   ├── registry.py     # Auto-discovery of collector modules
│       │   ├── classic/        # ~30 resource type collectors
│       │   │   ├── virtual_servers.py
│       │   │   ├── bare_metal.py
│       │   │   ├── vlans.py
│       │   │   ├── subnets.py
│       │   │   ├── gateways.py
│       │   │   ├── firewalls.py
│       │   │   ├── security_groups.py
│       │   │   ├── load_balancers.py
│       │   │   ├── block_storage.py
│       │   │   ├── file_storage.py
│       │   │   ├── object_storage.py
│       │   │   ├── ssl_certificates.py
│       │   │   ├── ssh_keys.py
│       │   │   ├── dns.py
│       │   │   ├── billing.py
│       │   │   ├── users.py
│       │   │   ├── event_log.py
│       │   │   ├── images.py
│       │   │   ├── dedicated_hosts.py
│       │   │   ├── placement_groups.py
│       │   │   ├── reserved_capacity.py
│       │   │   ├── vpn_tunnels.py
│       │   │   ├── transit_gateways.py
│       │   │   ├── direct_links.py
│       │   │   └── relationships.py
│       │   ├── vpc/            # ~26 resource type collectors
│       │   │   ├── instances.py
│       │   │   ├── vpcs.py
│       │   │   ├── subnets.py
│       │   │   └── ... (security_groups, floating_ips, etc.)
│       │   ├── powervs/        # ~22 resource type collectors
│       │   │   ├── workspaces.py
│       │   │   ├── instances.py
│       │   │   ├── volumes.py
│       │   │   └── ... (networks, images, ssh_keys, etc.)
│       │   └── vmware/         # VMware resource collectors
│       │       ├── instances.py
│       │       ├── clusters.py
│       │       ├── hosts.py
│       │       └── ...
│       └── utils/
│           ├── __init__.py
│           ├── pagination.py   # Generic paginator
│           └── formatting.py   # Data transforms
└── tests/
```

## Authentication

- Accept API key via `--api-key` flag or `IBMCLOUD_API_KEY` env var
- Supports both personal API keys and Service ID API keys (both use IAM)
- Call IAM token endpoint to get bearer token
- Use ibm-platform-services to list accessible accounts
- Filter by `--account` if specified
- Create domain-specific clients per account

## Data Flow

```
1. Parse CLI args, resolve API key
2. Authenticate via IAM
3. Discover accessible accounts
4. Filter by --account / --region if specified
5. For each account:
   a. Check for resumable cache
   b. Create domain clients (SL, VPC, PowerVS, VMware)
   c. Run collectors per domain (parallel within domain):
      Classic → VPC → PowerVS → VMware
   d. Build relationship mappings (after all collectors complete)
   e. Generate XLSX
   f. Clean up cache
   g. Print summary
```

## Collector Interface

```python
class BaseCollector(ABC):
    domain: str          # "classic", "vpc", "powervs", "vmware"
    resource_type: str   # e.g., "virtualServers"
    worksheet_name: str  # e.g., "vVirtualServers"

    @abstractmethod
    def collect(self, client, context: dict) -> list[dict]:
        """Collect resources. Returns list of row dicts."""
        ...

    @property
    @abstractmethod
    def columns(self) -> list[ColumnDef]:
        """Column definitions matching classic_analyser schema."""
        ...
```

## Parallel Collection

- ThreadPoolExecutor within each domain
- Independent collectors run concurrently (default 5 threads, configurable via --concurrency)
- Domains run sequentially (different client types)
- Dependent collectors (e.g., relationships) run after independent ones

## Caching / Resume

- After each collector completes, save results to `.cloud-harvester-cache/<account_id>/` as JSON
- Manifest tracks: timestamps, API key hash, completion status per collector
- On startup with existing cache: prompt to resume or start fresh
- `--resume` auto-resumes, `--no-cache` forces fresh
- Cache deleted after successful XLSX generation

## XLSX Output Format

Must exactly match classic_analyser's expected format:

- **Summary sheet:** 2-column key-value pairs (Account Name, Account ID, Email, Owner, Timestamp, resource counts)
- **Resource worksheets:** Named with `v` prefix (classic/VPC) or `p` prefix (PowerVS)
- **Header row:** Bold, white text, blue background (#0F62FE), height 24
- **Column widths:** Auto-calculated, max 60 chars
- **Data types:** string, number, boolean, date, currency, array, bytes
- **Arrays:** Comma-separated strings
- **Booleans:** "Yes" / "No"
- **Currency:** Numeric with $ formatting
- **Empty results:** Include worksheet with headers only

Column definitions in `schema.py` are the single source of truth for XLSX compatibility with classic_analyser.

## Error Handling

- **Auth failures:** Clear message with IBM Cloud IAM docs link
- **Permission errors (403):** Skip resource type, warn, continue
- **Rate limiting (429):** Exponential backoff with jitter, max 3 retries
- **Network errors:** Retry with backoff, then skip and warn
- **Partial failures:** Always produce XLSX with collected data, mark failures in summary

## Resource Types

### Classic (~30 types)
Virtual Servers, Bare Metal, Dedicated Hosts, Image Templates, VLANs, Subnets, Network Gateways, Firewalls, Security Groups, Security Group Rules, Load Balancers, VPN Tunnels, Transit Gateways, Transit GW Connections, TGW Route Prefixes, TGW VPC VPN Gateways, Direct Links, Block Storage, File Storage, Object Storage, SSL Certificates, SSH Keys, DNS Domains, DNS Records, Billing Items, Placement Groups, Reserved Capacity, Users, Event Log, Relationships

### VPC (~26 types)
Instances, Bare Metal, Dedicated Hosts, Placement Groups, VPCs, Subnets, Security Groups, Floating IPs, Public Gateways, Network ACLs, Load Balancers, VPN Gateways, VPN Gateway Connections, Transit Gateways, Transit GW Connections, Direct Link Gateways, Direct Link Virtual Connections, Endpoint Gateways, Routing Tables, Routes, Volumes, SSH Keys, Images, Flow Log Collectors

### PowerVS (~22 types)
Workspaces, PVM Instances, Shared Processor Pools, Placement Groups, Host Groups, Networks, Network Ports, Network Security Groups, Cloud Connections, DHCP Servers, VPN Connections, IKE Policies, IPSec Policies, Volumes, Volume Groups, Snapshots, SSH Keys, System Pools, SAP Profiles, Images, Stock Images, Events

### VMware (~7 types)
VMware Instances, Clusters, Hosts, VLANs, Subnets, Director Sites, PVDCs
