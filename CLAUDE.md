# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

cloud-harvester (PyPI package: `ibm-cloud-harvester`) is a Python CLI tool that collects IBM Cloud infrastructure data across four domains (Classic, VPC, PowerVS, VMware) via read-only APIs and produces XLSX files compatible with [classic_analyser](https://github.com/IBM/classic_analyser). 82 resource types across the four domains.

## Build & Development Commands

```bash
# Install in dev mode (requires Python 3.11+)
pip install -e ".[dev]"

# Run all tests with coverage
pytest tests/ -v --cov=cloud_harvester

# Run a single test file
pytest tests/test_vpc_collectors.py -v

# Run a single test function
pytest tests/test_classic_collectors.py::test_collect_virtual_servers -v

# Lint
ruff check src/ tests/

# Lint with auto-fix
ruff check --fix src/ tests/

# Run the CLI
cloud-harvester --api-key <key>
# Or: IBMCLOUD_API_KEY=<key> cloud-harvester
```

## Architecture

### Data Flow

```
cli.py (Click) → harvester.py (orchestrator) → collectors/<domain>/*.py → xlsx_writer.py
                                              ↕
                                          cache.py (resume support)
```

**Entry point**: `src/cloud_harvester/cli.py` — Click CLI that parses options, then calls `run_harvest()` in `harvester.py`.

**Orchestrator** (`harvester.py`): Authenticates via IAM, discovers account info, iterates domains sequentially, runs collectors within each domain in parallel via `ThreadPoolExecutor`, writes XLSX output, cleans up cache.

### Collector Plugin Architecture

Each domain (`classic/`, `vpc/`, `powervs/`, `vmware/`) has a `get_collectors()` function in its `__init__.py` returning `list[tuple[str, callable]]` — pairs of `(resource_type, collector_fn)`.

Every collector function has the same signature:

```python
def collect_<resource>(api_key: str, token: str, regions: list[str]) -> list[dict]:
```

Returns a list of row dicts where keys match the field names defined in `schema.py`. To add a new collector: create the module, add it to the domain's `get_collectors()`, and add a matching `ResourceSchema` entry in `schema.py`.

### API Client Patterns by Domain

- **Classic**: SoftLayer SDK via `SoftLayer.create_client_from_env(username='apikey', api_key=api_key)`. Uses object masks for eager loading. Each collector creates its own client via a `_create_sl_client()` helper (mocked in tests).
- **VPC**: IBM VPC SDK with pagination handling and region iteration.
- **PowerVS**: Custom REST client using IAM bearer tokens.
- **VMware**: Custom REST client for VCD and VCF APIs.

### Schema System (`schema.py`)

Defines `ResourceSchema` and `ColumnDef` dataclasses. Four domain dicts (`CLASSIC_SCHEMAS`, `VPC_SCHEMAS`, `POWERVS_SCHEMAS`, `VMWARE_SCHEMAS`) map `resource_type` string → `ResourceSchema`. The schema drives both XLSX column headers and data extraction. Column `field` names must match the dict keys returned by collectors.

### XLSX Output (`xlsx_writer.py`)

- Summary sheet with account metadata and per-type resource counts
- One worksheet per resource type, named by `ResourceSchema.worksheet_name`
- IBM Carbon styling: blue `#0F62FE` headers, auto-sized columns (max 60 chars)
- Booleans rendered as "Yes"/"No", arrays as comma-separated strings

### Naming Conventions

- **Resource types**: camelCase (`virtualServers`, `vpcInstances`, `pvsNetworks`)
- **Worksheet names**: prefixed `v` (Classic/VPC/VMware) or `p` (PowerVS), e.g. `vVirtualServers`, `pPvsInstances`
- **Collector files**: snake_case matching the resource (`virtual_servers.py`, `bare_metal.py`)

## Testing Patterns

Tests use `unittest.mock` to mock API clients. Classic collectors mock `_create_sl_client`, VPC/PowerVS/VMware mock their respective client constructors. XLSX tests use `openpyxl.load_workbook()` to validate output. CLI tests use Click's `CliRunner`. File I/O tests use `tempfile.TemporaryDirectory()`.

## Key Conventions

- **Error handling**: API errors (403/429/timeouts) are caught per-collector and return empty lists — partial failures don't block XLSX generation.
- **Line length**: 120 characters (configured in `pyproject.toml` for ruff).
- **Python target**: 3.11+ (uses `list[str]` syntax, `|` union types).
- **Data access**: Safe access with `.get()` and defaults throughout collectors.
- **Cache location**: `.cloud-harvester-cache/<account_id>/` — JSON per resource type with manifest tracking.
