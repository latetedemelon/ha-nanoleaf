#!/usr/bin/env python3
"""Load the integration the way Home Assistant does, and fail if it cannot.

Catches the failure mode a plain syntax check misses: the component importing
something the pinned library no longer provides. Run against a real Home
Assistant install with the library from `manifest.json` present.

    python3 scripts/smoke_test.py
"""

from __future__ import annotations

import asyncio
import importlib
import json
import logging
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent.parent
COMPONENT = REPO / "custom_components" / "nanoleaf"
DOMAIN = "nanoleaf"

# Platforms Home Assistant will ask this integration for.
PLATFORMS = (
    "light",
    "select",
    "number",
    "binary_sensor",
    "event",
    "button",
    "config_flow",
    "diagnostics",
    "device_trigger",
)


def modules() -> list[str]:
    """Return every module in the component, __init__ first."""
    names = sorted(p.stem for p in COMPONENT.glob("*.py") if p.stem != "__init__")
    return ["__init__", *names]


def check_imports() -> list[str]:
    """Import every module, reporting those that fail."""
    failures = []
    sys.path.insert(0, str(REPO))
    for name in modules():
        target = f"custom_components.{DOMAIN}.{name}"
        try:
            importlib.import_module(target)
            print(f"  ok    {target}")
        except Exception as err:  # noqa: BLE001 - reporting, not handling
            failures.append(f"{target}: {type(err).__name__}: {err}")
            print(f"  FAIL  {target}: {type(err).__name__}: {err}")
    return failures


async def check_loader() -> list[str]:
    """Resolve the integration and every platform through Home Assistant."""
    # Imported here rather than at module scope so the manifest checks still
    # run when Home Assistant is not installed.
    from homeassistant import loader  # noqa: PLC0415
    from homeassistant.core import HomeAssistant  # noqa: PLC0415

    failures = []
    hass = HomeAssistant(str(REPO))
    loader.async_setup(hass)
    try:
        integration = await loader.async_get_integration(hass, DOMAIN)
        if integration.is_built_in:
            failures.append("resolved to the built-in integration, not this one")
        if integration.version is None:
            failures.append("manifest has no version, so the loader would block it")
        print(
            f"  ok    resolved v{integration.version}, "
            f"type {integration.integration_type}"
        )
        print(f"        requirements: {integration.requirements}")

        await integration.async_get_component()
        for platform in PLATFORMS:
            try:
                await integration.async_get_platform(platform)
                print(f"  ok    platform {platform}")
            except Exception as err:  # noqa: BLE001 - reporting, not handling
                failures.append(f"platform {platform}: {type(err).__name__}: {err}")
                print(f"  FAIL  platform {platform}: {type(err).__name__}: {err}")
    finally:
        await hass.async_stop()
    return failures


def check_manifest() -> list[str]:
    """Check the manifest says what the component needs it to say."""
    failures = []
    manifest = json.loads((COMPONENT / "manifest.json").read_text())

    if "version" not in manifest:
        failures.append(
            "manifest needs a version; custom integrations without one are blocked"
        )
    if manifest.get("domain") != DOMAIN:
        failures.append(
            f"manifest domain is {manifest.get('domain')!r}, expected {DOMAIN!r}"
        )

    requirements = manifest.get("requirements", [])
    library = [r for r in requirements if r.startswith("aionanoleaf")]
    if not library:
        failures.append("manifest does not require an aionanoleaf library")
    elif not all(r.startswith("aionanoleaf2") for r in library):
        failures.append(f"manifest still requires the old library: {library}")
    # git+ URLs need a git binary, which the Home Assistant container may lack.
    for requirement in requirements:
        if "git+" in requirement:
            failures.append(
                f"requirement uses git+, prefer an archive URL: {requirement}"
            )

    hacs = json.loads((REPO / "hacs.json").read_text())
    if "homeassistant" not in hacs:
        failures.append("hacs.json should declare a minimum homeassistant version")

    if not failures:
        print(f"  ok    manifest v{manifest['version']}, requires {library}")
        print(f"  ok    hacs.json minimum Home Assistant {hacs['homeassistant']}")
    return failures


def main() -> int:
    logging.basicConfig(level=logging.ERROR)
    failures: list[str] = []

    print("manifest:")
    failures += check_manifest()
    print("imports:")
    failures += check_imports()
    print("loader:")
    failures += asyncio.run(check_loader())

    print()
    if failures:
        print(f"{len(failures)} failure(s):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("smoke test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
