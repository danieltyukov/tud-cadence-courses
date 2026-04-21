# SMPC Mini-Project 2 — Closed-Loop Voltage-Mode Control

**Design plan, derivations, and implementation roadmap for Assignment 7.**

Authors: Raghavendra Joshi (6438180), Daniel Tyukov (5714699)
Baseline cell: `SMPC1_partB` (from ass-6, before final-project re-parameterisation)

---

## 0. Problem Statement & Specifications

Close a voltage-mode control loop around the ass-6 buck converter.

| Spec | Value | Source |
|---|---|---|
| V_bat (battery, = control supply) | 5.0 V | brief |
| V_out (regulated) | 1.8 V | ass-6 target |
| R_L (load) | 4 Ω | ass-6 target |
| L | 10 µH | ass-6 |
| C | 1 µF | ass-6 |
| f_sw | 2.0 MHz | ass-6 |
| Dead-time | 10 ns | ass-6 |
| V_ref (bandgap, ideal) | 1.0 V | brief |
| V_saw (PWM carrier, pk-pk) | 4.0 V | brief |
| **Phase margin** | **> 60°** | requirement |
| **Loop gain @ 200 Hz** | **≥ 40 dB** | requirement |
| **Max resistor** | 10 MΩ | requirement |
| **Max capacitor** | 100 pF | requirement |
| **Input disturbance test** | 1 Vpp, 200 Hz on V_bat | requirement |

Amplifiers in the compensator may be **ideal**.

---

## 1. LC Power-Stage Analysis

### 1.1 LC cutoff frequency (nominal)

```
 f₀ = 1/(2π·√(L·C))
    = 1/(2π·√(10·10⁻⁶ · 1·10⁻⁶))
    = 1/(2π·√(10⁻¹¹))
    = 1/(2π·3.162·10⁻⁶)
    = 50.33 kHz
```

**→ f₀ = 50.33 kHz, ω₀ = 3.162·10⁵ rad/s**

### 1.2 Quality factor

```
 Q = R_L·√(C/L) = 4·√(10⁻⁶/10·10⁻⁶) = 4·√0.1 = 4·0.3162 = 1.265
```

Resonant peak at f₀: +20·log₁₀(Q) = +2.04 dB.
Damping ratio: ζ = 1/(2Q) = 0.395 (lightly damped, typical for a heavy-load buck).

### 1.3 LC transfer function

```
 H_LC(s) = ω₀² / (s² + (ω₀/Q)·s + ω₀²)
         = 1 / (1 + (s/(Qω₀)) + (s/ω₀)²)
```

Asymptotic behaviour:
- f ≪ f₀: |H_LC| ≈ 1 (0 dB), phase ≈ 0°
- f = f₀: |H_LC| = Q = 1.265 (2 dB), phase = −90°
- f ≫ f₀: |H_LC| ≈ (f₀/f)² (−40 dB/dec), phase → −180°

### 1.4 Tolerance analysis (±20 % on L and C)

```
 f_LC(L,C) = 1/(2π·√(L·C))
```

