"""
OrcaSlicer Profile Generator
=============================

Generates process profiles, machine profiles, and filament profiles for
Brian's Bambu Lab X1 Carbon (X1C) and A1 Mini (A1M) printers across
0.2/0.4/0.6/0.8mm nozzle sizes and 8 material modes.

Outputs: 8 machine profiles, 64 process profiles, ~13 filament profiles.
Run `python generate.py` to backup + regenerate everything.

Also patches OrcaSlicer.conf for flush multiplier (0.85) and printer names.

BASELINE PHILOSOPHY
-------------------
All profiles start from Bambu Lab's system defaults and apply a conservative
override strategy. The guiding principle is "if it works at 300mm/s it works
even better at 90mm/s." We trade speed for reliability and universal
compatibility across all PLA brands and irregular object geometries.

- Slow first layer (20mm/s speed, 25mm/s infill, 75 accel) for bed adhesion
- Wider line widths (105% outer, 112% inner/infill) for strength and gap filling
- Wall print order: inner/outer/inner (sandwich mode for best dimensional accuracy)
- Seam on back of model (less visible than BBL's default "aligned")
- No brim by default (enabled per-project)
- Detect thin walls always on (BBL leaves this off, skipping thin features)
- Elephant foot compensation 0.15mm (BBL A1M default was 0, corrected)
- Support pre-configured but disabled (consistent settings when user enables)
- Support on build plate only (interior support via manual painting)
- Reduce crossing walls (less stringing)
- Gyroid infill at 10% on X1C (strongest per material, low accel to absorb shaking)
- Crosshatch infill at 15% on A1M (less violent direction changes for gantry arm)
- Ironing pre-configured for museum quality but not enabled (see IRONING section)
- Flush into infill enabled (redirects purge into infill to reduce waste)
- Shell thickness targets: top 1.0mm / bottom 0.8mm (PLA/Silk/Delicate/MM)
                           top 0.8mm / bottom 0.6mm (PLA Fast, PETG)
  Layers calculated dynamically from targets, minimum 2 layers always (except Draft)

PRINTER VARIANTS: X1C vs A1M
-----------------------------
The A1M has a cantilevered gantry arm instead of the X1C's rigid enclosed CoreXY.
This fundamentally limits what the printer can handle.

- A1M max print speed hard cap: 150mm/s (including travel)
- A1M max acceleration hard cap: 5000 mm/s²
- A1M infill: crosshatch instead of gyroid (less violent, gentler on gantry)
- A1M infill accel: 3000 (capped below 5000 for stability on small parts)
- A1M first layer: hard cap at 16/20 mm/s (speed/infill) for bed adhesion
- A1M Delicate mode: accel cap 1500, travel cap 60, speeds 35% slower than base
- A1M filament retraction: +0.1mm over X1C baseline
- A1M plate temps for PLA: 57°C across all plates (X1C: 48°C, enclosure traps heat)
- Both printers: z-offset gcode (-0.04 textured PEI, -0.02 everything else)
- Both printers: custom gcode bundled as JSON files (single source of truth)

MATERIAL MODES
--------------
All modes share the universal baseline above. Each mode changes the speed/accel
philosophy and structural settings for different use cases.

B PLA (default standard):
  - Conservative speeds: 60 outer wall, 90 inner wall, 65 infill
  - High outer wall accel (10000) for Bambu input shaping on visible surfaces
  - Works reliably across all PLA brands including cheap ones
  - 2 walls, top 1.0mm / bottom 0.8mm shell targets

B PLA Fast:
  - Balanced speed: visually accurate (good benchy) but faster than standard
  - Outer wall 100mm/s (most conservative - biggest visual impact), inner 200, infill 175
  - Outer wall accel halved to 5000 (community consensus for reducing ringing)
  - Crosshatch infill on all printers (less vibration than gyroid at speed)
  - Thinner shells: top 0.8mm / bottom 0.6mm
  - Ref: https://forum.bambulab.com/t/outer-wall-acceleration/192135
  - Ref: https://forum.bambulab.com/t/easy-path-to-high-quality-150mm-s-print-speed/60639

B PETG ABS:
  - All speeds 45mm/s - Brian's tested sweet spot for PETG
  - Very slow first layer: 12mm/s speed, 15mm/s infill (critical for PETG adhesion)
  - All acceleration capped at 2500
  - Alternate extra wall for PETG's weaker inter-layer bonding
  - Overhang speeds all 30mm/s (PETG droops more)
  - Thinner shells: top 0.8mm / bottom 0.6mm
  - 0.8mm nozzle: 1 wall + alternate (already thick enough)
  - Primary profile for 0.6mm nozzle functional prints on portable A1M

B PLA Silk:
  - Slower speeds (~80% of PLA): 48 outer, 70 inner
  - LOW acceleration (1500 outer/top, 2500 inner/infill) - NOT high
  - Silk PLA additives make flow inconsistencies highly visible as blotchy shimmer
  - Low accel avoids nozzle pressure spikes that cause uneven extrusion
  - 3 walls for better silk surface quality

B PLA Draft:
  - As fast as the printer allows: 125mm/s everything
  - Single wall + alternate, 1 bottom layer, max layer height for nozzle
  - Just need to see what the shape looks like in 3D, nothing else matters
  - Tree support for easy removal, cubic infill at 7%
  - 0.2mm nozzle exception: 2 walls, no alternate, 2 top/bottom layers

B PLA Delicate:
  - Ultra-conservative for small intricate parts (D&D minis, etc)
  - All speeds 45mm/s, all acceleration 500 mm/s²
  - Low accel prevents jolting that knocks over tiny fragile features
  - 3 walls, cubic infill 15%, interlocking beam enabled
  - X1C: 20% speed reduction on top of base (speeds become ~36mm/s)
  - A1M: 35% speed reduction on top of base (speeds become ~29mm/s)
    - A1M Delicate accel cap: 1500 (tighter than general 5000)
    - A1M Delicate travel cap: 60mm/s

B PLA MM (Multi-Material):
  - Slower than PLA standard (75/55/60 inner/infill/outer) with 2500 accel cap
  - Intentionally conservative: colors bleeding, materials not sticking, prime tower
    issues all improve with slower speeds
  - Flush into infill (saves material) but NOT into support (needs clean surfaces)
  - Cubic infill 15% (less wall deformation than gyroid, pattern doesn't align with walls)
  - Dynamic wall count: minimum 1.0mm wall thickness target (3 walls on 0.4mm,
    2 walls on 0.6/0.8mm nozzle where 2 walls already exceeds 1mm)

B PLA+PETG+PVA MM:
  - Most conservative profile: PLA and PETG don't naturally adhere
  - 0.18mm layer height for more inter-material bonding surface area
  - Zero support z-distance so PVA prints directly against model surface
  - Concentric support interface with zero spacing (solid PVA interface layer)
  - Very slow speeds (40-55mm/s) for precise multi-material deposition
  - Same 1.0mm minimum wall thickness target and cubic infill as PLA MM

NOZZLE SCALING
--------------
- Layer height: 50% of nozzle diameter (draft: ~60%, PVA MM: ~45%)
- Wall loops: +2 on 0.2mm nozzle to maintain minimum wall thickness
  (or dynamically calculated from min_wall_thickness target for MM profiles)
- Speed: 0.9x at 0.6mm, 0.85x at 0.8mm (larger bead = more material per second)
- Acceleration: 0.95x at 0.6mm, 0.9x at 0.8mm (larger bead = more ringing)
- Support z-distance: scales with layer height
- PETG 0.8mm nozzle: 1 wall + alternate extra wall (already exceeds thickness min)
- Draft 0.2mm nozzle: 2 walls, no alternate, 2 top/bottom layers

FILAMENT PROFILES
-----------------
- Generated per-printer (B PLA, B PLA A1M, etc)
- Materials: PLA, PETG, ABS (X1C only), PVA, BVOH, PLA Silk, PLA Wood
- A1M variants get +0.1mm retraction length
- X1C PLA plate temps: 48°C across all plate types (enclosure traps heat)
- A1M PLA plate temps: 57°C across all plate types (open air needs more heat)
- ABS supertack: 90°C
- PVA first layer: 215°C (lower than regular 220 to reduce stringing/degradation)
- PLA Wood: max volumetric 2 mm³/s, first layer 210°C (wood particles clog at high temp)
- PLA Silk: first layer 225°C (lower than regular 232°C to reduce globbing)
- BVOH: 210°C, 2.5 mm³/s volumetric, compatible with both PLA and PETG unlike PVA

MACHINE PROFILES
----------------
- Brian X1C 0.2/0.4/0.6/0.8: inherit BBL X1C + custom gcode (brian_x1c_gcode.json)
- Brian A1M 0.2/0.4/0.6/0.8: inherit BBL A1M + custom gcode (brian_a1m_gcode.json)
- Both gcode files are bundled as the single source of truth
- See comment block above gcode loading functions for detailed change lists

IRONING
-------
Pre-configured for museum quality but NOT enabled by default (user enables per-project).
Settings tuned for maximum smoothness when ironing is explicitly desired.

- Flow: 20% (BBL default 10% causes patchy gaps; community range 18-39%)
- Spacing: 0.1mm (tightest practical; nozzle covers each point ~4x for uniform smoothing)
- Speed: 80mm/s (slower than BBL default 30mm/s would need less flow, but 80mm/s with
  20% flow is the sweet spot; avoids corner bump artifacts that occur at 150mm/s)
- Ref: https://forum.bambulab.com/t/ironing-help/198091
- Ref: https://forum.bambulab.com/t/why-is-my-ironing-patchy/75896
- Ref: https://creativestudios.com/3d-printing/3d-printing---perfect-ironing-settings

ORCASLICER.CONF PATCHES
------------------------
- Flush multiplier: 0.85 (15% reduction, conservative, safe for all filaments)
  BBL's auto-calculated volumes are ~57% higher than needed per community calibration.
  0.85 is well within safe range for all filaments including silk and PVA.
  Ref: https://forum.bambulab.com/t/ams-flushing-volumes-calibration-purge-reduction/37062
- Printer names: "X1 Carbon" and "A1 Mini" (friendlier than serial-based defaults)
- Known printer serials and access codes maintained for LAN mode

COMMUNITY REFERENCES
--------------------
Key values chosen based on community research and consensus:

Silk PLA acceleration (1500/2500 low accel, not high):
  https://www.sovol3d.com/blogs/news/how-many-3d-print-top-layers-for-smooth-strong-results
  https://www.creality.com/blog/pla-print-temperature

A1M PLA bed temperature (57°C, not BBL's 60-65°C default):
  https://forum.bambulab.com/t/wth-bed-temperature-for-a1-vs-p1s/51628
  https://github.com/bambulab/BambuStudio/issues/4883

ABS supertack plate temperature (90°C, was erroneously 35°C):
  Community consensus for ABS bed temp on supertack/high-temp plate.

PVA first layer temperature (215°C, lowered from 225°C):
  PVA degrades and strings at high temps. Lower first layer reduces issues.

PLA Wood max volumetric speed (2 mm³/s) and first layer temp (210°C):
  Wood particles restrict flow and char at high temps, causing clogs.
  https://colorfabb.com/blog/post/how-to-print-with-woodfill-filament

Shell thickness targets (1.0mm top / 0.8mm bottom):
  https://www.sovol3d.com/blogs/news/how-many-3d-print-top-layers-for-smooth-strong-results
  https://www.hubs.com/knowledge-base/selecting-optimal-shell-and-infill-parameters-fdm-3d-printing/

PLA Fast outer wall acceleration (5000, halved from 10000):
  Community consensus: outer wall accel matters more than speed for surface quality.
  https://forum.bambulab.com/t/outer-wall-acceleration/192135

A1M start gcode optimizations (fan reduction, z-offset):
  https://forum.bambulab.com/t/optimized-a1-mini-start-g-code-quick-and-quiet-version/116364

Filament change travel speed reduction (F18000/F15000 -> F9000):
  Conservative approach prioritizing reliability over toolchange speed.

BVOH vs PVA comparison (BVOH superior but expensive):
  https://support.bcn3d.com/knowledge/bvoh-vs-pva
  https://help.prusa3d.com/article/water-soluble-materials-pva-bvoh_162860
"""

import json
import math
import os
import platform
import shutil
import sys
import time
from copy import deepcopy
from pathlib import Path

# =============================================================================
# PATHS
# =============================================================================


def _detect_orca_dir() -> Path:
    """Detect OrcaSlicer config directory based on OS."""
    system = platform.system()
    if system == "Windows":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return Path(appdata) / "OrcaSlicer"
        return Path.home() / "AppData" / "Roaming" / "OrcaSlicer"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "OrcaSlicer"
    elif system == "Linux":
        # Check XDG first, then fallback
        xdg = os.environ.get("XDG_CONFIG_HOME", "")
        if xdg:
            return Path(xdg) / "OrcaSlicer"
        return Path.home() / ".config" / "OrcaSlicer"
    else:
        print(f"WARNING: Unknown OS '{system}', defaulting to current directory")
        return Path("OrcaSlicer")


