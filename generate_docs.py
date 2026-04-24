#!/usr/bin/env python3
"""
Generate MDX documentation from products.json for the Smartify Fumadocs site.
Run: python3 generate_docs.py
"""

import json
import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
PRODUCTS_JSON = Path("/Users/abhi/Github/Smartify/smartify-product-catalog/products.json")
IMAGES_SRC = Path("/Users/abhi/Github/Smartify/smartify-product-catalog/images")
CONTENT_DIR = SCRIPT_DIR / "content" / "docs"
PUBLIC_IMAGES = SCRIPT_DIR / "public" / "images"

# ── Category mapping ───────────────────────────────────────────────────────────
# Maps products.json category[0] → folder slug, display name, description, icon
CATEGORY_MAP = {
    "Smart Switches": {
        "slug": "switches",
        "title": "TAC Smart Switches",
        "description": "Zigbee smart switches for in-wall installation — TAC series.",
        "icon": "ToggleLeft",
        "order": 3,
    },
    "Smart Panels": {
        "slug": "panels",
        "title": "Smart Panels",
        "description": "TOQ capacitive touch panels and large-format control panels.",
        "icon": "LayoutGrid",
        "order": 4,
    },
    "Retrofit Switches": {
        "slug": "retrofit",
        "title": "Retrofit Relays & Dimmers",
        "description": "Zigbee modules that retrofit behind existing switches — no new hardware required.",
        "icon": "Wrench",
        "order": 5,
    },
    "Retrofit Dimmers": {
        "slug": "retrofit",
        "title": "Retrofit Relays & Dimmers",
        "description": "Zigbee modules that retrofit behind existing switches — no new hardware required.",
        "icon": "Wrench",
        "order": 5,
    },
    "Curtain & Shutter Control": {
        "slug": "retrofit",
        "title": "Retrofit Relays & Dimmers",
        "description": "Zigbee modules that retrofit behind existing switches — no new hardware required.",
        "icon": "Wrench",
        "order": 5,
    },
    "Sensors": {
        "slug": "sensors",
        "title": "Sensors",
        "description": "Zigbee sensors for occupancy, motion, contact, vibration, and presence detection.",
        "icon": "Activity",
        "order": 6,
    },
    "Gateways": {
        "slug": "gateways",
        "title": "Gateways & Hubs",
        "description": "Zigbee coordinators and protocol bridges — the brain of your Smartify setup.",
        "icon": "Network",
        "order": 7,
    },
    "IR Controllers": {
        "slug": "ir-blasters",
        "title": "IR Blasters",
        "description": "WiFi IR blasters to control ACs, TVs, and IR-based appliances.",
        "icon": "Wifi",
        "order": 8,
    },
    "IR & RF Controllers": {
        "slug": "ir-blasters",
        "title": "IR Blasters",
        "description": "WiFi IR blasters to control ACs, TVs, and IR-based appliances.",
        "icon": "Wifi",
        "order": 8,
    },
    "Smart Lighting": {
        "slug": "led-controllers",
        "title": "LED Controllers",
        "description": "Zigbee LED controllers for CV RGB+CCT and CCT strip lighting.",
        "icon": "Lightbulb",
        "order": 9,
    },
    "Scene Controllers": {
        "slug": "switches",
        "title": "TAC Smart Switches",
        "description": "Zigbee smart switches for in-wall installation — TAC series.",
        "icon": "ToggleLeft",
        "order": 3,
    },
    "Smart Sockets": {
        "slug": "switches",
        "title": "TAC Smart Switches",
        "description": "Zigbee smart switches for in-wall installation — TAC series.",
        "icon": "ToggleLeft",
        "order": 3,
    },
}

