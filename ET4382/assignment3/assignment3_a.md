# Homework Assignment 3A - Power Stage Design

## Context from Previous Assignments
- LC filter (Assignment 1A): L = 18 μH, C = 820 nF, R = 4 Ω
- f₀ = 41.4 kHz, Q = 0.854, f₋₃dB = 48.66 kHz
- Attenuation @ 1MHz: 55.45 dB
- fPWM = 1 MHz

---

## Overview

Design a Class-D output stage (Lecture 3, slide 6 topology) with:
- NMOS powerFETs (`nld12_g5a_nbl_mac`) in half-bridge: M_H (highside) + M_L (lowside)
- Single +12V power supply (VSUP)
- 5V gate driver supply (VREG)
- CMOS inverter gate drivers (`nmos5v_mac` + `pmos5v_mac`): M_PH/M_NH for highside, M_PL/M_NL for lowside
- vcvs level shifters (simplified bootstrap) for high-side gate drive
- 5ns dead time via ahdlLib logic gates (simplified break-before-make)
- Target: R_ON ≤ 50 mΩ at 150°C

### Reference Circuit (Lecture 3, slide 6)
```
                    V_BST (= vcvs: VPWM + 5V)          V_SUP (+12V)
                      |                                    |
                    M_PH (pmos5v_mac)                     |
                      |                                    |
   off_H ──────────>──┤     ┌─── V_GH ────> gate ──┤ M_H (nld12_g5a_nbl_mac)
                      |     |                       |  drain=VSUP, body diode
   in_H  ──────────>──┤─────┘                       |
                    M_NH (nmos5v_mac)                |
                      |                              |
                   VPWM (= M_H source)        ──────┤── V_PWM output
                                                     |
                    V_REG (+5V)                      |
                      |                              |
                    M_PL (pmos5v_mac)                |
                      |                              |
   off_L ──────────>──┤     ┌─── V_GL ────> gate ──┤ M_L (nld12_g5a_nbl_mac)
                      |     |                       |  drain=VPWM, body diode
   in_L  ──────────>──┤─────┘                       |
                    M_NL (nmos5v_mac)                |
                      |                              |
                     GND (= M_L source)        ─── GND
```

### Dead Time Logic (Break-Before-Make, slide 11)
```
PWM ──┬──> AND ──> in_H    (PWM AND NOT off_H)
      |     ^
      |     └── off_H (from on-off detection / delayed)
      |
      ├──────────> off_H   (immediate: PWM inverted)
      ├──────────> off_L   (immediate: PWM direct)
      |
      └──> NOR ──> in_L    (NOT PWM AND NOT off_L)
              ^
              └── off_L
```
Simplified for 3A: use ahdlLib logic gates with tdel parameter to create 5ns dead time.
- in_H = PWM delayed by 5ns (only goes HIGH 5ns after PWM goes HIGH)
- in_L = NOT(PWM) delayed by 5ns (only goes HIGH 5ns after PWM goes LOW)
- This ensures both FETs are OFF during the 5ns dead time interval.

### Simplified Dead Time Implementation
```
PWM ──> inv (tdel=0) ──> PWM_bar
PWM ──> and2(PWM, PWM_delayed_bar) ──> in_H    ... OR simpler:

Approach: Two non-overlapping signals using buffers with delay
PWM ───> buf (tdel=5ns) ──> in_H_raw ──> AND(PWM, in_H_raw) ──> in_H
PWM_bar ─> buf (tdel=5ns) ──> in_L_raw ──> AND(PWM_bar, in_L_raw) ──> in_L
```

Actually the simplest approach: derive in_H and in_L from PWM using ahdlLib gates:
- in_H: AND gate with inputs PWM and delayed PWM → rising edge delayed by tdel
- in_L: AND gate with inputs PWM_bar and delayed PWM_bar → rising edge delayed by tdel
- off_H = in_L (when lowside turns on, highside must be off) — but with vcvs we skip on-off detection
- off_L = in_H (when highside turns on, lowside must be off)