def _setup_paths(output_dir: Path = None):
    """Configure all path globals. If output_dir is specified, profiles are
    written there instead of the OrcaSlicer config directory."""
    global ORCA_DIR, PROCESS_DIR, MACHINE_DIR, FILAMENT_DIR
    global FILAMENT_BASE_SUBDIR
    global ORCA_CONF_PATH

    ORCA_DIR = _detect_orca_dir()

    if output_dir:
        # Write profiles to arbitrary directory (no OrcaSlicer.conf patching)
        base = Path(output_dir)
        PROCESS_DIR = base / "process"
        MACHINE_DIR = base / "machine"
        FILAMENT_DIR = base / "filament"
    else:
        # Write to OrcaSlicer user profile directories
        PROCESS_DIR = ORCA_DIR / "user" / "default" / "process"
        MACHINE_DIR = ORCA_DIR / "user" / "default" / "machine"
        FILAMENT_DIR = ORCA_DIR / "user" / "default" / "filament"

    FILAMENT_BASE_SUBDIR = FILAMENT_DIR / "base"

    # OrcaSlicer.conf (only patched when not using --output-dir)
    ORCA_CONF_PATH = ORCA_DIR / "OrcaSlicer.conf"


# Initialize with defaults (may be reconfigured in main via --output-dir)
ORCA_DIR = _detect_orca_dir()
PROCESS_DIR = ORCA_DIR / "user" / "default" / "process"
MACHINE_DIR = ORCA_DIR / "user" / "default" / "machine"
FILAMENT_DIR = ORCA_DIR / "user" / "default" / "filament"
FILAMENT_BASE_SUBDIR = FILAMENT_DIR / "base"
ORCA_CONF_PATH = ORCA_DIR / "OrcaSlicer.conf"

BACKUP_DIR = Path(__file__).parent / "backups"
ORCA_PROFILE_VERSION = "1.10.0.35"

# =============================================================================
# USER-MODIFIABLE: ENABLED PRINTERS
# Toggle which printers to generate profiles for.
# Set to True to enable, False to disable.
# =============================================================================

# =============================================================================
# PROFILE GUIDE: CHOOSING THE RIGHT PROFILE
#
# PLA (Standard)
#   Your everyday default. Use this for most PLA prints. Prioritizes
#   reliability across all brands and geometries over speed. Good strength,
#   clean surfaces, works well with irregular shapes and overhangs.
#   When in doubt, use this one.
#
# PLA Fast
#   For prints where speed matters and the geometry is forgiving - models
#   with broad flat surfaces, simple curves, and consistent wall angles.
#   Produces a visually accurate print (good benchy quality) but may show
#   minor artifacts on very fine details or sharp overhangs. Not ideal for
#   miniatures or parts with tiny contact patches on the build plate.
#
# PETG ABS
#   For functional parts in PETG or ABS. Very conservative speeds tuned
#   for PETG's tendency to string and droop. The extremely slow first layer
#   is critical - do not increase it. Use this for anything structural:
#   brackets, mounts, enclosures, mechanical parts. On the A1M this is
#   the primary profile for 0.6mm nozzle portable/on-site work.
#
# PLA Silk
#   For silk/shimmer PLA filaments. Low acceleration keeps extrusion
#   perfectly uniform so the silk effect is consistent across the entire
#   surface. Slower than standard but the visual result is worth it.
#   Three walls help the shimmer look its best.
#
# PLA Draft
#   Maximum speed, minimum structure. Use this to quickly visualize what
#   an object will look like in 3D before committing to a full print.
#   Single wall, thin top/bottom, tall layers. The result has essentially
#   no structural integrity - it's a shape preview, not a usable part.
#
# PLA Delicate
#   For small, intricate parts with fine features: D&D miniatures, jewelry
#   prototypes, detailed figurines, or any model with features under ~3mm.
#   Ultra-low acceleration prevents vibration from knocking over fragile
#   features or distorting tiny details. Three walls and cubic infill give
#   uniform strength even on very small cross-sections.
#
# PLA MM (Multi-Material)
#   For multi-color PLA prints. Slowed down from standard to improve
#   reliability of color changes and reduce color bleed between materials.
#   Cubic infill minimizes wall deformation that could show through as
#   visual artifacts on decorative multi-color surfaces.
#
# PLA+PETG+PVA MM
#   The most conservative profile, for prints combining PLA, PETG, and
#   dissolvable PVA support. Finer layer height and zero support gap
#   maximize adhesion between materials that don't naturally bond well.
#   Very slow to ensure precise deposition of each material.
#
# TPU (optional, enable in OPTIONAL_FILAMENTS)
#   For flexible parts: phone cases, gaskets, bumpers, grips. Very slow
#   speeds (30mm/s) and gentle acceleration are required - TPU is flexible
#   and will jam if pushed too fast. Cannot use AMS; filament must be fed
#   manually. Grid infill gives the most predictable flex behavior.
#   NOTE: Community-consensus settings, not personally tested.
#
# ENCLOSURE NOTES (X1C / P1S)
# ----------------------------
# All X1C and P1S settings assume the enclosure is CLOSED during printing,
# with the following exceptions:
#
# *** PETG REQUIRES THE LID TO BE REMOVED ***
# *** Printing PETG with the enclosure fully closed WILL cause heat creep ***
# *** in the hotend, leading to clogs and failed prints. Remove the top ***
# *** lid (glass panel on X1C, plastic lid on P1S) before printing PETG. ***
#
# ABS and ASA require the enclosure closed (they warp without it).
# PLA works either way but benefits from the chamber fan running (auto in gcode).
#
# MANUAL CONSIDERATIONS
# ---------------------
# These settings must be adjusted per-project in OrcaSlicer:
#
# Support:
#   Support is DISABLED by default across all profiles. Enable it per-project
#   as needed. The support configuration (spacing, z-distance, speeds) is
#   pre-set consistently so behavior is predictable when you turn it on.
#
# Flush into infill (multi-material):
#   Enabled by default to reduce waste. DISABLE this manually when printing
#   with white, light-colored, or translucent filaments - the colored purge
#   material routed into infill can show through thin walls. This is most
#   visible on parts with 2 walls; 3-wall profiles (Silk, Delicate, MM)
#   are largely immune.
#
# PVA/BVOH as support interface:
#   PVA and BVOH are ONLY for support interface layers - never use them
#   for the bulk support structure or as a build plate contact material.
#   Always use PLA for the support base and only PVA/BVOH for the
#   interface layers that touch the model. This saves expensive material
#   and avoids adhesion issues.
#   In OrcaSlicer: set the support interface filament to your PVA/BVOH
#   slot (e.g. filament slot 4). Leave the support filament as your
#   primary PLA. The PLA+PETG+PVA MM profile has this pre-configured.
#
# Brim:
#   Disabled by default. Enable manually for parts with very small bed
#   contact area or tall thin geometry that's prone to tipping. Most prints
#   on supertack plate don't need it.
#
# Ironing:
#   Pre-configured but not enabled. Turn on per-project for flat top
#   surfaces that need a glossy finish (e.g. nameplates, signs, lids).
#   Adds significant time - only use where the top surface matters.
#
# Build plate type:
#   Plate temperatures are set per-filament-profile and vary by plate type.
#   PEI plates (textured, smooth, engineering) and SuperTack use 48°C on
#   enclosed printers, 57°C on open-air. Cool plate uses 35°C on all
#   printers (it has a low-temp coating that PLA softens on above 55°C).
#   Switching plates in OrcaSlicer applies the correct temp automatically.
#
# Part removal:
#   PEI plates: wait for the bed to cool before removing parts. Pulling
#   parts off hot PEI can damage the coating.
#   SuperTack: parts release naturally as the plate cools. No force needed.
#
# Elephant foot compensation:
#   Set to 0.15mm globally. If a first layer is too tight or too loose,
#   adjust the Z-offset in the machine gcode (-0.02 for most plates,
#   -0.04 for textured PEI) rather than changing this value.
# =============================================================================

ENABLED_PRINTERS = {
    "X1C": True,     # Bambu Lab X1 Carbon (enclosed CoreXY, hardened nozzle, lidar)
    "X1":  False,    # Bambu Lab X1 (enclosed CoreXY, stainless nozzle, lidar)
    "X1E": False,    # Bambu Lab X1E (enclosed CoreXY, enterprise, air filtration)
    "P1S": False,    # Bambu Lab P1S (enclosed CoreXY, no lidar)
    "P1P": False,    # Bambu Lab P1P (open-frame CoreXY, no enclosure)
    "A1":  False,    # Bambu Lab A1 (i3 gantry, 256mm bed)
    "A1M": True,     # Bambu Lab A1 Mini (i3 gantry, 180mm bed)
}

# =============================================================================
# USER-MODIFIABLE: OPTIONAL FILAMENTS & PROFILES
# Core filaments (PLA, PETG, ABS, PVA) are always generated.
# Toggle optional specialty filaments and their associated process profiles.
#
# NOTE: PLA-CF, ASA, and TPU profiles are based on community consensus and
# conservative optimizations but have NOT been personally tested by the author.
# Please provide feedback if you use these and discover any issues.
#
# Enclosure requirements:
#   ASA requires an enclosure (X1C/P1S only, will not generate for A1/A1M)
#   PLA-CF and TPU do not require an enclosure
#   *** PETG REQUIRES the enclosure lid to be REMOVED on X1C/P1S ***
#   *** Printing PETG with the lid closed WILL cause heat creep and clogging ***
# =============================================================================

OPTIONAL_FILAMENTS = {
    "PLA Silk": True,    # Shimmer PLA - needs own process profile (low accel)
    "PLA Wood": True,    # Wood-fill PLA - uses PLA process, low volumetric speed
    "PLA-CF":   False,   # Carbon fiber PLA - uses PLA process, needs hardened nozzle
    "ASA":      False,   # UV-resistant ABS alt - uses PETG/ABS process, enclosure required
    "TPU":      False,   # Flexible - needs own process profile (very slow)
    "PVA":      True,    # Dissolvable support interface - requires AMS
    "BVOH":     False,   # Dissolvable support - better than PVA, works with PETG, requires AMS
}

# =============================================================================
# PRINTERS
# =============================================================================

# Printer group: determines which settings philosophy to use.
# "corexy" = CoreXY frame (X1C, X1, X1E, P1S, P1P) - uses corexy speed/accel/infill
# "i3"     = cantilevered gantry (A1, A1M) - uses i3 caps and crosshatch infill
PRINTER_GROUP = {
    "X1C": "corexy",
    "X1":  "corexy",
    "X1E": "corexy",
    "P1S": "corexy",
    "P1P": "corexy",
    "A1":  "i3",
    "A1M": "i3",
}

# Whether the printer has an enclosure (affects ABS/ASA availability)
PRINTER_ENCLOSED = {
    "X1C": True,
    "X1":  True,
    "X1E": True,
    "P1S": True,
    "P1P": False,   # Open frame - no enclosure
    "A1":  False,
    "A1M": False,
}

# Profile name suffix per printer (X1C is default, no suffix)
PRINTER_SUFFIX = {
    "X1C": "",
    "X1":  " X1",
    "X1E": " X1E",
    "P1S": " P1S",
    "P1P": " P1P",
    "A1":  " A1",
    "A1M": " A1M",
}

# Filament profile suffix per printer (used in filament naming)
# Each printer gets its own filament profiles even if values are shared,
# so compatible_printers is always specific to that printer.
FILAMENT_PRINTER_SUFFIX = {
    "X1C": " X1C",
    "X1":  " X1",
    "X1E": " X1E",
    "P1S": " P1S",
    "P1P": " P1P",
    "A1":  " A1",
    "A1M": " A1M",
}