# ── Installation guides per category ──────────────────────────────────────────
INSTALL_GUIDES = {
    "switches": """
## Installation

### Requirements
- Standard 2-module or 4-module flush box
- Live, Neutral, and Load wires available at the switch location
- Zigbee coordinator (gateway) within range

### Steps
1. **Turn off the circuit breaker** for the circuit you're working on.
2. Remove the existing switch plate and pull out the wires.
3. Connect **Live (L)** → L terminal, **Neutral (N)** → N terminal, **Load** → the load terminal(s).
4. Tuck the module into the flush box and fit the TAC switch plate.
5. Restore power. The LED indicator will blink — the device is ready to pair.
6. Open your Zigbee coordinator app (Home Assistant, SmartThings, etc.) and put it in pairing mode.
7. Press and hold the switch for 5 seconds until the LED blinks rapidly — pairing begins.

### Wiring Notes
- Neutral wire is **required** for all TAC switches.
- Maximum load per channel: see product specifications.
- For ceiling fans, use the TAC F (fan speed controller variant).
""",
    "panels": """
## Installation

### Requirements
- Standard flush box compatible with panel dimensions
- Live, Neutral, Load wires
- Zigbee coordinator within range

### Steps
1. Switch off the circuit breaker.
2. Mount the backplate/box to the wall.
3. Connect wiring per the channel labels on the panel.
4. Snap or screw the panel into position.
5. Restore power and pair with your Zigbee coordinator.
6. Configure scenes and buttons in the Smartify or Home Assistant UI.

### Notes
- Touch panels must be grounded to avoid false triggers.
- Ensure the panel is flush against the wall for reliable capacitive touch detection.
""",
    "retrofit": """
## Installation

### Requirements
- Existing wall switch in a flush box (≥ 60mm depth recommended)
- Live, Neutral, and Load wires in the flush box
- Zigbee coordinator within range

### Steps
1. **Turn off the circuit breaker** for the affected circuit.
2. Remove the existing switch plate. The retrofit module sits *behind* the existing switch — no visible hardware change.
3. Connect wiring:
   - **Live** → L input
   - **Neutral** → N input
   - **Load** → load output(s)
4. Fit the module into the flush box. Use DIN rail adapters for panel board installation.
5. Replace the switch plate.
6. Restore power. The device will blink — ready to pair.
7. Pair with your Zigbee coordinator.

### Load Limits
- Standard relay: up to 4A direct. For 4–10A, use an external relay/SSR/contactor.
- 40A relay: rated for direct high-current switching. Proper cable sizing and circuit protection mandatory.
- Dimmer modules: resistive and leading-edge dimmable loads only. Not suitable for ceiling fans.

### Shutter Module
The shutter module controls motorised curtains, blinds, and shutters:
- **M1, M2** → motor up/down terminals
- Configure travel time in your coordinator for accurate position reporting.
""",
    "sensors": """
## Placement & Setup

### Motion Sensor
- Mount at 2–2.5m height, angled downward for best coverage.
- Avoid direct sunlight, HVAC vents, and heat sources to prevent false triggers.
- Detection angle: ~110°, range: ~7m.

### mmWave Presence Sensor (USB & Ceiling)
- Designed for **continuous presence detection** — detects stationary occupants unlike PIR sensors.
- Ceiling mount: Install in the centre of the room, directly above the target zone.
- USB variant: Connect to a USB-A power adapter; position near the area to monitor.
- Configure sensitivity and detection zones in Home Assistant.

### Contact Sensor
- Attach the main sensor to the door/window frame and the magnet to the moving panel.
- Align within 10mm for reliable open/close detection.
- Battery-powered; typical life 1–2 years.

### Vibration Sensor
- Attach to surfaces you want to monitor (doors, windows, appliances).
- Sensitive to physical shock and movement.
- Tune sensitivity via coordinator to avoid false alarms from nearby vibrations.
""",
    "gateways": """
## Setup

### Wired Gateway
1. Connect via Ethernet to your router or switch.
2. Power via USB-C.
3. Add the gateway in Home Assistant (Zigbee integration → EZSP or Zigbee2MQTT).
4. Begin pairing Zigbee devices.

### Matter Gateway (Convergia)
1. Connect via Ethernet.
2. Add to Apple Home, Google Home, or SmartThings using the Matter QR code on the device.
3. All Zigbee child devices appear automatically in the Matter fabric.

### VRV Gateway
Bridges Zigbee to VRV/VRF air conditioning systems (Daikin, Mitsubishi, etc.).
- Connect the RS-485 port to the VRV indoor unit or centralised controller.
- Configure address and baud rate per your VRV system documentation.

### DALI Gateway
Bridges Zigbee to DALI-2 lighting systems.
- Connect DALI bus terminals to the DALI line.
- Each gateway supports up to 64 DALI addresses.
- Configure via Home Assistant DALI integration.
""",
    "ir-blasters": """
## Setup

### Network
- Connect to 2.4GHz WiFi (5GHz not supported).
- Use the Smartify or Tuya Smart app for initial pairing.

### Adding Devices
1. In the app, select the IR blaster.
2. Add a new device → choose the appliance type (AC, TV, Fan, etc.).
3. Point the IR blaster at the appliance and follow the learning/preset instructions.

### AC Control (with Temp/Humidity Sensor)
The IR Blaster w/ Analog Screen includes a built-in temperature and humidity display:
- Use automations to trigger AC on/off based on room temperature.
- Integrates with Home Assistant via local Tuya or cloud Tuya integration.

### Placement
- Place in line-of-sight of target devices.
- Range: up to 8m in open space.
- Avoid placing behind glass or thick obstacles.
""",
    "led-controllers": """
## Wiring

### CV RGB+CCT Controller
- **R, G, B** → respective colour channels of your LED strip
- **WW, CW** → warm white and cool white channels
- **12V / 24V** → match your strip's voltage
- Maximum load: check product specifications per channel

### CV CCT Controller
- **WW, CW** → warm and cool white channels
- Enables smooth colour temperature tuning from warm to cool white

### Setup
1. Wire the controller per the diagram above.
2. Connect to power.
3. Pair with your Zigbee coordinator.
4. In Home Assistant, the light entity will expose colour temperature and brightness controls.

### Tips
- Use a power supply rated at ≥1.2× the total LED strip wattage.
- Run separate power supplies for runs longer than 5m to avoid voltage drop.
""",
}

