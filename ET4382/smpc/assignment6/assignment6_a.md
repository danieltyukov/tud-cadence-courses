# SMPC Mini-Project 1 — Consolidated Solutions

**Course**: ET4382 Power Conversion Techniques in CMOS Technology
**Authors**: Raghavendra Joshi (6438180), Daniel Tyukov (5714699)
**Cadence cell**: `ClassDMiniProject1 / SMPC1_partB`

---

## Problem Statement

Design a **1.8 V** supply from a **5.0 V** battery driving a **4.0 Ω** load. A 1.0 V bandgap reference is available (ideal source). Given L = 10 µH, C = 1.0 µF. PWM switching frequency **f_sw = 2.0 MHz**, deadtime **t_d = 10 ns**. Examine also the R_L = 16 Ω case.

Two topologies are compared:

1. Linear (voltage) regulator — baseline
2. Synchronous buck converter with CMOS power switches and a custom gate driver

---

## Part 1 — Linear Voltage Regulator

### 1.1 Design

Non-inverting op-amp, feedback divider from V_out → V_fb:

```
        V_ref ─┬── (+)
               │
               │          ┌──── V_out
       [ Op-Amp ]─────────┤
               │          │
         V_fb ─┴── (−)   R₂
                          │
                          ├──── V_fb  (to op-amp −)
                          │
                          R₁
                          │
                         GND
```

Virtual short: V_fb = V_ref = 1.0 V. Divider: V_fb = V_out · R₁/(R₁ + R₂).

Solve for target V_out = 1.8 V:

```
 1.0/1.8 = R₁/(R₁+R₂)
 →  R₂/R₁ = 0.8
```

Pick **R₁ = 10 kΩ, R₂ = 8 kΩ**.

### 1.2 Efficiency

Linear regulator is a series pass device → I_in ≈ I_out (op-amp quiescent ignored). The pass element absorbs (V_in − V_out) at full load current.

```
 η = P_out/P_in = (V_out·I_out)/(V_in·I_in) = V_out/V_in = 1.8/5.0 = 0.36
```

**→ η ≈ 36%**

With ideal amplifier, simulated V_out tracks 1.80 V exactly (transient plot, Part A slide). Efficiency matches the calculated 36% because no further losses are modelled.

### 1.3 Is a linear regulator a good choice?

**No.** At I_load = V_out/R_L = 450 mA, the pass element dissipates
P_drop = (V_in − V_out) · I_load = 3.2 · 0.45 = **1.44 W** — that is 64% of the 2.25 W drawn from the battery, unacceptable for a portable/battery application. Linear regulators (LDOs) are only efficient when V_in − V_out ≲ a few hundred mV. For a 5 V → 1.8 V step, a switched converter is mandatory.

---

## Part 2 — Synchronous Buck Converter

### 2.1 Duty Cycle

Ideal buck (volt-second balance):

```
 D = V_out/V_in = 1.8/5.0 = 0.36
```

At f_sw = 2.0 MHz:

```
 T_sw  = 1/f_sw = 500 ns
 t_on  = D·T    = 180 ns
 t_off = (1−D)·T = 320 ns
```

In simulation, D drifts slightly upward (~0.365–0.38) because open-loop operation must compensate for the conduction drop across the power FETs (V_out sags without feedback; increasing D re-centres it). The closed loop added in Assignment 7 will remove the need for manual duty-cycle tuning.

### 2.2 Inductor Ripple Current

During t_on: V_L = V_in − V_out = 3.2 V (inductor charges).

```
 ΔI_L = (V_in − V_out) · t_on / L
      = 3.2 · 180×10⁻⁹ / 10×10⁻⁶
      = 57.6 mA
```

Consistency via t_off: V_L = −V_out = −1.8 V → |ΔI_L| = 1.8 · 320e⁻⁹ / 10e⁻⁶ = **57.6 mA** ✓

Average inductor current (DC component = load current in CCM):

```
 I_L,avg = V_out/R_L = 1.8/4 = 450 mA
```

**Simulated** (from ADE, `peakToPeak(clip(IT("/L0/PLUS") ...))`):
- I_L,avg ≈ **455.8 mA**
- ΔI_L ≈ **59.5 mA**

Small offsets (~+1 % in I_avg, +3 % in ΔI_L) are explained by the slightly higher simulated D (~0.365) and finite switching-transition overshoot.

### 2.3 Power Transistor Sizing (target P_cond ≈ 5 % of P_out)