ALL_PRINTERS = {
    "X1C": {
        "nozzle_base_profiles": {
            0.2: ("0.10mm Standard @BBL X1C 0.2 nozzle", "GP007"),
            0.4: ("0.20mm Standard @BBL X1C", "GP004"),
            0.6: ("0.30mm Standard @BBL X1C 0.6 nozzle", "GP010"),
            0.8: ("0.40mm Standard @BBL X1C 0.8 nozzle", "GP009"),
        },
        "machine_profile_names": {
            0.2: "Brian X1C 0.2",
            0.4: "Brian X1C 0.4",
            0.6: "Brian X1C 0.6",
            0.8: "Brian X1C 0.8",
        },
        "machine_base_profiles": {
            0.2: ("Bambu Lab X1 Carbon 0.2 nozzle", "GM002"),
            0.4: ("Bambu Lab X1 Carbon 0.4 nozzle", "GM001"),
            0.6: ("Bambu Lab X1 Carbon 0.6 nozzle", "GM005"),
            0.8: ("Bambu Lab X1 Carbon 0.8 nozzle", "GM004"),
        },
        "machine_extras": {
            "printable_area": ["0x0", "256x0", "256x248", "0x248"],
            "thumbnails": "48x48/PNG, 300x300/PNG",
        },
        "gcode_file": "brian_x1c_gcode.json",
    },
    "X1": {
        "nozzle_base_profiles": {
            0.2: ("0.10mm Standard @BBL X1C 0.2 nozzle", "GP007"),  # X1 uses X1C process profiles
            0.4: ("0.20mm Standard @BBL X1C", "GP004"),
            0.6: ("0.30mm Standard @BBL X1C 0.6 nozzle", "GP010"),
            0.8: ("0.40mm Standard @BBL X1C 0.8 nozzle", "GP009"),
        },
        "machine_profile_names": {
            0.2: "Brian X1 0.2",
            0.4: "Brian X1 0.4",
            0.6: "Brian X1 0.6",
            0.8: "Brian X1 0.8",
        },
        "machine_base_profiles": {
            0.2: ("Bambu Lab X1 0.2 nozzle", "GM008"),
            0.4: ("Bambu Lab X1 0.4 nozzle", "GM003"),
            0.6: ("Bambu Lab X1 0.6 nozzle", "GM006"),
            0.8: ("Bambu Lab X1 0.8 nozzle", "GM007"),
        },
        "machine_extras": {
            "printable_area": ["0x0", "256x0", "256x248", "0x248"],
            "thumbnails": "48x48/PNG, 300x300/PNG",
        },
        "gcode_file": "brian_x1_gcode.json",  # identical to X1C gcode
    },
    "X1E": {
        "nozzle_base_profiles": {
            0.2: ("0.10mm Standard @BBL X1C 0.2 nozzle", "GP007"),  # X1E uses X1C process profiles
            0.4: ("0.20mm Standard @BBL X1C", "GP004"),
            0.6: ("0.30mm Standard @BBL X1C 0.6 nozzle", "GP010"),
            0.8: ("0.40mm Standard @BBL X1C 0.8 nozzle", "GP009"),
        },
        "machine_profile_names": {
            0.2: "Brian X1E 0.2",
            0.4: "Brian X1E 0.4",
            0.6: "Brian X1E 0.6",
            0.8: "Brian X1E 0.8",
        },
        "machine_base_profiles": {
            0.2: ("Bambu Lab X1E 0.2 nozzle", "GM025"),
            0.4: ("Bambu Lab X1E 0.4 nozzle", "GM026"),
            0.6: ("Bambu Lab X1E 0.6 nozzle", "GM027"),
            0.8: ("Bambu Lab X1E 0.8 nozzle", "GM028"),
        },
        "machine_extras": {},
        "gcode_file": "brian_x1e_gcode.json",
    },
    "P1S": {
        "nozzle_base_profiles": {
            0.2: ("0.10mm Standard @BBL X1C 0.2 nozzle", "GP007"),  # P1S uses X1C process profiles
            0.4: ("0.20mm Standard @BBL X1C", "GP004"),
            0.6: ("0.30mm Standard @BBL X1C 0.6 nozzle", "GP010"),
            0.8: ("0.40mm Standard @BBL X1C 0.8 nozzle", "GP009"),
        },
        "machine_profile_names": {
            0.2: "Brian P1S 0.2",
            0.4: "Brian P1S 0.4",
            0.6: "Brian P1S 0.6",
            0.8: "Brian P1S 0.8",
        },
        "machine_base_profiles": {
            0.2: ("Bambu Lab P1S 0.2 nozzle", "GM015"),
            0.4: ("Bambu Lab P1S 0.4 nozzle", "GM014"),
            0.6: ("Bambu Lab P1S 0.6 nozzle", "GM016"),
            0.8: ("Bambu Lab P1S 0.8 nozzle", "GM017"),
        },
        "machine_extras": {},
        "gcode_file": "brian_p1s_gcode.json",
    },
    "P1P": {
        "nozzle_base_profiles": {
            0.2: ("0.10mm Standard @BBL X1C 0.2 nozzle", "GP007"),  # P1P uses X1C process profiles
            0.4: ("0.20mm Standard @BBL X1C", "GP004"),
            0.6: ("0.30mm Standard @BBL X1C 0.6 nozzle", "GP010"),
            0.8: ("0.40mm Standard @BBL X1C 0.8 nozzle", "GP009"),
        },
        "machine_profile_names": {
            0.2: "Brian P1P 0.2",
            0.4: "Brian P1P 0.4",
            0.6: "Brian P1P 0.6",
            0.8: "Brian P1P 0.8",
        },
        "machine_base_profiles": {
            0.2: ("Bambu Lab P1P 0.2 nozzle", "GM010"),
            0.4: ("Bambu Lab P1P 0.4 nozzle", "GM013"),
            0.6: ("Bambu Lab P1P 0.6 nozzle", "GM011"),
            0.8: ("Bambu Lab P1P 0.8 nozzle", "GM012"),
        },
        "machine_extras": {},
        "gcode_file": "brian_p1p_gcode.json",
    },
    "A1": {
        "nozzle_base_profiles": {
            0.2: ("0.10mm Standard @BBL A1 0.2 nozzle", "GP083"),
            0.4: ("0.20mm Standard @BBL A1", "GP079"),
            0.6: ("0.30mm Standard @BBL A1 0.6 nozzle", "GP096"),
            0.8: ("0.40mm Standard @BBL A1 0.8 nozzle", "GP098"),
        },
        "machine_profile_names": {
            0.2: "Brian A1 0.2",
            0.4: "Brian A1 0.4",
            0.6: "Brian A1 0.6",
            0.8: "Brian A1 0.8",
        },
        "machine_base_profiles": {
            0.2: ("Bambu Lab A1 0.2 nozzle", "GM031"),
            0.4: ("Bambu Lab A1 0.4 nozzle", "GM030"),
            0.6: ("Bambu Lab A1 0.6 nozzle", "GM032"),
            0.8: ("Bambu Lab A1 0.8 nozzle", "GM033"),
        },
        "machine_extras": {},
        "gcode_file": "brian_a1_gcode.json",
    },
    "A1M": {
        "nozzle_base_profiles": {
            0.2: ("0.10mm Standard @BBL A1M 0.2 nozzle", "GP083"),
            0.4: ("0.20mm Standard @BBL A1M", "GP000"),
            0.6: ("0.30mm Standard @BBL A1M 0.6 nozzle", "GP096"),
            0.8: ("0.40mm Standard @BBL A1M 0.8 nozzle", "GP098"),
        },
        "machine_profile_names": {
            0.2: "Brian A1M 0.2",
            0.4: "Brian A1M 0.4",
            0.6: "Brian A1M 0.6",
            0.8: "Brian A1M 0.8",
        },
        "machine_base_profiles": {
            0.2: ("Bambu Lab A1 mini 0.2 nozzle", "GM021"),
            0.4: ("Bambu Lab A1 mini 0.4 nozzle", "GM020"),
            0.6: ("Bambu Lab A1 mini 0.6 nozzle", "GM022"),
            0.8: ("Bambu Lab A1 mini 0.8 nozzle", "GM023"),
        },
        "machine_extras": {},
        "gcode_file": "brian_a1m_gcode.json",
    },
}

# Active printers dict (filtered by ENABLED_PRINTERS)
PRINTERS = {k: v for k, v in ALL_PRINTERS.items() if ENABLED_PRINTERS.get(k, False)}

NOZZLE_SIZES = [0.2, 0.4, 0.6, 0.8]

# =============================================================================
# LAYER 1: UNIVERSAL BRIAN OVERRIDES
# Applied to every single profile regardless of printer/nozzle/material.
# =============================================================================

UNIVERSAL_OVERRIDES = {
    # First layer - slow for bed adhesion reliability
    "initial_layer_speed": "20",
    "initial_layer_infill_speed": "25",
    "initial_layer_acceleration": "75",
    "initial_layer_line_width": "125%",
    "initial_layer_travel_speed": "75%",
    "slow_down_layers": "3",

    # Line widths - slightly over-extruded for strength and gap filling
    "line_width": "105%",
    "outer_wall_line_width": "105%",
    "inner_wall_line_width": "112%",
    "sparse_infill_line_width": "112%",
    "internal_solid_infill_line_width": "105%",
    "top_surface_line_width": "105%",
    "support_line_width": "105%",

    # Structural preferences
    "elefant_foot_compensation": "0.15",
    "detect_thin_wall": "1",
    "reduce_crossing_wall": "1",
    "wall_infill_order": "inner wall/outer wall/inner wall",
    "seam_position": "back",
    "brim_type": "no_brim",
    "bottom_shell_layers": "2",
    "top_shell_layers": "4",
    "top_shell_thickness": "1.0",
    "bottom_shell_thickness": "0.8",

    # Ironing (configured, not enabled - user enables per project)
    "ironing_flow": "20%",
    "ironing_spacing": "0.1",
    "ironing_speed": "80",

    # Support (configured, DISABLED by default - user enables per project)
    "enable_support": "0",
    "support_on_build_plate_only": "1",
    "support_base_pattern_spacing": "5",
    "support_bottom_interface_spacing": "1",
    "support_interface_spacing": "1",
    "support_interface_speed": "35",
    "support_bottom_z_distance": "0.15",
    "support_top_z_distance": "0.15",
    "support_object_first_layer_gap": "0.5",
    "support_speed": "90",

    # Raft
    "raft_first_layer_density": "25%",
    "raft_first_layer_expansion": "1",

    # Multi-material (configured for when it's needed)
    "flush_into_infill": "1",
    "independent_support_layer_height": "0",
}

# =============================================================================
# LAYER 2: PRINTER-SPECIFIC DELTAS
# Differences driven by printer hardware design.
# =============================================================================

PRINTER_DELTAS = {
    "corexy": {
        # Gyroid: strongest per material used, but shakes the printer.
        # Low infill accel (2000) absorbs the shock on rigid CoreXY frame.
        "sparse_infill_pattern": "gyroid",
        "sparse_infill_density": "10%",
        "sparse_infill_acceleration": "2000",
        "travel_acceleration": "2500",
    },
    "i3": {
        # Crosshatch: less violent direction changes than gyroid.
        # Better match for cantilevered gantry arm (A1/A1M).
        # 15% compensates for crosshatch being slightly weaker than gyroid.
        # 3000 accel: crosshatch is gentler so can go higher than corexy's 2000,
        # but still capped well below 6000 default for gantry stability on small parts.
        "sparse_infill_pattern": "crosshatch",
        "sparse_infill_density": "15%",
        "sparse_infill_acceleration": "3000",
        "travel_acceleration": "4500",
    },
}

# =============================================================================
# LAYER 3: MATERIAL MODES
# Each mode is a dict of overrides applied on top of universal + printer deltas.
# =============================================================================

# --- PLA Standard ---
# Conservative baseline. ~30-45% of BBL speeds.
# Works reliably across all PLA brands and object geometries.
PLA_STANDARD = {
    "outer_wall_speed": "60",
    "inner_wall_speed": "90",
    "sparse_infill_speed": "65",
    "internal_solid_infill_speed": "90",
    "gap_infill_speed": "50",
    "top_surface_speed": "90",
    "travel_speed": "175",
    # Acceleration
    "outer_wall_acceleration": "10000",
    "top_surface_acceleration": "3500",
    "internal_solid_infill_acceleration": "5000",
    # Layer
    "layer_height": "0.20",
    # Walls
    "wall_loops": "2",
    "ensure_vertical_shell_thickness": "ensure_moderate",
}

# --- PLA Fast ---
# Balanced speed: visually accurate (good benchy) but meaningfully faster than standard.
# Outer wall gets extra conservative treatment since it's the most visible surface.
# Uses crosshatch infill on all printers to reduce vibration at speed.
PLA_FAST = {
    "outer_wall_speed": "100",       # 50% of BBL - most impactful for visual quality
    "inner_wall_speed": "200",       # 67% of BBL - hidden, can be fast
    "sparse_infill_speed": "175",    # 65% of BBL - slowed for vibration
    "internal_solid_infill_speed": "175",  # matches infill
    "gap_infill_speed": "150",       # between walls, quality matters
    "top_surface_speed": "120",      # visible surface, moderate
    "support_speed": "120",          # faster than standard
    "travel_speed": "350",           # 70% of BBL
    # Acceleration - outer wall halved from standard for surface quality
    "outer_wall_acceleration": "5000",
    "top_surface_acceleration": "2500",
    "internal_solid_infill_acceleration": "3000",
    "travel_acceleration": "4000",
    # Crosshatch on all printers for PLA Fast - less vibration than gyroid at speed
    "sparse_infill_pattern": "crosshatch",
    "sparse_infill_density": "15%",
    "sparse_infill_acceleration": "3000",
    # Layer
    "layer_height": "0.20",
    # Shells - thinner than standard, faster print
    "top_shell_thickness": "0.8",
    "bottom_shell_thickness": "0.6",
    # Walls
    "wall_loops": "2",
    "ensure_vertical_shell_thickness": "ensure_moderate",
}

# --- PETG/ABS ---
# Slow and careful. PETG needs restraint - stringy, worse layer adhesion.
# Very slow first layer is critical for PETG bed adhesion.
# 45 mm/s is Brian's tested sweet spot for PETG.
PETG_ABS = {
    "outer_wall_speed": "45",
    "inner_wall_speed": "45",
    "sparse_infill_speed": "45",
    "internal_solid_infill_speed": "45",
    "gap_infill_speed": "30",
    "top_surface_speed": "45",
    "support_speed": "45",
    "support_interface_speed": "30",
    "travel_speed": "200",
    # Very slow first layer - critical for PETG
    "initial_layer_speed": "12",
    "initial_layer_infill_speed": "15",
    "initial_layer_travel_speed": "30",
    # Acceleration - moderate, all uniform
    "default_acceleration": "2500",
    "outer_wall_acceleration": "2500",
    "inner_wall_acceleration": "2500",
    "top_surface_acceleration": "2500",
    "travel_acceleration": "5000",
    # Layer
    "layer_height": "0.20",
    # Walls - alternate extra wall for PETG bonding strength
    "wall_loops": "2",
    "alternate_extra_wall": "1",
    "ensure_vertical_shell_thickness": "ensure_moderate",
    # Overhangs - PETG droops more
    "overhang_1_4_speed": "30",
    "overhang_2_4_speed": "30",
    "overhang_4_4_speed": "30",
    "bridge_speed": "30",
    # Shells
    "top_shell_thickness": "0.8",
    "bottom_shell_thickness": "0.6",
    # Infill
    "sparse_infill_density": "11%",
    "support_threshold_angle": "35",
}

