;===== machine: X1E =========================
;===== date: 20240919 =====================
;===== preheat nozzle =====
M104 S75 ; preheat nozzle to 75 (activates HB fan, prevents ooze)
;===== reset machine =====
G91
M17 Z0.4 ; lower z-motor current for safe homing
G380 S2 Z30 F300 ; probe down to find bed
G380 S2 Z-25 F300 ; retract probe
G1 Z5 F300;
G90
M17 X1.2 Y1.2 Z0.75 ; restore motor current to default
M960 S5 P1 ; logo lamp on
G90
M220 S100 ; reset feedrate to 100%
M221 S100 ; reset flow to 100%
M73.2   R1.0 ; reset time estimate
M1002 set_gcode_claim_speed_level : 5 ; reset speed display
M221 X0 Y0 Z0 ; disable soft endstops
G29.1 Z{+0.0} ; clear z-trim
M204 S10000 ; init ACC set to 10m/s^2

;==== if Chamber Cooling is necessary ====

; Cool chamber to safe temp for PLA/PETG/TPU/PVA before heating bed
{if (filament_type[initial_no_support_extruder]=="PLA") || (filament_type[initial_no_support_extruder]=="PETG") || (filament_type[initial_no_support_extruder]=="TPU") || (filament_type[initial_no_support_extruder]=="PVA") || (filament_type[initial_no_support_extruder]=="PLA-CF") || (filament_type[initial_no_support_extruder]=="PETG-CF")}
M1002 gcode_claim_action : 29
G28
G90
G1 X60 F12000
G1 Y245
G1 Y265 F3000
G1 Z75
M140 S0 ; turn off bed heater
M106 P2 S255 ; open auxiliary fan for cooling
M106 P3 S255 ; chamber fan 100%
M191 S0 ; wait for chamber temp
M106 P3 S0 ; chamber fan off
M106 P2 S0 ; aux fan off
{endif}

;===== heat bed =====
M1002 gcode_claim_action : 2
M140 S[bed_temperature_initial_layer_single] ; set bed temp
M190 S[bed_temperature_initial_layer_single] ; wait for bed temp

; Register lidar for first-layer scan if enabled
{if scan_first_layer}
;=========register first layer scan=====
M977 S1 P60
{endif}

;=============turn on fans to prevent PLA jamming=================
{if filament_type[initial_no_support_extruder]=="PLA"}
    {if (bed_temperature[initial_no_support_extruder] >50)||(bed_temperature_initial_layer[initial_no_support_extruder] >50)}
    M106 P3 S255 ; chamber fan 100%
    {elsif (bed_temperature[initial_no_support_extruder] >45)||(bed_temperature_initial_layer[initial_no_support_extruder] >45)}
    M106 P3 S180 ; chamber fan 70% (PLA anti-jam)
    {endif};Prevent PLA from jamming
    M142 P1 R35 S40
{endif}
M106 P2 S100 ; aux fan on

;===== prepare filament =====
M104 S[nozzle_temperature_initial_layer] ;set extruder temp
G91
G0 Z10 F1200
G90
G28 X
M975 S1 ; vibration suppression on
; Park at wipe area
G1 X60 F12000
G1 Y245
G1 Y265 F3000
M620 M ; enable AMS remap
M620 S[initial_no_support_extruder]A   ; switch material if AMS exist
    M109 S[nozzle_temperature_initial_layer]
    G1 X120 F12000

    ; AMS load: move to front, T-command, return to park
    G1 X20 Y50 F12000
    G1 Y-3
    T[initial_no_support_extruder]
    G1 X54 F12000
    G1 Y265
    M400
M621 S[initial_no_support_extruder]A
M620.1 E F{filament_max_volumetric_speed[initial_no_support_extruder]/2.4053*60} T{nozzle_temperature_range_high[initial_no_support_extruder]}

M412 S1 ; filament runout detection on

; Heat to flush temp (290 for X1E), extrude two stages to prime
M109 S290 ;set nozzle to common flush temp
M106 P1 S0 ; part fan off
G92 E0
G1 E50 F200
M400
M104 S[nozzle_temperature_initial_layer]
G92 E0
G1 E50 F200
M400
M106 P1 S255 ; part fan 100%
G92 E0
G1 E5 F300
M109 S{nozzle_temperature_initial_layer[initial_no_support_extruder]-20} ; drop nozzle temp, make filament shink a bit
G92 E0
G1 E-0.5 F300