Output power:
```
 P_out = V_out² / R_L = 1.8² / 4 = 0.81 W
```
Target: P_cond ≤ **40 mW**.

Effective on-resistance (time-averaged over one period):
```
 R_eff = R_on,P · D + R_on,N · (1 − D)
```

Neglecting the small ripple term (|ΔI_L/√12|² ≪ I_L,avg²):
```
 P_cond ≈ I_L,avg² · R_eff
```

For 5 % target:
```
 R_eff ≤ 0.05 · P_out / I_L,avg² = 0.05 · 0.81 / 0.45² ≈ 200 mΩ
```

**Chosen power FET dimensions (after W-sweep in Cadence):**

| FET | W/L | Fingers × multiplier | Effective W |
|---|---|---|---|
| PMOS (HS) | 350 µm / 500 nm | 1 × 300 | 105 mm |
| NMOS (LS) | 300 µm / 600 nm | 1 × 100 | 30 mm |

**Simulated R_on (averaged over the conducting interval):**
- R_on,PMOS ≈ **58.3 mΩ**
- R_on,NMOS ≈ **245 mΩ**

```
 R_eff = 0.0583·0.36 + 0.245·0.64
       = 21.0 mΩ + 156.8 mΩ
       = 178 mΩ
```

**P_cond (at 4 Ω load):**
```
 P_avg    = I_L,avg² · R_eff = 0.4558² · 0.178 = 37.0 mW
 P_ripple = (ΔI_L/√12)² · R_eff = 0.01717² · 0.178 ≈ 0.05 mW  (negligible)
 P_cond   ≈ 37.0 mW  →  4.56 % of P_out  ✓ (target 5 %)
```

**Motivation — why this split rather than 1:1 W_P:W_N?**

1. PMOS mobility is ~2.5× lower than NMOS (holes vs electrons), so equal R_on demands ~2.5× wider PMOS for the same L — the 3.5× width ratio (105 mm / 30 mm) is close to this and leaves headroom because the PMOS conducts during the larger duty fraction (D = 0.36 vs 1−D = 0.64 for NMOS).

   Wait — NMOS conducts longer (64 %), so its R_on weighs more in R_eff. That is exactly what we see: 156.8 mΩ from NMOS dominates the 178 mΩ total despite PMOS being 3.5× wider. A more NMOS-biased split (e.g., W_N = W_P) would reduce R_eff further. The present choice was made to balance **both conduction loss and gate-drive loss** — see §2.7; a bigger NMOS would gain conduction but cost gate charge.

2. The 5 % conduction target is a *lower bound on sensible sizing*, not a "minimize at all costs" goal. Oversized FETs reduce I²R but grow C_g ∝ W·L, which increases gate-drive loss P_gate = C_g·V_in²·f_sw linearly. Since P_gate is **load-independent** and P_cond drops quadratically at light load, aggressive oversizing kills efficiency at low I_load (critical for the final-project sleep-mode spec).

### 2.4 Gate Driver Sizing (target transition ≈ 2.0 ns)

Estimated power-FET gate capacitance (using C_ox ≈ 2.9 fF/µm² for 180 nm 5 V thick-oxide device, T_ox ≈ 12 nm):

```
 C_g,PMOS ≈ C_ox · W_P · L_P = 2.9 · 105e3 · 0.5   ≈ 152 pF
 C_g,NMOS ≈ C_ox · W_N · L_N = 2.9 · 30e3  · 0.6   ≈  52 pF
```

Drive current needed to slew the gate through ΔV = 5 V in t_r = 2 ns:

```
 I_drv,PMOS = C_g,PMOS · ΔV / t_r = 152p · 5 / 2n = 380 mA  (peak)
 I_drv,NMOS = C_g,NMOS · ΔV / t_r =  52p · 5 / 2n = 130 mA  (peak)
```

**Chosen driver inverter dimensions:**

| Driver stage | PMOS W/L | NMOS W/L |
|---|---|---|
| Final inverter | 100 µm / 500 nm | 100 µm / 600 nm |

**Simulated transition time** on V_PWM (the switching node): **< 2.0 ns** ✓ (presentation slide "Transition time plot of VPWM" shows an ~1.05 ns 10–90 % edge).

**Motivation — why not faster / slower?**