# --- PLA Silk ---
# Slower speeds with LOW acceleration for consistent extrusion.
# Silk PLA additives make flow inconsistencies highly visible as blotchy shimmer.
# Low acceleration avoids pressure spikes in the nozzle that cause uneven extrusion.
# Outer walls and top surfaces get the lowest accel (1500) since they're most visible.
PLA_SILK = {
    "outer_wall_speed": "48",
    "inner_wall_speed": "70",
    "sparse_infill_speed": "55",
    "internal_solid_infill_speed": "70",
    "gap_infill_speed": "50",
    "top_surface_speed": "70",
    "travel_speed": "175",
    # LOW acceleration - smooth, even extrusion for consistent silk shimmer
    "default_acceleration": "2500",
    "outer_wall_acceleration": "1500",
    "inner_wall_acceleration": "2500",
    "top_surface_acceleration": "1500",
    "internal_solid_infill_acceleration": "2500",
    "travel_acceleration": "5000",
    # Layer
    "layer_height": "0.20",
    # Extra wall for silk surface quality
    "wall_loops": "3",
    "ensure_vertical_shell_thickness": "ensure_moderate",
}

# --- PLA Draft ---
# As fast as the printer is designed for. Visualize shape quickly.
# Structural integrity and surface quality don't matter.
# Single wall, minimal shells, max layer height for nozzle.
PLA_DRAFT = {
    "outer_wall_speed": "125",
    "inner_wall_speed": "125",
    "sparse_infill_speed": "125",
    "internal_solid_infill_speed": "125",
    "gap_infill_speed": "125",
    "top_surface_speed": "125",
    "support_speed": "100",
    "support_interface_speed": "75",
    "travel_speed": "175",
    # Acceleration - fast but not insane
    "default_acceleration": "5000",
    "inner_wall_acceleration": "5000",
    "top_surface_acceleration": "3500",
    "travel_acceleration": "2500",
    # Layer - tallest recommended for nozzle (scaled in nozzle layer)
    "layer_height": "0.24",
    # Minimal structure
    "wall_loops": "1",
    "alternate_extra_wall": "1",
    "bottom_shell_layers": "1",
    "bottom_shell_thickness": "0.2",
    "top_shell_layers": "2",
    "top_shell_thickness": "0.3",
    # Minimal infill
    "sparse_infill_density": "7%",
    "sparse_infill_pattern": "cubic",
    # Tree support for easy removal on draft prints
    "support_type": "tree(auto)",
    "skirt_loops": "2",
    "slow_down_layers": "2",
    "initial_layer_line_width": "105%",
}

# --- PLA Delicate ---
# Ultra-conservative for small intricate parts (D&D minis etc).
# 45 mm/s everything, 500 accel everywhere.
# Low accel prevents jolting that knocks over small fragile features.
PLA_DELICATE = {
    "outer_wall_speed": "45",
    "inner_wall_speed": "45",
    "sparse_infill_speed": "45",
    "internal_solid_infill_speed": "45",
    "gap_infill_speed": "45",
    "top_surface_speed": "45",
    "support_speed": "40",
    "support_interface_speed": "45",
    "travel_speed": "100",
    # Ultra-low acceleration everywhere
    "default_acceleration": "500",
    "outer_wall_acceleration": "500",
    "inner_wall_acceleration": "500",
    "top_surface_acceleration": "500",
    "travel_acceleration": "500",
    # Layer
    "layer_height": "0.20",
    # Extra walls for tiny parts
    "wall_loops": "3",
    # Cubic infill - more uniform than gyroid for tiny parts
    "sparse_infill_pattern": "cubic",
    "sparse_infill_density": "15%",
    # Extra features for small parts
    "interlocking_beam": "1",
    "skirt_loops": "2",
    "support_threshold_angle": "35",
    "enable_prime_tower": "0",
}

# --- PLA MM (Multi-Material) ---
# Slower than standard for inter-material reliability.
# Colors bleeding, materials not sticking, prime tower issues all
# improve with slower speeds.
PLA_MM = {
    "outer_wall_speed": "60",
    "inner_wall_speed": "75",
    "sparse_infill_speed": "55",
    "internal_solid_infill_speed": "75",
    "gap_infill_speed": "55",
    "top_surface_speed": "55",
    "support_speed": "75",
    "support_interface_speed": "40",
    "travel_speed": "175",
    # Capped acceleration for MM reliability
    "default_acceleration": "2500",
    "outer_wall_acceleration": "10000",
    "inner_wall_acceleration": "2500",
    "sparse_infill_acceleration": "2000",
    "travel_acceleration": "2500",
    # Layer
    "layer_height": "0.20",
    # Cubic infill - less wall deformation than gyroid, pattern doesn't align with walls
    "sparse_infill_pattern": "cubic",
    "sparse_infill_density": "15%",
    # Wall thickness target: 1mm minimum for color separation (calculated dynamically)
    "min_wall_thickness": "1.0",
    # MM-specific
    "flush_into_infill": "1",
    "flush_into_support": "0",
    "timelapse_type": "1",
    "support_filament": "1",
    "support_base_pattern_spacing": "3.5",
    "support_interface_pattern": "rectilinear_interlaced",
    "support_threshold_angle": "35",
    # Raft
    "raft_first_layer_density": "50%",
    "raft_first_layer_expansion": "1.5",
    "initial_layer_line_width": "105%",
}

# --- PLA+PETG+PVA MM ---
# Most conservative profile. PLA and PETG don't naturally adhere.
# PVA is fragile. Fine layer height for inter-material bonding.
# Zero support z-distance for clean PVA dissolution.
PLA_PETG_PVA_MM = {
    "outer_wall_speed": "40",
    "inner_wall_speed": "50",
    "sparse_infill_speed": "55",
    "internal_solid_infill_speed": "55",
    "gap_infill_speed": "35",
    "top_surface_speed": "40",
    "support_speed": "80",
    "support_interface_speed": "22",
    "travel_speed": "175",
    # All acceleration capped at 2500
    "default_acceleration": "2500",
    "outer_wall_acceleration": "2500",
    "inner_wall_acceleration": "2500",
    "top_surface_acceleration": "2500",
    "travel_acceleration": "2500",
    # Finer layer height for inter-material adhesion
    "layer_height": "0.18",
    # Cubic infill - less wall deformation than gyroid, pattern doesn't align with walls
    "sparse_infill_pattern": "cubic",
    "sparse_infill_density": "15%",
    # Wall thickness target: 1mm minimum (calculated dynamically)
    "min_wall_thickness": "1.0",
    # MM-specific - PVA support settings
    "flush_into_infill": "1",
    "timelapse_type": "1",
    "support_filament": "1",
    "support_interface_filament": "4",
    "support_interface_pattern": "concentric",
    "support_interface_spacing": "0",
    "support_interface_top_layers": "3",
    "support_bottom_z_distance": "0",
    "support_top_z_distance": "0",
    "support_base_pattern_spacing": "3.5",
    "support_object_xy_distance": "1",
    "support_threshold_angle": "35",
    # Shells
    # Raft
    "raft_first_layer_density": "25%",
    "raft_first_layer_expansion": "1.5",
    "initial_layer_line_width": "105%",
}

# --- TPU ---
# Very slow, gentle settings for flexible filament.
# TPU jams easily with fast moves or aggressive retraction.
# Cannot use AMS - must be fed manually.
# Community consensus: 25-35mm/s walls, minimal retraction, low accel.
# Ref: https://wiki.bambulab.com/en/knowledge-sharing/tpu-printing-guide
# Ref: https://forum.bambulab.com/t/what-is-your-tpu-setting-on-bambu-lab-studio/3890
TPU = {
    "outer_wall_speed": "30",
    "inner_wall_speed": "35",
    "sparse_infill_speed": "40",
    "internal_solid_infill_speed": "35",
    "gap_infill_speed": "30",
    "top_surface_speed": "30",
    "support_speed": "30",
    "support_interface_speed": "25",
    "travel_speed": "120",
    # Very gentle acceleration - TPU is flexible and bounces with fast moves
    "default_acceleration": "1500",
    "outer_wall_acceleration": "1000",
    "inner_wall_acceleration": "1500",
    "top_surface_acceleration": "1000",
    "internal_solid_infill_acceleration": "1500",
    "sparse_infill_acceleration": "1500",
    "travel_acceleration": "2000",
    # Slow first layer for adhesion
    "initial_layer_speed": "15",
    "initial_layer_infill_speed": "20",
    # Layer
    "layer_height": "0.20",
    # Shells - standard thickness
    "top_shell_thickness": "1.0",
    "bottom_shell_thickness": "0.8",
    # Walls
    "wall_loops": "2",
    "ensure_vertical_shell_thickness": "ensure_moderate",
    # TPU is flexible so gyroid/crosshatch doesn't matter for vibration,
    # but grid gives the most predictable flex behavior
    "sparse_infill_pattern": "grid",
    "sparse_infill_density": "15%",
}

# Registry of all material modes
# Core modes are always generated. Optional modes check OPTIONAL_FILAMENTS.
CORE_MATERIAL_MODES = {
    "PLA": PLA_STANDARD,
    "PLA Fast": PLA_FAST,
    "PETG ABS": PETG_ABS,
    "PLA Draft": PLA_DRAFT,
    "PLA Delicate": PLA_DELICATE,
    "PLA MM": PLA_MM,
    "PLA+PETG+PVA MM": PLA_PETG_PVA_MM,
}

# Optional modes: (mode_dict, optional_filament_key_or_None)
# If key is None, always included. If key is set, only included when that
# optional filament is enabled.
OPTIONAL_MATERIAL_MODES = {
    "PLA Silk": (PLA_SILK, "PLA Silk"),
    "TPU": (TPU, "TPU"),
}

# Build active material modes from core + enabled optionals
MATERIAL_MODES = dict(CORE_MATERIAL_MODES)
for mode_name, (mode_dict, opt_key) in OPTIONAL_MATERIAL_MODES.items():
    if opt_key is None or OPTIONAL_FILAMENTS.get(opt_key, False):
        MATERIAL_MODES[mode_name] = mode_dict

# =============================================================================
# FILAMENT PROFILES
# =============================================================================

# Base filament definitions. These are standalone (no BBL inheritance).
# Each is generated per-printer (X1C, A1M) with:
#   - compatible_printers set to all nozzle variants for that printer
#   - A1M variants get +0.05mm z_hop

# Common settings shared across all filament types
_FILAMENT_COMMON = {
    "adaptive_pressure_advance": ["0"],
    "adaptive_pressure_advance_bridges": ["0"],
    "adaptive_pressure_advance_model": ["0,0,0\n0,0,0"],
    "adaptive_pressure_advance_overhangs": ["0"],
    "activate_chamber_temp_control": ["0"],
    "chamber_temperature": ["0"],
    "dont_slow_down_outer_wall": ["0"],
    "filament_cooling_final_speed": ["3.4"],
    "filament_cooling_initial_speed": ["2.2"],
    "filament_cooling_moves": ["4"],
    "filament_density": ["1.24"],
    "filament_diameter": ["1.75"],
    "filament_is_support": ["0"],
    "filament_loading_speed": ["28"],
    "filament_loading_speed_start": ["3"],
    "filament_minimal_purge_on_wipe_tower": ["15"],
    "filament_multitool_ramming": ["0"],
    "filament_multitool_ramming_flow": ["10"],
    "filament_multitool_ramming_volume": ["10"],
    "filament_ramming_parameters": ["120 100 6.6 6.8 7.2 7.6 7.9 8.2 8.7 9.4 9.9 10.0| 0.05 6.6 0.45 6.8 0.95 7.8 1.45 8.3 1.95 9.7 2.45 10 2.95 7.6 3.45 7.6 3.95 7.6 4.45 7.6 4.95 7.6"],
    "filament_shrink": ["100%"],
    "filament_shrinkage_compensation_z": ["100%"],
    "filament_soluble": ["0"],
    "filament_stamping_distance": ["0"],
    "filament_stamping_loading_speed": ["0"],
    "filament_toolchange_delay": ["0"],
    "filament_unloading_speed": ["90"],
    "filament_unloading_speed_start": ["100"],
    "filament_vendor": ["B"],
    "idle_temperature": ["0"],
    "internal_bridge_fan_speed": ["-1"],
    "ironing_fan_speed": ["-1"],
    "pellet_flow_coefficient": ["0.4157"],
    "required_nozzle_HRC": ["3"],
}

FILAMENT_B_PLA = {
    **_FILAMENT_COMMON,
    "filament_type": ["PLA"],
    "filament_cost": ["20"],
    "filament_flow_ratio": ["0.985"],
    "filament_max_volumetric_speed": ["10"],
    # Retraction
    "filament_retraction_length": ["0.75"],
    "filament_retraction_speed": ["30"],
    "filament_deretraction_speed": ["30"],
    "filament_retract_before_wipe": ["75%"],
    "filament_retract_lift_above": ["0.2"],
    "filament_wipe": ["1"],
    "filament_wipe_distance": ["0.5"],
    "filament_z_hop": ["0.15"],
    "filament_z_hop_types": ["Spiral Lift"],
    # Temps
    "nozzle_temperature": ["210"],
    "nozzle_temperature_initial_layer": ["210"],
    "nozzle_temperature_range_high": ["250"],
    "nozzle_temperature_range_low": ["190"],
    "cool_plate_temp": ["40"],
    "cool_plate_temp_initial_layer": ["45"],
    "eng_plate_temp": ["58"],
    "eng_plate_temp_initial_layer": ["58"],
    "hot_plate_temp": ["58"],
    "hot_plate_temp_initial_layer": ["58"],
    "supertack_plate_temp": ["55"],  # A1M override to 60 below
    "supertack_plate_temp_initial_layer": ["55"],
    "textured_cool_plate_temp": ["55"],
    "textured_cool_plate_temp_initial_layer": ["55"],
    "textured_plate_temp": ["58"],
    "textured_plate_temp_initial_layer": ["58"],
    "temperature_vitrification": ["55"],
    # Fan
    "activate_air_filtration": ["1"],
    "additional_cooling_fan_speed": ["0"],
    "complete_print_exhaust_fan_speed": ["30"],
    "during_print_exhaust_fan_speed": ["70"],
    "enable_overhang_bridge_fan": ["1"],
    "fan_cooling_layer_time": ["100"],
    "fan_max_speed": ["100"],
    "fan_min_speed": ["75"],
    "full_fan_speed_layer": ["3"],
    "close_fan_the_first_x_layers": ["1"],
    "overhang_fan_speed": ["100"],
    "overhang_fan_threshold": ["50%"],
    "reduce_fan_stop_start_freq": ["1"],
    "support_material_interface_fan_speed": ["100"],
    # Cooling
    "slow_down_for_layer_cooling": ["1"],
    "slow_down_layer_time": ["8"],
    "slow_down_min_speed": ["20"],
    # Pressure advance
    "enable_pressure_advance": ["0"],
    "pressure_advance": ["0.02"],
    # Gcode
    "filament_start_gcode": [""],
    "filament_end_gcode": [""],
}

