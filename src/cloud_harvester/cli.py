"""CLI entry point for cloud-harvester."""
import sys

import click
from rich.console import Console

from cloud_harvester import __version__

console = Console()


@click.command()
@click.option("--api-key", envvar="IBMCLOUD_API_KEY", help="IBM Cloud API key (or set IBMCLOUD_API_KEY)")
@click.option("--domains", default="classic,vpc,powervs,vmware", help="Comma-separated domains to collect")
@click.option("--skip", default="", help="Comma-separated resource types to skip")
@click.option("--account", default="", help="Comma-separated account IDs to limit collection")
@click.option("--region", default="", help="Comma-separated regions/datacenters to filter")
@click.option("--output", default=".", help="Output directory for XLSX files")
@click.option("--concurrency", default=5, type=int, help="Parallel threads per domain")
@click.option("--resume/--no-resume", default=False, help="Resume interrupted collection")
@click.option("--no-cache", is_flag=True, help="Force fresh collection, ignore cache")
@click.version_option(version=__version__)
def main(api_key, domains, skip, account, region, output, concurrency, resume, no_cache):
    """Collect IBM Cloud infrastructure data into XLSX for classic_analyser."""
    if not api_key:
        console.print("[red]Error:[/red] API key required. Use --api-key or set IBMCLOUD_API_KEY environment variable.")
        sys.exit(1)

    domain_list = [d.strip() for d in domains.split(",") if d.strip()]
    skip_list = [s.strip() for s in skip.split(",") if s.strip()]
    account_list = [a.strip() for a in account.split(",") if a.strip()]
    region_list = [r.strip() for r in region.split(",") if r.strip()]

    from cloud_harvester.harvester import run_harvest

    run_harvest(
        api_key=api_key,
        domains=domain_list,
        skip=skip_list,
        accounts=account_list,
        regions=region_list,
        output_dir=output,
        concurrency=concurrency,
        resume=resume,
        no_cache=no_cache,
    )