For the gate drivers (inverters), the control signals drive the inverters:
- When in_H = HIGH → M_NH pulls V_GH LOW (turns OFF M_H)... wait, that's inverted.

**Corrected gate driver logic:**
The gate drivers are CMOS inverters. So:
- in_H HIGH → inverter output LOW → V_GH LOW → M_H OFF
- in_H LOW → inverter output HIGH → V_GH HIGH → M_H ON

This means the control signals are **active-low** for turning ON the powerFET:
- To turn ON M_H: in_H = LOW (inverter drives gate HIGH)
- To turn ON M_L: in_L = LOW (inverter drives gate HIGH)

But looking at slide 6 more carefully: in_H connects to the NMOS of the gate driver (M_NH), and off_H connects to some detection circuit. The topology has separate on/off control paths.

**For our simplified implementation:** We just need two non-overlapping gate drive signals:
- VGH: goes 0→5V (relative to VPWM) to turn ON M_H, 5V→0 to turn OFF
- VGL: goes 0→5V (relative to GND) to turn ON M_L, 5V→0 to turn OFF
- Dead time = interval where BOTH VGH and VGL are LOW (both FETs off)

**Simplest implementation with vcvs + ahdlLib:**
1. PWM signal (0/5V) → ahdlLib logic gates generate two non-overlapping signals
2. Signal for lowside drives gate driver inverter for M_L → VGL
3. Signal for highside → vcvs level-shifts to VPWM-referenced domain → drives gate driver inverter for M_H → VGH

---

## Part 1: PowerFET Sizing

### Device: nld12_g5a_nbl_mac (tsmc018)
- 12V LDMOS NMOS from TSMC 0.18μm BCD process
- Asymmetric HV-MOSFET: deep N-well drift region shields gate oxide from high drain voltage
- Body always connected to source → built-in body diode (source-drain)
- Gate oxide rated for 5V (VGS_max = VREG = 5V)
- Need to find W (total gate width) or number of fingers for R_ON ≤ 50 mΩ at 150°C

### R_ON Measurement Setup (DC Simulation)
Per tutorial slide 3: R = V/I with FET fully ON, usually V = 100mV
- VGS = 5V (fully ON, gate driven by VREG)
- VDS = 100 mV (deep linear region)
- Temperature = 150°C (R_ON increases with temperature due to mobility degradation)
- R_ON = VDS / ID = 0.1V / ID

### Calculation Approach
1. Place single nld12_g5a_nbl_mac: gate to VGS=5V, drain to VDS=100mV, source to GND
2. DC simulation at T=150°C, measure ID
3. R_ON_single = 0.1 / ID
4. Number of fingers needed: N = ceil(R_ON_single / 0.05)
5. Verify with N fingers: R_ON_final = R_ON_single / N ≤ 50 mΩ

### Simulation Results

| Parameter | Value |
|-----------|-------|
| Device | nld12_g5a_nbl_mac |
| VGS | 5V |
| VDS | 100 mV |
| Temperature | 150°C |
| Single-finger R_ON | ___ Ω |
| Fingers needed | ___ |
| Final R_ON | ___ mΩ |
| Total gate width (W) | ___ μm |

### Screenshots
- `part1_ron_setup.png` — DC simulation schematic for R_ON measurement
- `part1_ron_result.png` — ID at VDS=100mV confirming R_ON

---

## Part 2: Gate Charge Q_G and Threshold Voltage V_TH

### V_TH Extraction
- DC sweep: VGS from 0V to 5V, VDS = 100mV, T = 27°C (or 150°C)
- V_TH = VGS where ID just starts flowing (extrapolation method or fixed current criterion)

### Q_G Measurement Setup (Transient Simulation)
Per tutorial slide 4: C_GS and C_GD are nonlinear → must simulate with Miller effect
- PowerFET in half-bridge context: drain connected to VSUP through load, source to GND
- Drive gate with voltage step: 0V → 5V (through a current source or resistor)
- Measure gate current I_G over time
- Q_G = ∫ I_G dt (use `integ` or `iinteg` function in calculator)

