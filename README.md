# Bambu Lab OrcaSlicer Profile Generator

A curated set of pre-tested, opinionated [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) profiles for Bambu Lab 3D printers, distributed as a generator. These are the settings I personally use on my own printers, tuned for reliability over speed.

Rather than sharing static profile files that go stale, this generator produces a complete matrix of process, machine, and filament profiles for every combination of printer, nozzle size, and material mode - all from a single script with documented, research-backed constants. Enable your printers, run the script, and get a consistent set of profiles that are correctly scaled and cross-referenced.

## What It Generates

From a single `python generate.py` command:

- **Machine profiles** for every printer/nozzle combination with custom gcode
- **Process profiles** for every printer/nozzle/material mode combination
- **Filament profiles** for every material/printer combination with appropriate plate temps
- **OrcaSlicer.conf patches** for flush multiplier and printer names

All profiles inherit from Bambu Lab's system baselines and only store overrides, exactly as OrcaSlicer expects.

## Supported Printers

All current Bambu Lab printers are supported, plus Anycubic Kobra 3 and newer.
Enable the ones you own:

| Printer | Type | Enclosure | Nozzles |
|---------|------|-----------|---------|
| Bambu X1 Carbon | CoreXY | Yes | 0.2 / 0.4 / 0.6 / 0.8 |
| Bambu X1 | CoreXY | Yes | 0.2 / 0.4 / 0.6 / 0.8 |
| Bambu X1E | CoreXY | Yes | 0.2 / 0.4 / 0.6 / 0.8 |
| Bambu P1S | CoreXY | Yes | 0.2 / 0.4 / 0.6 / 0.8 |
| Bambu P1P | CoreXY | No | 0.2 / 0.4 / 0.6 / 0.8 |
| Bambu A1 | i3 gantry | No | 0.2 / 0.4 / 0.6 / 0.8 |
| Bambu A1 Mini | i3 gantry | No | 0.2 / 0.4 / 0.6 / 0.8 |
| Anycubic Kobra 3 | bedslinger | No | 0.4 / 0.6 / 0.8 |
| Anycubic Kobra 3 Max | bedslinger | No | 0.4 / 0.6 / 0.8 |
| Anycubic Kobra S1 | CoreXY | Yes | 0.4 |
| Anycubic Kobra S1 Max | CoreXY | Yes | 0.4 / 0.6 / 0.8 |
| Anycubic Kobra X | bedslinger | No | 0.4 |

**Elegoo** (all OrcaSlicer-supported FDM models) are supported the same way:

| Enclosed CoreXY (mirror X1C) | Open-frame bedslingers (mirror A1) |
|------------------------------|------------------------------------|
| Centauri, Centauri Carbon, Centauri Carbon 2 | Neptune, Neptune 2 / 2D / 2S / 3 / 3 Max / 3 Plus / 3 Pro, Neptune 4 / 4 Max / 4 Plus / 4 Pro, Neptune X, OrangeStorm Giga |