; Shake to drop purge blob
G1 X70 F9000
G1 X76 F15000
G1 X65 F15000
G1 X76 F15000
G1 X65 F15000; shake to put down garbage
G1 X80 F6000
G1 X95 F15000
G1 X80 F15000
G1 X165 F15000; wipe and shake
M400
M106 P1 S0 ; part fan off

; Start chamber heating if target >= 40C
;===== set chamber temperature ==========
{if (overall_chamber_temperature >= 40)}
M106 P2 S255 ; open big fan to help heating
M141 S[overall_chamber_temperature] ; Let Chamber begin to heat
{endif}

;===== filament ready =====


;===== wipe nozzle =====
M1002 gcode_claim_action : 14
M975 S1 ; vibration suppression on
; Move to front-edge brush position, first rough wipe
M106 S255
G1 X65 Y230 F18000
G1 Y264 F6000
M109 S{nozzle_temperature_initial_layer[initial_no_support_extruder]-20}
G1 X100 F18000 ; first wipe mouth

; Z-home on exposed steel surface, disable ABL
G0 X135 Y253 F20000  ; move to exposed steel surface edge
G28 Z P0 T300; home z with low precision,permit 300deg temperature
G29.2 S0 ; ABL off
G0 Z5 F20000

; Second multi-pass wipe at purge bucket
G1 X60 Y265
G92 E0
G1 E-0.5 F300 ; retrack more
G1 X100 F5000; second wipe mouth
G1 X70 F15000
G1 X100 F5000
G1 X70 F15000
G1 X100 F5000
G1 X70 F15000
G1 X100 F5000
G1 X70 F15000
G1 X90 F5000
; Descend to steel surface for hard nozzle scrub
G0 X128 Y261 Z-1.5 F20000  ; move to exposed steel surface and stop the nozzle
M104 S140 ; cool nozzle to 140 (safe for bed contact)
M106 S255 ; turn on fan (G28 has turn off fan)

; 7-pass lateral scrub on steel surface (Z-1.01)
M221 S; push soft endstop status
M221 Z0 ;turn off Z axis endstop
G0 Z0.5 F20000
G0 X125 Y259.5 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y262.5
G0 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y260.0
G0 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y262.0
G0 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y260.5
G0 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y261.5
G0 Z-1.01
G0 X131 F211
G0 X124
G0 Z0.5 F20000
G0 X125 Y261.0
G0 Z-1.01
G0 X131 F211
G0 X124
; Circular wipe on steel surface, slow then fast after cool
G0 X128
G2 I0.5 J0 F300
G2 I0.5 J0 F300
G2 I0.5 J0 F300
G2 I0.5 J0 F300

M109 S140 ; wait nozzle temp down to heatbed acceptable
G2 I0.5 J0 F3000
G2 I0.5 J0 F3000
G2 I0.5 J0 F3000
G2 I0.5 J0 F3000

; Restore endstops, lift, move to center, re-enable ABL
M221 R; pop softend status
G1 Z10 F1200
M400
G1 Z10
G1 F30000
G1 X128 Y128
G29.2 S1 ; ABL on
;G28 ; home again after hard wipe mouth
M106 S0 ; turn off fan , too noisy
;===== wipe done =====

; Scanner self-check (T1100/M972)
;===== check scanner =====
G1 X128 Y128 F24000
G28 Z P0
M972 S5 P0
G1 X230 Y15 F24000
;===== scanner check done =====

;===== bed leveling =====
M1002 judge_flag g29_before_print_flag
M622 J1

    M1002 gcode_claim_action : 1
    G29 A X{first_layer_print_min[0]} Y{first_layer_print_min[1]} I{first_layer_print_size[0]} J{first_layer_print_size[1]} ; auto bed level
    M400
    M500 ; save calibration data

M623
;===== bed leveling done =====

;===== home after wipe =====
M1002 judge_flag g29_before_print_flag
M622 J0

    M1002 gcode_claim_action : 13
    G28

M623
;===== homing done =====

M975 S1 ; vibration suppression on

