"""
OrcaSlicer Profile Generator
=============================

Generates process profiles, machine profiles, and filament profiles for
Brian's Bambu Lab X1 Carbon (X1C) and A1 Mini (A1M) printers across
0.2/0.4/0.6/0.8mm nozzle sizes and 8 material modes.

Outputs: 8 machine profiles, 64 process profiles, ~11 filament profiles.
Run `python generate.py` to backup + regenerate everything.

BASELINE PHILOSOPHY
-------------------
All profiles start from Bambu Lab's system defaults and apply a conservative
override strategy. The guiding principle is "if it works at 300mm/s it works
even better at 90mm/s." We trade speed for reliability and universal
compatibility across all PLA brands and irregular object geometries.

- Slow first layer (25mm/s, 75 accel) for bed adhesion reliability
- Wider line widths (105% outer, 112% inner/infill) for strength and gap filling
- Seam on back of model (less visible than BBL's default "aligned")
- No brim by default (enabled per-project)
- Detect thin walls always on (BBL leaves this off, skipping thin features)
- Support pre-configured but disabled (consistent settings when user enables)
- Support on build plate only (interior support via manual painting)
- Reduce crossing walls (less stringing)
- Gyroid infill at 10% on X1C (strongest per material, low accel to absorb shaking)
- Crosshatch infill at 15% on A1M (less violent direction changes for gantry arm)
- Ironing pre-configured but not enabled (ready for per-project use)

PRINTER VARIANTS: X1C vs A1M
-----------------------------
The A1M has a cantilevered gantry arm instead of the X1C's rigid enclosed CoreXY.
This fundamentally limits what the printer can handle.

- A1M max print speed hard cap: 150mm/s (including travel)
- A1M max acceleration hard cap: 5000 mm/s²
- A1M infill: crosshatch instead of gyroid (less violent, gentler on gantry)
- A1M infill accel: 3000 (capped, crosshatch is gentler but still cap it)
- A1M first layer: hard cap at 16/20 mm/s (speed/infill) for bed adhesion
- A1M filament retraction: +0.1mm over X1C baseline (compensate for bowden-like path)
- A1M z-offset gcode: same as X1C (-0.04 textured PEI, -0.02 everything else)
- A1M supertack plate: 60°C for PLA (vs 55 on X1C, no enclosure heat buildup)

MATERIAL MODES
--------------
All modes share the universal baseline above. Each mode changes the speed/accel
philosophy and structural settings for different use cases.

B PLA (default standard):
  - Conservative speeds: 60 outer wall, 90 inner wall, 65 infill
  - High outer wall accel (10000) for Bambu input shaping on visible surfaces
  - Works reliably across all PLA brands including cheap ones
  - 2 walls, gyroid 10% (X1C) / crosshatch 15% (A1M)

B PLA Fast:
  - 75% of BBL baseline speeds (150 outer, 225 inner, 200 infill)
  - "We don't need to go 120mph in an 80" - slightly below max for reliability
  - Used for on-site A1M prototyping where print time matters but failures are costly
  - A1M travel: 525mm/s (75% of A1M's 700 baseline), capped to 150 by A1M cap

B PETG ABS:
  - All speeds 45mm/s - Brian's tested sweet spot for PETG
  - Very slow first layer: 12mm/s speed, 15mm/s infill (critical for PETG adhesion)
  - All acceleration capped at 2500
  - Alternate extra wall for PETG's weaker inter-layer bonding
  - Overhang speeds all 30mm/s (PETG droops more)
  - Primary profile for 0.6mm nozzle functional prints on portable A1M

B PLA Silk:
  - Slower speeds (~80% of PLA): 48 outer, 70 inner
  - LOW acceleration (1500 outer/top, 2500 inner/infill) - NOT high
  - Silk PLA additives make flow inconsistencies highly visible as blotchy shimmer
  - Low accel avoids nozzle pressure spikes that cause uneven extrusion
  - 3 walls for better silk surface quality

B PLA Draft:
  - As fast as the printer allows: 125mm/s everything
  - Single wall, 1 bottom layer, 0.24mm layer height (tallest for 0.4 nozzle)
  - Just need to see what the shape looks like in 3D, nothing else matters
  - Tree support for easy removal, cubic infill at 7%

B PLA Delicate:
  - Ultra-conservative for small intricate parts (D&D minis, etc)
  - All speeds 45mm/s, all acceleration 500 mm/s²
  - Low accel prevents jolting that knocks over tiny fragile features
  - 3 walls, cubic infill 12%, interlocking beam enabled
  - X1C: 20% speed reduction on top of base (speeds become ~36mm/s)
  - A1M: 35% speed reduction on top of base (speeds become ~29mm/s)
    - A1M Delicate accel cap: 1500 (tighter than general 5000)
    - A1M Delicate travel cap: 60mm/s

B PLA MM (Multi-Material):
  - Slower than PLA standard (75/55/60 inner/infill/outer) with 2500 accel cap
  - Intentionally conservative: colors bleeding, materials not sticking, prime tower
    issues all improve with slower speeds
  - Flush into infill (saves material) but NOT into support (needs clean surfaces)
  - 3 walls for color separation

B PLA+PETG+PVA MM:
  - Most conservative profile: PLA and PETG don't naturally adhere
  - 0.18mm layer height for more inter-material bonding surface area
  - Zero support z-distance so PVA prints directly against model surface
  - Concentric support interface with zero spacing (solid PVA interface layer)
  - Very slow speeds (40-55mm/s) for precise multi-material deposition

NOZZLE SCALING
--------------
- Layer height: 50% of nozzle diameter (draft: 60%, PVA MM: 45%)
- Wall loops: +2 on 0.2mm nozzle to maintain minimum 0.84mm wall thickness
- Speed: 0.9x at 0.6mm, 0.85x at 0.8mm (larger bead = more material per second)
- Acceleration: 0.95x at 0.6mm, 0.9x at 0.8mm (larger bead = more ringing)
- Support z-distance: scales with layer height

FILAMENT PROFILES
-----------------
- Generated per-printer (B PLA, B PLA A1M, etc)
- ABS is X1C-only (needs enclosure)
- PVA available on both printers
- A1M variants get +0.1mm retraction length
- A1M PLA/Silk/Wood/PVA supertack plate: 60°C (X1C: 55°C, enclosure traps heat)
- PLA plate temps corrected from old 48-everywhere to proper per-plate values:
    Cool plate 40/45°C, Textured 55-58°C, Engineering/Hot/Supertack 55-60°C
- ABS supertack fixed from erroneous 35°C to correct 90°C

MACHINE PROFILES
----------------
- Brian X1C 0.2/0.4/0.6/0.8: inherit BBL X1C + Brian's custom gcode
- Brian A1M 0.2/0.4/0.6/0.8: inherit BBL A1M + patched z-offset gcode
- X1C gcode: custom start/end/toolchange/layer_change with z-offset logic
- A1M gcode: BBL base with patched z-offset (-0.04 textured, -0.02 everything else)
- Gcode falls back to bundled brian_x1c_gcode.json if no existing profile found
"""