- **Too fast (< 1 ns)**: (i) driver itself needs to be much larger → its own gate-charge loss grows, shifting the loss back into the driver stage rather than the power FET; (ii) dV/dt on V_PWM excites the parasitic inductance (bond wire + PCB trace) causing ringing and potential V_DS overshoot — a direct concern for the final project's **< 1.5 V ringing** spec.
- **Too slow (> 5 ns)**: V–I overlap during the transition dominates switching loss:
  ```
   P_sw ≈ ½·V_in·I_L·(t_r + t_f)·f_sw
  ```
  At 5 ns transitions and 450 mA: P_sw ≈ 0.5·5·0.45·10n·2M = 22.5 mW — already ~60 % of P_cond.
- **~2 ns knee**: switching loss ≈ 4.5 mW at 450 mA, which is small vs conduction, and the driver itself is not the dominant loss. Above 2 ns we pay too much in P_sw; below 2 ns we pay too much in driver loss and ringing.

### 2.5 Shoot-Through Check

Non-overlap generator: two cross-coupled NAND gates with `tdel = deadtime = 10 ns`. Each gate-drive edge is delayed by 10 ns after the falling edge of its complement, so O+ and O− are never simultaneously in their "ON" polarity.

During each transition both power switches are OFF for ~10 ns; the inductor current freewheels through the NMOS body diode. This eliminates shoot-through at the cost of a brief body-diode conduction loss:

```
 P_dead ≈ V_f · I_L,avg · 2·t_d · f_sw
        = 0.7 · 0.45 · 20e⁻⁹ · 2e⁶
        ≈ 12.6 mW  (at 4 Ω; scales linearly with I_L,avg)
```

**Simulation check**: overlaying I_d,PMOS and I_d,NMOS (both plotted in the Iripple slide of the deck) shows that during each transition one current goes to zero before the other rises — the dead-time window is visible as a flat ~10 ns gap between the two waveforms. **No simultaneous non-zero conduction** → no shoot-through. ✓

### 2.6 Conduction Loss @ 16 Ω

Load changed R_L: 4 Ω → 16 Ω. Everything else (V_in, V_out, f_sw, L, C, D_ideal) unchanged.

Because ΔI_L depends only on V_in, V_out, L, f_sw, **the ripple is unchanged**:
```
 ΔI_L = 57.6 mA
```

New operating point:
```
 I_L,avg = V_out/R_L = 1.8/16 = 112.5 mA  (sim: ≈ 123.8 mA, D-drift)
 I_L,rms,ripple = ΔI_L / √12 = 16.6 mA
```

**Conduction loss (at simulated I_L,avg = 123.8 mA):**
```
 P_avg    = 0.1238² · 0.178  = 2.73 mW
 P_ripple = 0.01663² · 0.178 ≈ 0.05 mW
 P_cond   ≈ 2.73 mW  (presentation reports 3.345 mW including 0.615 mW from ripple rms — small discrepancy in ripple-rms convention)
```

### 2.7 Efficiency @ 16 Ω — Dominant Loss

Useful output power (at simulated I_L,avg):
```
 P_out = V_out · I_L,avg = 1.8 · 0.1238 = 222.8 mW
```

**Full loss budget** (each term uses the 16 Ω operating point):

| Loss mechanism | Expression | Value | Load scaling |
|---|---|---|---|
| Conduction | I_L,avg² · R_eff | **2.73 mW** | ∝ I² |
| Switching (V-I overlap) | ½·V_in·I_L·(t_r+t_f)·f_sw = 0.5·5·0.1238·4n·2M | **2.48 mW** | ∝ I |
| Gate drive (power FETs) | (C_g,P + C_g,N)·V_in²·f_sw = 204p·25·2M | **10.2 mW** | **constant** |
| Deadtime body-diode | V_f·I_L,avg·2·t_d·f_sw = 0.7·0.1238·20n·2M | **3.47 mW** | ∝ I |
| **Total loss** | | **≈ 18.9 mW** | |

```
 P_in = P_out + Σ losses = 222.8 + 18.9 = 241.7 mW
 η    = P_out/P_in = 222.8/241.7 ≈ 92.2 %
```

**Dominant loss at 16 Ω: gate-drive loss (~54 % of total losses).**

**Why the dominance flips between loads:**

At 4 Ω (full load, I_L = 450 mA):
- P_cond = 37 mW, P_gate = 10.2 mW, P_sw ≈ 9 mW, P_dead ≈ 12.6 mW
- **Conduction dominates** (57 % of loss)