# ── Category-level installation page descriptions ─────────────────────────────
CATEGORY_OVERVIEW = {
    "switches": (
        "In-wall Zigbee smart switches in the TAC series. "
        "Single, double, triple, quad, heavy-load, fan speed, scene switch, and curtain variants. "
        "Compatible with standard Indian flush boxes."
    ),
    "panels": (
        "Capacitive touch control panels in the TOQ series and large 4\"/10\" Android panels. "
        "Multi-touch, scene control, fan and socket combinations."
    ),
    "retrofit": (
        "Zigbee relay and dimmer modules that fit behind your existing switches — "
        "no visible hardware change. Also includes the Zigbee shutter module for motorised blinds."
    ),
    "sensors": (
        "Zigbee sensors for automating your home: motion, contact, vibration, and cutting-edge "
        "mmWave presence sensors that detect stationary occupants."
    ),
    "gateways": (
        "Zigbee coordinators and protocol bridges. Wired Ethernet, Matter-compatible, VRV, and DALI variants "
        "to integrate any Smartify device with any smart home platform."
    ),
    "ir-blasters": (
        "WiFi IR blasters to bring legacy appliances — ACs, TVs, fans — into your smart home "
        "without hardware replacement."
    ),
    "led-controllers": (
        "Zigbee LED controllers for CV RGB+CCT and CCT LED strips. "
        "Full colour and tunable white control via Home Assistant."
    ),
}


def slugify(name: str) -> str:
    """Convert product name to URL-safe slug."""
    s = name.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def inr(amount: int) -> str:
    """Format INR with Indian number system."""
    s = str(int(amount))
    if len(s) <= 3:
        return f"₹{s}"
    # Insert commas for Indian format
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.append(rest)
    parts.reverse()
    return "₹" + ",".join(parts) + "," + last3