### Gate Charge Theory (Lecture 3)
- Q_GL (low-side) = C_GSL × (VREG + VSUP) + C_GDL × (VREG + 3×VSUP)
  - The 3×VSUP term: C_GD sees full output swing (2×VSUP for SE, VSUP for single supply) plus gate swing (VREG)
  - For our single-supply +12V: C_GDL sees VREG + VSUP during turn-on (Miller plateau at VSUP swing)
- Q_GH = Q_GL (symmetric NMOS devices)
- Gate charge power: P_Q = fPWM × 2 × VSUP × (Q_GL + Q_GH)
  - Factor 2×VSUP because charge comes from VSUP rail through VREG regulator

### Simulation Results

| Parameter | Value |
|-----------|-------|
| V_TH | ___ V |
| Q_G (total gate charge) | ___ nC |

### Screenshots
- `part2_qg_waveform.png` — Gate voltage and gate current vs time showing Miller plateau
- `part2_vth_sweep.png` — VGS vs ID for V_TH extraction

---

## Part 3: Gate Driver Sizing

### Devices: nmos5v_mac + pmos5v_mac (tsmc018)
- CMOS inverter topology (per Lecture 3 slide 6)
- Supply: VREG = 5V (lowside) / VBST (highside, = VPWM + 5V via vcvs)
- Target: rise and fall time ≈ 25 ns at powerFET gate
- Must avoid shoot-through in the inverter AND in the power stage

### Shoot-Through Prevention (Lecture 3, slides 10/15)
- During VPWM transition: dVPWM/dt couples through C_GD of the OFF powerFET
- This capacitive coupling tries to turn the OFF device back ON → shoot-through
- Solution: skew the gate driver inverter: W_NMOS >> W_PMOS
  - Strong pull-down keeps gate below V_TH during capacitive pull-up
  - Asymmetric: fast turn-OFF (NMOS), slower turn-ON (PMOS)

### Sizing Approach
1. Gate driver must charge/discharge powerFET gate (Q_G) in ~25 ns
2. Required average current: I_avg = Q_G / t_rise
3. Size M_NL/M_NH (nmos5v_mac) for pull-down: determines fall time of VG
4. Size M_PL/M_PH (pmos5v_mac) for pull-up: determines rise time of VG
5. Skew: W_N > W_P to prevent shoot-through from C_GD coupling
6. Iterate in simulation until rise ≈ fall ≈ 25 ns AND no shoot-through

### Simulation Results

| Parameter | Value |
|-----------|-------|
| NMOS driver (M_NH, M_NL) W/L | ___ μm / ___ μm |
| PMOS driver (M_PH, M_PL) W/L | ___ μm / ___ μm |
| Rise time (VG: 0→5V) | ___ ns |
| Fall time (VG: 5V→0) | ___ ns |
| Shoot-through | None / ___ |

### Screenshots
- `part3_driver_schematic.png` — Gate driver inverter + powerFET gate load
- `part3_driver_waveforms.png` — Input, VG output, rise/fall time measurement

---

## Part 4: Dead Time Generation & Level Shifting

### Dead Time Logic (5 ns, ahdlLib)
- PWM input (0/5V, 1 MHz) → generate non-overlapping gate drive signals
- Use ahdlLib logic gates with tdel (propagation delay) parameter

**Implementation approach:**
```
PWM ──────────────────────────────── inv (tdel=0) ──> PWM_bar

For lowside (M_L turns ON when PWM=LOW):
  PWM_bar ──> buf/inv_inv (tdel=5ns) ──> PWM_bar_delayed
  AND(PWM_bar, PWM_bar_delayed) ──> drive_L
  Rising edge of drive_L delayed by 5ns after PWM goes LOW

For highside (M_H turns ON when PWM=HIGH):
  PWM ──> buf (tdel=5ns) ──> PWM_delayed
  AND(PWM, PWM_delayed) ──> drive_H
  Rising edge of drive_H delayed by 5ns after PWM goes HIGH
```

This creates 5ns dead time on every transition: after one side turns OFF, there's a 5ns gap before the other side turns ON.