;=============turn on fans to prevent PLA jamming=================
{if filament_type[initial_no_support_extruder]=="PLA"}
    {if (bed_temperature[initial_no_support_extruder] >45)||(bed_temperature_initial_layer[initial_no_support_extruder] >45)}
    M106 P3 S180 ; chamber fan 70% (PLA anti-jam)
    {elsif (bed_temperature[initial_no_support_extruder] >50)||(bed_temperature_initial_layer[initial_no_support_extruder] >50)}
    M106 P3 S255 ; chamber fan 100%
    {endif};Prevent PLA from jamming
    M142 P1 R35 S40
{endif}
M106 P2 S100 ; aux fan on

M104 S{nozzle_temperature_initial_layer[initial_no_support_extruder]} ; set extrude temp earlier, to reduce wait time

;===== vibration check =====
; Y-axis resonance sweep
G1 X128 Y128 Z10 F20000
M400 P200 ; wait 200ms
M970.3 Q1 A7 B30 C80  H15 K0
M974 Q1 S2 P0

; X-axis resonance sweep
G1 X128 Y128 Z10 F20000
M400 P200 ; wait 200ms
M970.3 Q0 A7 B30 C90 Q0 H15 K0
M974 Q0 S2 P0

; Re-home X after vibration check
M975 S1 ; vibration suppression on
G1 F30000
G1 X230 Y15
G28 X ; re-home XY
;===== vibration check =====

; Start lidar bed scan if enabled
{if scan_first_layer}
;start heatbed  scan====================================
M976 S2 P1
G90
G1 X128 Y128 F20000
M976 S3 P2  ;register void printing detection
{endif}

;===== purge line =====
M975 S1 ; vibration suppression on
G90
M83
T1000
G1 X18.0 Y1.0 Z0.8 F18000;Move to start position
M109 S{nozzle_temperature[initial_no_support_extruder]}
G1 Z0.2
; Extrude purge line along front edge
G0 E2 F300
G0 X239 E15 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
G0 Y12 E0.7 F{outer_wall_volumetric_speed/(0.3*0.5)/4* 60}

;===== z-offset per plate type =====
;curr_bed_type={curr_bed_type}
{if curr_bed_type=="Textured PEI Plate"}
G29.1 Z{-0.04} ; z-offset -0.04 for textured PEI
{else}
G29.1 Z{-0.02} ; for other plates
{endif}

; Flow calibration (lidar extrusion cali paint) if enabled
;===== flow calibration paint =====
M1002 judge_flag extrude_cali_flag
M622 J1

    M1002 gcode_claim_action : 8

    T1000

    G0 F1200.0 X231 Y15   Z0.2 E0.741
    G0 F1200.0 X226 Y15   Z0.2 E0.275
    G0 F1200.0 X226 Y8    Z0.2 E0.384
    G0 F1200.0 X216 Y8    Z0.2 E0.549
    G0 F1200.0 X216 Y1.5  Z0.2 E0.357

    G0 X48.0 E12.0 F{outer_wall_volumetric_speed/(0.3*0.5)     * 60}
    G0 X48.0 Y14 E0.92 F1200.0
    G0 X35.0 Y6.0 E1.03 F1200.0

    ;=========== extruder cali extrusion ==================
    T1000
    M83
    {if default_acceleration > 0}
        {if outer_wall_acceleration > 0}
            M204 S[outer_wall_acceleration]
        {else}
            M204 S[default_acceleration]
        {endif}
    {endif}
    G0 X35.000 Y6.000 Z0.300 F30000 E0
    G1 F1500.000 E0.800
    M106 S0 ; turn off fan
    G0 X185.000 E9.35441 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G0 X187 Z0
    G1 F1500.000 E-0.800
    G0 Z1
    G0 X180 Z0.3 F18000

    ; PA cali line 1: K=0.040
    M900 L1000.0 M1.0
    M900 K0.040
    G0 X45.000 F30000
    G0 Y8.000 F30000
    G1 F1500.000 E0.800
    G1 X65.000 E1.24726 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X70.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X75.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X80.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X85.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X90.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X95.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X100.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X105.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X110.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X115.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X120.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X125.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X130.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X135.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X140.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X145.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X150.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X155.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X160.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X165.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X170.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X175.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X180.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 F1500.000 E-0.800
    G1 X183 Z0.15 F30000
    G1 X185
    G1 Z1.0
    G0 Y6.000 F30000 ; move y to clear pos
    G1 Z0.3
    M400

    ; PA cali line 2: K=0.020
    G0 X45.000 F30000
    M900 K0.020
    G0 X45.000 F30000
    G0 Y10.000 F30000
    G1 F1500.000 E0.800
    G1 X65.000 E1.24726 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X70.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X75.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X80.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X85.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X90.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X95.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X100.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X105.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X110.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X115.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X120.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X125.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X130.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X135.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X140.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X145.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X150.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X155.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X160.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X165.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X170.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X175.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X180.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 F1500.000 E-0.800
    G1 X183 Z0.15 F30000
    G1 X185
    G1 Z1.0
    G0 Y6.000 F30000 ; move y to clear pos
    G1 Z0.3
    M400

    ; PA cali line 3: K=0.000
    G0 X45.000 F30000
    M900 K0.000
    G0 X45.000 F30000
    G0 Y12.000 F30000
    G1 F1500.000 E0.800
    G1 X65.000 E1.24726 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X70.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X75.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X80.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X85.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X90.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X95.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X100.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X105.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X110.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X115.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X120.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X125.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X130.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X135.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X140.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X145.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X150.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X155.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X160.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X165.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X170.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X175.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X180.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 F1500.000 E-0.800
    G1 X183 Z0.15 F30000
    G1 X185
    G1 Z1.0
    G0 Y6.000 F30000 ; move y to clear pos
    G1 Z0.3

    G0 X45.000 F30000 ; move to start point