def image_path_for(product: dict) -> str | None:
    """Return the public path to the product's hero image."""
    hero = product.get("images", {}).get("hero", "")
    if not hero:
        return None
    filename = Path(hero).name
    return f"/images/{filename}"


def specs_table(specs: dict) -> str:
    """Render specs as an MDX table."""
    rows = []
    field_labels = {
        "channels": "Channels",
        "max_switching_capacity": "Max Switching",
        "recommended_load": "Recommended Load",
        "installation": "Installation",
        "compatibility": "Compatibility",
    }
    # Add summary if present
    summary = specs.get("summary", "")

    for key, label in field_labels.items():
        val = specs.get(key, "")
        if val:
            rows.append(f"| {label} | {mdx_safe(val)} |")

    # Parse summary for additional specs
    if summary:
        for part in summary.split("|"):
            part = part.strip()
            if ":" in part:
                k, v = part.split(":", 1)
                label = k.strip()
                val = mdx_safe(v.strip())
                # Avoid duplicates
                if not any(label.lower() in r.lower() for r in rows):
                    rows.append(f"| {label} | {val} |")

    if not rows:
        return ""

    return "| Specification | Value |\n|---|---|\n" + "\n".join(rows)


def assistants_badges(assistants: list[str]) -> str:
    if not assistants:
        return ""
    badges = " · ".join(f"`{a}`" for a in assistants)
    return f"\n**Works with:** {badges}\n"


def yaml_str(s: str) -> str:
    """Return a YAML-safe quoted string (double-quoted, internal quotes escaped)."""
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def mdx_safe(s: str) -> str:
    """Escape characters that would be treated as JSX in MDX table cells."""
    return s.replace("<", "&lt;").replace(">", "&gt;")


def product_page(p: dict) -> str:
    """Generate MDX content for a single product page."""
    name = p["name"]
    desc_consumer = p.get("description", {}).get("consumer", "")
    desc_technical = p.get("description", {}).get("technical", "")
    specs = p.get("specs", {})
    pricing = p.get("pricing", {})
    limitations = p.get("limitations", "")
    dependencies = p.get("dependencies", "")
    assistants = p.get("assistants", [])
    protocol = p.get("protocol", "")
    device_type = p.get("device_type", "")
    img = image_path_for(p)

    first_line = (desc_consumer.splitlines()[0] if desc_consumer else f"{name} — Smartify smart home product")
    frontmatter = f"""---
title: {yaml_str(name)}
description: {yaml_str(first_line)}
---
"""

    # Hero image
    hero = f"\n![{name}]({img})\n" if img else ""

    # Quick-info callouts
    quick = []
    if protocol:
        quick.append(f"**Protocol:** {protocol}")
    if device_type:
        quick.append(f"**Type:** {device_type}")
    if pricing.get("srp_inr"):
        quick.append(f"**SRP:** {inr(pricing['srp_inr'])}")
    quick_str = "  ·  ".join(quick)
    quick_block = f"\n{quick_str}\n" if quick_str else ""

    # Assistants
    assistants_str = assistants_badges(assistants)

    # Consumer description
    consumer_section = ""
    if desc_consumer:
        consumer_section = f"\n## Overview\n\n{desc_consumer}\n"

    # Technical description
    tech_section = ""
    if desc_technical:
        tech_section = f"\n## Technical Overview\n\n{desc_technical}\n"

    # Specs table
    specs_str = specs_table(specs)
    specs_section = f"\n## Specifications\n\n{specs_str}\n" if specs_str else ""

    # Pricing
    pricing_rows = []
    if pricing.get("srp_inr"):
        pricing_rows.append(f"| SRP (incl. GST) | {inr(pricing['srp_inr'])} |")
    if pricing.get("dealer_price_inr"):
        pricing_rows.append(f"| Dealer Price | {inr(pricing['dealer_price_inr'])} |")
    if pricing.get("gst_rate"):
        pricing_rows.append(f"| GST Rate | {pricing['gst_rate']}% |")
    if pricing.get("hsn"):
        pricing_rows.append(f"| HSN Code | {pricing['hsn']} |")
    pricing_section = ""
    if pricing_rows:
        pricing_section = "\n## Pricing\n\n| | |\n|---|---|\n" + "\n".join(pricing_rows) + "\n"

    # Limitations + dependencies
    notes = []
    if limitations:
        notes.append(f"> **Important:** {limitations}")
    if dependencies:
        notes.append(f"> **Requires:** {dependencies}")
    notes_section = ("\n" + "\n\n".join(notes) + "\n") if notes else ""

    return (
        frontmatter
        + hero
        + quick_block
        + assistants_str
        + consumer_section
        + tech_section
        + specs_section
        + pricing_section
        + notes_section
    )