import json
import os
import shutil
import sys
import time
from copy import deepcopy
from pathlib import Path

# =============================================================================
# PATHS
# =============================================================================

APPDATA = os.environ.get("APPDATA", "")
ORCA_DIR = Path(APPDATA) / "OrcaSlicer"

# User-level directories
USER_PROCESS_DIR = ORCA_DIR / "user" / "default" / "process"
USER_MACHINE_DIR = ORCA_DIR / "user" / "default" / "machine"
USER_FILAMENT_DIR = ORCA_DIR / "user" / "default" / "filament"

# Output directories (user-level)
PROCESS_DIR = USER_PROCESS_DIR
MACHINE_DIR = USER_MACHINE_DIR
FILAMENT_DIR = USER_FILAMENT_DIR

# Legacy system vendor directory (for cleanup)
BRIAN_VENDOR_DIR = ORCA_DIR / "system" / "Brian"
BRIAN_VENDOR_MANIFEST = ORCA_DIR / "system" / "Brian.json"

BACKUP_DIR = Path(__file__).parent / "backups"
ORCA_PROFILE_VERSION = "1.10.0.35"
FILAMENT_BASE_SUBDIR = USER_FILAMENT_DIR / "base"

# =============================================================================
# PRINTERS
# =============================================================================

PRINTERS = {
    "X1C": {
        "base_profile_template": "{layer_height_str} Standard @BBL X1C",
        "base_profile_0.4": "0.20mm Standard @BBL X1C",
        "base_id": "GP004",
        "nozzle_base_profiles": {
            0.2: ("0.10mm Standard @BBL X1C 0.2 nozzle", "GP007"),
            0.4: ("0.20mm Standard @BBL X1C", "GP004"),
            0.6: ("0.30mm Standard @BBL X1C 0.6 nozzle", "GP010"),
            0.8: ("0.40mm Standard @BBL X1C 0.8 nozzle", "GP009"),
        },
        # Machine profile names (what we generate in user/default/machine/)
        "machine_profile_names": {
            0.2: "Brian X1C 0.2",
            0.4: "Brian X1C 0.4",
            0.6: "Brian X1C 0.6",
            0.8: "Brian X1C 0.8",
        },
        # BBL system machine profiles these inherit from
        "machine_base_profiles": {
            0.2: ("Bambu Lab X1 Carbon 0.2 nozzle", "GM002"),
            0.4: ("Bambu Lab X1 Carbon 0.4 nozzle", "GM001"),
            0.6: ("Bambu Lab X1 Carbon 0.6 nozzle", "GM005"),
            0.8: ("Bambu Lab X1 Carbon 0.8 nozzle", "GM004"),
        },
    },
    "A1M": {
        "base_profile_template": "{layer_height_str} Standard @BBL A1M",
        "base_profile_0.4": "0.20mm Standard @BBL A1M",
        "base_id": "GP000",
        "nozzle_base_profiles": {
            0.2: ("0.10mm Standard @BBL A1M 0.2 nozzle", "GP083"),
            0.4: ("0.20mm Standard @BBL A1M", "GP000"),
            0.6: ("0.30mm Standard @BBL A1M 0.6 nozzle", "GP096"),
            0.8: ("0.40mm Standard @BBL A1M 0.8 nozzle", "GP098"),
        },
        # Machine profile names
        "machine_profile_names": {
            0.2: "Brian A1M 0.2",
            0.4: "Brian A1M 0.4",
            0.6: "Brian A1M 0.6",
            0.8: "Brian A1M 0.8",
        },
        # BBL system machine profiles these inherit from
        "machine_base_profiles": {
            0.2: ("Bambu Lab A1 mini 0.2 nozzle", "GM021"),
            0.4: ("Bambu Lab A1 mini 0.4 nozzle", "GM020"),
            0.6: ("Bambu Lab A1 mini 0.6 nozzle", "GM022"),
            0.8: ("Bambu Lab A1 mini 0.8 nozzle", "GM023"),
        },
    },
}