Both extremes of 20 % tolerance occur when L and C move in the same direction (they **don't** compensate):

```
 f_LC,min : L,C both +20 %  →  (L·C) → 1.44·(L·C)_nom
           f_LC,min = f₀/√1.44 = 50.33/1.2 = 41.94 kHz

 f_LC,max : L,C both −20 %  →  (L·C) → 0.64·(L·C)_nom
           f_LC,max = f₀/√0.64 = 50.33/0.8 = 62.91 kHz
```

**→ f_LC range: 41.9 kHz – 62.9 kHz (±25 % around nominal)**

**Implication for compensator design**: corner frequencies should be placed with this spread in mind. In particular, the LHP-zero–pole pair that cancels the LC resonance (§3) must span this entire range.

---

## 2. Open-Loop Frequency Response (pre-compensator)

The loop around V_out (break at output, inject at V_ref) consists of three frequency-dependent blocks:

```
 L_open(s) = [feedback divider] · [error amp A(s)] · [PWM modulator] · [LC filter]
```

### 2.1 Feedback divider

V_out = 1.8 V must be scaled to V_fb = V_ref = 1.0 V at DC:
```
 V_fb/V_out = R_bot/(R_top + R_bot) = 1.0/1.8 = 0.5556
 R_top/R_bot = 0.8
```

**Choice**: R_bot = 10 kΩ, R_top = 8 kΩ → divider ratio **k_div = 0.5556 (−5.1 dB)**.
(Both ≪ 10 MΩ; current through divider = 1.0 V / 10 kΩ = 100 µA — fine.)

### 2.2 PWM modulator gain

With a sawtooth of V_saw,pp = 4 V compared against a control voltage V_c:
```
 D = V_c/V_saw,pp   (linearisation around operating D)
 V_sw,avg = V_bat · D  →  dV_sw/dV_c = V_bat/V_saw = 5/4 = 1.25
```

**→ PWM gain = V_bat/V_saw = 1.25 (+1.94 dB)**, frequency-independent (ideal sampled-PWM).

### 2.3 DC loop gain (uncompensated, A = 1)

```
 |L_open(0)| = k_div · 1 · 1.25 · 1 = 0.695 (−3.15 dB)
```

Well below the 100 (40 dB) requirement at 200 Hz — the compensator must supply at least **+43.2 dB** of extra gain at 200 Hz.

---

## 3. Compensator Architecture — Why Type-III

| Option | Phase at f_c (typical) | Enough for our LC? |
|---|---|---|
| Type I (pure integrator) | −90° | No. LC adds −180° at crossover → total −270°, PM = −90°. |
| Type II (integrator + 1 zero + 1 pole) | −90° + 90° − 0° = 0° → max +90° boost region | Marginal — works for current-mode (1st-order plant), **not** voltage-mode (2nd-order plant). |
| **Type III (integrator + 2 zeros + 2 poles)** | **Up to +180° phase boost** via LHP zero-pole pair bracketing f₀ | ✔ Correct choice for voltage-mode buck. |

The Type-III adds a second LHP-zero / LHP-pole pair that can bracket the LC resonance and contribute an additional **+90° phase boost** right where the LC is dumping phase. This is the standard voltage-mode workhorse.

### 3.1 Transfer function

Topology (inverting op-amp with R1, R3-C3 input network and R2-C2, C1 feedback):

```
                      C1
                      ──┤├──
                      │     │
               C2  R2 │     │
        V_fb ─┬─┤├──/\/\─┬──┴────── V_c (op-amp output)
              │          │
              R1         │
              │          │
              ├──────────┤──── V−  (op-amp inverting input)
              │
              C3    R3
              ─┤├──/\/\─── V_out  (via a second path = phase-boost)
              │
             V+  ← V_ref (op-amp non-inverting input)
```

Derivation (assuming C₁ ≪ C₂ and R₃ ≪ R₁, which the final values will respect):

```
 H_c(s) = −Z_f(s)/Z_i(s)

 Z_i = R1 ∥ (R3 + 1/sC3)
     = R1·(1 + sR3C3)/(1 + s(R1+R3)C3)  ≈ R1·(1 + sR3C3)/(1 + sR1C3)

 Z_f = (R2 + 1/sC2) ∥ (1/sC1)
     = (1 + sR2C2) / [sC2·(1 + sR2C1)]     (for C1 ≪ C2)
```

Combining:

```
          1        (1 + s/ω_ZEA)·(1 + s/ω_FZ)
 H_c(s)= ─── · ────────────────────────────────
         sR1C2   (1 + s/ω_FP)·(1 + s/ω_HF)
```

Four corner frequencies (the fundamental parameters to design):

| Corner | Expression | Role |
|---|---|---|
| f_ZEA (inverted-zero from C2) | 1 / (2π·R2·C2) | Above this: flat; below: integrator → huge DC gain |
| f_FZ (LHP zero from C3) | 1 / (2π·R1·C3) | Starts a +20 dB/dec boost and +90° phase |
| f_FP (LHP pole from R3·C3) | 1 / (2π·R3·C3) | Ends the +20 dB/dec boost |
| f_HF (LHP pole from C1) | 1 / (2π·R2·C1) | HF roll-off to attenuate switching ripple |

Mid-band magnitude (f_ZEA ≪ f ≪ f_FZ):
```
 A_mid = R2/R1
```

Between f_FZ and f_FP (rising):
```
 |H_c(f)| ≈ A_mid · (f/f_FZ)
```

---

## 4. Corner-Frequency Placement — Derivation

### 4.1 Constraints carried forward

- f_UGB (unity gain) < f_sw/π = 2 MHz / π = **636.6 kHz** (Berkhout ceiling)
- |L_loop(200 Hz)| ≥ 100 (40 dB)
- PM ≥ 60°
- All R ≤ 10 MΩ, all C ≤ 100 pF

### 4.2 Place f_ZEA

f_ZEA creates the integrator action below itself. For minimum phase impact at the eventual crossover f_c, standard practice is:

```
 f_ZEA ≤ f_c / 10
```

Simultaneously, f_ZEA must be low enough that loop gain at 200 Hz still meets the 40 dB target. In the integrator region (f < f_ZEA):
```
 |A_c(f)| = A_mid · (f_ZEA / f)        (integrator asymptote)
 |L(f)| = k_div · |A_c| · PWM · |H_LC| = 0.695 · A_mid · (f_ZEA/f) · 1
```

For f = 200 Hz:
```
 |L(200)| = 0.695 · A_mid · (f_ZEA / 200)   ≥ 100
 A_mid · f_ZEA ≥ 100·200/0.695 = 28 780  (Hz)
```

Choose **f_ZEA = 5 kHz** → need A_mid ≥ 28 780 / 5 000 = **5.76**.

Pick **A_mid = 7** (16.9 dB) for ~3 dB margin → needed loop gain at 200 Hz = 0.695 · 7 · 25 = 121.6 (**41.7 dB** ✔).

### 4.3 Place f_FZ, f_FP (the boost pair bracketing f₀)

Goal: cancel the −40 dB/dec, −180° drop of the LC filter around f₀, turning the loop into a clean −20 dB/dec / ~−90° slope through crossover.

**Rule of thumb**: centre the geometric mean of (f_FZ, f_FP) near the expected f_c:
```
 √(f_FZ · f_FP) ≈ f_c
```
Phase boost from a zero-pole pair peaks at this geometric mean. For max boost ≥ 70°, spread **f_FP / f_FZ ≥ ~100**.

**Chosen**:
- f_FZ = 30 kHz (just below f_LC,min = 41.9 kHz — guarantees the zero is placed before LC phase starts dropping even in tolerance worst-case)
- f_FP = 3.3 MHz (well above f_LC,max = 62.9 kHz and above intended f_c, but below f_HF = 2 MHz → we revisit f_HF below)

Wait: for these to be consistent, f_FP < f_HF is OK but both must sit sensibly. Revised:

- **f_FZ = 30 kHz** ← start boost
- **f_FP = 3.3 MHz** ← end boost (peak phase boost at geo-mean √(30k·3.3M) = 315 kHz)
- **f_HF = 2 MHz** ← final HF pole for ripple attenuation (below f_FP is fine as long as Type-III transfer magnitudes are consistent)

Note — the order of f_FP vs f_HF is not physically constrained; either can come first. Placing f_HF below f_FP just means the +20 dB/dec boost stops earlier than the HF roll-off, which is benign here.

### 4.4 Expected crossover frequency

From f_LC the loop slope is −20 dB/dec (LC rolls at −40 dB/dec; compensator boosts at +20 dB/dec between f_FZ and f_FP; net: −20 dB/dec).

Loop gain at f_LC (approximate — LC has Q-peak here):
```
 |L(f_LC)| = k_div · |A_c(f_LC)| · PWM · |H_LC(f_LC)|
            = 0.556 · A_mid·(f_LC/f_FZ) · 1.25 · Q
            = 0.556 · 7 · (50.33/30) · 1.25 · 1.265
            = 10.3 (20.3 dB)
```

Crossover (|L| = 0 dB), −20 dB/dec slope from f_LC:
```
 f_c = f_LC · 10^(20.3/20) = 50.33 · 10.3 = 518 kHz
```

**→ f_c ≈ 518 kHz** ← well below Berkhout limit 636 kHz ✔

### 4.5 Phase margin calculation

Loop phase contributions (PWM and divider are real):

```
 ∠L(f) = ∠A_c(f) + ∠H_LC(f)
```

**Compensator phase** (using exact arctan formulas):
```
 ∠A_c(f) = −90° + atan(f/f_ZEA) + atan(f/f_FZ) − atan(f/f_FP) − atan(f/f_HF)
```

At f_c = 518 kHz:
- atan(518/5) = atan(103.6) = 89.45°
- atan(518/30) = atan(17.27) = 86.68°
- atan(518/3300) = atan(0.157) = 8.93°
- atan(518/2000) = atan(0.259) = 14.52°

```
 ∠A_c(518 kHz) = −90° + 89.45° + 86.68° − 8.93° − 14.52° = 62.68°
```

**LC phase** at f_c = 518 kHz (ω/ω₀ = 518/50.33 = 10.29, above resonance):
```
 ∠H_LC(jω) = −atan2( (ω/ω₀)/Q , 1 − (ω/ω₀)² )
```
- (ω/ω₀)/Q = 10.29 / 1.265 = 8.13
- 1 − (ω/ω₀)² = 1 − 105.9 = −104.9 (negative → 2nd quadrant)
- arctan(8.13 / 104.9) = 4.43° (reference angle)
- ∠H_LC = −(180° − 4.43°) = **−175.6°**

```
 ∠L(518 kHz) = 62.68° + (−175.6°) = −112.9°
 PM = 180° + ∠L = 180° − 112.9° = 67.1°
```

**→ PM ≈ 67° ✔** (target > 60°)

### 4.6 Summary of the compensator design targets

| Corner | Chosen | Rationale |
|---|---|---|
| f_ZEA | 5 kHz | 10× below intended f_c; A_mid = 7 lands loop gain @ 200 Hz = 41.7 dB |
| f_FZ | 30 kHz | Below worst-case f_LC,min = 41.9 kHz; begins phase boost |
| f_FP | 3.3 MHz | √(f_FZ·f_FP) = 315 kHz (central phase boost peak); ≫ f_LC,max |
| f_HF | 2 MHz | ≈ f_sw for ripple filtering; sits below f_FP, benignly |
| A_mid | 7 (16.9 dB) | Gives |L(200 Hz)| = 41.7 dB with ~1.7 dB margin |

**Performance prediction**: f_c = 518 kHz, PM = 67°, |L(200 Hz)| = 41.7 dB.

---

## 5. Component Value Selection

From the four corner-frequency equations and a choice of R1 (anchor resistor):

```
 R1 = 100 kΩ                     ← choice (anchor)
 R2 = A_mid · R1 = 7 · 100 k = 700 kΩ
 C2 = 1/(2π·R2·f_ZEA) = 1/(2π·700k·5k) = 45.5 pF
 C3 = 1/(2π·R1·f_FZ) = 1/(2π·100k·30k) = 53.05 pF
 R3 = 1/(2π·C3·f_FP) = 1/(2π·53.05p·3.3M) = 910 Ω
 C1 = 1/(2π·R2·f_HF) = 1/(2π·700k·2M) = 0.1137 pF = 113.7 fF
```

Feedback divider (separate):
```
 R_top = 8 kΩ, R_bot = 10 kΩ  →  V_fb/V_out = 0.556,  V_out = 1.8 V when V_fb = V_ref
```

### 5.1 Constraint check

| Component | Value | Limit | ✔ |
|---|---|---|---|
| R1 | 100 kΩ | ≤ 10 MΩ | ✔ |
| R2 | 700 kΩ | ≤ 10 MΩ | ✔ |
| R3 | 910 Ω | ≤ 10 MΩ | ✔ |
| R_top | 8 kΩ | ≤ 10 MΩ | ✔ |
| R_bot | 10 kΩ | ≤ 10 MΩ | ✔ |
| C1 | 113.7 fF | ≤ 100 pF | ✔ |
| C2 | 45.5 pF | ≤ 100 pF | ✔ |
| C3 | 53.05 pF | ≤ 100 pF | ✔ |

All in bounds. R3 is small (910 Ω) but still respectable; larger R3 would require smaller C3 and the limited phase-boost span would shift.

### 5.2 Verification — corner frequencies recomputed from component values

```
 f_ZEA = 1/(2π·700k·45.5p)   = 4 996 Hz   ≈ 5 kHz   ✔
 f_FZ  = 1/(2π·100k·53.05p)  = 30 000 Hz  = 30 kHz  ✔
 f_FP  = 1/(2π·910·53.05p)   = 3.299 MHz  ≈ 3.3 MHz ✔
 f_HF  = 1/(2π·700k·113.7f)  = 2.001 MHz  ≈ 2 MHz   ✔
```

### 5.3 Design-validation assumptions

Recall the approximations in the derivation:
- C1 ≪ C2: 113.7 fF ≪ 45.5 pF → ratio 1/400 ✔
- R3 ≪ R1: 910 Ω ≪ 100 kΩ → ratio 1/110 ✔

Both hold comfortably, so the simplified transfer function is accurate.

---

## 6. Predicted Disturbance Rejection (Task 6)

A perturbation δV_bat on the input propagates to V_out through the PWM → LC path. At DC the open-loop gain is D = 0.36. With the loop closed:
```
 V_out/δV_bat |closed = (D) / (1 + L(s))
```

At 200 Hz, |L(j·2π·200)| = 121.6 (41.7 dB). Therefore:
```
 |V_out/δV_bat| @ 200 Hz = 0.36 / (1 + 121.6) ≈ 0.36 / 122.6 = 2.94·10⁻³
```

For an input perturbation of 1 Vpp @ 200 Hz:
```
 V_out ripple @ 200 Hz ≈ 2.94 mVpp
 PSRR = 20·log₁₀(2.94·10⁻³) = −50.6 dB
```

**Comfortably below the implicit −40 dB target.**

---

## 7. Schematic Modifications Required (from ass-6 SMPC1_partB)

### 7.1 Revert ass-6 baseline (undo final-project re-parameterisation)

Before anything else, restore the ass-6 operating point. Starting from the snapshot in `final/schematic_state_snapshot.md`:

| Variable | Final-prj snapshot | Set for ass-7 |
|---|---|---|
| V_bat (V0 `vdc`) | 3.3 V | **5.0 V** |
| Von (V1 `v1`) | 3.3 V | **5.0 V** |
| L | 10 µH | 10 µH (unchanged) |
| C | 6.6 nF | **1.0 µF** |
| RL | 120 Ω | **4.0 Ω** |
| fsw | 4 MHz | **2.0 MHz** |
| V1 vpulse period | 250 ns | **500 ns** |
| deadtime | 10 ns | 10 ns (unchanged) |
| Power FET M0 simM/totalM | 300/300 | Re-check; ass-6 submission used **totalM = 300 @ W = 350 µm** (different vs. snapshot 500 µm/300). Options:<br>(a) keep 500 µm × 300 (matches snapshot; loss slightly different from ass-6 deck) or<br>(b) revert to 350 µm × 300 (matches ass-6 deck). Pick **(a)** to avoid device rework — loop behaviour is dominated by L, C, and the compensator, not the exact R_on. |
| Power FET M1 | 500 µm / 600 nm × 100 | Keep (snapshot matches) |
| Gate-drv M2–M5 | 500 µm × 300/100 | Consider reverting to ass-6 smaller driver (100 µm × 1) to match deck — **optional**, only matters for t_r fidelity which is not loop-critical at AC-analysis frequencies. |

**Primary-path deliverable**: get loop design working at the correct L, C, R_L, f_sw, V_bat. FET-size fidelity to the ass-6 deck is second-order.

### 7.2 Remove open-loop PWM source

- **Delete V1 (vpulse)**. It will be replaced by the closed-loop PWM coming from a comparator.
- Preserve the non-overlap generator (I0, I1 NANDs, I2 inverter), the level shifters (E0, E1 VCVS), and the power stage (M0–M5, L, C, R_L). These remain intact.

### 7.3 Add the feedback divider

- New instance `R_top` = 8 kΩ from `/Vout` → new net `/Vfb`.
- New instance `R_bot` = 10 kΩ from `/Vfb` → `gnd!`.

### 7.4 Add the Type-III compensator

New sub-network:

```
Nets: /Vfb (input), /Vx (summing node, = op-amp inv. input), /Vc (compensator output)

Components (all analogLib):
 R1  = 100 kΩ   from /Vfb to /Vx
 R3  = 910 Ω    in series with C3 = 53 pF, from /Vfb to /Vx (parallel to R1)
 R2  = 700 kΩ   in series with C2 = 45.5 pF, from /Vc to /Vx (feedback)
 C1  = 114 fF   from /Vc to /Vx (feedback, parallel to R2+C2)

Op-amp: ideal (analogLib `amp_dc` or a VCVS with enormous gain like egain=1e6 + output clamp).
  V+ = /Vref (new vdc source, vdc = 1.0 V)
  V− = /Vx
  Out = /Vc
  Supplies: ±something sufficient (e.g., vdc=±5 V, or rails tied to V_bat and gnd for a 0→5 V swing if using a rail-to-rail model).
```

### 7.5 Add the PWM modulator

PWM comparator compares V_c against a 4 V pk-pk sawtooth at 2 MHz:

- **Sawtooth source** — use `analogLib vpulse` with:
  - v1 = 0 V (ramp start)
  - v2 = 4 V (ramp peak)
  - period = 1/fsw = 500 ns
  - trise = period − ε ≈ 499 ns (ramp up almost the full period)
  - tfall = ε = ~1 ns (near-instant reset)
  - pulsewidth = tfall (so v2 is held only briefly before restart)

  *Alternative*: `vpwl` with explicit piecewise-linear table for cleaner ramp.

- **Comparator** — use `ahdlLib comparator` with:
  - vin = V_c, vref = V_saw (or vice-versa depending on polarity — verify sign in sim)
  - sigout_high = V_bat = 5 V
  - sigout_low = 0 V
  - Output goes to the `/input` net of the existing non-overlap generator (replacing the removed V1).

### 7.6 Full signal chain after modifications

```
 V_out ──┬── to feedback divider ──► V_fb ──► [Type-III comp] ──► V_c ──┐
         │                                                              │
         │  regulated output                                             ▼
         │                                                        [PWM comparator]
         │                                                              │
         │              V_saw sawtooth ─────────────────────────────────┘
         │                                                              │
         │                                                              ▼
         │                                                      [Non-overlap gen]
         │                                                              │
         │                                                              ▼
         │                                                      [Gate drivers]
         │                                                              │
         │                                                              ▼
         │                                                  [Power FETs M0/M1]
         │                                                              │
         │                                                              ▼
         └─── L – C – R_L filter ◄──────────────────────────── V_PWM (switch node)
```

---

## 8. Simulation Plan

### 8.1 AC testbench (loop gain / Bode plot) — **Task 3 & 4**

**Approach**: break the loop at a convenient point (e.g., just after the feedback divider at `/Vfb`), inject a small AC signal there, and measure from the injection point around the loop back to itself. In Cadence, this is the **middle-brook / probe-insertion** technique.

Simplest practical setup:
1. Keep the loop closed at DC (otherwise the operating point explodes).
2. Insert an `iprobe` or a specialised `vcvs` with `egain=1` as a "transparent link" between two nodes; sim across that link gives the loop gain.
3. Or: open the loop at `/Vfb`, drive the comparator side with `V_fb + δV_AC`, and tie the divider output to a DC source set to the operating-point V_fb (≈ 1.0 V) so the power stage still runs.

**Simpler approximate method**: since the plant is linearisable, simulate the compensator and the LC separately:
- Compute H_comp(s) symbolically in the ADE calculator or in a separate .cir file with ideal LC model
- Multiply by LC transfer analytically

For the report, the clean way is the explicit AC break-point.

**Analysis**: `ac` from 1 Hz to 10 MHz, 100 points/decade (log).

**Measurements on Bode plot**:
- Gain at 200 Hz (mark, annotate "≥ 40 dB" check)
- Unity gain (0 dB) crossover frequency f_c
- Phase margin at f_c
- Phase at 200 Hz (should be near −90° — integrator)

**Expected results**:
- |L(200 Hz)| ≈ 41.7 dB
- f_c ≈ 518 kHz
- PM ≈ 67°

### 8.2 Transient verification — **Task 5**

**Test 1: startup**. All sources step from 0 to nominal at t = 0 (use pulse sources with short trise, e.g., 1 µs). Watch:
- V_out: should rise monotonically, settle at 1.8 V in a few hundred µs without ringing
- V_c (compensator output): should show well-damped settling
- D (duty): should converge to ≈ 0.37–0.38

Duration: 0 → 500 µs with maxstep = 10 ns.

**Test 2: load step**. After t = 500 µs, step R_L from 4 Ω to 8 Ω (or use a parametric switched load). Check:
- V_out excursion: < 100 mV
- Settling time: < 100 µs
- No oscillation

**Test 3: stability sanity**. Sweep a perturbation (e.g., small V_ref step) and verify no sustained oscillation.

### 8.3 Disturbance rejection — **Task 6**

Add to V_bat source: a 1 Vpp sine at 200 Hz on top of the 5 V DC (so V_bat = 5 + 0.5·sin(2π·200·t) V).

- Run transient for ≥ 50 ms (to accumulate enough 200 Hz cycles for accurate DFT)
- maxstep = 100 ns (switching noise filtered enough without blowing simulation time)
- Measure: `dB20(mag(dft("/Vout" 40m 50m 2048)))` — extract the 200 Hz bin
- Expected: 200 Hz component in V_out ≈ 2.94 mVpp → PSRR ≈ −50 dB

**Note**: for a clean DFT, time window must contain an integer number of 200 Hz cycles. 200 Hz → period = 5 ms. Window of 10 ms = 2 periods (clean). Use `clip` on the transient result to the 40–50 ms window.

### 8.4 Simulation matrix summary

| # | Name | Analysis | Duration / Span | Output(s) |
|---|---|---|---|---|
| 1 | Loop AC | ac | 1 Hz – 10 MHz | `db(V("/loop_out"))`, `ph(V("/loop_out"))` |
| 2 | Startup | tran | 0 – 500 µs | V_out, V_c, D, I_L |
| 3 | Load step | tran | 0 – 2 ms | V_out, I_L |
| 4 | Input disturbance | tran | 0 – 50 ms | V_out (DFT post-processing) |

---

## 9. Pre-flight Checks Before Starting

- [ ] Open `SMPC1_partB`, save a backup schematic copy as `SMPC1_partB_finalproj_snapshot` (so the snapshot state is preserved in-tool, not just in this .md).
- [ ] Update Design Variables to ass-6 spec (§7.1 table).
- [ ] Delete V1 (open-loop PWM); make sure no floating inputs.
- [ ] Add compensator + divider + comparator + sawtooth per §7.3–7.5.
- [ ] Sanity DC sim: V_fb = 1.0 V, V_out = 1.8 V at steady state (compensator should saturate to a duty ≈ 0.37).
- [ ] Sanity transient: confirm regulation before running AC.
- [ ] AC testbench: break-point mechanism set up correctly (verify by computing loop gain at DC manually and comparing to sim).

---

## 10. Deliverables (what ends up in the presentation)

1. **LC cutoff analysis** (§1): f₀ = 50.33 kHz nominal; tolerance range 41.9 – 62.9 kHz.
2. **Compensator design walkthrough** (§3–§5): topology choice, corner placements, component values with motivation.
3. **Bode plot** (§8.1): loop gain magnitude and phase, annotated with (a) |L(200 Hz)| ≥ 40 dB marker, (b) f_c (unity gain), (c) PM.
4. **Transient startup & stability** (§8.2): V_out, V_c, I_L traces.
5. **Disturbance rejection** (§8.3): V_out waveform under 1 Vpp @ 200 Hz perturbation + DFT extracting the 200 Hz component; state PSRR.
6. **Discussion**: motivate every pole/zero placement; discuss sensitivity to L, C tolerance (compensator robustness across f_LC range).

---

## 11. Risk Register / Watch-outs

| Risk | Symptom | Mitigation |
|---|---|---|
| Break-point in AC sim at wrong place | Loop gain way off expected | Break at a low-impedance driven node; verify by hand-calculating DC loop gain and comparing to sim low-freq value |
| Op-amp model has finite bandwidth | PM lower than predicted | Use truly ideal VCVS with egain = 1e6 and no output cap; or use the `analogLib ideal_amplifier` |
| C1 = 114 fF is below Cadence's sensible cap range | Weird sim artefacts | Use C1 = 0.1 pF (rounded up); shifts f_HF to 2.27 MHz, negligible impact |
| f_FP = 3.3 MHz requires R3 = 910 Ω; voltage drop across R3 affects DC operating point | V_out shift | R3 only carries AC current (in series with C3) — no DC current, no DC drop |
| Saw-tooth has non-ideal shape (trise not exactly period−ε) | Non-linear PWM gain | Use vpwl for a clean 0–4–0 sawtooth; verify PWM gain by injecting DC Vc and observing avg V_out = D·V_bat |
| Closed-loop transient exhibits sub-harmonic oscillation | V_out wobbles at f_sw/2 | Not a current-mode issue here (voltage-mode); if seen, PM is actually < 60° — re-run Bode |
| DFT window not aligned with 200 Hz period | False harmonic peaks | Take integer multiples of 5 ms; use Hann window if necessary |
| Saturation of V_c against rails | Clipped duty, nonlinear loop | Ensure comparator-side rails accommodate full V_c swing; pick op-amp rails ≥ 0 V and ≤ 5 V |

---

## 12. Open Questions to Resolve Before Implementation

- Does the ass-7 brief require the **exact** ass-6 ideal duty of 0.36, or is a tuned D acceptable? (Doesn't matter once the loop closes — whatever D yields V_out = 1.8 V is correct.)
- Should the sawtooth centre be at 0 V or at V_bat/2? (Affects linearisation point — use 0 → 4 V so mean V_c = 1.8 V · 4/5 = 1.44 V lies comfortably in range.)
- Do we draw the op-amp as an ideal VCVS or use a behavioural model from analogLib? (VCVS is cleanest for ideal behaviour.)

These can be resolved at implementation time; none are blockers.

---

## Summary

Design lands at:
- **f_c ≈ 518 kHz** (below Berkhout 636 kHz ✔)
- **PM ≈ 67°** (> 60° ✔)
- **|L(200 Hz)| ≈ 41.7 dB** (> 40 dB ✔)
- **Predicted PSRR @ 200 Hz ≈ −50 dB** (< −40 dB, exceeds likely target)
- Component count: 5 R + 3 C + 2 sources + 1 op-amp + 1 comparator — all within spec.

The path is: (1) revert schematic to ass-6 baseline, (2) add divider + Type-III + comparator + sawtooth, (3) run AC → transient → disturbance sims, (4) assemble Bode plot + waveforms for the presentation.