def category_index(slug: str, title: str, products: list[dict]) -> str:
    """Generate MDX for a category index page."""
    overview = CATEGORY_OVERVIEW.get(slug, f"{title} products from Smartify.")
    overview_safe = overview.replace(":", "—")  # Avoid YAML colon issues if used in frontmatter
    install_guide = INSTALL_GUIDES.get(slug, "")

    # Product list
    product_links = []
    for p in products:
        img = image_path_for(p)
        img_md = f"![{p['name']}]({img})" if img else ""
        desc = (p.get("description", {}).get("consumer", "") or "").splitlines()[0]
        srp = p.get("pricing", {}).get("srp_inr")
        srp_str = f" — {inr(srp)}" if srp else ""
        link_slug = p.get("slug") or slugify(p["name"])
        product_links.append(f"- [{p['name']}](./{link_slug}){srp_str}  \n  {desc}")

    products_list = "\n".join(product_links)

    return f"""---
title: {yaml_str(title)}
description: {yaml_str(overview)}
---

{overview}

## Products in this category

{products_list}

{install_guide}
"""


def top_level_index(by_category: dict) -> str:
    """Generate the top-level docs/index.mdx welcome page."""
    cat_links = []
    for slug, data in sorted(by_category.items(), key=lambda x: x[1]["order"]):
        cat_links.append(
            f"- **[{data['title']}](./{slug})** — {CATEGORY_OVERVIEW.get(slug, '')}"
        )
    cat_list = "\n".join(cat_links)

    return f"""---
title: "Smartify Documentation"
description: "Technical documentation, installation guides, and product specs for Smartify smart home automation products."
---

# Welcome to Smartify Docs

Smartify is a Zigbee-based smart home automation platform built for the Indian market.
This documentation covers every product in the catalog — specs, wiring guides, and integration references.

## Product Categories

{cat_list}

## Ecosystem

All Smartify products use **Zigbee 3.0** and integrate natively with:

- **Home Assistant** — local, no cloud, full control
- **Apple HomeKit** (via Matter hub)
- **Amazon Alexa** (via hub)
- **Google Home** (via hub)

## Getting Started

New to Smartify? Start with the [Getting Started guide](./getting-started).
"""


def getting_started() -> str:
    return """---
title: "Getting Started"
description: "Introduction to the Smartify ecosystem — what you need to get started with smart home automation."
---

# Getting Started with Smartify

## What is Smartify?

Smartify is a Zigbee 3.0 smart home automation platform designed and sold in India.
The product range covers in-wall switches, touch panels, retrofit modules, sensors, gateways, IR blasters, and LED controllers.

## What you need

| Component | Description |
|---|---|
| **Zigbee Gateway** | The coordinator that all devices connect to. Required for every installation. |
| **Switches / Panels / Sensors** | The devices you want to automate. Mix and match from the catalog. |
| **Smart Home Platform** | Home Assistant (recommended), or Apple HomeKit / Google Home / Alexa via the gateway. |
| **Internet connection** | Only needed for cloud integrations. Home Assistant runs fully local. |

## Recommended setup

1. **Start with a gateway** — the [Zigbee Gateway (Wired)](../gateways/zigbee-gateway-wired) is the most versatile option for Home Assistant users.
2. **Install Home Assistant** on a Raspberry Pi, NUC, or VM. [Home Assistant installation guide →](https://www.home-assistant.io/installation/)
3. **Add the Zigbee integration** in Home Assistant (ZHA or Zigbee2MQTT).
4. **Pair your devices** — follow the installation guide in each product's page.
5. **Build automations** using Home Assistant's automation editor.

## Network requirements

- All Zigbee devices create a **mesh network** — the more mains-powered devices, the stronger the mesh.
- Sensors and battery-powered devices are end devices and do not extend the mesh.
- Gateways require **2.4GHz WiFi or Ethernet**. 5GHz is not supported.

## Support

- [Smartify website →](https://smartify.in)
- [Home Assistant community forums →](https://community.home-assistant.io/)
"""


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✓ {path.relative_to(SCRIPT_DIR)}")


