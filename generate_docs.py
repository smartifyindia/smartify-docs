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
DOCS_DIR = SCRIPT_DIR / "content" / "docs"
CONTENT_DIR = DOCS_DIR / "products"
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
    """Return the public path to the product's hero image (URL-encoded)."""
    from urllib.parse import quote
    hero = product.get("images", {}).get("hero", "")
    if not hero:
        return None
    filename = Path(hero).name
    return f"/images/{quote(filename)}"


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


def strip_embedded_specs(text: str) -> str:
    """Strip 'Key Specifications' bullet list and inline warnings from technical description.

    The technical description in products.json embeds a spec list and ⚠ warnings
    that duplicate the structured Specifications table. This strips everything from
    the first 'Key Specifications' heading or '⚠' line onward.
    """
    for marker in ["\nKey Specifications", "\n⚠"]:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    return text.strip()


def product_page(p: dict, category_slug: str) -> str:
    """Generate MDX content for a single product page."""
    name = p["name"]
    desc_technical = p.get("description", {}).get("technical", "")
    specs = p.get("specs", {})
    pricing = p.get("pricing", {})
    limitations = p.get("limitations", "")
    dependencies = p.get("dependencies", "")
    assistants = p.get("assistants", [])
    protocol = p.get("protocol", "")
    device_type = p.get("device_type", "")
    img = image_path_for(p)

    # Frontmatter — use first line of technical description (not marketing tagline)
    tech_prose = strip_embedded_specs(desc_technical)
    tech_first_line = (
        tech_prose.splitlines()[0]
        if tech_prose
        else f"{name} — Smartify smart home product"
    )
    frontmatter = f"""---
title: {yaml_str(name)}
description: {yaml_str(tech_first_line)}
---
"""

    # Hero image
    hero = f"\n![{name}]({img})\n" if img else ""

    # Quick-info line
    quick = []
    if protocol:
        quick.append(f"**Protocol:** {protocol}")
    if device_type:
        quick.append(f"**Type:** {device_type}")
    if pricing.get("srp_inr"):
        quick.append(f"**SRP:** {inr(pricing['srp_inr'])}")
    quick_block = f"\n{'  ·  '.join(quick)}\n" if quick else ""

    # Works with badges
    assistants_str = assistants_badges(assistants)

    # Callouts — moved to top, before any section headings
    callouts = []
    if limitations:
        callouts.append(f'<Callout type="warn">{limitations}</Callout>')
    if dependencies:
        callouts.append(f'<Callout type="info">Requires: {dependencies}</Callout>')
    callouts_section = ("\n" + "\n\n".join(callouts) + "\n") if callouts else ""

    # Description — technical prose only (embedded spec list stripped)
    desc_section = f"\n## Description\n\n{tech_prose}\n" if tech_prose else ""

    # Specifications table
    specs_str = specs_table(specs)
    specs_section = f"\n## Specifications\n\n{specs_str}\n" if specs_str else ""

    # Installation — category guide on every product page (self-contained for installers)
    install_guide = INSTALL_GUIDES.get(category_slug, "")
    install_section = f"\n{install_guide}\n" if install_guide else ""

    # Ordering (renamed from Pricing)
    pricing_rows = []
    if pricing.get("srp_inr"):
        pricing_rows.append(f"| SRP (incl. GST) | {inr(pricing['srp_inr'])} |")
    if pricing.get("gst_rate"):
        pricing_rows.append(f"| GST Rate | {pricing['gst_rate']}% |")
    if pricing.get("hsn"):
        pricing_rows.append(f"| HSN Code | {pricing['hsn']} |")
    ordering_section = (
        "\n## Ordering\n\n| | |\n|---|---|\n" + "\n".join(pricing_rows) + "\n"
        if pricing_rows
        else ""
    )

    return (
        frontmatter
        + hero
        + quick_block
        + assistants_str
        + callouts_section
        + desc_section
        + specs_section
        + install_section
        + ordering_section
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
        card_desc = f"{desc}{srp_str}" if srp_str else desc
        safe_title = p["name"].replace('"', "&quot;")
        product_links.append(
            f'  <Card href="/docs/{slug}/{link_slug}" title="{safe_title}">\n    {card_desc}\n  </Card>'
        )

    products_cards = "<Cards>\n" + "\n".join(product_links) + "\n</Cards>"

    return f"""---
title: {yaml_str(title)}
description: {yaml_str(overview)}
---

{overview}

## Products in this category

{products_cards}

{install_guide}
"""


def top_level_index(by_category: dict) -> str:
    """Generate the top-level docs/index.mdx welcome page."""
    card_items = []
    for slug, data in sorted(by_category.items(), key=lambda x: x[1]["order"]):
        safe_title = data["title"].replace('"', "&quot;")
        desc = CATEGORY_OVERVIEW.get(slug, "")
        card_items.append(
            f'  <Card href="./{slug}" title="{safe_title}">\n    {desc}\n  </Card>'
        )
    cards_block = "<Cards>\n" + "\n".join(card_items) + "\n</Cards>"

    return f"""---
title: "Intro"
description: "Technical documentation for Smartify — specs, wiring guides, and integration references for every product in the catalog."
---

This is the technical documentation for **Smartify** — a Zigbee 3.0 smart home platform built for Indian homes.

## What's in these docs

| Section | What you'll find |
|---|---|
| [Getting Started](./getting-started) | Gateway setup, Home Assistant install, first device pairing |
| [Why Smartify](./why-smartify) | How Zigbee compares to WiFi switches, platform independence, Indian market fit |
| [Products](#products) | Specs, wiring, and integration details for every device in the catalog |
| [Support](./support) | Troubleshooting, contact info, community links |
| [Warranty](./warranty) | 5-year warranty terms and how to make a claim |
| [For Installers](./for-installers) | Pairing & reset procedures, Home Assistant config, wiring reference, dealer onboarding |

## Products

{cards_block}

## Compatible Platforms

All Smartify devices use **Zigbee 3.0**. Supported platforms:

- **Home Assistant** — local control, no cloud required (recommended)
- **Apple HomeKit** — via Matter-compatible gateway
- **Amazon Alexa** — via gateway
- **Google Home** — via gateway
"""


def getting_started() -> str:
    return """---
title: "Getting Started"
description: "Introduction to the Smartify ecosystem — what you need to get started with smart home automation."
---

## What you need

| Component | Description |
|---|---|
| **Zigbee Gateway** | The coordinator that all devices connect to. Required for every installation. |
| **Switches / Panels / Sensors** | The devices you want to automate. Mix and match from the catalog. |
| **Smart Home Platform** | Home Assistant (recommended), or Apple HomeKit / Google Home / Alexa via the gateway. |
| **Internet connection** | Only needed for cloud integrations. Home Assistant runs fully local. |

## Setup

<Steps>
<Step>
### Choose a gateway
The [Zigbee Gateway (Wired)](../gateways/zigbee-gateway-wired) is the most versatile option.
For Matter-native setups, use the [Convergia](../gateways/convergia).
</Step>
<Step>
### Install Home Assistant
Run on a Raspberry Pi, NUC, or VM. [Home Assistant installation →](https://www.home-assistant.io/installation/)
</Step>
<Step>
### Add the Zigbee integration
In Home Assistant: **Settings → Devices &amp; Services → Add Integration → Zigbee Home Automation (ZHA)** or Zigbee2MQTT.
</Step>
<Step>
### Pair your devices
Power on each device. Follow the pairing instructions on its product page.
</Step>
<Step>
### Build automations
Use Home Assistant's automation editor to trigger devices by time, sensor state, or scene.
</Step>
</Steps>

## Zigbee Network Notes

- All Zigbee devices create a **mesh network** — the more mains-powered devices, the stronger the mesh.
- Sensors and battery-powered devices are end devices and do not extend the mesh.
- Gateways require **2.4GHz WiFi or Ethernet**. 5GHz is not supported.

## Resources

- [Smartify website →](https://smartify.in)
- [Home Assistant community forums →](https://community.home-assistant.io/)
"""


def why_smartify() -> str:
    return """---
title: "Why Smartify"
description: "How Smartify compares to typical WiFi smart home products — protocol, reliability, and ecosystem."
---

## Zigbee vs WiFi

| | Smartify (Zigbee 3.0) | Typical WiFi switches |
|---|---|---|
| **Protocol** | Zigbee 3.0 mesh | WiFi (2.4GHz) |
| **Cloud dependency** | None — works fully local via Home Assistant | Requires vendor cloud; breaks if cloud goes down |
| **Mesh range** | Self-healing mesh — every mains device extends coverage | Point-to-point — dead zones common in large homes |
| **Network load** | Separate Zigbee radio — zero WiFi congestion | Adds every device to your WiFi router |
| **Interoperability** | Open standard — works with Home Assistant, HomeKit, Alexa, Google | Locked to vendor app; cross-brand automations unreliable |
| **Wiring** | Fits standard Indian 3-module flush boxes — no new wiring | Same, but often requires neutral wire |
| **Retrofit** | Relay and dimmer modules fit behind existing switches | Limited retrofit options |
| **Longevity** | Zigbee 3.0 is a decade-old open standard with broad support | Vendor may discontinue app or cloud service |

## Platform independence

Smartify devices are not tied to any vendor cloud or app. Because they use the open Zigbee 3.0 standard, you can control them with:

- **Home Assistant** — fully local, no subscription, unlimited automations
- **Apple HomeKit** — via Matter-compatible Convergia gateway
- **Amazon Alexa / Google Home** — via gateway

If a platform stops supporting a feature, you can switch to another without replacing hardware.

## Built for Indian homes

- All switches fit **standard 3-module and 4-module flush boxes** used across India — no custom boxes or special backboxes
- Neutral wire is **not required** for switch modules — works in older wiring layouts
- Retrofit relays and dimmers fit **behind existing switches** — no visible hardware change
- Tested for **230V / 50Hz** mains with Indian load profiles (fans, geysers, AC units)
"""


def support_page() -> str:
    return """---
title: "Support"
description: "Get help with Smartify products — technical support, troubleshooting, and contact information."
---

## Contact Support

- **Email:** support@smartify.in
- **Website:** [smartify.in/contact](https://smartify.in/contact)
- **WhatsApp:** Available via the website

## Troubleshooting

Before contacting support, check:

1. **Device not pairing** — ensure the gateway is in pairing mode and the device has been factory reset. See [Pairing & Reset](./for-installers/pairing-and-reset) for per-device procedures.
2. **Device offline** — check Zigbee mesh coverage. Mains-powered devices extend the mesh; battery devices do not.
3. **Gateway unreachable** — verify 2.4GHz WiFi or Ethernet connection. 5GHz is not supported.

## Community

- [Home Assistant community forums →](https://community.home-assistant.io/)
- [Home Assistant Zigbee docs →](https://www.home-assistant.io/integrations/zha/)
"""


def warranty_page() -> str:
    return """---
title: "Warranty"
description: "Smartify product warranty terms and how to make a warranty claim."
---

## Coverage

All Smartify products carry a **5-year warranty** from the date of purchase against manufacturing defects.

**Covered:**
- Hardware failure under normal operating conditions
- Factory defects in materials or workmanship

**Not covered:**
- Physical damage, water ingress, or incorrect installation
- Damage from voltage surges or wiring faults
- Products modified outside Smartify-authorised channels

## Making a Claim

1. Email **support@smartify.in** with your order number and a description of the issue
2. Attach proof of purchase — invoice or order confirmation
3. Smartify support will confirm eligibility and arrange replacement or repair

## Contact

- **Email:** support@smartify.in
- **Website:** [smartify.in/contact](https://smartify.in/contact)
"""


def for_installers_index() -> str:
    return """---
title: "For Installers"
description: "Technical reference for Smartify installation professionals — gateway selection, wiring, pairing, Home Assistant config, and dealer onboarding."
---

Technical reference for installation professionals. Use [**pro.smartify.in**](https://pro.smartify.in) to create estimates, manage leads, and access dealer pricing.

<Cards>
  <Card href="./gateway-selection" title="Gateway Selection">
    Which Smartify gateway to specify for each installation type — standard, HomeKit, HVAC, commercial DALI, and on-premise.
  </Card>
  <Card href="./wiring-reference" title="Wiring Reference">
    Load ratings, wiring diagrams, and compatibility notes for switches, retrofit relays, dimmers, and shutter modules.
  </Card>
  <Card href="./pairing-and-reset" title="Pairing &amp; Reset">
    Zigbee pairing modes and factory reset procedures for every Smartify device category.
  </Card>
  <Card href="./home-assistant-config" title="Home Assistant Config">
    ZHA and Zigbee2MQTT configuration, channel selection, and automation examples.
  </Card>
  <Card href="./estimate-workflow" title="Estimate Workflow">
    Step-by-step guide to creating a smart home estimate on pro.smartify.in — property details, device selection, and PDF generation.
  </Card>
  <Card href="./dealer-onboarding" title="Dealer Onboarding">
    Partnership tiers, onboarding steps, lead subscription model, and how to get started on pro.smartify.in.
  </Card>
</Cards>
"""


def for_installers_pairing() -> str:
    return """---
title: "Pairing & Reset"
description: "Zigbee pairing modes and factory reset procedures for Smartify devices."
---

Most Smartify devices enter pairing mode when **powered on for the first time** or immediately after a factory reset. The gateway must be in pairing/permit-join mode before powering on the device.

## TAC Smart Switches

| Action | Procedure |
|---|---|
| **Pair** | Power on — enters pairing mode automatically if not previously paired |
| **Factory reset** | Press and hold the top button for **10 seconds** until the LED flashes rapidly |

## TOQ Touch Panels

| Action | Procedure |
|---|---|
| **Pair** | Power on — enters pairing mode automatically if not previously paired |
| **Factory reset** | Press and hold the reset pinhole for **5 seconds** |

## Retrofit Relays & Dimmers

| Action | Procedure |
|---|---|
| **Pair** | Power on — enters pairing mode automatically if not previously paired |
| **Factory reset** | Press the reset button **5 times rapidly** within 3 seconds |

## Sensors (Contact, Motion, Vibration)

| Action | Procedure |
|---|---|
| **Pair** | Insert battery — enters pairing mode automatically |
| **Factory reset** | Remove battery, hold reset button, reinsert battery while holding, release after 5 seconds |

## mmWave Sensors

| Action | Procedure |
|---|---|
| **Pair** | Power on — enters pairing mode automatically if not previously paired |
| **Factory reset** | Press and hold reset button for **10 seconds** |

## IR Blasters

| Action | Procedure |
|---|---|
| **Pair** | Power on — enters pairing mode automatically if not previously paired |
| **Factory reset** | Press reset button **3 times** within 2 seconds |

## Tips

- If a device does not appear in ZHA/Z2M within 60 seconds, factory reset and retry.
- Pair devices close to the gateway first, then move to final location.
- Pair mains-powered devices (switches, relays) before battery sensors — they extend the mesh.
"""


def for_installers_ha_config() -> str:
    return """---
title: "Home Assistant Config"
description: "YAML examples and ZHA / Zigbee2MQTT configuration for Smartify installations."
---

## ZHA (Zigbee Home Automation)

ZHA is built into Home Assistant — no additional software needed. Recommended for most installations.

**Enable:** Settings &rarr; Devices &amp; Services &rarr; Add Integration &rarr; Zigbee Home Automation

Select the gateway's serial port or IP address and click Submit.

### Channel selection

```yaml
# configuration.yaml
zha:
  zigpy_config:
    network:
      channel: 15   # avoid channels 1, 6, 11 which overlap common WiFi bands
```

### Automation example — motion-triggered light

```yaml
alias: "Motion — Living Room Light On"
trigger:
  - platform: state
    entity_id: binary_sensor.living_room_motion
    to: "on"
action:
  - service: light.turn_on
    target:
      entity_id: light.living_room_switch
```

## Zigbee2MQTT

Zigbee2MQTT exposes devices over MQTT and gives more control over device configuration.

Install via the **Zigbee2MQTT add-on** in Home Assistant. Minimal `configuration.yaml`:

```yaml
serial:
  port: /dev/ttyUSB0
advanced:
  network_key: GENERATE
  pan_id: GENERATE
frontend:
  enabled: true
```

### Permit join via MQTT

```bash
mosquitto_pub -t zigbee2mqtt/bridge/request/permit_join -m '{"value": true, "time": 60}'
```

## Useful automations

| Automation | Trigger | Action |
|---|---|---|
| Away mode | No motion for 10 min | Turn off all lights |
| Morning scene | Time 07:00 | Lights at 40% |
| AC control | Temp sensor &gt; 28°C | IR blaster: AC on 24°C |
| Night mode | Time 22:00 | Dim all lights to 10% |
"""


def for_installers_wiring() -> str:
    return """---
title: "Wiring Reference"
description: "Load ratings, wiring diagrams, and compatibility notes for Smartify switches, retrofit relays, dimmers, LED controllers, and shutter modules."
---

<Callout type="info">
  All TAC smart switches and retrofit relays work **without a neutral wire** — Live and Load only. TOQ panels require neutral.
</Callout>

## Load Ratings

| Device | Rating | Notes |
|---|---|---|
| TAC standard switch (1–6G) | 10A / 2300W per channel | Shared L input, separate output per gang |
| TAC HL heavy-load switch | 16A / 3680W | Pumps, geysers, high-draw loads |
| TAC F fan switch | 1A / 230W | Fan speed control only |
| Retrofit relay 1Ch (standard) | 4A | Behind existing switch, no rewiring |
| Retrofit relay 1Ch (heavy) | 40A | Pumps, geysers, HVAC compressors |
| Retrofit relay 2Ch | 4A per channel | 2 independent circuits, 1 module |
| Retrofit dimmer 1Ch | 200W resistive / 100W LED | Phase-cut — dimmable loads only |
| 0–10V dimmer | — | Commercial LED drivers with 0–10V input |
| Shutter module | 5A / 1150W | AC motors with end-stop protection only |
| TAC SH shutter switch | 5A | Premium wall-switch shutter control |

## TAC Smart Switches

No neutral required. Each gang has its own output terminal; all share a single L input.

```mermaid
flowchart LR
  ML([Mains Live]) --> L[L — shared input]
  L --> L1[L1 — Load 1]
  L --> L2[L2 — Load 2]
  L --> L3[L3 — Load 3\nmulti-gang only]
```

## Retrofit Relay

Installs **behind the existing wall switch** — no rewiring, no new backbox. The existing switch toggles locally; Zigbee overrides it remotely.

```mermaid
flowchart LR
  ML([Mains Live]) --> L[L — input]
  SW([Existing Switch]) --> S1[S1 — local toggle]
  L --> RL{{Retrofit Relay}}
  S1 --> RL
  RL --> L1[L1 — Load output]
```

**Standard (4A)** — lighting, fans, general loads.
**Heavy-duty (40A)** — pumps, geysers, AC compressors, high-inrush motors.

## Retrofit Dimmer

<Callout type="warn">
  Phase-cut dimming only. **Not compatible** with non-dimmable LED drivers, fluorescent fixtures, or motors.
</Callout>

```mermaid
flowchart LR
  ML([Mains Live]) --> L[L — input]
  L --> DIM{{Retrofit Dimmer}}
  DIM --> L1[L1 — Dimmable Load]
```

- Minimum load: **5W**
- Maximum load: **200W resistive / 100W dimmable LED**
- Dimmable LED drivers must be explicitly rated for phase-cut dimming

### 0–10V Dimmer

For **commercial LED drivers** with a 0–10V control input (common in offices, retail, hospitality).

```mermaid
flowchart LR
  ML([Mains Live]) --> L[L — power input]
  L --> DIM{{0-10V Dimmer}}
  DIM --> L1[L1 — switched output]
  DIM --> DP[DIM+ / DIM−\n0–10V signal]
  L1 --> LED([LED Driver])
  DP --> LED
```

## LED Controllers

### CV-RGB+CCT (Constant Voltage)

For 12V or 24V LED strip lights. Controls RGB colour + warm/cool colour temperature simultaneously.

```mermaid
flowchart LR
  PS([12V / 24V DC PSU]) --> CTRL{{CV-RGB+CCT\nController}}
  CTRL --> R[R — Red]
  CTRL --> G[G — Green]
  CTRL --> B[B — Blue]
  CTRL --> WW[WW — Warm White]
  CTRL --> CW[CW — Cool White]
```

### CC-CCT (Constant Current)

For current-fed LED fixtures and commercial downlights (350 mA / 500 mA / 700 mA).

```mermaid
flowchart LR
  ML([Mains Live]) --> CTRL{{CC-CCT\nController}}
  CTRL --> FIX([LED Fixture\n350 / 500 / 700 mA])
```

## Shutter / Blind Module

<Callout type="warn">
  AC motors only. Motor **must have built-in end-stop protection** — do not use with motors lacking end-stops.
</Callout>

```mermaid
flowchart LR
  ML([Mains Live]) --> L[L — input]
  L --> SH{{Shutter Module}}
  SH --> L1[L1 — Motor Up]
  SH --> L2[L2 — Motor Down]
```

The module detects end-stop via current sensing. Configure travel time in the Zigbee coordinator after installation.

## TOQ Touch Panels

TOQ panels **replace** the existing switch backbox. They require a **neutral wire** in addition to Live.

```mermaid
flowchart LR
  ML([Mains Live]) --> L[L]
  N([Neutral]) --> NT[N]
  L --> TOQ{{TOQ Panel}}
  NT --> TOQ
  TOQ --> L1[L1 — Load 1]
  TOQ --> L2[L2 — Load 2\nmulti-output variants]
```

Available in 1-gang, 2-gang, and 3-gang backbox form factors.
"""


def for_installers_gateway_selection() -> str:
    return """---
title: "Gateway Selection"
description: "Which Smartify gateway to specify for each installation type — standard, HomeKit, HVAC, commercial DALI, and on-premise."
---

Every Smartify installation requires at least one gateway. All gateways act as Zigbee coordinators and support up to **128 Zigbee devices** per gateway.

## Choosing the Right Gateway

| Scenario | Recommended Gateway |
|---|---|
| Standard home automation (Home Assistant / Alexa / Google) | Zigbee Gateway (Wired) |
| Apple HomeKit integration | Zigbee Gateway (Matter) |
| Large home (&gt;128 devices) | Multiple Zigbee Gateways (Wired) |
| VRV / VRF HVAC control | Zigbee VRV Gateway |
| KNX + Zigbee + local on-premise | Convergia |
| Commercial DALI lighting | Zigbee DALI Gateway |

## Gateway Details

### Zigbee Gateway (Wired)

The standard coordinator for most residential installations.

- Connects via **Ethernet or 2.4GHz WiFi** (5GHz not supported)
- Supports **ZHA** (Zigbee Home Automation) and **Zigbee2MQTT**
- Capacity: 128 Zigbee devices
- Integrates with Home Assistant, Amazon Alexa, Google Home

### Zigbee Gateway (Matter)

Same as the Wired gateway plus Matter bridge — exposes Zigbee devices natively to **Apple HomeKit**, Google Home (Matter), and Amazon Alexa (Matter).

- Requires iOS 16+ / HomePod mini or Apple TV 4K as Matter controller
- All Zigbee devices appear as native HomeKit accessories

### Convergia

On-premise local gateway for premium installations.

- Runs locally — **no internet required for automation**
- Protocols: **Zigbee + KNX + WiFi + Matter**
- Use for: luxury residential, hospitality, offices with KNX infrastructure
- Includes local UI for configuration and scene management

### Zigbee VRV Gateway

Bridges Zigbee to **VRV/VRF HVAC systems** (Daikin, Mitsubishi, Hitachi, etc.).

- Enables thermostat-style control of centralised AC from Home Assistant
- Required for any installation with VRV/VRF indoor units

### Zigbee DALI Gateway

For **commercial lighting** with DALI ballasts and drivers.

- Controls DALI-addressed fixtures individually or in groups
- Use in offices, retail, hospitality where DALI infrastructure already exists

## Scaling Beyond 128 Devices

Add a second (or third) gateway on the same Zigbee channel with different PAN IDs. In Home Assistant, each gateway is a separate ZHA/Z2M integration instance.

<Callout type="info">
  Pair mains-powered devices (switches, relays, panels) before battery sensors. Every mains device extends the Zigbee mesh — a dense mesh improves reliability for sensors at the edges.
</Callout>
"""


def for_installers_estimate_workflow() -> str:
    return """---
title: "Estimate Workflow"
description: "Step-by-step guide to creating a smart home estimate on pro.smartify.in — property details, AI device selection, and PDF generation."
---

Estimates are created in [**pro.smartify.in**](https://pro.smartify.in) using a 3-phase workflow. The output is a professional itemised quote with GST breakdown, ready to share with the client.

## Phase 1 — Property Details

<Steps>
<Step>
### Select or create a client contact
Search existing contacts or add a new one (name, phone, email).
</Step>
<Step>
### Enter property details
- **Property type:** Studio/1RK, 1BHK–7BHK+, Villa, Penthouse, Commercial
- **Carpet area** (sqft)
- **Construction status:** Pre-construction, Under Construction, Constructed, Under Renovation
</Step>
<Step>
### Upload floor plan (optional)
Upload a JPG or PNG floor plan. The AI analyses it to detect rooms and suggest device placement. You can adjust room polygons manually.
</Step>
<Step>
### Select automation categories
Choose which systems to include:
- Security &amp; Safety (sensors, presence detection)
- Comfort &amp; Climate (fans, AC, VRV)
- Lighting &amp; Atmosphere (dimmers, LED strips, motorised blinds)
- Energy Efficiency (retrofit relays, smart switching)
- Smart Living (wall switches, touch panels, IR control)
</Step>
<Step>
### Set technology preferences
- Protocol: Zigbee, Matter, KNX, WiFi, etc.
- Brand preferences (Smartify + 25 other brands supported)
- Expert installation toggle
</Step>
</Steps>

## Phase 2 — Device Selection

<Steps>
<Step>
### AI recommendation (optional)
Enable AI analysis to get an automatic device list based on property type, carpet area, and selected categories. The AI suggests SKUs, quantities, and room placement.
</Step>
<Step>
### Review and adjust
Browse the suggested list room by room. Add, remove, or change quantities. You can also search the full catalog manually and add any device.
</Step>
<Step>
### Add custom items
Add non-catalog items (third-party devices, accessories, labour) as custom line items.
</Step>
</Steps>

## Phase 3 — Report Generation

The platform automatically:

1. Fetches live pricing from the product catalog
2. Applies your org-level dealer pricing (up to 30% off MRP)
3. Calculates GST per item (rates: 5%, 12%, 18%, or 28% depending on HSN code)
4. Scores the project across 5 automation categories (0–5 stars each)
5. Generates a full PDF with itemised BOM, GST summary, and installation notes

## Sharing the Estimate

- **PDF share link** — send to client via WhatsApp or email directly from the platform
- **Status tracking** — move estimates through: Draft → Sent → Quoted → Won / Lost
- **Lead lock-in** — sharing an estimate with a client triggers 30-day lead exclusivity (prevents another installer from claiming the same lead)

## Pricing Rules

| Rule | Detail |
|---|---|
| Max dealer discount | 30% off MRP (Smartify products) |
| GST | Calculated per item based on HSN code |
| Custom items | Manually set price + GST rate |
| Estimate range | Low / Medium / High based on device mix |
"""


def for_installers_dealer() -> str:
    return """---
title: "Dealer Onboarding"
description: "Partnership tiers, onboarding steps, and the lead subscription model for Smartify installers."
---

## Smartify Pro — Installer Platform

[**pro.smartify.in**](https://pro.smartify.in) gives registered dealers access to:

- AI-powered smart home estimate builder
- Full product catalog with dealer pricing (up to 30% off MRP)
- Lead pipeline from Smartify's customer portals
- PDF estimate generation and client sharing
- Team management and CRM integrations (Zoho, Zapier, Make, Google Sheets, WhatsApp)

## Partnership Tiers

| | Franchisee Partner | Multi-brand Partner |
|---|---|---|
| **Annual fee** | ₹30,000 | ₹60,000 |
| **Commission** | 7.5% | 15% |
| **ROI guarantee** | — | Yes |
| **Demo kit** | Required (purchase) | Not required |
| **Training** | Required | — |
| **Uncovered locations** | Free leads | Free leads |
| **Qualification fee** | ₹2,500 | ₹2,500 |

## Onboarding Steps

<Steps>
<Step>
### Phone verification
Register at [pro.smartify.in](https://pro.smartify.in). Verify your phone number via OTP.
</Step>
<Step>
### Choose partnership type
Select Franchisee or Multi-brand Partner based on your business model.
</Step>
<Step>
### Business details
Enter company name, GST number, address, and contact information.
</Step>
<Step>
### Select service categories
Choose which automation categories you specialise in (Security, Lighting, Climate, etc.).
</Step>
<Step>
### Select serviceable locations
Pick the cities and pin codes you serve. Demand scoring is shown per location.
</Step>
<Step>
### Pay qualification fee
₹2,500 qualification fee to activate your account.
</Step>
<Step>
### Account active
Dashboard, estimate builder, and lead pipeline are immediately available.
</Step>
</Steps>

## Lead Subscription Model

Leads come from Smartify's customer portals and are distributed to registered installers in the relevant area.

### Location demand tiers

| Demand | Cities | Cost per lead |
|---|---|---|
| Uncovered | Any unsubscribed city | 0 credits (free) |
| Low | Kolkata, Jaipur, Lucknow, Patna, etc. | 10 credits |
| Medium | Hyderabad, Pune, Ahmedabad, Chennai, Kochi | 45 credits |
| High | Mumbai, Delhi, Bangalore | 120 credits |

### Monthly lead volume tiers

| Tier | Leads/month | Annual cost |
|---|---|---|
| Base | 6 (uncovered only) | Free |
| Tier 1 | 12 | ₹1,20,000/year |
| Tier 2 | 20 | ₹2,40,000/year |
| Tier 3 | 30 | ₹3,60,000/year |
| Tier 4 | 42 | ₹4,80,000/year |
| Tier 5 | 56 | ₹6,00,000/year |

### Boost campaigns (one-time paid lead batches)

| Spend | Expected leads |
|---|---|
| ₹5,000 | 7–12 |
| ₹10,000 | 15–25 |
| ₹15,000 | 20–35 |
| ₹20,000 | 30–50 |
| ₹25,000 | 35–60 |
| ₹30,000 | 45–75 |

### Lead rules

- **Lock-in:** Sharing an estimate with a client triggers 30-day exclusivity — no other installer can claim that lead
- **Referral:** Unused leads can be referred back for credit
- **Conversion minimum:** 15% conversion rate required to access additional leads
- **Pipeline cap:** Max 15 active pipeline leads per installer

## Contact

For dealer enquiries: **sales@smartify.in**
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
    write_file(CONTENT_DIR / "getting-started.mdx", getting_started())

    # ── Write why-smartify ─────────────────────────────────────────────────────
    print("\nWriting why-smartify…")
    write_file(CONTENT_DIR / "why-smartify.mdx", why_smartify())

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
            write_file(cat_dir / f"{p_slug}.mdx", product_page(p, slug))
            page_slugs.append(p_slug)

        # meta.json
        meta = {"title": title, "pages": page_slugs}
        write_file(cat_dir / "meta.json", json.dumps(meta, indent=2))

    # ── Write support / warranty ───────────────────────────────────────────────
    print("\nWriting support & warranty…")
    write_file(CONTENT_DIR / "support.mdx", support_page())
    write_file(CONTENT_DIR / "warranty.mdx", warranty_page())

    # ── Write for-installers ───────────────────────────────────────────────────
    print("\nWriting for-installers…")
    fi_dir = DOCS_DIR / "for-installers"
    write_file(fi_dir / "index.mdx", for_installers_index())
    write_file(fi_dir / "gateway-selection.mdx", for_installers_gateway_selection())
    write_file(fi_dir / "wiring-reference.mdx", for_installers_wiring())
    write_file(fi_dir / "pairing-and-reset.mdx", for_installers_pairing())
    write_file(fi_dir / "home-assistant-config.mdx", for_installers_ha_config())
    write_file(fi_dir / "estimate-workflow.mdx", for_installers_estimate_workflow())
    write_file(fi_dir / "dealer-onboarding.mdx", for_installers_dealer())
    write_file(
        fi_dir / "meta.json",
        json.dumps({
            "title": "Installation Guides",
            "description": "Wiring, pairing, and configuration guides",
            "root": True,
            "pages": [
                "index",
                "gateway-selection",
                "wiring-reference",
                "pairing-and-reset",
                "home-assistant-config",
                "estimate-workflow",
                "dealer-onboarding",
            ],
        }, indent=2),
    )

    # ── Write products meta.json ──────────────────────────────────────────────
    product_slugs = [s for s, _ in sorted(by_slug.items(), key=lambda x: x[1]["order"])]
    products_pages = [
        "index",
        "getting-started",
        "why-smartify",
        "---Catalog---",
        *product_slugs,
        "---Support---",
        "support",
        "warranty",
    ]
    write_file(
        CONTENT_DIR / "meta.json",
        json.dumps({
            "title": "Products",
            "description": "Smart home device catalog and guides",
            "root": True,
            "pages": products_pages,
        }, indent=2),
    )

    # ── Write root meta.json ──────────────────────────────────────────────────
    write_file(
        DOCS_DIR / "meta.json",
        json.dumps({
            "pages": ["products", "for-installers", "smartify-pro"],
        }, indent=2),
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