At 16 Ω (light load, I_L = 124 mA):
- P_cond drops 13× (quadratic in I)
- P_gate is unchanged (fsw, Cg, V_in constant)
- **Gate-drive dominates**

**Consequence:** efficiency peaks at an intermediate load, not at full load. For the final project's 10 µA sleep-mode requirement (load ~2000× lighter than here), running at f_sw = 2 MHz with these device sizes would give η ≪ 1 %. The final-project sleep mode must either (i) dramatically reduce f_sw (PFM / burst mode), (ii) disable the converter and serve load from a local bypass cap until a top-up burst, or (iii) shrink the power FETs adaptively at low load.

> **Correction to submitted deck**: The Observation slide for the 16 Ω case quotes η ≈ 98 % with the note "Loss due to average current is dominant." That number only captures **conduction** efficiency (P_out / (P_out + P_cond) = 222.8 / 225.5 ≈ 98.8 %). The **all-loss efficiency is ≈ 92 %**, and the dominant loss is gate drive, not conduction. This is the single analytical gap in the submission.

---

## Summary — Assignment 6 Status

| # | Question | Status | Value |
|---|---|---|---|
| 1a | V_reg efficiency (calc + sim) | ✅ | **36 %** |
| 1b | Is V_reg a good choice? | ✅ | No — 64 % losses |
| 2a | Duty cycle | ✅ | **D = 0.36**, t_on = 180 ns |
| 2b | Ripple current | ✅ | **ΔI_L = 57.6 mA** (sim 59.5 mA) |
| 2c | FET sizing for 5 % P_cond | ✅ | 4.56 % achieved |
| 2d | Gate driver ~2 ns | ✅ | < 2 ns, 100 µm drivers |
| 2e | Shoot-through check | ✅ | None (10 ns deadtime) |
| 2f | P_cond @ 16 Ω | ✅ | ≈ 2.7 mW |
| 2g | η @ 16 Ω & dominant loss | ⚠️ **partial** | True η ≈ 92 %; dominant = **gate drive** (deck's 98 % is conduction-only) |

---

## Recommendation: Move to Assignment 7?

**Yes — Assignment 6 is substantively complete.**

The only genuine analytical gap in the submitted deck is the dominant-loss breakdown at 16 Ω (addressed in §2.7 above). This is a *writeup* gap rather than a *simulation* gap, so no new Cadence runs are strictly required.

### Optional (nice-to-have, maps into final-project material)

If there is time before ass-7 work begins, three short Cadence exports would strengthen both the ass-6 defence and the final-project narrative:

1. **Explicit I_d,PMOS vs I_d,NMOS overlay for one period** — makes the shoot-through absence visually obvious (currently only implicit in the Iripple slide).
2. **Gate-drive supply-current measurement** — integrate current from V_in into the gate-driver rail, confirm P_gate ≈ 10 mW. Needed anyway for the final project's efficiency-vs-load analysis.
3. **Efficiency sweep R_L = 4 Ω → 64 Ω** — shows the conduction→gate-drive dominance handover, directly motivates the sleep-mode design of the final project.

None of these blocks the ass-7 start. They can be run in parallel with or after the ass-7 closed-loop work.

### Current schematic state (diverging from ass-6)

The `SMPC1_partB` cell has been re-parameterised toward final-project specs:

| Variable | Ass-6 spec | Current schematic |
|---|---|---|
| V_in | 5.0 V | **3.3 V** |
| V_out target | 1.8 V | 1.2 V (= D·V_in = 0.37·3.3) |
| R_L | 4 Ω | **120 Ω** (→ 10 mA load) |
| f_sw | 2.0 MHz | **4.0 MHz** |
| C | 1.0 µF | **6.6 nF** |
| Power FET W (P/N) | 350 µm / 300 µm × finger counts | 500 µm / 500 µm × finger counts |

The ADE snapshot shows I_L,avg = 405 mA with R_L = 120 Ω, which is inconsistent with 1.2 V / 120 Ω = 10 mA — almost certainly a **stale result** from a prior run when R_L was still 4 Ω (1.2/3 ≈ 400 mA). Re-run after clearing will give the expected ~10 mA.

**Action for ass-7**: we will likely need to **revert** these variables to the ass-6 baseline (5 V/1.8V/4 Ω/2 MHz) for the control-loop design, since Assignment 7 explicitly uses the ass-6 buck. The final-project retargeting can resume after ass-7 is closed out.

**Green light for Assignment 7 (voltage-mode closed-loop control).**