### Logic Gate Parameters (ahdlLib)
| Parameter | Value |
|-----------|-------|
| sigout_high | 5V |
| sigout_low | 0V |
| tdel (delay gates) | 5 ns |
| trise, tfall | 1 ns (fast) |

### Level Shifter (vcvs from analogLib)
- **Lowside:** drive_L signal (0-5V, GND-referenced) directly drives the lowside gate driver inverter. No level shifting needed.
- **Highside:** drive_H signal (0-5V, GND-referenced) must be shifted to VPWM-referenced domain.
  - vcvs with gain = 1: output+ referenced to VPWM (M_H source)
  - Input: drive_H (0-5V relative to GND)
  - Output: 0-5V relative to VPWM → drives highside gate driver inverter
  - vcvs acts as ideal floating voltage source tracking VPWM

### Note on Gate Driver Inverter Polarity
- drive_H = HIGH → gate driver inverter output = LOW → VGH = VPWM (M_H OFF)
- drive_H = LOW → gate driver inverter output = HIGH → VGH = VPWM + 5V (M_H ON)

Wait — this is inverted. We want drive_H HIGH to turn M_H ON. Two options:
1. Add another inverter in the chain (extra delay)
2. Use the drive signal directly to the gate (bypass inverter, use vcvs output as VGH directly)

**Simplest approach for the assignment:** Use vcvs to directly generate the gate voltage:
- For lowside: vcvs output = drive_L_inverted × 5V referenced to GND → VGL
- For highside: vcvs output = drive_H_inverted × 5V referenced to VPWM → VGH

Or even simpler: let the ahdlLib gates produce the correct polarity and use vcvs as ideal gate drivers (gain=1 voltage followers from the logic domain to the floating gate domain).

### Simulation Results

| Parameter | Value |
|-----------|-------|
| Dead time (measured) | ___ ns |
| High-side VGH swing | VPWM to VPWM + 5V |
| Low-side VGL swing | 0V to 5V |

### Screenshots
- `part4_deadtime_schematic.png` — Dead time logic + level shifters + gate driver inverters
- `part4_deadtime_waveforms.png` — PWM, drive_H, drive_L, VGH, VGL, VPWM

---

## Part 5: Complete Half-Bridge Verification (±2A Load)

### Test Setup
- VSUP = +12V (vdc, analogLib), VREG = 5V (vdc, analogLib)
- PWM input: vpulse at 1 MHz, 50% duty cycle, 0-5V
- Load: idc current source = ±2A (test both polarities separately)
- Transient simulation, several PWM cycles

### What to Verify
1. **VPWM switches between 0V and +12V** (clean square wave)
2. **No shoot-through:** supply current should not spike during transitions
3. **Dead time visible:** brief high-Z interval in VPWM where body diode conducts
4. **Correct gate waveforms:** VGH and VGL are non-overlapping, proper 0-5V swing
5. **+2A load (current flowing OUT of VPWM):** soft switching — output current assists falling edge, body diode conducts AFTER transition
6. **-2A load (current flowing IN to VPWM):** hard switching — output current resists falling edge, body diode conducts DURING deadtime, reverse recovery

### Switching Dynamics Summary (Lecture 3)

| | Soft Switching (+2A out) | Hard Switching (-2A in) |
|---|---|---|
| Output current | Assists transition | Resists transition |
| dVPWM/dt | Faster | Slower |
| Body diode | After transition | During deadtime (before) |
| Reverse recovery | No | Yes |

### Simulation Results

| Parameter | +2A Load | -2A Load |
|-----------|----------|----------|
| VPWM high level | ___ V | ___ V |
| VPWM low level | ___ V | ___ V |
| Rise time (VPWM) | ___ ns | ___ ns |
| Fall time (VPWM) | ___ ns | ___ ns |
| Dead time (measured) | ___ ns | ___ ns |
| Shoot-through | None / ___ | None / ___ |

### Screenshots
- `part5_halfbridge_schematic.png` — Complete half-bridge
- `part5_waveforms_2A.png` — VPWM, VGH, VGL, I_SUP with +2A load
- `part5_waveforms_neg2A.png` — Same with -2A load

---

## Part 6: BTL Configuration with LC Filter