def main():
    print("Loading products.json…")
    products = json.loads(PRODUCTS_JSON.read_text())
    print(f"  {len(products)} products loaded")

    # Group products by output folder slug
    by_slug: dict[str, dict] = {}  # slug → {title, order, products: []}
    for p in products:
        primary_cat = (p.get("category") or ["Unknown"])[0]
        mapping = CATEGORY_MAP.get(primary_cat)
        if not mapping:
            print(f"  ⚠ No mapping for category: {primary_cat!r} ({p['name']})")
            continue
        slug = mapping["slug"]
        if slug not in by_slug:
            by_slug[slug] = {
                "title": mapping["title"],
                "order": mapping["order"],
                "products": [],
            }
        by_slug[slug]["products"].append(p)

    # ── Write top-level index ──────────────────────────────────────────────────
    print("\nWriting top-level index…")
    write_file(CONTENT_DIR / "index.mdx", top_level_index(by_slug))

    # ── Write getting-started ──────────────────────────────────────────────────
    print("\nWriting getting-started…")
    write_file(CONTENT_DIR / "getting-started" / "index.mdx", getting_started())
    write_file(
        CONTENT_DIR / "getting-started" / "meta.json",
        json.dumps({"title": "Getting Started", "pages": ["index"]}, indent=2),
    )

    # ── Write category pages ───────────────────────────────────────────────────
    for slug, data in sorted(by_slug.items(), key=lambda x: x[1]["order"]):
        cat_dir = CONTENT_DIR / slug
        title = data["title"]
        cat_products = data["products"]
        print(f"\nWriting {slug}/ ({len(cat_products)} products)…")

        # index.mdx
        write_file(cat_dir / "index.mdx", category_index(slug, title, cat_products))

        # per-product pages
        page_slugs = ["index"]
        for p in cat_products:
            p_slug = p.get("slug") or slugify(p["name"])
            write_file(cat_dir / f"{p_slug}.mdx", product_page(p))
            page_slugs.append(p_slug)

        # meta.json
        meta = {"title": title, "pages": page_slugs}
        write_file(cat_dir / "meta.json", json.dumps(meta, indent=2))

    # ── Write top-level meta.json ──────────────────────────────────────────────
    top_pages = ["index", "getting-started"] + [
        s for s, _ in sorted(by_slug.items(), key=lambda x: x[1]["order"])
    ]
    # Deduplicate while preserving order
    seen = set()
    top_pages_dedup = []
    for p in top_pages:
        if p not in seen:
            seen.add(p)
            top_pages_dedup.append(p)

    write_file(
        CONTENT_DIR / "meta.json",
        json.dumps({"pages": top_pages_dedup}, indent=2),
    )
    print("\n✓ All MDX files written")

    # ── Copy images ────────────────────────────────────────────────────────────
    print(f"\nCopying images from {IMAGES_SRC}…")
    PUBLIC_IMAGES.mkdir(parents=True, exist_ok=True)
    count = 0
    for img in IMAGES_SRC.glob("*.png"):
        dest = PUBLIC_IMAGES / img.name
        shutil.copy2(img, dest)
        count += 1
    print(f"  ✓ {count} images copied to public/images/")

    print("\n✅ Done! Run `npm install && npm run dev` to start the site.")


if __name__ == "__main__":
    main()