FILAMENT_B_PETG = {
    **_FILAMENT_COMMON,
    "filament_type": ["PETG"],
    "filament_density": ["1.27"],
    "filament_cost": ["16"],
    "filament_flow_ratio": ["0.95"],
    "filament_max_volumetric_speed": ["3.5"],
    "filament_notes": ["2.8 flow rate = 35mm/s, we are shooting slightly over that at 3"],
    # Retraction
    "filament_retraction_length": ["0.8"],
    "filament_retraction_speed": ["40"],
    "filament_deretraction_speed": ["35"],
    "filament_retract_before_wipe": ["75%"],
    "filament_wipe": ["1"],
    "filament_wipe_distance": ["0.3"],
    "filament_z_hop": ["0.15"],
    "filament_z_hop_types": ["Spiral Lift"],
    # Temps
    "nozzle_temperature": ["232"],
    "nozzle_temperature_initial_layer": ["237"],
    "nozzle_temperature_range_high": ["260"],
    "nozzle_temperature_range_low": ["225"],
    "cool_plate_temp": ["75"],
    "cool_plate_temp_initial_layer": ["77"],
    "eng_plate_temp": ["77"],
    "eng_plate_temp_initial_layer": ["77"],
    "hot_plate_temp": ["77"],
    "hot_plate_temp_initial_layer": ["77"],
    "supertack_plate_temp": ["77"],
    "supertack_plate_temp_initial_layer": ["77"],
    "textured_cool_plate_temp": ["77"],
    "textured_cool_plate_temp_initial_layer": ["77"],
    "textured_plate_temp": ["77"],
    "textured_plate_temp_initial_layer": ["77"],
    "temperature_vitrification": ["85"],
    # Fan
    "activate_air_filtration": ["0"],
    "additional_cooling_fan_speed": ["20"],
    "complete_print_exhaust_fan_speed": ["20"],
    "during_print_exhaust_fan_speed": ["20"],
    "enable_overhang_bridge_fan": ["1"],
    "fan_cooling_layer_time": ["35"],
    "fan_max_speed": ["45"],
    "fan_min_speed": ["5"],
    "full_fan_speed_layer": ["2"],
    "close_fan_the_first_x_layers": ["1"],
    "overhang_fan_speed": ["90"],
    "overhang_fan_threshold": ["10%"],
    "reduce_fan_stop_start_freq": ["0"],
    "support_material_interface_fan_speed": ["100"],
    # Cooling
    "slow_down_for_layer_cooling": ["0"],
    "slow_down_layer_time": ["12"],
    "slow_down_min_speed": ["9"],
    # Pressure advance
    "enable_pressure_advance": ["0"],
    "pressure_advance": ["0.01"],
    # Gcode
    "filament_start_gcode": ["; adjust z up slightly\nM106 P3 S60\n\nM221 S100 ;Reset Flowrate"],
    "filament_end_gcode": ["\nM106 P3 S0\n"],
}

FILAMENT_B_ABS = {
    **_FILAMENT_COMMON,
    "filament_type": ["ABS"],
    "filament_density": ["1.04"],
    "filament_cost": ["24.99"],
    "filament_flow_ratio": ["0.95"],
    "filament_max_volumetric_speed": ["16"],
    # Retraction - use defaults (nil inherits from system)
    "filament_z_hop": ["0.15"],
    "filament_z_hop_types": ["Spiral Lift"],
    # Temps
    "nozzle_temperature": ["275"],
    "nozzle_temperature_initial_layer": ["255"],
    "nozzle_temperature_range_high": ["280"],
    "nozzle_temperature_range_low": ["240"],
    "cool_plate_temp": ["0"],
    "cool_plate_temp_initial_layer": ["0"],
    "eng_plate_temp": ["100"],
    "eng_plate_temp_initial_layer": ["100"],
    "hot_plate_temp": ["90"],
    "hot_plate_temp_initial_layer": ["91"],
    "supertack_plate_temp": ["90"],
    "supertack_plate_temp_initial_layer": ["90"],
    "textured_cool_plate_temp": ["40"],
    "textured_cool_plate_temp_initial_layer": ["40"],
    "textured_plate_temp": ["90"],
    "textured_plate_temp_initial_layer": ["90"],
    "temperature_vitrification": ["100"],
    # Fan
    "activate_air_filtration": ["0"],
    "additional_cooling_fan_speed": ["0"],
    "complete_print_exhaust_fan_speed": ["70"],
    "during_print_exhaust_fan_speed": ["70"],
    "enable_overhang_bridge_fan": ["1"],
    "fan_cooling_layer_time": ["30"],
    "fan_max_speed": ["60"],
    "fan_min_speed": ["10"],
    "full_fan_speed_layer": ["0"],
    "close_fan_the_first_x_layers": ["3"],
    "overhang_fan_speed": ["80"],
    "overhang_fan_threshold": ["25%"],
    "reduce_fan_stop_start_freq": ["1"],
    "support_material_interface_fan_speed": ["-1"],
    # Cooling
    "slow_down_for_layer_cooling": ["1"],
    "slow_down_layer_time": ["12"],
    "slow_down_min_speed": ["20"],
    # Pressure advance
    "enable_pressure_advance": ["0"],
    "pressure_advance": ["0.02"],
    # Gcode
    "filament_start_gcode": ["; Filament gcode\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}"],
    "filament_end_gcode": ["; filament end gcode \n; cham fan full\nM106 P3 S255\n\n"],
}

FILAMENT_B_PVA = {
    **_FILAMENT_COMMON,
    "filament_type": ["PVA"],
    "filament_cost": ["50"],
    "filament_flow_ratio": ["0.95"],
    "filament_max_volumetric_speed": ["2"],
    "filament_is_support": ["1"],
    "filament_soluble": ["1"],
    # Retraction
    "filament_retraction_length": ["1"],
    "filament_retraction_speed": ["30"],
    "filament_retraction_minimum_travel": ["0.6"],
    "filament_deretraction_speed": ["20"],
    "filament_retract_before_wipe": ["50%"],
    "filament_retract_lift_above": ["0.25"],
    "filament_wipe": ["1"],
    "filament_wipe_distance": ["0.5"],
    "filament_z_hop": ["0.1"],
    "filament_z_hop_types": ["Spiral Lift"],
    # Temps - PVA degrades and strings at high temps, keep first layer moderate
    "nozzle_temperature": ["220"],
    "nozzle_temperature_initial_layer": ["215"],
    "nozzle_temperature_range_high": ["250"],
    "nozzle_temperature_range_low": ["190"],
    # Plate temps: cool plate is low-temp coating (35°C), everything else uses
    # PEI/SuperTack surfaces that work at 48-57°C. Printer overrides adjust
    # the non-cool plates based on enclosure (48 enclosed, 57 open-air).
    # Cool plate stays at 35°C on all printers - higher temps soften PLA on this coating.
    "cool_plate_temp": ["35"],
    "cool_plate_temp_initial_layer": ["35"],
    "eng_plate_temp": ["55"],
    "eng_plate_temp_initial_layer": ["55"],
    "hot_plate_temp": ["55"],
    "hot_plate_temp_initial_layer": ["55"],
    "supertack_plate_temp": ["55"],
    "supertack_plate_temp_initial_layer": ["55"],
    "textured_cool_plate_temp": ["50"],
    "textured_cool_plate_temp_initial_layer": ["50"],
    "textured_plate_temp": ["55"],
    "textured_plate_temp_initial_layer": ["55"],
    "temperature_vitrification": ["55"],
    # Fan
    "activate_air_filtration": ["1"],
    "additional_cooling_fan_speed": ["50"],
    "complete_print_exhaust_fan_speed": ["30"],
    "during_print_exhaust_fan_speed": ["70"],
    "enable_overhang_bridge_fan": ["1"],
    "fan_cooling_layer_time": ["100"],
    "fan_max_speed": ["100"],
    "fan_min_speed": ["100"],
    "full_fan_speed_layer": ["0"],
    "close_fan_the_first_x_layers": ["1"],
    "overhang_fan_speed": ["100"],
    "overhang_fan_threshold": ["50%"],
    "reduce_fan_stop_start_freq": ["1"],
    "support_material_interface_fan_speed": ["50"],
    # Cooling
    "slow_down_for_layer_cooling": ["1"],
    "slow_down_layer_time": ["7"],
    "slow_down_min_speed": ["20"],
    # Pressure advance
    "enable_pressure_advance": ["1"],
    "pressure_advance": ["0.01"],
    # Gcode
    "filament_start_gcode": [""],
    "filament_end_gcode": ["\n\n"],
}

FILAMENT_B_BVOH = {
    **_FILAMENT_COMMON,
    "filament_type": ["PVA"],  # OrcaSlicer treats BVOH as PVA type
    "filament_cost": ["120"],
    "filament_flow_ratio": ["0.95"],
    "filament_max_volumetric_speed": ["2.5"],  # slightly more tolerant than PVA
    "filament_is_support": ["1"],
    "filament_soluble": ["1"],
    # Retraction - moderate, BVOH clogs less than PVA but still be careful
    "filament_retraction_length": ["0.8"],
    "filament_retraction_speed": ["30"],
    "filament_retraction_minimum_travel": ["0.6"],
    "filament_deretraction_speed": ["20"],
    "filament_retract_before_wipe": ["50%"],
    "filament_retract_lift_above": ["0.25"],
    "filament_wipe": ["1"],
    "filament_wipe_distance": ["0.5"],
    "filament_z_hop": ["0.1"],
    "filament_z_hop_types": ["Spiral Lift"],
    # Temps - BVOH prints 200-230°C, conservative at 210
    "nozzle_temperature": ["210"],
    "nozzle_temperature_initial_layer": ["210"],
    "nozzle_temperature_range_high": ["230"],
    "nozzle_temperature_range_low": ["200"],
    # Plate temps - same structure as PLA (PLA-like material)
    "cool_plate_temp": ["35"],
    "cool_plate_temp_initial_layer": ["35"],
    "eng_plate_temp": ["55"],
    "eng_plate_temp_initial_layer": ["55"],
    "hot_plate_temp": ["55"],
    "hot_plate_temp_initial_layer": ["55"],
    "supertack_plate_temp": ["55"],
    "supertack_plate_temp_initial_layer": ["55"],
    "textured_cool_plate_temp": ["50"],
    "textured_cool_plate_temp_initial_layer": ["50"],
    "textured_plate_temp": ["55"],
    "textured_plate_temp_initial_layer": ["55"],
    "temperature_vitrification": ["55"],
    # Fan - aggressive cooling like PVA
    "activate_air_filtration": ["1"],
    "additional_cooling_fan_speed": ["50"],
    "complete_print_exhaust_fan_speed": ["30"],
    "during_print_exhaust_fan_speed": ["70"],
    "enable_overhang_bridge_fan": ["1"],
    "fan_cooling_layer_time": ["100"],
    "fan_max_speed": ["100"],
    "fan_min_speed": ["100"],
    "full_fan_speed_layer": ["0"],
    "close_fan_the_first_x_layers": ["1"],
    "overhang_fan_speed": ["100"],
    "overhang_fan_threshold": ["50%"],
    "reduce_fan_stop_start_freq": ["1"],
    "support_material_interface_fan_speed": ["50"],
    # Cooling
    "slow_down_for_layer_cooling": ["1"],
    "slow_down_layer_time": ["7"],
    "slow_down_min_speed": ["20"],
    # Pressure advance
    "enable_pressure_advance": ["1"],
    "pressure_advance": ["0.01"],
    # Gcode
    "filament_start_gcode": [""],
    "filament_end_gcode": ["\n\n"],
}

# Child filament: overrides on top of B PLA
FILAMENT_B_PLA_SILK_OVERRIDES = {
    "filament_cost": ["22"],
    "filament_max_volumetric_speed": ["2.6"],
    "filament_retraction_length": ["0.4"],
    "nozzle_temperature": ["232"],
    "nozzle_temperature_initial_layer": ["225"],
}

FILAMENT_B_PLA_WOOD_OVERRIDES = {
    "filament_cost": ["30"],
    "filament_max_volumetric_speed": ["2"],  # wood particles restrict flow, higher = clog risk
    "filament_retraction_length": ["0.5"],
    "filament_z_hop": ["0.15"],
    "filament_z_hop_types": ["Auto Lift"],
    "nozzle_temperature_initial_layer": ["210"],  # high temp chars wood particles and clogs
}

