# Assignment 3A - Speech Notes

## Slide 1 - Title
- Assignment 3A, Power Stage Design, Class-D amplifier
- TSMC 0.18um BCD process

## Slide 2 - Circuit Overview (OutputStage.png)
- NMOS half-bridge: two power FETs (M4 high-side, M5 low-side) between 12V and GND
- Each FET has a CMOS gate driver (PMOS + NMOS inverter)
- High-side needs level shifter because its source floats at sw node - gate must be sw+5V not just 5V
- Non-overlap generator (NAND + NOT) creates dead time between O+ and O-

## Slide 3 - Part 1 Section
- Goal: R_ON <= 50 mOhm at 150C worst case

## Slide 4 - Part 1 Text
- R_ON = V_DS/I_D = 100mV/I_D
- 150C is worst case: higher temp = higher R_ON (more phonon scattering)
- Result: 400 fingers, W=103mm, R_ON = 50.02 mOhm
- Conduction loss per FET: P = I^2 x R_ON = 4 x 0.05 = 200mW

## Slide 5 - Part 1 Image (50mOhm_Ron.png)
- Top: I_D linear with width in linear region
- Bottom: R_ON drops as 1/W
- Marker at 103mm where R_ON = 50 mOhm

## Slide 6 - Part 2 Section
- Characterize V_TH and Q_G of the sized FET

## Slide 7 - Part 2 Text
- V_TH = 0.75V, matters for shoot-through analysis
- Q_G = 1.247nC, determines gate driver power: P_Q = f_SW x 2 x V_SUP x Q_G
- P_Q is constant, independent of output power

## Slide 8 - V_TH (Vth_extraction.png)
- DC sweep V_GS 0-5V, current onset at 0.75V

## Slide 9 - Gate Charge (GateCharge.png)
- Gate current peaks ~450mA
- Integrated charge = 1.247nC
- Miller plateau visible: flat region where C_GD charges as drain collapses
- Drain drops from 20V to ~0V

## Slide 10 - Part 3 Section
- Size gate drivers for target rise/fall times

## Slide 11 - Part 3 Text
- I_avg = Q_G/t_rise = 1.247nC/25ns = 50mA needed
- Skewed: NMOS 4x wider than PMOS
- Fast turn-OFF (2.6ns) prevents shoot-through
- Slow turn-ON (19ns) is OK, dead time gives margin

## Slide 12 - Rise Time (RiseTime.png)
- Vgl 0 to 5V in 19.19ns, weak PMOS pull-up
- Within 25ns target

## Slide 13 - Fall Time (FallTime.png)
- VgsH 5V to 0V in 2.61ns, strong NMOS pull-down
- 7x faster than rise, intentional asymmetry

## Slide 14 - Part 4 Section
- Verify dead time

## Slide 15 - Part 4 Text
- 5ns break-before-make gap
- O- falls first, then 5ns later O+ rises
- Both FETs OFF during gap, prevents shoot-through

## Slide 16 - Dead Time (Deadtime.png)
- Markers show 5.04ns between transitions
- Clean non-overlapping signals

## Slide 17 - Part 5 Section
- Full verification at +/-2A

## Slide 18 - Part 5 Text
- Soft (+2A): load assists transition, clean VgsH
- Hard (-2A): load opposes, C_GD coupling pushes VgsH up to ~3V
- I_GD = C_GD x dV_sw/dt
- Skewed driver clamps it back down, no shoot-through

## Slide 19 - All Signals +2A (a3a_p1_all.png)
- Clean Vsw 0-12V, proper VgsH/VgsL alternation
- No supply current overlap

## Slide 20 - All Signals -2A (a3a_p1_all_neg2A.png)
- VgsH rises to ~3V during dead time from C_GD coupling
- Duration too short for significant shoot-through current

## Slide 21 - Vsw Zoomed
- Clean -1V to 12V transition
- -1V is body diode forward voltage during dead time
- No ringing

## Slide 22 - Shoot-Through Check
- ~2.79A spike lasting ~5ns is capacitive C_oss charging, not shoot-through
- Settles cleanly to load current after

## Slide 23 - Load Current
- Initial inrush to ~3.2A, settles to 2A
- Normal startup behavior

## Slide 24 - Part 6 Section
- BTL with LC filter

## Slide 25 - Part 6 BTL Text
- Single half-bridge has 6V DC offset, BTL cancels it differentially
- AD-PWM: swap O+/O- on bridge B so when A=HIGH, B=LOW
- Gives constant V_cm = V_SUP/2 regardless of signal
- LC filter: f_0 = 1/(2pi sqrt(18u x 820n)) = 41.4kHz, blocks 1MHz switching

## Slide 26 - BTL Schematic (btl_schematic.png)
- Two half-bridges, bridge B has swapped O+/O-
- LC filter on each side, 4 Ohm load between outputs

## Slide 27 - BTL Settling (btl_mi0_settling.png)
- sw_A and sw_B inverted square waves
- Outputs settle to ~6V after ~40us
- V_diff settles to ~0V, V_cm steady at 6V

## Slide 28 - BTL Settled (btl_mi0_settled.png)
- V_diff = -24.5mV (essentially zero at mi=0)
- V_cm = 6.0V constant, confirms AD-PWM working

## Slide 29 - Efficiency Text
- Replaced vpulse with comparator: triangle carrier vs DC level (mi)
- eta = P_load / (P_sup + P_reg)
- Losses: conduction (grows with mi), gate charge (constant), switching
- Swept mi = 0 to 0.9

## Slide 30 - PWM Input Stage
- Triangle 1MHz (-1V to +1V), DC = mi, comparator outputs 0/5V PWM
- Variable duty cycle feeds non-overlap generator

## Slide 31 - Efficiency vs mi 1x
- P_reg ~20mW constant, confirms gate loss is signal-independent
- Efficiency poor at low mi (fixed losses dominate)
- Increases at high mi as P_load grows faster than losses

## Slide 32 - Part 7 Section
- Compare 1x vs 4x driver sizes

## Slide 33 - Part 7 Text
- Tradeoff: bigger driver = less P_X (faster switching) but more P_Q (more gate cap)
- 4x: pmos_w=12u, nmos_w=48u
- Result: nearly identical to 1x
- Ideal vcvs and ahdlLib gates don't model real capacitive loading

## Slide 34 - Efficiency vs mi 4x
- Same shape as 1x, P_reg only 0.3mW higher

## Slide 35 - 1x vs 4x Table
- P_reg nearly identical, P_load identical
- Real silicon would show bigger difference

## Slide 36 - Summary
- R_ON=50mOhm, V_TH=0.75V, Q_G=1.247nC
- Skewed driver: 19ns rise / 2.6ns fall, 5ns dead time
- No shoot-through at +/-2A
- BTL removes DC offset, AD-PWM gives constant V_cm
- 1x vs 4x masked by ideal components
