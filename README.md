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

All current Bambu Lab printers are supported. Enable the ones you own:

| Printer | Type | Enclosure |
|---------|------|-----------|
| X1 Carbon | CoreXY | Yes |
| X1 | CoreXY | Yes |
| X1E | CoreXY | Yes |
| P1S | CoreXY | Yes |
| P1P | CoreXY | No |
| A1 | i3 gantry | No |
| A1 Mini | i3 gantry | No |

Each printer supports 0.2mm, 0.4mm, 0.6mm, and 0.8mm nozzle sizes.

## Material Modes

| Profile | Purpose |
|---------|---------|
| **PLA** | Conservative everyday default. Works with all PLA brands and geometries. |
| **PLA Fast** | Near-stock speeds with targeted quality reductions. Good benchy quality. |
| **PETG/ABS** | Slow and careful. Tuned for PETG's stringy nature and slow first layer. |
| **PLA Silk** | Low acceleration for uniform shimmer across the entire surface. |
| **PLA Draft** | Maximum speed, minimum structure. Shape preview only. |
| **PLA Delicate** | Ultra-conservative for miniatures and tiny features. Very low acceleration. |
| **PLA MM** | Multi-material color prints. Slower for reliable color changes. |
| **PLA+PETG+PVA MM** | Multi-material with dissolvable support. Most conservative profile. |
| **TPU** | Flexible filament. Very slow, minimal retraction. *(optional, community-tested)* |

## Optional Filaments

Core filaments (PLA, PETG, ABS) are always generated. Specialty filaments can be toggled:

| Filament | Default | Notes |
|----------|---------|-------|
| PLA Silk | Enabled | Shimmer PLA with own process profile |
| PLA Wood | Enabled | Wood-fill, low volumetric speed to prevent clogs |
| PLA-CF | Disabled | Carbon fiber PLA, requires hardened nozzle *(community-tested)* |
| ASA | Disabled | UV-resistant ABS alternative, enclosure required *(community-tested)* |
| TPU | Disabled | Flexible, requires own process profile *(community-tested)* |
| PVA | Enabled | Dissolvable support interface, requires AMS |
| BVOH | Disabled | Better dissolvable support, works with PETG unlike PVA |

Profiles marked *(community-tested)* are based on community consensus and conservative optimizations but have not been personally validated by the author. Feedback welcome via issues.

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