M623 ; end of "draw extrinsic para cali paint"


; Skip cali paint: extend purge line instead
M1002 judge_flag extrude_cali_flag
M622 J0
    G0 X231 Y1.5 F30000
    G0 X18 E14.3 F{outer_wall_volumetric_speed/(0.3*0.5)     * 60}
M623

; Cool nozzle before laser/RGB calibration
M104 S140 ; cool nozzle to 140 (safe for bed contact)


;=========== laser and rgb calibration ===========
; Disable extruder, save settings, initialize scanner
M400
M18 E ; disable extruder motor
M500 R ; save settings

M973 S3 P14

; Horizontal laser auto-exposure (T1100)
G1 X120 Y1.0 Z0.3 F18000.0;Move to first extrude line pos
T1100
G1 X235.0 Y1.0 Z0.3 F18000.0;Move to first extrude line pos
M400 P100 ; wait 100ms
M960 S1 P1 ; laser on
M400 P100 ; wait 100ms
M973 S6 P0; use auto exposure for horizontal laser by xcam
M960 S0 P0

; Vertical laser auto-exposure
G1 X240.0 Y6.0 Z0.3 F18000.0;Move to vertical extrude line pos
M960 S2 P1 ; laser on
M400 P100 ; wait 100ms
M973 S6 P1; use auto exposure for vertical laser by xcam
M960 S0 P0

