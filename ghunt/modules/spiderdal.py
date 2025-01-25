import asyncio
from dataclasses import dataclass
from pathlib import Path

from ghunt import globals as gb
from ghunt.objects.base import GHuntCreds
from ghunt.objects.utils import TMPrinter
from ghunt.helpers.utils import get_httpx_client
from ghunt.apis.digitalassetslinks import DigitalAssetsLinksHttp
from ghunt.helpers.playstore import app_exists

import httpx


@dataclass
class Asset:
    site: str
    package_name: str
    certificate: str

async def identify_public_pkgs(as_client: httpx.AsyncClient, pkg_name: str, pkgs: dict[str, str], limiter: asyncio.Semaphore):
    async with limiter:
        if await app_exists(as_client, pkg_name):
            pkgs[pkg_name] = "public"
        else:
            pkgs[pkg_name] = "private"

async def analyze_single(as_client: httpx.AsyncClient, dal: DigitalAssetsLinksHttp, current_target: Asset, sites: dict[str, dict], pkgs: dict[str, dict], visited: set, limiter: asyncio.Semaphore):
    short_pkg_name = f"{current_target.package_name}${current_target.certificate}"

    async with limiter:
        if current_target.site:
            _, res = await dal.list_statements(as_client, website=current_target.site)
        elif current_target.package_name:
            _, res = await dal.list_statements(as_client, android_package_name=current_target.package_name, android_cert_fingerprint=current_target.certificate)

    for item in res.statements:
        if item.target.web.site:
            clean_site = item.target.web.site.strip('.')
            if clean_site not in sites:
                sites[clean_site] = {
                    "asset": Asset(site=clean_site, package_name=None, certificate=None),
                    "first_origin": current_target,
                    "origins": set(),
                }
            sites[clean_site]["origins"].add(current_target.site if current_target.site else short_pkg_name)

        if item.target.android_app.package_name:
            temp_name = f"{item.target.android_app.package_name}${item.target.android_app.certificate.sha_fingerprint}"

            if temp_name not in pkgs:
                pkgs[temp_name] = {
                    "asset": Asset(site=None, package_name=item.target.android_app.package_name, certificate=item.target.android_app.certificate.sha_fingerprint),
                    "first_origin": current_target,
                    "origins": set(),
                }
            pkgs[temp_name]["origins"].add(current_target.site if current_target.site else short_pkg_name)

    if current_target.site:
        visited.add(current_target.site)
        if res.statements and current_target.site not in sites:
            sites[current_target.site] = {
                "asset": current_target,
                "first_origin": None,
                "origins": set(),
            }
    if current_target.package_name:
        visited.add(short_pkg_name)
        if res.statements and short_pkg_name not in pkgs:
            pkgs[short_pkg_name] = {
                "asset": current_target,
                "first_origin": None,
                "origins": set(),
            }

async def main(url: str, package: str, fingerprint: str, strict: bool, json_file: Path):
    ghunt_creds = GHuntCreds()
    ghunt_creds.load_creds()

    as_client = get_httpx_client()
    digitalassetslink = DigitalAssetsLinksHttp(ghunt_creds)

    tmprinter = TMPrinter()

    sites: dict = {}
    pkgs: dict = {}
    visited = set()

    limiter = asyncio.Semaphore(10)

    current_targets: list[Asset] = []

    if url:
        http = False
        if url.startswith("http"):
            http = True

        if url.startswith(("http://", "https://")):
            domain = url.split("//")[1]
        else:
            domain = url

        temp_targets = []
        temp_targets.append(f"https://{domain}")
        if http:
            temp_targets.append(f"http://{domain}")
        if not strict:
            temp_targets.append(f"https://www.{domain}")
            if http:
                temp_targets.append(f"http://www.{domain}")

        for target in temp_targets:
            current_targets.append(Asset(site=target, package_name=None, certificate=None))

    if package and fingerprint:
        current_targets.append(Asset(site=None, package_name=package, certificate=fingerprint))

    round = 0
    total_scanned = 0
    print()
    while current_targets:
        round += 1
        total_scanned += len(current_targets)
        
        tmprinter.out(f"🕷️ [R{round}]: Investigating {len(current_targets)} targets...", style="bold magenta")

        await asyncio.gather(
            *[
                analyze_single(as_client, digitalassetslink, target, sites, pkgs, visited, limiter)
                for target in current_targets
            ]
        )

        # Next candidates
        next_sites = [site["asset"] for name,site in sites.items() if not name in visited]
        next_pkgs = [pkg["asset"] for name,pkg in pkgs.items() if not name in visited]
        current_targets = next_sites + next_pkgs

    tmprinter.clear()
    gb.rc.print(f"🕷️ [R{round}]: Investigation done ! {total_scanned} assets scanned.", style="bold magenta")

    # Sort
    pkgs_names = {x:None for x in set([x["asset"].package_name for x in pkgs.values()])}
    await asyncio.gather(
        *[
            identify_public_pkgs(as_client, pkg_name, pkgs_names, limiter)
            for pkg_name in pkgs_names
        ]
    )

    # Print results
    if sites:
        gb.rc.print(f"\n🌐 {len(sites)} site{'s' if len(sites) > 1 else ''} found !", style="white")
        for site_url, site in sites.items():
            if site["first_origin"]:
                if site["first_origin"].site:
                    gb.rc.print(f"- [deep_sky_blue1][link={site_url}]{site_url}[/link][/deep_sky_blue1] [steel_blue italic](leaked by : {site['first_origin'].site})[/steel_blue italic]")
                else:
                    gb.rc.print(f"- [deep_sky_blue1][link={site_url}]{site_url}[/link][/deep_sky_blue1] [steel_blue italic](leaked by : {site['first_origin'].package_name})[/steel_blue italic]")
            else:
                gb.rc.print(f"- [deep_sky_blue1][link={site_url}]{site_url}[/link][/deep_sky_blue1]")
    else:
        gb.rc.print("\nNo sites found.", style="italic bright_black")

    if pkgs:
        gb.rc.print(f"\n📦 {len(pkgs_names)} Android package{'s' if len(pkgs) > 1 else ''} found !", style="white")
        for pkg_name, state in pkgs_names.items():
            if state == "public":
                gb.rc.print(f"- 🏪  {pkg_name}", style="light_steel_blue")
            else:
                gb.rc.print(f"- 🥷 {pkg_name}", style="light_steel_blue")
            gb.rc.print("\tFingerprints (SHA256) :", style="steel_blue")
            for pkg in pkgs.values():
                fingerprints_cache = set()
                if pkg["asset"].package_name == pkg_name:
                    if pkg["asset"].certificate not in fingerprints_cache:
                        if pkg["first_origin"].site:
                            gb.rc.print(f"\t\t- {pkg['asset'].certificate} (leaked by : {pkg['first_origin'].site})", style="steel_blue italic", emoji=False)
                        else:
                            gb.rc.print(f"\t\t- {pkg['asset'].certificate} (leaked by : {pkg['first_origin'].package_name})", style="steel_blue italic", emoji=False)
                    fingerprints_cache.add(pkg["asset"].certificate)
    else:
        gb.rc.print("\nNo packages found.", style="bright_black italic")

    if json_file:
        import json
        from ghunt.objects.encoders import GHuntEncoder;
        with open(json_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "sites": sites,
                "packages": pkgs
            }, cls=GHuntEncoder, indent=4))
        gb.rc.print(f"\n[+] JSON output wrote to {json_file} !\n", style="italic")
    else:
        print()