The Anycubic and Elegoo profiles inherit each printer's **default OrcaSlicer
start/end gcode**, but every speed, temperature, and acceleration setting mirrors
the equivalent Bambu profile: enclosed models mirror the X1C, open-frame models
mirror the A1. This requires the built-in Anycubic / Elegoo profiles that ship
with current OrcaSlicer (enable those vendors in OrcaSlicer's printer selection).
Nozzle sizes without a matching vendor "Standard" preset (e.g. Anycubic Kobra 3's
0.2, S1 Max's 0.25, and Elegoo's 1.0mm variants) are omitted; the older Elegoo
Neptunes (2 / 2D / 2S / 3 / X) share Elegoo's common "Neptune" process preset.

## Material Modes

| Profile | Purpose |
|---------|---------|
| **PLA** | Conservative everyday default. Works with all PLA brands and geometries. |
| **PLA Fast** | Near-stock speeds for faster prints while keeping good visual accuracy. |
| **PETG/ABS** | Slow and careful. Tuned for PETG's stringy nature and slow first layer. |
| **PLA Silk** | Low acceleration for uniform shimmer across the entire surface. |
| **PLA Draft** | Maximum speed, minimum structure. Shape preview only. |
| **PLA Delicate** | Ultra-conservative for miniatures and tiny features. Very low acceleration. |
| **PLA MM** | Multi-material color prints. Slower for reliable color changes. |
| **PLA+PETG+PVA MM** | Multi-material with dissolvable support. Most conservative profile. |
| **TPU** | Flexible filament. Very slow, minimal retraction. |

## Filaments

| Filament | Optional | Notes |
|----------|----------|-------|
| PLA | No | Standard PLA, works with all brands |
| PETG | No | Functional parts, slow and careful |
| ABS | No | Enclosure required |
| PLA Silk | Yes | Shimmer PLA with own process profile |
| PLA Wood | Yes | Wood-fill, low volumetric speed to prevent clogs |
| PVA | Yes | Dissolvable support interface, requires AMS |
| PLA-CF | Yes | Carbon fiber PLA, requires hardened nozzle |
| ASA | Yes | UV-resistant ABS alternative, enclosure required |
| TPU | Yes | Flexible, requires own process profile |
| BVOH | Yes | Better dissolvable support, works with PETG unlike PVA |

**Tested filaments:** PLA, PETG, ABS, PVA, PLA Silk, and PLA Wood have all been personally tested and validated by the author. PLA-CF, ASA, TPU, and BVOH are configured based on research into community consensus and conservative optimizations - feedback welcome via issues if you use these.

## Philosophy

The guiding principle is **"if it works at 300 mm/s it should work even better at 90 mm/s."** We trade speed for reliability and universal compatibility.

- **Conservative by default.** PLA Standard runs at 30-45% of Bambu's stock speeds. Every PLA brand works, every geometry prints.
- **Never exceed stock.** No speed or acceleration value is higher than Bambu Lab's own defaults.
- **Printer-aware.** CoreXY printers (X1C, P1S) use gyroid infill with low acceleration. Gantry printers (A1, A1M) use crosshatch with speed/accel caps to reduce bed vibration.
- **Nozzle-scaled.** Layer heights, wall counts, shell thicknesses, speeds, and accelerations are calculated from nozzle diameter. Change one constant, get correct values everywhere.
- **Enclosure-aware.** ABS/ASA only generate for enclosed printers. Plate temps adjust for trapped vs ambient heat.
- **Tested values, cited sources.** Key decisions reference community research with linked forum threads and wiki pages.

Full technical documentation, design justifications, community references, and a profile selection guide are in the docblock at the top of `generate.py`.

## Quick Start

### 1. Clone

```bash
git clone https://github.com/hansonxyz/Bambu-Labs-Orcaslicer-Generator.git
cd Bambu-Labs-Orcaslicer-Generator
```

### 2. Configure

Open `generate.py` and edit the two configuration sections near the top:

**Enable your printers:**
```python
ENABLED_PRINTERS = {
    "X1C": True,     # set True for printers you own
    "P1S": False,
    "A1M": True,
    # ...
}
```

**Enable optional filaments:**
```python
OPTIONAL_FILAMENTS = {
    "PLA Silk": True,
    "PLA Wood": True,
    "TPU":      False,   # set True if you print flexible
    # ...
}
```

### 3. Close OrcaSlicer

This is important. OrcaSlicer overwrites profile files when it closes. Always close it before generating.

### 4. Generate

```bash
python generate.py
```

That's it. Open OrcaSlicer and your profiles are ready.

## Command Line Options

| Option | Description |
|--------|-------------|
| *(no args)* | Backup existing profiles, then generate and overwrite |
| `--dry-run` | Show what would be generated without writing any files |
| `--backup-only` | Create a backup and exit |
| `--clean --yes` | Delete all existing generated profiles before generating new ones |
| `--clean` | Same as above but prompts for confirmation (requires interactive terminal) |
| `--output-dir <path>` | Write profiles to a custom directory instead of OrcaSlicer's config |

### Typical Workflows

**After OrcaSlicer trampled your settings:**
```bash
python generate.py
```

**First time setup or switching printers:**
```bash
python generate.py --clean --yes
```

**Preview what will be generated:**
```bash
python generate.py --dry-run
```

**Export profiles for another machine:**
```bash
python generate.py --output-dir ./export
```

## Desktop App (GUI)

Prefer not to edit Python? A cross-platform desktop front-end (`gui.py`) exposes
the same configuration as checkboxes and runs the generator with one click,
streaming its output into a log pane. Your selections are saved to `config.json`,
so the GUI and the `python generate.py` CLI stay in sync.

**Run from source:**
```bash
pip install -r requirements.txt
python gui.py
```

The controls shown in the GUI are not hard-coded — they are defined declaratively
in `gui_schema.json`. To expose a new printer, filament, or option, add an entry
to that file; no GUI code changes are needed.

### Building a distributable

The app bundles into a single executable (and, on Windows, an installer) with
[PyInstaller](https://pyinstaller.org/) and [Inno Setup](https://jrsoftware.org/isinfo.php):

```bash
pip install -r requirements.txt

# One-file app -> dist/OrcaConfGen[.exe]  (dist/OrcaConfGen.app on macOS)
pyinstaller --noconfirm OrcaConfGen.spec

# Windows installer (per-user, no admin) -> Output/OrcaConfGen-Setup-<version>.exe
iscc installer.iss
```

The installer is per-user, so the app can write `config.json` and `backups/`
next to its own executable without administrator rights. Tagged pushes (`v*`)
also build Windows/macOS/Linux artifacts automatically via GitHub Actions
(`.github/workflows/build.yml`).

## Backups

Every run (except `--output-dir`) creates a timestamped backup of your existing profiles in the `./backups/` directory before writing anything. If something goes wrong, your previous profiles are preserved.

## Platform Support

The generator auto-detects your operating system and finds OrcaSlicer's config directory:

- **Windows:** `%APPDATA%/OrcaSlicer/`
- **macOS:** `~/Library/Application Support/OrcaSlicer/`
- **Linux:** `~/.config/OrcaSlicer/`

## Custom Gcode

Each printer has a bundled gcode file (`brian_*_gcode.json`) containing custom start, end, and filament change gcode. Key customizations over Bambu Lab stock:

- Parallel nozzle pre-heating during bed heating (faster startup)
- Z-offset for all build plate types (-0.04mm textured PEI, -0.02mm others)
- Shorter purge line (less waste)
- Reduced toolchange travel speeds (less vibration, more reliable)
- Annotated with block-level comments explaining each operation

To modify gcode, edit the JSON files directly and regenerate.

## Documentation

The complete technical documentation lives in the docblock at the top of `generate.py`, including:

- Baseline philosophy and every universal override with rationale
- Printer variant differences (CoreXY vs i3, enclosed vs open-air)
- Each material mode's speed/accel/structural philosophy
- Nozzle scaling rules
- Filament profile details and temperature research
- Ironing settings with community references
- Custom gcode change lists per printer
- OrcaSlicer.conf patches
- Community reference links for all research-based values
- Profile selection guide and manual considerations for users

## Contributing

This project is a living configuration that evolves with testing and community feedback. If you use these profiles and find improvements or issues, especially with the community-tested filaments (PLA-CF, ASA, TPU), please open an issue.

## License

[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](LICENSE.md)

Copyright (c) 2026 Brian Hanson ([HansonXYZ](https://github.com/hansonxyz))