;=========== handeye calibration ======================
; Hand-eye calibration sequence (lidar + camera, run 1)
M1002 judge_flag extrude_cali_flag
M622 J1

    M973 S3 P1 ; camera start stream
    M400 P500 ; wait 500ms
    M973 S1
    G0 F6000 X228.500 Y4.500 Z0.000
    M960 S0 P1
    M973 S1
    M400 P800
    M971 S6 P0
    M973 S2 P0
    M400 P500 ; wait 500ms
    G0 Z0.000 F12000
    M960 S0 P0
    M960 S1 P1 ; laser on
    G0 X221.00 Y4.50
    M400 P200 ; wait 200ms
    M971 S5 P1
    M973 S2 P1
    M400 P500 ; wait 500ms
    M960 S0 P0
    M960 S2 P1 ; laser on
    G0 X228.5 Y11.0
    M400 P200 ; wait 200ms
    M971 S5 P3
    G0 Z0.500 F12000
    M960 S0 P0
    M960 S2 P1 ; laser on
    G0 X228.5 Y11.0
    M400 P200 ; wait 200ms
    M971 S5 P4
    M973 S2 P0
    M400 P500 ; wait 500ms
    M960 S0 P0
    M960 S1 P1 ; laser on
    G0 X221.00 Y4.50
    M400 P500 ; wait 500ms
    M971 S5 P2
    M963 S1
    M400 P1500
    M964
    ; Hand-eye calibration run 2 (T1100)
    T1100
    G0 F6000 X228.500 Y4.500 Z0.000
    M960 S0 P1
    M973 S1
    M400 P800
    M971 S6 P0
    M973 S2 P0
    M400 P500 ; wait 500ms
    G0 Z0.000 F12000
    M960 S0 P0
    M960 S1 P1 ; laser on
    G0 X221.00 Y4.50
    M400 P200 ; wait 200ms
    M971 S5 P1
    M973 S2 P1
    M400 P500 ; wait 500ms
    M960 S0 P0
    M960 S2 P1 ; laser on
    G0 X228.5 Y11.0
    M400 P200 ; wait 200ms
    M971 S5 P3
    G0 Z0.500 F12000
    M960 S0 P0
    M960 S2 P1 ; laser on
    G0 X228.5 Y11.0
    M400 P200 ; wait 200ms
    M971 S5 P4
    M973 S2 P0
    M400 P500 ; wait 500ms
    M960 S0 P0
    M960 S1 P1 ; laser on
    G0 X221.00 Y4.50
    M400 P500 ; wait 500ms
    M971 S5 P2
    M963 S1
    M400 P1500
    M964
    T1100
    G1 Z3 F3000

    M400
    M500 ; save calibration data

    M104 S{nozzle_temperature[initial_no_support_extruder]} ; rise nozzle temp now ,to reduce temp waiting time.

    ; M969 lidar scan for PA calibration
    T1100
    M400 P400
    M960 S0 P0
    G0 F30000.000 Y10.000 X65.000 Z0.000
    M400 P400
    M960 S1 P1 ; laser on
    M400 P50

    M969 S1 N3 A2000
    G0 F360.000 X181.000 Z0.000
    M980.3 A70.000 B{outer_wall_volumetric_speed/(1.75*1.75/4*3.14)*60/4} C5.000 D{outer_wall_volumetric_speed/(1.75*1.75/4*3.14)*60} E5.000 F175.000 H1.000 I0.000 J0.020 K0.040
    M400 P100 ; wait 100ms
    G0 F20000
    G0 Z1 ; rise nozzle up
    T1000 ; change to nozzle space
    G0 X45.000 Y4.000 F30000 ; move to test line pos
    M969 S0 ; turn off scanning
    M960 S0 P0

    ; Print PA test line, check result, apply K value
    G1 Z2 F20000
    T1000
    G0 X45.000 Y4.000 F30000 E0
    M109 S{nozzle_temperature[initial_no_support_extruder]}
    G0 Z0.3
    G1 F1500.000 E3.600
    G1 X65.000 E1.24726 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X70.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X75.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X80.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X85.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X90.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X95.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X100.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X105.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X110.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X115.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X120.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X125.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X130.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X135.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}

    ; see if extrude cali success, if not ,use default value
    M1002 judge_last_extrude_cali_success
    M622 J0
        M400
        M900 K0.02 M{outer_wall_volumetric_speed/(1.75*1.75/4*3.14)*0.02}
    M623

    G1 X140.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X145.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X150.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X155.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X160.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X165.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X170.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X175.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X180.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X185.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X190.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X195.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X200.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X205.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X210.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X215.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    G1 X220.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)/ 4 * 60}
    G1 X225.000 E0.31181 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
    M973 S4

M623

;===== wait chamber temperature reaching the reference value =======
{if (overall_chamber_temperature >= 40)}
M191 S[overall_chamber_temperature] ; wait for chamber temp
M106 P2 S0 ; aux fan off
{endif}

;===== wait for print temp =====
M1002 gcode_claim_action : 0
; Turn off scanner, wait for final nozzle temp, turn off all fans
M973 S4 ; turn off scanner
M400 ; wait all motion done before implement the emprical L parameters
;M900 L500.0 ; Empirical parameters
M109 S[nozzle_temperature_initial_layer]
M960 S1 P0 ; laser off
M960 S2 P0 ; laser off
M106 S0 ; turn off fan
M106 P2 S0 ; aux fan off
M106 P3 S0 ; chamber fan off

M975 S1 ; vibration suppression on
G90
M83
T1000
;===== purge line to wipe the nozzle ============================
; Final short purge at print temp before first layer
G1 E{-retraction_length[initial_no_support_extruder]} F1800
G1 X18.0 Y2.5 Z0.8 F18000.0;Move to start position
G1 E{retraction_length[initial_no_support_extruder]} F1800
M109 S{nozzle_temperature_initial_layer[initial_no_support_extruder]}
G1 Z0.2
G0 X239 E15 F{outer_wall_volumetric_speed/(0.3*0.5)    * 60}
G0 Y12 E0.7 F{outer_wall_volumetric_speed/(0.3*0.5)/4* 60}