# Child filament: overrides on top of B PLA for carbon fiber PLA
# Ref: https://bambulab.com/en-us/filament/pla-cf
# NOTE: Requires hardened steel nozzle (CF is abrasive)
FILAMENT_B_PLA_CF_OVERRIDES = {
    "filament_cost": ["28"],
    "filament_max_volumetric_speed": ["8"],  # CF particles restrict flow vs PLA's 10
    "filament_retraction_length": ["0.8"],   # slightly more than PLA's 0.75
    "filament_flow_ratio": ["0.95"],         # CF is slightly less consistent
    "nozzle_temperature": ["230"],           # higher than PLA (220-240 range, conservative)
    "nozzle_temperature_initial_layer": ["225"],
    "required_nozzle_HRC": ["40"],           # hardened steel required
}

# ASA: UV-resistant ABS alternative. Enclosure required.
# Ref: https://forum.bambulab.com/t/asa-settings/76407
# Ref: https://wiki.bambulab.com/en/filament/abs_asa_pc
FILAMENT_B_ASA = {
    **_FILAMENT_COMMON,
    "filament_type": ["ASA"],
    "filament_density": ["1.07"],
    "filament_cost": ["25"],
    "filament_flow_ratio": ["0.95"],
    "filament_max_volumetric_speed": ["12"],  # slightly less than ABS's 16
    # Retraction
    "filament_z_hop": ["0.15"],
    "filament_z_hop_types": ["Spiral Lift"],
    # Temps - similar to ABS
    "nozzle_temperature": ["250"],
    "nozzle_temperature_initial_layer": ["250"],
    "nozzle_temperature_range_high": ["270"],
    "nozzle_temperature_range_low": ["240"],
    "cool_plate_temp": ["0"],
    "cool_plate_temp_initial_layer": ["0"],
    "eng_plate_temp": ["100"],
    "eng_plate_temp_initial_layer": ["100"],
    "hot_plate_temp": ["100"],
    "hot_plate_temp_initial_layer": ["100"],
    "supertack_plate_temp": ["90"],
    "supertack_plate_temp_initial_layer": ["90"],
    "textured_cool_plate_temp": ["0"],
    "textured_cool_plate_temp_initial_layer": ["0"],
    "textured_plate_temp": ["100"],
    "textured_plate_temp_initial_layer": ["100"],
    "temperature_vitrification": ["100"],
    # Fan - low, same philosophy as ABS
    "activate_air_filtration": ["0"],
    "additional_cooling_fan_speed": ["0"],
    "complete_print_exhaust_fan_speed": ["70"],
    "during_print_exhaust_fan_speed": ["70"],
    "enable_overhang_bridge_fan": ["1"],
    "fan_cooling_layer_time": ["30"],
    "fan_max_speed": ["50"],
    "fan_min_speed": ["10"],
    "full_fan_speed_layer": ["0"],
    "close_fan_the_first_x_layers": ["3"],
    "overhang_fan_speed": ["60"],
    "overhang_fan_threshold": ["25%"],
    "reduce_fan_stop_start_freq": ["1"],
    "support_material_interface_fan_speed": ["-1"],
    # Cooling
    "slow_down_for_layer_cooling": ["1"],
    "slow_down_layer_time": ["12"],
    "slow_down_min_speed": ["20"],
    # Pressure advance
    "enable_pressure_advance": ["0"],
    "pressure_advance": ["0.02"],
    # Gcode - same as ABS
    "filament_start_gcode": ["; Filament gcode\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}"],
    "filament_end_gcode": ["; filament end gcode \n; cham fan full\nM106 P3 S255\n\n"],
}

# TPU: Flexible filament. Cannot use AMS.
# Ref: https://wiki.bambulab.com/en/knowledge-sharing/tpu-printing-guide
# Ref: https://forum.bambulab.com/t/what-is-your-tpu-setting-on-bambu-lab-studio/3890
FILAMENT_B_TPU = {
    **_FILAMENT_COMMON,
    "filament_type": ["TPU"],
    "filament_density": ["1.21"],
    "filament_cost": ["30"],
    "filament_flow_ratio": ["1.0"],  # TPU needs full flow
    "filament_max_volumetric_speed": ["2.5"],  # very slow, flexible filament
    # Retraction - minimal, TPU jams with too much retraction
    "filament_retraction_length": ["0.5"],
    "filament_retraction_speed": ["20"],
    "filament_deretraction_speed": ["15"],
    "filament_retract_before_wipe": ["0%"],
    "filament_wipe": ["0"],
    "filament_wipe_distance": ["0"],
    "filament_z_hop": ["0.2"],
    "filament_z_hop_types": ["Spiral Lift"],
    # Temps
    "nozzle_temperature": ["225"],
    "nozzle_temperature_initial_layer": ["220"],
    "nozzle_temperature_range_high": ["240"],
    "nozzle_temperature_range_low": ["210"],
    "cool_plate_temp": ["50"],
    "cool_plate_temp_initial_layer": ["50"],
    "eng_plate_temp": ["50"],
    "eng_plate_temp_initial_layer": ["50"],
    "hot_plate_temp": ["50"],
    "hot_plate_temp_initial_layer": ["50"],
    "supertack_plate_temp": ["50"],
    "supertack_plate_temp_initial_layer": ["50"],
    "textured_cool_plate_temp": ["50"],
    "textured_cool_plate_temp_initial_layer": ["50"],
    "textured_plate_temp": ["50"],
    "textured_plate_temp_initial_layer": ["50"],
    "temperature_vitrification": ["60"],
    # Fan - moderate
    "activate_air_filtration": ["0"],
    "additional_cooling_fan_speed": ["0"],
    "complete_print_exhaust_fan_speed": ["0"],
    "during_print_exhaust_fan_speed": ["0"],
    "enable_overhang_bridge_fan": ["1"],
    "fan_cooling_layer_time": ["100"],
    "fan_max_speed": ["50"],
    "fan_min_speed": ["30"],
    "full_fan_speed_layer": ["3"],
    "close_fan_the_first_x_layers": ["1"],
    "overhang_fan_speed": ["80"],
    "overhang_fan_threshold": ["25%"],
    "reduce_fan_stop_start_freq": ["0"],
    "support_material_interface_fan_speed": ["-1"],
    # Cooling
    "slow_down_for_layer_cooling": ["1"],
    "slow_down_layer_time": ["16"],
    "slow_down_min_speed": ["10"],
    # Pressure advance
    "enable_pressure_advance": ["0"],
    "pressure_advance": ["0.02"],
    # Gcode
    "filament_start_gcode": [""],
    "filament_end_gcode": [""],
}

# =============================================================================
# FILAMENT REGISTRY
# =============================================================================
# Format: name -> (data, parent_name_or_None, allowed_printers_or_None)
# - If parent_name is set, profile merges parent data + overrides
# - If allowed_printers is None, generate for all enabled printers
# - Enclosure-required filaments list only corexy printers
#
# Core filaments are always generated. Optional filaments check OPTIONAL_FILAMENTS.

_CORE_FILAMENTS = {
    "B PLA":      (FILAMENT_B_PLA, None, None),
    "B PETG":     (FILAMENT_B_PETG, None, None),
    "B ABS":      (FILAMENT_B_ABS, None, [k for k, v in PRINTER_ENCLOSED.items() if v]),
}

_OPTIONAL_FILAMENTS = {
    # (data, parent, allowed_printers, optional_key)
    "B PLA Silk": (FILAMENT_B_PLA_SILK_OVERRIDES, "B PLA", None, "PLA Silk"),
    "B PLA Wood": (FILAMENT_B_PLA_WOOD_OVERRIDES, "B PLA", None, "PLA Wood"),
    "B PLA-CF":   (FILAMENT_B_PLA_CF_OVERRIDES, "B PLA", None, "PLA-CF"),
    "B ASA":      (FILAMENT_B_ASA, None, [k for k, v in PRINTER_ENCLOSED.items() if v], "ASA"),
    "B TPU":      (FILAMENT_B_TPU, None, None, "TPU"),
    "B PVA":      (FILAMENT_B_PVA, None, None, "PVA"),
    "B BVOH":     (FILAMENT_B_BVOH, None, None, "BVOH"),
}

# Build active registry from core + enabled optionals
FILAMENT_REGISTRY = dict(_CORE_FILAMENTS)
for name, (data, parent, printers, opt_key) in _OPTIONAL_FILAMENTS.items():
    if OPTIONAL_FILAMENTS.get(opt_key, False):
        FILAMENT_REGISTRY[name] = (data, parent, printers)

# A1M z_hop increase (mm) over X1C baseline
A1M_ZHOP_INCREASE = 0.05


# =============================================================================
# LAYER 4: NOZZLE SCALING
# =============================================================================

# Default layer heights per nozzle (50% of nozzle diameter)
NOZZLE_DEFAULT_LAYER_HEIGHT = {
    0.2: 0.10,
    0.4: 0.20,
    0.6: 0.30,
    0.8: 0.40,
}

# Draft layer heights (~60% of nozzle diameter)
NOZZLE_DRAFT_LAYER_HEIGHT = {
    0.2: 0.14,
    0.4: 0.24,
    0.6: 0.36,
    0.8: 0.48,
}

# PLA+PETG+PVA layer heights (finer for adhesion, ~45% of nozzle)
NOZZLE_PVA_MM_LAYER_HEIGHT = {
    0.2: 0.10,
    0.4: 0.18,
    0.6: 0.24,
    0.8: 0.32,
}

# Speed multiplier per nozzle size
# Larger nozzles push more material at same mm/s; slight reduction keeps
# us within volumetric flow limits and gives cleaner extrusion.
NOZZLE_SPEED_MULTIPLIER = {
    0.2: 1.0,
    0.4: 1.0,
    0.6: 0.9,
    0.8: 0.85,
}

# Acceleration multiplier per nozzle size
# Larger beads have more momentum, cause more ringing at direction changes.
NOZZLE_ACCEL_MULTIPLIER = {
    0.2: 1.0,
    0.4: 1.0,
    0.6: 0.95,
    0.8: 0.9,
}

# Minimum wall thickness target (mm) - what 0.4mm nozzle at 2 walls produces
# with 105% line width: 0.4 * 1.05 * 2 = 0.84mm
MIN_WALL_THICKNESS_MM = 0.84

# Wall loop additions per nozzle to maintain minimum wall thickness
# 0.2mm * 1.05 = 0.21mm per wall -> need 4 walls for 0.84mm -> +2 from base 2
# 0.6mm * 1.05 = 0.63mm per wall -> 2 walls = 1.26mm (already exceeds min)
# 0.8mm * 1.05 = 0.84mm per wall -> 2 walls = 1.68mm (already exceeds min)
NOZZLE_WALL_LOOP_ADDITION = {
    0.2: 2,
    0.4: 0,
    0.6: 0,
    0.8: 0,
}

# Support z-distance scales with layer height
# (calculated dynamically based on final layer height)

# Settings that are speeds (mm/s) and should be scaled by nozzle multiplier
SPEED_KEYS = {
    "outer_wall_speed", "inner_wall_speed", "sparse_infill_speed",
    "internal_solid_infill_speed", "gap_infill_speed", "top_surface_speed",
    "support_speed", "support_interface_speed", "travel_speed",
    "initial_layer_speed", "initial_layer_infill_speed", "ironing_speed",
    "bridge_speed", "overhang_1_4_speed", "overhang_2_4_speed",
    "overhang_4_4_speed",
}

# Settings that are accelerations and should be scaled by nozzle accel multiplier
ACCEL_KEYS = {
    "default_acceleration", "outer_wall_acceleration", "inner_wall_acceleration",
    "top_surface_acceleration", "internal_solid_infill_acceleration",
    "sparse_infill_acceleration", "travel_acceleration",
    "initial_layer_acceleration",
}

# Settings that are percentage strings (should not be numerically scaled)
PERCENTAGE_KEYS = {
    "initial_layer_line_width", "initial_layer_travel_speed",
    "line_width", "outer_wall_line_width", "inner_wall_line_width",
    "sparse_infill_line_width", "internal_solid_infill_line_width",
    "top_surface_line_width", "support_line_width",
    "ironing_flow", "raft_first_layer_density",
    "sparse_infill_density", "ensure_vertical_shell_thickness",
}


# =============================================================================
# PROFILE NAME GENERATION
# =============================================================================

NOZZLE_SHORT = {
    0.2: " 0.2n",
    0.4: "",         # 0.4 is default, no suffix
    0.6: " 0.6n",
    0.8: " 0.8n",
}


def make_profile_name(mode_name: str, printer: str, nozzle: float) -> str:
    """Generate a profile name like 'B PLA' or 'B PETG ABS A1M 0.6n'."""
    return f"B {mode_name}{PRINTER_SUFFIX[printer]}{NOZZLE_SHORT[nozzle]}"


# =============================================================================
# PROFILE GENERATION LOGIC
# =============================================================================

def scale_numeric_value(value_str: str, multiplier: float) -> str:
    """Scale a numeric string value by a multiplier, returning rounded int string."""
    try:
        val = float(value_str)
        scaled = val * multiplier
        # Round to nearest int for speeds/accels
        return str(int(round(scaled)))
    except (ValueError, TypeError):
        return value_str


def _ceil_div(numerator: float, denominator: float) -> int:
    """Ceiling division for calculating layer counts from thickness targets."""
    return math.ceil(numerator / denominator)


def _calc_shell_layers(target_thickness: float, layer_height: float, min_layers: int = 2) -> int:
    """Calculate shell layer count from thickness target, enforcing minimum."""
    return max(min_layers, _ceil_div(target_thickness, layer_height))


