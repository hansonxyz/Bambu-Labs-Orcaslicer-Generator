; Begin AMS toolchange, set acceleration
M620 S[next_extruder]A
M204 S9000
; Spiral lift on second+ toolchange if z-hop type requires it
{if toolchange_count > 1 && (z_hop_types[current_extruder] == 0 || z_hop_types[current_extruder] == 3)}
G17
G2 Z{z_after_toolchange + 0.4} I0.86 J0.86 P1 F10000 ; spiral lift a little from second lift
{endif}
; Raise Z clear of print, move to wipe bucket
G1 Z{max_layer_z + 3.0} F1200

G1 X70 F9000
G1 Y245
G1 Y265 F3000
M400
M106 P1 S0 ; part fan off
M106 P2 S0 ; aux fan off
; Heat old filament if needed
{if old_filament_temp > 142 && next_extruder < 255}
M104 S[old_filament_temp]
{endif}
; Move to AMS swap position, optional long retract before swap
G1 X90 F3000
G1 Y255 F4000
G1 X100 F5000
G1 X120 F9000
{if long_retraction_when_cut && retraction_distance_when_cut > 2}
; Long retract to cut filament at extruder
G1 E-[retraction_distance_when_cut] F200
M400
{endif}
; Move to AMS load position
G1 X20 Y50 F9000
G1 Y-3
; Record travel waypoints on first toolchange
{if toolchange_count == 2}
; get travel path for change filament
M620.1 X[travel_point_1_x] Y[travel_point_1_y] F9000 P0
M620.1 X[travel_point_2_x] Y[travel_point_2_y] F9000 P1
M620.1 X[travel_point_3_x] Y[travel_point_3_y] F9000 P2
{endif}
; Execute AMS filament switch (T command triggers load sequence)
M620.1 E F[old_filament_e_feedrate] T{nozzle_temperature_range_high[previous_extruder]}
T[next_extruder]
M620.1 E F[new_filament_e_feedrate] T{nozzle_temperature_range_high[next_extruder]}

{if next_extruder < 255}
M400
; Slowly recover long retract to seat new filament
{if long_retraction_when_cut && retraction_distance_when_cut > 2}
G1 E{retraction_distance_when_cut - 2} F200
G1 E2 F20
M400
{endif}
G92 E0
{if flush_length_1 > 1}
M83
; FLUSH_START
; always use highest temperature to flush
M400
; Heat to flush temp based on next filament type
{if filament_type[next_extruder] == "PETG"}
M109 S260
{elsif filament_type[next_extruder] == "PVA"}
M109 S210
{else}
M109 S[nozzle_temperature_range_high]
{endif}
; Flush stage 1: prime then pulsatile extrusion
{if flush_length_1 > 23.7}
G1 E23.7 F{old_filament_e_feedrate} ; do not need pulsatile flushing for start part
G1 E{(flush_length_1 - 23.7) * 0.02} F50
G1 E{(flush_length_1 - 23.7) * 0.23} F{old_filament_e_feedrate}
G1 E{(flush_length_1 - 23.7) * 0.02} F50
G1 E{(flush_length_1 - 23.7) * 0.23} F{new_filament_e_feedrate}
G1 E{(flush_length_1 - 23.7) * 0.02} F50
G1 E{(flush_length_1 - 23.7) * 0.23} F{new_filament_e_feedrate}
G1 E{(flush_length_1 - 23.7) * 0.02} F50
G1 E{(flush_length_1 - 23.7) * 0.23} F{new_filament_e_feedrate}
{else}
G1 E{flush_length_1} F{old_filament_e_feedrate}
{endif}
; FLUSH_END
G1 E-[old_retract_length_toolchange] F1800
G1 E[old_retract_length_toolchange] F300
{endif}

{if flush_length_2 > 1}
; Step aside, flush stage 2
G91
G1 X3 F12000; move aside to extrude
G90
M83

; FLUSH_START
G1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_2 * 0.02} F50
G1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_2 * 0.02} F50
G1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_2 * 0.02} F50
G1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_2 * 0.02} F50
G1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_2 * 0.02} F50
; FLUSH_END
G1 E-[new_retract_length_toolchange] F1800
G1 E[new_retract_length_toolchange] F300
{endif}

{if flush_length_3 > 1}
; Step aside, flush stage 3
G91
G1 X3 F12000; move aside to extrude
G90
M83

; FLUSH_START
G1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_3 * 0.02} F50
G1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_3 * 0.02} F50
G1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_3 * 0.02} F50
G1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_3 * 0.02} F50
G1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_3 * 0.02} F50
; FLUSH_END
G1 E-[new_retract_length_toolchange] F1800
G1 E[new_retract_length_toolchange] F300
{endif}

{if flush_length_4 > 1}
; Step aside, flush stage 4
G91
G1 X3 F12000; move aside to extrude
G90
M83

; FLUSH_START
G1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_4 * 0.02} F50
G1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_4 * 0.02} F50
G1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_4 * 0.02} F50
G1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_4 * 0.02} F50
G1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}
G1 E{flush_length_4 * 0.02} F50
; FLUSH_END
{endif}
; Final temp stabilization and retract
; FLUSH_START
M400
M109 S[new_filament_temp]
G1 E2 F{new_filament_e_feedrate} ;Compensate for filament spillage during waiting temperature
; FLUSH_END
M400
G92 E0
G1 E-[new_retract_length_toolchange] F1800
M106 P1 S255 ; part fan 100%
M400 S3

; Wipe flushed material on purge bucket
G1 X70 F5000
G1 X90 F3000
G1 Y255 F4000
G1 X105 F5000
G1 Y265 F5000
G1 X70 F10000
G1 X100 F5000
G1 X70 F10000
G1 X100 F5000

; Shake nozzle to drop debris, then wipe
G1 X70 F10000
G1 X80 F9000
G1 X60
G1 X80
G1 X60
G1 X80 ; shake to put down garbage
G1 X100 F5000
G1 X165 F9000; wipe and shake
; Return to print height and resume
G1 Y256 ; move Y to aside, prevent collision
M400
G1 Z{max_layer_z + 3.0} F3000
{if layer_z <= (initial_layer_print_height + 0.001)}
M204 S[initial_layer_acceleration]
{else}
M204 S[default_acceleration]
{endif}
{else}
; Toolchange to 255 (unload): return directly to print position
G1 X[x_after_toolchange] Y[y_after_toolchange] Z[z_after_toolchange] F12000
{endif}
M621 S[next_extruder]A