### Circuit Description
- Two identical half-bridges (Bridge-Tied Load)
- Each drives one end of the load through an LC filter
- LC filter: L = 18 μH, C = 820 nF (from Assignment 1A)
- Load: R = 4 Ω connected between the two filter outputs

### BTL Topology
```
         Half-Bridge A                              Half-Bridge B
         VSUP (+12V)                                VSUP (+12V)
           |                                          |
          M_AH                                      M_BH
           |                                          |
          VPWM_A ─── L_A ─── C_A ──┬── R=4Ω ──┬── C_B ─── L_B ─── VPWM_B
                                    |           |
                                   GND         GND
           |                                          |
          M_AL                                      M_BL
           |                                          |
          GND                                        GND
```

### AD-PWM Generation (fPWM = 1 MHz)
- **AD-PWM:** P-side and M-side use inverted PWM signals
  - Half-bridge A (P): comparator(Vsig, Vtri) → PWM_A
  - Half-bridge B (M): comparator(-Vsig, Vtri) → PWM_B = inverted PWM_A
  - Use comparator from ahdlLib + triangle carrier (vpulse) at 1 MHz
  - Signal: vdc with amplitude = mi × Vtri_peak (modulation index)

Or simpler: use vpulse for PWM_A, and inv gate for PWM_B.

### Output at Zero Modulation Index (mi = 0)
- Both sides at 50% duty cycle, inverted from each other
- **Differential mode (DM):** VPWM_A - VPWM_B after LC filter
  - AD-PWM: both sides switch simultaneously but in opposite direction
  - DM output should be ~0V with small dead-time-related ripple
  - LC filter attenuates the PWM switching frequency content
- **Common mode (CM):** (VPWM_A + VPWM_B) / 2 after LC filter
  - AD-PWM at mi=0: CM = constant = VSUP/2 = 6V
  - Key property of AD-PWM: CM is signal-independent (unlike BD-PWM)

### Efficiency Calculation
From Lecture 3, total loss = P_R + P_Q + P_X:

**P_R (conduction loss):**
- P_R_sig = P_OUT × R_ON / R_LOAD (signal current)
- P_R_rip = (1/3) × (VSUP / (8 × L × fPWM))² × R_ON (ripple current)
- Two FETs conduct at any time (one per half-bridge)

**P_Q (gate charge loss):**
- P_Q = fPWM × 2 × VSUP × (Q_GL + Q_GH) per half-bridge
- ×2 for BTL (both half-bridges)
- **Don't forget gate driver CMOS inverter self-consumption** (short-circuit current during transitions)

**P_X (transition/switching loss):**
- P_X = fPWM × t_x × VSUP × (I_OUT + I_RR) — only during hard switching

**Simulation approach:**
- η = P_load / (P_VSUP + P_VREG)
- P_VSUP = VSUP × average(I_VSUP)
- P_VREG = VREG × average(I_VREG)  ← gate driver current!
- P_load = average(V_diff × I_load) or V_out_rms² / R

### Modulation Index Sweep
- Parametric sweep: `mi` from 0 to 0.9 (or 0.95)
- PWM generation: comparator + triangle at 1 MHz
  - Vtri: vpulse, V1=-1, V2=+1, Rise=499n, Fall=499n, Period=1u
  - Vsig_A: vdc = mi (or sine for AC test)
  - Vsig_B: vdc = -mi
  - Comparator A: sig > tri → HIGH (+12V side) / LOW (0V side)
  - Comparator B: -sig > tri → inverted

### Simulation Results

| mi | P_load (W) | P_SUP (W) | P_REG (W) | η (%) |
|----|------------|-----------|-----------|-------|
| 0.0 | ___ | ___ | ___ | ___ |
| 0.1 | ___ | ___ | ___ | ___ |
| 0.2 | ___ | ___ | ___ | ___ |
| 0.3 | ___ | ___ | ___ | ___ |
| 0.4 | ___ | ___ | ___ | ___ |
| 0.5 | ___ | ___ | ___ | ___ |
| 0.6 | ___ | ___ | ___ | ___ |
| 0.7 | ___ | ___ | ___ | ___ |
| 0.8 | ___ | ___ | ___ | ___ |
| 0.9 | ___ | ___ | ___ | ___ |