def _raise_infill_to_max_speed(profile: dict):
    """On A1M, raise sparse infill speed to match the fastest non-infill speed.
    Crosshatch is gentle enough that there's no reason to artificially slow it."""
    speed_keys = ["outer_wall_speed", "inner_wall_speed", "internal_solid_infill_speed",
                  "top_surface_speed", "gap_infill_speed"]
    speeds = []
    for k in speed_keys:
        if k in profile:
            try:
                speeds.append(int(float(profile[k])))
            except ValueError:
                pass
    if speeds:
        max_speed = max(speeds)
        current = int(float(profile.get("sparse_infill_speed", "0")))
        if current < max_speed:
            profile["sparse_infill_speed"] = str(max_speed)


def _apply_speed_multiplier(profile: dict, multiplier: float):
    """Scale all speed values by a multiplier."""
    for key in list(profile.keys()):
        if key in SPEED_KEYS:
            profile[key] = scale_numeric_value(profile[key], multiplier)


def _apply_caps(profile: dict, max_accel: int, max_speed: int, travel_cap: int,
                first_layer_caps: dict = None):
    """Apply hard caps to speeds and accelerations.

    Args:
        max_accel: Maximum acceleration for any accel setting
        max_speed: Maximum speed for any non-travel speed setting
        travel_cap: Maximum travel speed (may differ from max_speed)
        first_layer_caps: Optional dict of {key: cap} for first layer overrides
    """
    if first_layer_caps:
        for key, cap in first_layer_caps.items():
            if key in profile:
                try:
                    val = int(float(profile[key]))
                    if val > cap:
                        profile[key] = str(cap)
                except (ValueError, TypeError):
                    pass

    for key in list(profile.keys()):
        if key in ACCEL_KEYS:
            try:
                val = int(float(profile[key]))
                if val > max_accel:
                    profile[key] = str(max_accel)
            except (ValueError, TypeError):
                pass
        if key in SPEED_KEYS:
            cap = travel_cap if key == "travel_speed" else max_speed
            try:
                val = int(float(profile[key]))
                if val > cap:
                    profile[key] = str(cap)
            except (ValueError, TypeError):
                pass


# Mode+nozzle specific overrides applied after nozzle scaling.
# Format: (mode_name, nozzle_size) -> dict of overrides
MODE_NOZZLE_OVERRIDES = {
    # PETG on 0.8mm nozzle: 1 wall + alternate (wall already thick enough)
    ("PETG ABS", 0.8): {
        "wall_loops": "1",
        "alternate_extra_wall": "1",
    },
    # Draft on 0.2mm nozzle: needs real structure since lines are so thin
    ("PLA Draft", 0.2): {
        "wall_loops": "2",
        "alternate_extra_wall": "0",
        "top_shell_layers": "2",
        "bottom_shell_layers": "2",
    },
}

# Delicate mode speed multipliers per printer group (applied before i3 caps)
DELICATE_SPEED_MULT = {
    "corexy": 0.80,  # 20% slower
    "i3":     0.65,  # 35% slower
}

# i3 (A1/A1M) hard caps per mode. Default caps apply to all modes unless overridden.
I3_CAPS = {
    "_default": {
        "max_accel": 5000,
        "max_speed": 150,
        "travel_cap": 150,
        "first_layer_caps": {
            "initial_layer_speed": 16,
            "initial_layer_infill_speed": 20,
        },
    },
    "PLA Delicate": {
        "max_accel": 1500,
        "max_speed": 150,
        "travel_cap": 60,
    },
}

# Layer height lookup per mode (which table to use)
MODE_LAYER_HEIGHT_TABLE = {
    "PLA Draft": NOZZLE_DRAFT_LAYER_HEIGHT,
    "PLA+PETG+PVA MM": NOZZLE_PVA_MM_LAYER_HEIGHT,
}


def build_profile(printer: str, nozzle: float, mode_name: str) -> dict:
    """
    Build a complete process profile by applying layers in order:

    1. Universal overrides (Brian's baseline preferences)
    2. Printer deltas (X1C vs A1M hardware differences)
    3. Material mode (speed/accel/structural philosophy)
    4. Nozzle scaling (layer height, wall count, speed/accel multipliers)
    5. Shell calculation (layers from thickness targets, min 2)
    6. Mode+nozzle overrides (specific combos needing special treatment)
    7. Speed reductions (Delicate mode per-printer slowdowns)
    8. Printer hard caps (A1M speed/accel limits, applied last)

    Order matters: reductions (step 7) must come before caps (step 8)
    so that Delicate speeds are reduced first, then capped.
    """
    profile = {}

    group = PRINTER_GROUP[printer]

    # --- Step 1-3: Build base profile from layers ---
    profile.update(deepcopy(UNIVERSAL_OVERRIDES))
    profile.update(deepcopy(PRINTER_DELTAS[group]))
    profile.update(deepcopy(MATERIAL_MODES[mode_name]))

    if group == "i3":
        _raise_infill_to_max_speed(profile)

    # --- Step 4: Nozzle scaling ---

    # Layer height
    lh_table = MODE_LAYER_HEIGHT_TABLE.get(mode_name, NOZZLE_DEFAULT_LAYER_HEIGHT)
    lh = lh_table[nozzle]
    profile["layer_height"] = f"{lh:.2f}"

    # Wall loops: either use min_wall_thickness target or add extra for small nozzles
    outer_w = nozzle * 1.05  # 105% line width
    inner_w = nozzle * 1.12  # 112% line width

    if "min_wall_thickness" in profile:
        # Dynamic: calculate walls needed to meet thickness target
        target = float(profile.pop("min_wall_thickness"))
        walls = 1
        while outer_w + (walls - 1) * inner_w < target:
            walls += 1
        walls = max(walls, 2)  # minimum 2 walls always
        profile["wall_loops"] = str(walls)
    else:
        # Static: use mode's wall_loops + nozzle addition for small nozzles
        base_walls = int(profile.get("wall_loops", "2"))
        profile["wall_loops"] = str(base_walls + NOZZLE_WALL_LOOP_ADDITION[nozzle])

    # Speed/accel scaling for larger nozzles
    speed_mult = NOZZLE_SPEED_MULTIPLIER[nozzle]
    accel_mult = NOZZLE_ACCEL_MULTIPLIER[nozzle]
    if speed_mult != 1.0:
        _apply_speed_multiplier(profile, speed_mult)
    if accel_mult != 1.0:
        for key in list(profile.keys()):
            if key in ACCEL_KEYS:
                profile[key] = scale_numeric_value(profile[key], accel_mult)

    # Support z-distance scales with layer height
    # (PLA+PETG+PVA MM forces 0 for PVA adhesion - set in mode constants)
    if mode_name != "PLA+PETG+PVA MM":
        profile["support_top_z_distance"] = f"{lh:.2f}"
        profile["support_bottom_z_distance"] = f"{lh:.2f}"

    # --- Step 5: Shell layer calculation ---
    # Rule: ceil(target / layer_height), min 2 layers (Draft exempt)
    min_shell = 1 if mode_name == "PLA Draft" else 2
    if "top_shell_thickness" in profile:
        profile["top_shell_layers"] = str(
            _calc_shell_layers(float(profile["top_shell_thickness"]), lh, min_shell))
    if "bottom_shell_thickness" in profile:
        profile["bottom_shell_layers"] = str(
            _calc_shell_layers(float(profile["bottom_shell_thickness"]), lh, min_shell))

    # --- Step 6: Mode+nozzle specific overrides ---
    overrides = MODE_NOZZLE_OVERRIDES.get((mode_name, nozzle))
    if overrides:
        profile.update(overrides)

    # --- Step 7: Per-printer-group speed reductions ---
    if mode_name == "PLA Delicate":
        mult = DELICATE_SPEED_MULT.get(group, 1.0)
        if mult != 1.0:
            _apply_speed_multiplier(profile, mult)

    # --- Step 8: i3 hard caps (must be last) ---
    if group == "i3":
        # PLA and PLA Fast on i3: enforce 1mm minimum wall thickness
        # (gantry arm benefits from thicker walls for rigidity)
        if mode_name in ("PLA", "PLA Fast"):
            min_thick = 1.0
            walls = int(profile.get("wall_loops", "2"))
            while outer_w + (walls - 1) * inner_w < min_thick:
                walls += 1
            profile["wall_loops"] = str(walls)

        caps = {**I3_CAPS["_default"]}
        mode_caps = I3_CAPS.get(mode_name)
        if mode_caps:
            caps.update(mode_caps)
        _apply_caps(
            profile,
            max_accel=caps["max_accel"],
            max_speed=caps["max_speed"],
            travel_cap=caps["travel_cap"],
            first_layer_caps=caps.get("first_layer_caps"),
        )

    return profile


def format_profile_json(name: str, inherits: str, overrides: dict) -> dict:
    """Format a process profile as OrcaSlicer user profile."""
    result = {
        "from": "User",
        "inherits": inherits,
        "is_custom_defined": "0",
        "name": name,
        "print_settings_id": name,
        "version": ORCA_PROFILE_VERSION,
    }
    # Add all overrides, excluding metadata keys
    skip_keys = {"from", "inherits", "is_custom_defined", "name",
                 "print_settings_id", "version"}
    for k, v in sorted(overrides.items()):
        if k not in skip_keys:
            result[k] = v
    return result


def format_info_file(base_id: str) -> str:
    """Generate the .info file content."""
    ts = int(time.time())
    return (
        f"sync_info = \n"
        f"user_id = \n"
        f"setting_id = \n"
        f"base_id = {base_id}\n"
        f"updated_time = {ts}\n"
    )


# =============================================================================
# MACHINE PROFILE GENERATION
# =============================================================================

# =============================================================================
# CUSTOM GCODE
# =============================================================================
#
# Both printers use bundled gcode JSON files as the single source of truth.
# Edit the JSON files directly, then regenerate.
#
# brian_x1c_gcode.json - X1C custom gcode (start, end, change_filament, layer_change)
#   Customizations vs stock BBL X1C:
#   - Parallel nozzle pre-heat (M104 S170) during bed heating for faster startup
#   - Z-offset for all plate types (-0.04 textured PEI, -0.02 all others)
#   - Shorter purge line (45mm two-pass vs stock 221mm) - less waste, faster
#   - More Z clearance after print (+2mm vs +0.5mm) to avoid dragging
#   - Reduced toolchange travel speeds (F15000/F21000 -> F9000) - less vibration
#   - Reduced toolchange shake speeds (F15000 -> F9000) - quieter
#   - Custom layer_change_gcode: timelapse support, logo lamp off, layer progress
#
# brian_a1m_gcode.json - A1M custom gcode (start, change_filament)
#   Customizations vs stock BBL A1M:
#   - Reduced startup fan speed (S255 -> S128 / 50%) for quieter operation
#   - Z-offset for all plate types (-0.04 textured PEI, -0.02 all others)
#   - Reduced toolchange travel speeds (F18000 -> F9000) - less vibration on gantry
#
# Both use OrcaSlicer variables so they work across all nozzle sizes.

BRIAN_X1C_GCODE_FILE = Path(__file__).parent / "brian_x1c_gcode.json"
BRIAN_A1M_GCODE_FILE = Path(__file__).parent / "brian_a1m_gcode.json"


def _load_gcode_file(path: Path) -> dict:
    """Load a bundled gcode JSON file."""
    if not path.exists():
        print(f"  ERROR: {path.name} not found")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        gcode = json.load(f)
    print(f"  Loaded gcode from: {path.name}")
    return gcode


# =============================================================================
# FILAMENT PROFILES
# =============================================================================

def generate_filament_profiles(dry_run: bool = False):
    """Generate filament profiles per printer from constants."""
    count = 0

    # Clear old filament files first
    if not dry_run:
        for subdir in [FILAMENT_DIR, FILAMENT_BASE_SUBDIR]:
            if subdir.exists():
                for f in list(subdir.glob("B *.json")) + list(subdir.glob("B *.info")):
                    f.unlink()
        FILAMENT_DIR.mkdir(parents=True, exist_ok=True)
        FILAMENT_BASE_SUBDIR.mkdir(parents=True, exist_ok=True)

    for filament_name, (fil_data, parent_name, allowed_printers) in FILAMENT_REGISTRY.items():
        # Build full filament data
        if parent_name:
            # Child: merge parent + overrides
            parent_data, _, _ = FILAMENT_REGISTRY[parent_name]
            full_data = deepcopy(parent_data)
            full_data.update(deepcopy(fil_data))
        else:
            full_data = deepcopy(fil_data)

        # Generate one per enabled printer
        for printer_key, printer_cfg in PRINTERS.items():
            if allowed_printers and printer_key not in allowed_printers:
                continue

            suffix = FILAMENT_PRINTER_SUFFIX[printer_key]
            group = PRINTER_GROUP[printer_key]
            profile_name = f"{filament_name}{suffix}"

            profile = deepcopy(full_data)
            profile["name"] = profile_name
            profile["filament_settings_id"] = [profile_name]
            profile["from"] = "User"
            profile["is_custom_defined"] = "0"
            profile["version"] = ORCA_PROFILE_VERSION

            # Set compatible_printers to all nozzle variants for this printer
            compat = [
                printer_cfg["machine_base_profiles"][nozzle][0]
                for nozzle in NOZZLE_SIZES
            ]
            profile["compatible_printers"] = compat

            # i3 printers: slightly more retraction for the gantry arm
            if group == "i3" and "filament_retraction_length" in profile:
                try:
                    base_ret = float(profile["filament_retraction_length"][0])
                    profile["filament_retraction_length"] = [f"{base_ret + 0.1:.2f}"]
                except (ValueError, IndexError):
                    pass

            # PEI/SuperTack plate keys (NOT cool plate - that's a different coating)
            PEI_PLATE_KEYS = [
                "eng_plate_temp", "eng_plate_temp_initial_layer",
                "hot_plate_temp", "hot_plate_temp_initial_layer",
                "supertack_plate_temp", "supertack_plate_temp_initial_layer",
                "textured_cool_plate_temp", "textured_cool_plate_temp_initial_layer",
                "textured_plate_temp", "textured_plate_temp_initial_layer",
            ]

            # Plate temps for PLA-based filaments depend on enclosure.
            # Only override PEI/SuperTack plates - cool plate stays at 35°C always
            # (it's a low-temp coating, PLA softens above 55°C on this surface).
            # Enclosed printers: 48°C (enclosure traps heat, less needed)
            # Open-air printers: 57°C (needs more heat to compensate for ambient loss)
            fil_type = profile.get("filament_type", [""])[0]
            if fil_type in ("PLA", "PVA"):
                is_enclosed = PRINTER_ENCLOSED.get(printer_key, False)
                plate_temp = "48" if is_enclosed else "57"
                for plate_key in PEI_PLATE_KEYS:
                    profile[plate_key] = [plate_temp]

            if dry_run:
                zhop = profile.get("filament_z_hop", ["?"])[0]
                print(f"  [DRY RUN] Would write filament: {profile_name} (z_hop={zhop})")
            else:
                # Base filaments go in base/, child filaments in top-level
                if parent_name:
                    out_dir = FILAMENT_DIR
                else:
                    out_dir = FILAMENT_BASE_SUBDIR

                json_path = out_dir / f"{profile_name}.json"
                info_path = out_dir / f"{profile_name}.info"

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(profile, f, indent=4, ensure_ascii=False)
                    f.write("\n")
                with open(info_path, "w", encoding="utf-8") as f:
                    f.write(format_info_file(""))

            count += 1

    return count


