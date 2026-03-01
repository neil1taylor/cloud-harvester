"""Main orchestrator for data collection."""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from cloud_harvester.auth import authenticate, get_account_info
from cloud_harvester.cache import CollectionCache
from cloud_harvester.schema import CLASSIC_SCHEMAS, VPC_SCHEMAS, POWERVS_SCHEMAS, VMWARE_SCHEMAS, ALL_SCHEMAS
from cloud_harvester.xlsx_writer import write_xlsx

console = Console()

DOMAIN_SCHEMAS = {
    "classic": CLASSIC_SCHEMAS,
    "vpc": VPC_SCHEMAS,
    "powervs": POWERVS_SCHEMAS,
    "vmware": VMWARE_SCHEMAS,
}


def run_harvest(
    api_key: str,
    domains: list[str],
    skip: list[str],
    accounts: list[str],
    regions: list[str],
    output_dir: str,
    concurrency: int,
    resume: bool,
    no_cache: bool,
) -> None:
    """Main entry point for data collection."""
    console.print("[bold blue]cloud-harvester[/bold blue] - IBM Cloud Infrastructure Collector\n")

    # Authenticate
    with console.status("Authenticating..."):
        token = authenticate(api_key)
    console.print("[green]Authenticated successfully[/green]")

    # Get account info
    with console.status("Discovering account..."):
        account = get_account_info(api_key)
    account_name = account.get("name", "unknown")
    account_id = account.get("account_id", "unknown")
    console.print(f"Account: [bold]{account_name}[/bold] ({account_id})")

    # Collect for the account
    collect_account(
        api_key=api_key,
        token=token,
        account=account,
        domains=domains,
        skip=skip,
        regions=regions,
        output_dir=output_dir,
        concurrency=concurrency,
        resume=resume,
        no_cache=no_cache,
    )


def collect_account(
    api_key: str,
    token: str,
    account: dict,
    domains: list[str],
    skip: list[str],
    regions: list[str],
    output_dir: str,
    concurrency: int,
    resume: bool,
    no_cache: bool,
) -> None:
    """Collect all data for a single account."""
    account_name = account.get("name", "unknown")
    account_id = account.get("account_id", "unknown")
    account_email = account.get("owner_email", "")
    owner = account.get("owner", "")

    # Set up cache
    api_key_hash = CollectionCache.hash_api_key(api_key)
    cache = CollectionCache(account_id, api_key_hash, output_dir)

    if not no_cache and cache.exists() and not resume:
        console.print("[yellow]Found cached data from previous run. Use --resume to continue or --no-cache to start fresh.[/yellow]")
        return

    all_data: dict[str, list[dict]] = {}
    errors: list[str] = []

    # Collect per domain
    for domain in domains:
        schemas = DOMAIN_SCHEMAS.get(domain, {})
        if not schemas:
            continue

        console.print(f"\n[bold]Collecting {domain} resources...[/bold]")

        # Import domain collectors lazily
        collectors = _get_domain_collectors(domain)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]{domain}", total=len(collectors))

            def collect_one(collector_info):
                resource_type, collector_fn = collector_info
                if resource_type in skip:
                    return resource_type, [], None
                if resume and not no_cache and resource_type in cache.completed_types():
                    cached = cache.load(resource_type)
                    if cached is not None:
                        return resource_type, cached, None
                try:
                    result = collector_fn(api_key, token, regions)
                    if not no_cache:
                        cache.save(resource_type, result)
                    return resource_type, result, None
                except Exception as e:
                    return resource_type, [], str(e)

            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = {executor.submit(collect_one, c): c for c in collectors}
                for future in as_completed(futures):
                    resource_type, result, error = future.result()
                    all_data[resource_type] = result
                    if error:
                        errors.append(f"{resource_type}: {error}")
                        progress.console.print(f"  [yellow]Warning:[/yellow] {resource_type} - {error}")
                    else:
                        count = len(result)
                        progress.console.print(f"  {resource_type}: {count} items")
                    progress.advance(task)

    # Build schemas for collected data
    collected_schemas = {}
    for domain in domains:
        collected_schemas.update(DOMAIN_SCHEMAS.get(domain, {}))

    # Write XLSX
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_name = account_name.replace(" ", "_").replace("/", "_")[:50]
    filename = f"{safe_name}_{account_id}_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)

    with console.status("Writing XLSX..."):
        account_info = {
            "name": account_name,
            "id": account_id,
            "email": account_email,
            "owner": owner,
        }
        write_xlsx(filepath, all_data, collected_schemas, account_info)

    # Cleanup cache
    cache.cleanup()

    # Summary
    console.print(f"\n[bold green]Done![/bold green] Saved to: {filepath}")
    total_resources = sum(len(v) for v in all_data.values())
    console.print(f"Total resources collected: {total_resources}")
    if errors:
        console.print(f"[yellow]Warnings: {len(errors)} resource types had errors[/yellow]")


def _get_domain_collectors(domain: str) -> list[tuple[str, callable]]:
    """Get collector functions for a domain. Returns list of (resource_type, fn)."""
    if domain == "classic":
        from cloud_harvester.collectors.classic import get_collectors
        return get_collectors()
    elif domain == "vpc":
        from cloud_harvester.collectors.vpc import get_collectors
        return get_collectors()
    elif domain == "powervs":
        from cloud_harvester.collectors.powervs import get_collectors
        return get_collectors()
    elif domain == "vmware":
        from cloud_harvester.collectors.vmware import get_collectors
        return get_collectors()
    return []