NOZZLE_SIZES = [0.2, 0.4, 0.6, 0.8]

# =============================================================================
# LAYER 1: UNIVERSAL BRIAN OVERRIDES
# Applied to every single profile regardless of printer/nozzle/material.
# =============================================================================

UNIVERSAL_OVERRIDES = {
    # First layer - slow for bed adhesion reliability (same on both printers)
    "initial_layer_speed": "25",
    "initial_layer_infill_speed": "30",
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
    "top_shell_thickness": "0.7",
    "bottom_shell_thickness": "0.5",

    # Ironing (configured, not enabled - user enables per project)
    "ironing_flow": "26%",
    "ironing_spacing": "0.2",
    "ironing_speed": "150",

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
    "X1C": {
        # Gyroid: strongest per material used, but shakes the printer.
        # Low infill accel (2000) absorbs the shock on X1C's rigid CoreXY frame.
        "sparse_infill_pattern": "gyroid",
        "sparse_infill_density": "10%",
        "sparse_infill_acceleration": "2000",
        "travel_acceleration": "2500",
    },
    "A1M": {
        # Crosshatch: less violent direction changes than gyroid.
        # Better match for A1M's cantilevered gantry arm.
        # 15% compensates for crosshatch being slightly weaker than gyroid.
        # 3000 accel: crosshatch is gentler so can go higher than X1C's 2000,
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
# 75% of BBL baseline speeds. For faster prints with reasonable reliability.
# "We don't need to go 120 mph in an 80."
PLA_FAST = {
    "outer_wall_speed": "150",
    "inner_wall_speed": "225",
    "sparse_infill_speed": "200",
    "internal_solid_infill_speed": "188",
    "gap_infill_speed": "188",
    "top_surface_speed": "150",
    "travel_speed": "375",
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

# PLA Fast gets higher travel on A1M (75% of A1M's 700 = 525)
PLA_FAST_A1M_EXTRA = {
    "travel_speed": "525",
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
    "bottom_shell_layers": "2",
    "bottom_shell_thickness": "0.35",
    "top_shell_layers": "3",
    "top_shell_thickness": "0.5",
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
    "sparse_infill_density": "12%",
    # Extra features for small parts
    "interlocking_beam": "1",
    "skirt_loops": "2",
    "support_threshold_angle": "35",
    # Shells
    "bottom_shell_thickness": "0.4",
    "top_shell_thickness": "0.5",
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
    # Extra wall for color separation
    "wall_loops": "3",
    # MM-specific
    "flush_into_infill": "1",
    "flush_into_support": "0",
    "timelapse_type": "1",
    "support_filament": "1",
    "support_base_pattern_spacing": "3.5",
    "support_interface_pattern": "rectilinear_interlaced",
    "support_threshold_angle": "35",
    # Shells
    "bottom_shell_thickness": "0.6",
    "top_shell_thickness": "0.8",
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
    # Extra walls
    "wall_loops": "3",
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
    "bottom_shell_thickness": "0.6",
    "top_shell_thickness": "0.8",
    # Raft
    "raft_first_layer_density": "25%",
    "raft_first_layer_expansion": "1.5",
    "initial_layer_line_width": "105%",
}

# Registry of all material modes
MATERIAL_MODES = {
    "PLA": PLA_STANDARD,  # Was "PLA Standard", renamed to just "PLA"
    "PLA Fast": PLA_FAST,
    "PETG ABS": PETG_ABS,
    "PLA Silk": PLA_SILK,
    "PLA Draft": PLA_DRAFT,
    "PLA Delicate": PLA_DELICATE,
    "PLA MM": PLA_MM,
    "PLA+PETG+PVA MM": PLA_PETG_PVA_MM,
}

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
    "filament_cost": ["40"],
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
    # Temps
    "nozzle_temperature": ["220"],
    "nozzle_temperature_initial_layer": ["225"],
    "nozzle_temperature_range_high": ["250"],
    "nozzle_temperature_range_low": ["210"],
    "cool_plate_temp": ["48"],
    "cool_plate_temp_initial_layer": ["48"],
    "eng_plate_temp": ["48"],
    "eng_plate_temp_initial_layer": ["48"],
    "hot_plate_temp": ["48"],
    "hot_plate_temp_initial_layer": ["48"],
    "supertack_plate_temp": ["48"],
    "supertack_plate_temp_initial_layer": ["48"],
    "textured_cool_plate_temp": ["48"],
    "textured_cool_plate_temp_initial_layer": ["48"],
    "textured_plate_temp": ["48"],
    "textured_plate_temp_initial_layer": ["48"],
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

# Child filament: overrides on top of B PLA
FILAMENT_B_PLA_SILK_OVERRIDES = {
    "filament_cost": ["22"],
    "filament_max_volumetric_speed": ["2.6"],
    "filament_retraction_length": ["0.4"],
    "nozzle_temperature": ["232"],
    "nozzle_temperature_initial_layer": ["220"],
}

FILAMENT_B_PLA_WOOD_OVERRIDES = {
    "filament_cost": ["30"],
    "filament_max_volumetric_speed": ["3"],
    "filament_retraction_length": ["0.5"],
    "filament_z_hop": ["0.15"],
    "filament_z_hop_types": ["Auto Lift"],
    "nozzle_temperature_initial_layer": ["230"],
}

# Registry: name -> (base_data, parent_name_or_None, printers_list_or_None)
# If parent_name is set, the profile merges parent data + overrides
# If printers is None, generate for all printers. Otherwise only listed ones.
# ABS is X1C-only (needs enclosure). PVA is X1C-only (used in enclosed MM setups).
FILAMENT_REGISTRY = {
    "B PLA":      (FILAMENT_B_PLA, None, None),
    "B PETG":     (FILAMENT_B_PETG, None, None),
    "B ABS":      (FILAMENT_B_ABS, None, ["X1C"]),
    "B PVA":      (FILAMENT_B_PVA, None, None),
    "B PLA Silk": (FILAMENT_B_PLA_SILK_OVERRIDES, "B PLA", None),
    "B PLA Wood": (FILAMENT_B_PLA_WOOD_OVERRIDES, "B PLA", None),
}

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

PRINTER_SHORT = {
    "X1C": "",       # X1C is default, no suffix
    "A1M": " A1M",
}

NOZZLE_SHORT = {
    0.2: " 0.2n",
    0.4: "",         # 0.4 is default, no suffix
    0.6: " 0.6n",
    0.8: " 0.8n",
}


def make_profile_name(mode_name: str, printer: str, nozzle: float) -> str:
    """Generate a profile name like 'B PLA Standard' or 'B PETG ABS A1M 0.6n'."""
    return f"B {mode_name}{PRINTER_SHORT[printer]}{NOZZLE_SHORT[nozzle]}"


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


def build_profile(printer: str, nozzle: float, mode_name: str) -> dict:
    """
    Build a complete profile by layering:
    1. Universal overrides
    2. Printer deltas
    3. Material mode
    4. Nozzle scaling
    """
    profile = {}

    # Layer 1: Universal overrides
    profile.update(deepcopy(UNIVERSAL_OVERRIDES))

    # Layer 2: Printer deltas
    profile.update(deepcopy(PRINTER_DELTAS[printer]))

    # Layer 3: Material mode
    mode = deepcopy(MATERIAL_MODES[mode_name])
    profile.update(mode)

    # PLA Fast A1M gets extra travel speed override
    if mode_name == "PLA Fast" and printer == "A1M":
        profile.update(PLA_FAST_A1M_EXTRA)

    # A1M infill speed: raise to match highest non-infill speed in profile
    if printer == "A1M":
        non_infill_speeds = []
        for k in ["outer_wall_speed", "inner_wall_speed", "internal_solid_infill_speed",
                   "top_surface_speed", "gap_infill_speed"]:
            if k in profile:
                try:
                    non_infill_speeds.append(int(float(profile[k])))
                except ValueError:
                    pass
        if non_infill_speeds:
            max_speed = max(non_infill_speeds)
            current_infill = int(float(profile.get("sparse_infill_speed", "0")))
            if current_infill < max_speed:
                profile["sparse_infill_speed"] = str(max_speed)

    # Layer 4: Nozzle scaling

    # 4a: Layer height
    if mode_name == "PLA Draft":
        base_lh = NOZZLE_DRAFT_LAYER_HEIGHT[nozzle]
    elif mode_name == "PLA+PETG+PVA MM":
        base_lh = NOZZLE_PVA_MM_LAYER_HEIGHT[nozzle]
    else:
        base_lh = NOZZLE_DEFAULT_LAYER_HEIGHT[nozzle]
    profile["layer_height"] = f"{base_lh:.2f}"

    # 4b: Wall loops - add extra for small nozzles to maintain wall thickness
    base_walls = int(profile.get("wall_loops", "2"))
    profile["wall_loops"] = str(base_walls + NOZZLE_WALL_LOOP_ADDITION[nozzle])

    # 4c: Speed and acceleration scaling for non-0.4 nozzles
    speed_mult = NOZZLE_SPEED_MULTIPLIER[nozzle]
    accel_mult = NOZZLE_ACCEL_MULTIPLIER[nozzle]

    if speed_mult != 1.0:
        for key in list(profile.keys()):
            if key in SPEED_KEYS:
                profile[key] = scale_numeric_value(profile[key], speed_mult)

    if accel_mult != 1.0:
        for key in list(profile.keys()):
            if key in ACCEL_KEYS:
                profile[key] = scale_numeric_value(profile[key], accel_mult)

    # 4d: Support z-distance scales with layer height
    # (except PLA+PETG+PVA MM which forces 0 for PVA adhesion)
    if mode_name != "PLA+PETG+PVA MM":
        lh = float(profile["layer_height"])
        profile["support_top_z_distance"] = f"{lh:.2f}"
        profile["support_bottom_z_distance"] = f"{lh:.2f}"

    # 4e: Shell thickness adjustments for layer height
    lh = float(profile["layer_height"])
    # bottom_shell_layers: ensure at least the thickness / layer_height
    if "bottom_shell_thickness" in profile:
        target_thickness = float(profile["bottom_shell_thickness"])
        min_layers = max(1, int(round(target_thickness / lh)))
        profile["bottom_shell_layers"] = str(min_layers)

    # 5: Delicate speed reductions (applied before A1M caps)
    # X1C Delicate: 20% slower across all speeds
    # A1M Delicate: 35% slower across all speeds
    if mode_name == "PLA Delicate":
        if printer == "X1C":
            delicate_mult = 0.80
        elif printer == "A1M":
            delicate_mult = 0.65
        else:
            delicate_mult = 1.0
        for key in list(profile.keys()):
            if key in SPEED_KEYS:
                profile[key] = scale_numeric_value(profile[key], delicate_mult)

    # 6: A1M hard caps - gantry arm can't handle high speeds/accels
    if printer == "A1M":
        A1M_MAX_ACCEL = 5000
        A1M_MAX_SPEED = 150
        A1M_TRAVEL_CAP = 150

        # A1M first layer: hard cap for bed adhesion on gantry printer
        A1M_MAX_FIRST_LAYER_SPEED = 16
        A1M_MAX_FIRST_LAYER_INFILL_SPEED = 20
        for key, cap in [("initial_layer_speed", A1M_MAX_FIRST_LAYER_SPEED),
                         ("initial_layer_infill_speed", A1M_MAX_FIRST_LAYER_INFILL_SPEED)]:
            if key in profile:
                try:
                    val = int(float(profile[key]))
                    if val > cap:
                        profile[key] = str(cap)
                except (ValueError, TypeError):
                    pass
        # Delicate on A1M gets tighter caps
        if mode_name == "PLA Delicate":
            A1M_MAX_ACCEL = 1500
            A1M_MAX_SPEED = 150  # already slowed by 35% above
            A1M_TRAVEL_CAP = 60

        for key in list(profile.keys()):
            if key in ACCEL_KEYS:
                try:
                    val = int(float(profile[key]))
                    if val > A1M_MAX_ACCEL:
                        profile[key] = str(A1M_MAX_ACCEL)
                except (ValueError, TypeError):
                    pass
            if key in SPEED_KEYS:
                cap = A1M_TRAVEL_CAP if key == "travel_speed" else A1M_MAX_SPEED
                try:
                    val = int(float(profile[key]))
                    if val > cap:
                        profile[key] = str(cap)
                except (ValueError, TypeError):
                    pass

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

# Brian's X1C 0.4 gcode customizations are read from the existing profile
# at generation time. Other X1C nozzle variants get the same gcode since
# it uses OrcaSlicer variables (not hardcoded nozzle-specific values).
# A1M profiles inherit BBL defaults with no gcode customization.

# Source locations to find Brian's gcode (checked in order)
# Falls back to bundled gcode data file if no existing profile found
BRIAN_GCODE_SOURCES = [
    MACHINE_DIR / "Brian X1C 0.4.json",
    MACHINE_DIR / "Brian 0.4 nozzle.json",
]
BRIAN_GCODE_FALLBACK = Path(__file__).parent / "brian_x1c_gcode.json"

GCODE_KEYS = ["machine_start_gcode", "machine_end_gcode",
              "change_filament_gcode", "layer_change_gcode"]


def load_brian_x1c_gcode() -> dict:
    """Load Brian's custom gcode from existing profile or bundled fallback."""
    # Try existing machine profiles first
    for path in BRIAN_GCODE_SOURCES:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            gcode = {k: data[k] for k in GCODE_KEYS if k in data}
            if gcode:
                print(f"  Loaded gcode from: {path.name}")
                return gcode

    # Fall back to bundled gcode data file
    if BRIAN_GCODE_FALLBACK.exists():
        with open(BRIAN_GCODE_FALLBACK, "r", encoding="utf-8") as f:
            gcode = json.load(f)
        print(f"  Loaded gcode from fallback: {BRIAN_GCODE_FALLBACK.name}")
        return gcode

    print("WARNING: Could not find Brian's X1C gcode from any source")
    return {}


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

        # Generate one per printer (respecting printer filter)
        for printer_key, printer_cfg in PRINTERS.items():
            if allowed_printers and printer_key not in allowed_printers:
                continue
            printer_suffix = " A1M" if printer_key == "A1M" else ""
            profile_name = f"{filament_name}{printer_suffix}"

            profile = deepcopy(full_data)
            profile["name"] = profile_name
            profile["filament_settings_id"] = [profile_name]
            profile["from"] = "User"
            profile["is_custom_defined"] = "0"
            profile["version"] = ORCA_PROFILE_VERSION

            # Set compatible_printers to all nozzle variants for this printer
            profile["compatible_printers"] = [
                printer_cfg["machine_base_profiles"][nozzle][0]
                for nozzle in NOZZLE_SIZES
            ]

            # A1M: slightly more retraction for the gantry arm
            if printer_key == "A1M" and "filament_retraction_length" in profile:
                try:
                    base_ret = float(profile["filament_retraction_length"][0])
                    profile["filament_retraction_length"] = [f"{base_ret + 0.1:.2f}"]
                except (ValueError, IndexError):
                    pass

            # A1M: supertack plate runs hotter for PLA-based filaments
            # (no enclosure to trap heat like X1C)
            if printer_key == "A1M":
                fil_type = profile.get("filament_type", [""])[0]
                if fil_type in ("PLA", "PVA"):
                    profile["supertack_plate_temp"] = ["60"]
                    profile["supertack_plate_temp_initial_layer"] = ["60"]

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


# Original A1M z-offset block (BBL default)
A1M_ZOFFSET_ORIGINAL = """;===== for Textured PEI Plate , lower the nozzle as the nozzle was touching topmost of the texture when homing ==
;curr_bed_type={curr_bed_type}
{if curr_bed_type=="Textured PEI Plate"}
G29.1 Z{-0.02} ; for Textured PEI Plate
{endif}"""

# Brian's replacement: Textured PEI gets -0.04, everything else gets -0.02
A1M_ZOFFSET_PATCHED = """;===== for Textured PEI Plate , lower the nozzle as the nozzle was touching topmost of the texture when homing ==
;curr_bed_type={curr_bed_type}
{if curr_bed_type=="Textured PEI Plate"}
G29.1 Z{-0.04} ; for Textured PEI Plate
{else}
; lower just slightly if other kinds of plates, i prefer the different bed adhesion
G29.1 Z{-0.02} ; for other plates
{endif}"""

SYSTEM_MACHINE_DIR = ORCA_DIR / "system" / "BBL" / "machine"


def load_a1m_patched_gcode(base_profile_name: str) -> str:
    """Load A1M base start gcode and patch in Brian's z-offset logic."""
    path = SYSTEM_MACHINE_DIR / f"{base_profile_name}.json"
    if not path.exists():
        print(f"  WARNING: Could not find {path.name} for A1M gcode patching")
        return ""

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    gcode = data.get("machine_start_gcode", "")
    if not gcode:
        # May need to walk inheritance chain
        parent = data.get("inherits", "")
        if parent:
            parent_path = SYSTEM_MACHINE_DIR / f"{parent}.json"
            if parent_path.exists():
                with open(parent_path, "r", encoding="utf-8") as f:
                    parent_data = json.load(f)
                gcode = parent_data.get("machine_start_gcode", "")

    if A1M_ZOFFSET_ORIGINAL in gcode:
        gcode = gcode.replace(A1M_ZOFFSET_ORIGINAL, A1M_ZOFFSET_PATCHED)
        return gcode

    print(f"  WARNING: Could not find z-offset block in {base_profile_name} gcode")
    return gcode if gcode else ""


def generate_machine_profiles(dry_run: bool = False):
    """Generate machine profiles for all printer/nozzle combinations."""
    count = 0
    brian_gcode = load_brian_x1c_gcode()

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

            # X1C profiles get Brian's custom gcode and overrides
            if printer_key == "X1C":
                profile.update(brian_gcode)
                profile["printable_area"] = ["0x0", "256x0", "256x248", "0x248"]
                profile["thumbnails"] = "48x48/PNG, 300x300/PNG"

            # A1M profiles: patch start gcode with Brian's z-offset logic
            if printer_key == "A1M":
                a1m_gcode = load_a1m_patched_gcode(base_name)
                if a1m_gcode:
                    profile["machine_start_gcode"] = a1m_gcode

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
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / timestamp
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    total_files = 0

    dirs_to_backup = [
        ("process", USER_PROCESS_DIR),
        ("machine", USER_MACHINE_DIR),
        ("filament", USER_FILAMENT_DIR),
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


def cleanup_system_vendor(dry_run: bool = False):
    """Remove the old system/Brian vendor directory if it exists."""
    cleaned = 0
    if BRIAN_VENDOR_DIR.exists():
        if dry_run:
            print(f"  [DRY RUN] Would remove: {BRIAN_VENDOR_DIR}")
        else:
            shutil.rmtree(BRIAN_VENDOR_DIR)
        cleaned += 1
    if BRIAN_VENDOR_MANIFEST.exists():
        if dry_run:
            print(f"  [DRY RUN] Would remove: {BRIAN_VENDOR_MANIFEST}")
        else:
            BRIAN_VENDOR_MANIFEST.unlink()
        cleaned += 1
    return cleaned


def main():
    dry_run = "--dry-run" in sys.argv
    backup_only = "--backup-only" in sys.argv

    print(f"OrcaSlicer Profile Generator")
    print(f"Process: {PROCESS_DIR}")
    print(f"Machine: {MACHINE_DIR}")
    print(f"Filament: {FILAMENT_DIR}")
    print()

    # Always backup first
    print("Creating backup...")
    create_backup()
    print()

    if backup_only:
        print("Backup-only mode. Done.")
        return

    action = "DRY RUN" if dry_run else "Generating"

    # Clean up old system vendor if it exists
    cleaned = cleanup_system_vendor(dry_run=dry_run)
    if cleaned:
        print(f"Cleaned up old system/Brian vendor ({cleaned} items).")
        print()

    # Generate machine profiles
    print(f"{action} machine profiles: {len(PRINTERS)} printers × {len(NOZZLE_SIZES)} nozzles")
    machine_count = generate_machine_profiles(dry_run=dry_run)
    print(f"  {'Would generate' if dry_run else 'Generated'} {machine_count} machine profiles.")
    print()

    # Update filament profiles (clear compatible_printers)
    print(f"{action} filament profiles...")
    filament_count = generate_filament_profiles(dry_run=dry_run)
    print(f"  {'Would update' if dry_run else 'Updated'} {filament_count} filament profiles.")
    print()

    # Generate process profiles
    print(f"{action} process profiles: {len(PRINTERS)} printers × {len(NOZZLE_SIZES)} nozzles × {len(MATERIAL_MODES)} modes")
    process_count = generate_all(dry_run=dry_run)
    print(f"  {'Would generate' if dry_run else 'Generated'} {process_count} process profiles.")
    print()

    total = machine_count + process_count
    print(f"Total: {total} profiles + {filament_count} filament updates.")


if __name__ == "__main__":
    main()