def generate_machine_profiles(dry_run: bool = False):
    """Generate machine profiles for all printer/nozzle combinations."""
    count = 0

    # Load all gcode files for enabled printers
    gcode_cache = {}
    for printer_key, printer_cfg in PRINTERS.items():
        gcode_filename = printer_cfg["gcode_file"]
        if gcode_filename not in gcode_cache:
            gcode_path = Path(__file__).parent / gcode_filename
            gcode_cache[gcode_filename] = _load_gcode_file(gcode_path)

    for printer_key, printer_cfg in PRINTERS.items():
        for nozzle in NOZZLE_SIZES:
            machine_name = printer_cfg["machine_profile_names"][nozzle]
            base_name, base_id = printer_cfg["machine_base_profiles"][nozzle]

            # Build the machine profile JSON
            profile = {
                "from": "User",
                "inherits": base_name,
                "is_custom_defined": "0",
                "name": machine_name,
                "printer_settings_id": machine_name,
                "version": ORCA_PROFILE_VERSION,
            }

            # Apply custom gcode from bundled file
            gcode = gcode_cache.get(printer_cfg["gcode_file"], {})
            if gcode:
                profile.update(gcode)

            # Apply any machine extras (printable_area, thumbnails, etc)
            if printer_cfg.get("machine_extras"):
                profile.update(printer_cfg["machine_extras"])

            if dry_run:
                print(f"  [DRY RUN] Would write machine: {machine_name} (inherits {base_name})")
            else:
                MACHINE_DIR.mkdir(parents=True, exist_ok=True)
                json_path = MACHINE_DIR / f"{machine_name}.json"
                info_path = MACHINE_DIR / f"{machine_name}.info"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(profile, f, indent=4, ensure_ascii=False)
                    f.write("\n")
                with open(info_path, "w", encoding="utf-8") as f:
                    f.write(format_info_file(base_id))

            count += 1

    return count


# =============================================================================
# BACKUP AND FILE I/O
# =============================================================================

def create_backup():
    """Backup user profile directories with timestamp."""
    timestamp = time.strftime("%Y%m%d_%H%M%S") + f"_{int(time.time() * 1000) % 1000:03d}"
    backup_path = BACKUP_DIR / timestamp
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    total_files = 0

    dirs_to_backup = [
        ("process", PROCESS_DIR),
        ("machine", MACHINE_DIR),
        ("filament", FILAMENT_DIR),
    ]

    for subdir_name, subdir_path in dirs_to_backup:
        if subdir_path.exists():
            dest = backup_path / subdir_name
            shutil.copytree(subdir_path, dest)
            file_count = sum(1 for _ in dest.rglob("*") if _.is_file())
            total_files += file_count
            print(f"  Backed up {subdir_name}/: {file_count} files")

    if total_files == 0:
        print("  WARNING: No files backed up (first run?)")

    print(f"  Backup location: {backup_path}")
    return backup_path


def write_profile(name: str, profile_json: dict, base_id: str, dry_run: bool = False):
    """Write a process profile's .json and .info files."""
    json_path = PROCESS_DIR / f"{name}.json"
    info_path = PROCESS_DIR / f"{name}.info"

    if dry_run:
        print(f"  [DRY RUN] Would write: {name}.json ({len(profile_json)} keys)")
        return

    PROCESS_DIR.mkdir(parents=True, exist_ok=True)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(profile_json, f, indent=4, ensure_ascii=False)
        f.write("\n")

    with open(info_path, "w", encoding="utf-8") as f:
        f.write(format_info_file(base_id))


# =============================================================================
# MAIN
# =============================================================================

def generate_all(dry_run: bool = False):
    """Generate all 64 profiles."""
    profiles_generated = 0

    for printer in PRINTERS:
        for nozzle in NOZZLE_SIZES:
            nozzle_info = PRINTERS[printer]["nozzle_base_profiles"].get(nozzle)
            if nozzle_info is None:
                print(f"  SKIP: No base profile for {printer} {nozzle}mm nozzle")
                continue

            inherits_name, base_id = nozzle_info

            for mode_name in MATERIAL_MODES:
                profile_name = make_profile_name(mode_name, printer, nozzle)

                # Build the override set
                overrides = build_profile(printer, nozzle, mode_name)

                # Format as OrcaSlicer JSON
                profile_json = format_profile_json(
                    name=profile_name,
                    inherits=inherits_name,
                    overrides=overrides,
                )

                write_profile(profile_name, profile_json, base_id, dry_run=dry_run)
                profiles_generated += 1

    return profiles_generated


# =============================================================================
# ORCASLICER.CONF GLOBAL SETTINGS
# =============================================================================

ORCA_CONF_PATH = ORCA_DIR / "OrcaSlicer.conf"

# Flush multiplier: 0.9 = 10% reduction from default purge volumes.
# Community tests show BBL's auto-calculated volumes are ~57% higher than needed.
# 0.9 is conservative and safe for all filaments including silk and PVA.
FLUSH_MULTIPLIER = "0.850000"

# Known printers: serial -> (friendly_name, ip, printer_type, access_code)
# Used to ensure local_machines and user_access_code are set in OrcaSlicer.conf
KNOWN_PRINTERS = {
    "00M00A322700314": {
        "dev_name": "X1 Carbon",
        "printer_type": "BL-P001",
    },
    "0300CA612500025": {
        "dev_name": "A1 Mini",
        "printer_type": "N1",
    },
}


def patch_orca_conf(dry_run: bool = False):
    """Patch global settings in OrcaSlicer.conf."""
    if not ORCA_CONF_PATH.exists():
        print("  WARNING: OrcaSlicer.conf not found")
        return

    with open(ORCA_CONF_PATH, "r", encoding="utf-8") as f:
        raw = f.read()

    # OrcaSlicer.conf may have a trailing MD5 comment line - strip it for parsing
    lines = raw.split("\n")
    json_lines = [l for l in lines if not l.startswith("# MD5")]
    conf = json.loads("\n".join(json_lines))

    changed = False

    # Flush multiplier
    old_flush = conf.get("flush_multiplier", "")
    if old_flush != FLUSH_MULTIPLIER:
        conf["flush_multiplier"] = FLUSH_MULTIPLIER
        if dry_run:
            print(f"  [DRY RUN] Would set flush_multiplier to {FLUSH_MULTIPLIER}")
        else:
            print(f"  Set flush_multiplier to {FLUSH_MULTIPLIER}")
        changed = True
    else:
        print(f"  flush_multiplier already {FLUSH_MULTIPLIER}")

    # Ensure known printers exist in local_machines with correct names
    local_machines = conf.setdefault("local_machines", {})
    for serial, info in KNOWN_PRINTERS.items():
        if serial not in local_machines:
            local_machines[serial] = {
                "dev_ip": "",
                "dev_name": info["dev_name"],
                "printer_type": info["printer_type"],
            }
            if dry_run:
                print(f"  [DRY RUN] Would add printer {info['dev_name']} ({serial})")
            else:
                print(f"  Added printer {info['dev_name']} ({serial})")
            changed = True
        elif local_machines[serial].get("dev_name") != info["dev_name"]:
            old_name = local_machines[serial].get("dev_name", "?")
            local_machines[serial]["dev_name"] = info["dev_name"]
            if dry_run:
                print(f"  [DRY RUN] Would rename {serial} from '{old_name}' to '{info['dev_name']}'")
            else:
                print(f"  Renamed {serial} from '{old_name}' to '{info['dev_name']}'")
            changed = True

    if not dry_run and changed:
        with open(ORCA_CONF_PATH, "w", encoding="utf-8") as f:
            json.dump(conf, f, indent=4, ensure_ascii=False)
            f.write("\n")


def clean_all_profiles(dry_run: bool = False):
    """Delete ALL user process, machine, and filament profiles (Brian-generated ones)."""
    cleaned = 0
    for subdir in [PROCESS_DIR, MACHINE_DIR]:
        if subdir.exists():
            for f in list(subdir.glob("B *.json")) + list(subdir.glob("B *.info")) + \
                     list(subdir.glob("Brian *.json")) + list(subdir.glob("Brian *.info")):
                if dry_run:
                    print(f"  [DRY RUN] Would delete: {f.name}")
                else:
                    f.unlink()
                cleaned += 1
    for subdir in [FILAMENT_DIR, FILAMENT_BASE_SUBDIR]:
        if subdir.exists():
            for f in list(subdir.glob("B *.json")) + list(subdir.glob("B *.info")):
                if dry_run:
                    print(f"  [DRY RUN] Would delete: {f.name}")
                else:
                    f.unlink()
                cleaned += 1
    return cleaned


def main():
    dry_run = "--dry-run" in sys.argv
    backup_only = "--backup-only" in sys.argv
    do_clean = "--clean" in sys.argv
    auto_yes = "--yes" in sys.argv

    # Parse --output-dir <path>
    output_dir = None
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
        else:
            print("ERROR: --output-dir requires a path argument")
            sys.exit(1)

    # Reconfigure paths if output dir specified or to pick up OS detection
    _setup_paths(output_dir)

    enabled = [k for k, v in ENABLED_PRINTERS.items() if v]

    print(f"OrcaSlicer Profile Generator ({platform.system()})")
    print(f"Enabled printers: {', '.join(enabled)}")
    if output_dir:
        print(f"Output dir: {output_dir}")
    else:
        print(f"OrcaSlicer dir: {ORCA_DIR}")
    print(f"Process: {PROCESS_DIR}")
    print(f"Machine: {MACHINE_DIR}")
    print(f"Filament: {FILAMENT_DIR}")
    print()

    if not enabled:
        print("ERROR: No printers enabled. Edit ENABLED_PRINTERS in generate.py.")
        sys.exit(1)

    # Backup (skip when using --output-dir since we're not touching OrcaSlicer)
    if not output_dir:
        print("Creating backup...")
        create_backup()
        print()

    if backup_only:
        print("Backup-only mode. Done.")
        return

    action = "DRY RUN" if dry_run else "Generating"

    # --clean: delete all existing profiles before generating
    if do_clean:
        if dry_run:
            print("[DRY RUN] Would clean all existing profiles...")
            clean_all_profiles(dry_run=True)
            print()
        else:
            if auto_yes:
                confirmed = True
            elif sys.stdin.isatty():
                resp = input("WARNING: --clean will delete ALL existing Brian/B profiles. Continue? [y/N] ")
                confirmed = resp.strip().lower() in ("y", "yes")
            else:
                print("ERROR: --clean requires interactive confirmation. Pass --yes to skip.")
                print("       (stdin is not a TTY)")
                sys.exit(1)

            if confirmed:
                print("Cleaning all existing profiles...")
                cleaned = clean_all_profiles(dry_run=False)
                print(f"  Deleted {cleaned} files.")
                print()
            else:
                print("Clean cancelled.")
                return

    # Generate machine profiles
    print(f"{action} machine profiles: {len(PRINTERS)} printers × {len(NOZZLE_SIZES)} nozzles")
    machine_count = generate_machine_profiles(dry_run=dry_run)
    print(f"  {'Would generate' if dry_run else 'Generated'} {machine_count} machine profiles.")
    print()

    # Generate filament profiles
    print(f"{action} filament profiles...")
    filament_count = generate_filament_profiles(dry_run=dry_run)
    print(f"  {'Would update' if dry_run else 'Updated'} {filament_count} filament profiles.")
    print()

    # Generate process profiles
    print(f"{action} process profiles: {len(PRINTERS)} printers × {len(NOZZLE_SIZES)} nozzles × {len(MATERIAL_MODES)} modes")
    process_count = generate_all(dry_run=dry_run)
    print(f"  {'Would generate' if dry_run else 'Generated'} {process_count} process profiles.")
    print()

    # Patch OrcaSlicer.conf global settings (skip with --output-dir)
    if not output_dir:
        print(f"{action} OrcaSlicer.conf tweaks...")
        patch_orca_conf(dry_run=dry_run)
        print()

    total = machine_count + process_count
    print(f"Total: {total} profiles + {filament_count} filament updates.")


if __name__ == "__main__":
    main()