### Screenshots
- `part6_btl_schematic.png` — Full BTL schematic with LC filters
- `part6_dm_cm_mi0.png` — DM and CM output voltage after LC filter at mi = 0
- `part6_efficiency_vs_mi.png` — Efficiency vs modulation index

---

## Part 7: 4× Gate Driver Size

### Changes
- Multiply BOTH NMOS and PMOS driver widths by 4:
  - W_N_new = 4 × W_N_original
  - W_P_new = 4 × W_P_original
- Keep everything else the same (powerFET size, dead time, etc.)

### Expected Effects (from Lecture 3 power loss theory)

**Faster switching → lower P_X:**
- 4× driver current → ~4× faster VPWM transitions
- t_x decreases → P_X = fPWM × t_x × VSUP × I decreases

**Higher gate drive power → higher P_Q:**
- 4× larger driver = 4× more gate capacitance on the driver transistors themselves
- VREG must supply more current to charge/discharge the driver gates
- P_Q increases (but note: powerFET Q_G stays the same, only the pre-driver stage changes)

**Conduction loss P_R unchanged:**
- Same powerFET size → same R_ON → same P_R

**Net effect on efficiency:**
- At **low mi** (small load current): P_Q dominates → η likely **decreases** (more driver loss, little switching loss to save)
- At **high mi** (large load current): P_X dominates → η likely **increases** (reduced switching loss outweighs extra driver loss)
- **Crossover point** where 4× driver becomes beneficial

### Simulation Results

| mi | η_1× (%) | η_4× (%) | Δη (%) |
|----|----------|----------|--------|
| 0.0 | ___ | ___ | ___ |
| 0.1 | ___ | ___ | ___ |
| 0.2 | ___ | ___ | ___ |
| 0.3 | ___ | ___ | ___ |
| 0.4 | ___ | ___ | ___ |
| 0.5 | ___ | ___ | ___ |
| 0.6 | ___ | ___ | ___ |
| 0.7 | ___ | ___ | ___ |
| 0.8 | ___ | ___ | ___ |
| 0.9 | ___ | ___ | ___ |

### Screenshots
- `part7_efficiency_comparison.png` — Efficiency vs mi: 1× vs 4× driver overlay

---

## Simulation Settings
- Analysis: Transient
  - Half-bridge verification: stop = 5-10 μs
  - BTL with LC filter + efficiency: stop = 5-10 μs (few PWM cycles, measure average)
- Accuracy: conservative
- **maxstep = 10 ns** (critical for 1 MHz PWM)
- Temperature: **150°C for R_ON measurement only**, 27°C for all other simulations
- DC simulation for R_ON: VDS = 100mV, VGS = 5V, T = 150°C
- DC sweep for V_TH: VGS from 0 to 5V
- Parametric sweep for efficiency: `mi` from 0 to 0.9

## Cadence Components Summary

| Component | Library | Cell | Key Parameters |
|-----------|---------|------|----------------|
| PowerFET (M_H, M_L) | tsmc018 | nld12_g5a_nbl_mac | W=___, nf=___ |
| NMOS driver (M_NH, M_NL) | tsmc018 | nmos5v_mac | W=___, L=___ μm |
| PMOS driver (M_PH, M_PL) | tsmc018 | pmos5v_mac | W=___, L=___ μm |
| Level shifter (highside) | analogLib | vcvs | gain=1 |
| Logic gates (dead time) | ahdlLib | and2 / inv / buf | tdel=5ns, sigout_high=5, sigout_low=0 |
| Power supply | analogLib | vdc | 12V (VSUP) |
| Gate driver supply | analogLib | vdc | 5V (VREG) |
| LC filter | analogLib | ind + cap | L=18μH, C=820nF |
| Load | analogLib | res | 4 Ω |
| PWM generator | analogLib | vpulse (or comparator+triangle) | fPWM=1MHz |
| Load current (verification) | analogLib | idc | ±2A |
