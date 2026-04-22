# SMPC Final Project — Design Plan & Derivations

**Project**: 3.3 V → 1.2 V synchronous buck with sleep-mode support, efficiency-optimised across load range.
**Authors**: Raghavendra Joshi (6438180), Daniel Tyukov (5714699)
**Baseline cell**: `SMPC1_partB` (post-ass-7, with loop added)

---

## 0. Specifications (from `final_project.txt`)

| Spec | Value | Notes |
|---|---|---|
| V_in (battery) | 3.3 V | |
| V_out | 1.2 V | D_ideal = 1.2/3.3 = 0.364 |
| Supply (output) ripple | < 100 mVpp | |
| Switch-node ringing | < 1.5 V peak | Due to parasitics |
| Load (active) | 10 mA | Peak |
| Load (sleep) | 10 µA | ≥ 1000× less than active |
| Peak efficiency | ≥ 90 % | |
| Efficiency analysis | Over output-power range | |
| Interference rejection | 40 dB attenuation @ 2 kHz | On V_in perturbation |
| Technology | 180 nm BCD | TSMC pch_5 / nch_5 |
| Package / PCB parasitics | **2 nH + 50 mΩ per connection** | Apply at every chip ↔ PCB pin |
| Area / BOM | Minimise | Small external L, C |
| Sleep-mode power | Minimise at 10 µA load | |
| Report | White background, large fonts | |
| Grading emphasis | Understanding + explanation | Not just numbers |

---

## 1. Design-space exploration

### 1.1 Key tradeoffs

| Knob | ↑ increases | ↓ decreases |
|---|---|---|
| f_sw | Gate-drive loss, switching loss, control-loop BW | Inductor/cap size, ripple |
| L | CCM range, filtering | Transient response, BOM |
| C | Transient headroom, ripple filtering | BOM (and self-resonance moves down) |
| Power FET W | Gate loss, die area | Conduction loss |
| Gate driver W | Transition time (faster), driver loss | Switching loss (V-I overlap) |
| Dead-time | Shoot-through safety | Body-diode loss |

### 1.2 Loss model (per operating point)

Used throughout to evaluate design choices:

```
 P_loss(I_L) ≈ P_cond + P_sw + P_gate + P_dead + P_quiescent

 P_cond     = I_L,avg² · R_eff          (+ I_ripple,rms² · R_eff, small)
   R_eff    = R_on,P · D + R_on,N · (1−D)

 P_sw       ≈ ½·V_in·I_L,avg·(t_r + t_f)·f_sw     (V–I overlap, both edges)

 P_gate     = (C_g,P + C_g,N) · V_in² · f_sw      (power FET gate drive)

 P_dead     = V_f,body · I_L,avg · 2·t_dead · f_sw (body-diode freewheel during DT)

 P_quiescent = V_in · I_q                          (op-amps, comparators, bias)
```

Efficiency:
```
 η = P_out / (P_out + P_loss)
   = V_out·I_L,avg / (V_out·I_L,avg + P_loss)
```

### 1.3 Scaling with load

At any load I_L,avg:
- P_cond ∝ I²   (quadratic)
- P_sw   ∝ I   (linear)
- P_dead ∝ I   (linear)
- **P_gate, P_quiescent: constant** (load-independent) ← dominant at low load

Consequence: η drops off rapidly as I_L,avg → 0 unless P_gate is eliminated (e.g., by sleeping the switcher and running only the bias circuits).

---

## 2. Frequency / Inductor / Capacitor Selection

### 2.1 Switching frequency

```
 P_gate(I_L,peak) = C_g,tot · V_in² · f_sw
```

At V_in = 3.3 V, C_g,tot ≈ 10 pF (reasonable for 10 mA-class power FETs — see §3):

| f_sw | P_gate | P_sw (@ 10 mA, 4 ns edges) | Margin at η = 90 % |
|---|---|---|---|
| 1 MHz | 109 µW | 66 µW | Plenty (room for P_cond) |
| 2 MHz | 218 µW | 132 µW | Comfortable |
| 4 MHz | 435 µW | 264 µW | Tight — P_gate alone is 3.6 % of P_out |
| 8 MHz | 871 µW | 528 µW | η_peak ≤ ~88 % even with zero conduction |

**Choice: f_sw = 2 MHz** — the knee where loss is still < 1 % of P_out for each mechanism, while keeping L in a reasonable 10–22 µH window and compensator BW well above the 2 kHz rejection target.

### 2.2 Inductor

Ripple:
```
 ΔI_L = (V_in − V_out)·t_on/L = (V_in − V_out)·D / (L·f_sw)
      = (3.3 − 1.2)·0.364 / (L·2·10⁶)   (A, with L in H)
      = 3.82·10⁻⁷ / L
```

CCM boundary at full load (I_L,avg = 10 mA): ΔI_L ≤ 2·I_L,avg = 20 mA:
```
 L_min,CCM = 3.82·10⁻⁷ / 0.02 = 19.1 µH
```

| L | ΔI_L | Mode @ 10 mA | Mode @ 1 mA | Mode @ 10 µA |
|---|---|---|---|---|
| 10 µH | 38 mA | DCM | DCM | DCM |
| 22 µH | 17.4 mA | CCM (borderline) | DCM | DCM |
| 47 µH | 8.1 mA | CCM | DCM | DCM |

At 10 µA load, everything is DCM regardless. At 10 mA, 22 µH keeps us in CCM (easier small-signal model) while still being "small" for BOM.

**Choice: L = 22 µH** (standard value). ΔI_L = 17.4 mA at 10 mA load, peak I_L = 18.7 mA (saturation headroom easy).

Alternative worth simulating: **L = 10 µH with ZCD-enabled synchronous rectification** — accepts DCM at all real loads but halves the inductor BOM. Decision contingent on sim result.

### 2.3 Capacitor

**Steady-state output ripple**:
```
 ΔV_out,ss = ΔI_L / (8·C·f_sw)
```

For ΔV_out ≤ 100 mVpp with ΔI_L = 17.4 mA, f_sw = 2 MHz:
```
 C ≥ ΔI_L / (8·ΔV·f_sw) = 17.4·10⁻³ / (8·0.1·2·10⁶) = 10.9 nF
```

**Load-step transient** — dominant cap requirement. Sudden load change ΔI causes V_out to move by approximately ΔI·√(L/C) before the loop responds:
```
 |ΔV_out,trans| ≈ ΔI·√(L/C) / ω_c_loop    (approximate — depends on loop BW)

 Stored-energy bound: ΔV_out,trans ≤ ΔI / (ω_c · C)
```

For the worst-case 10 mA load dump and target ΔV_out,trans ≤ 100 mV with ω_c ≈ 2π·200 kHz = 1.26 Mrad/s:
```
 C ≥ 10·10⁻³ / (1.26·10⁶·0.1) = 79 nF
```

**Choice: C = 100 nF** — comfortable steady-state margin, meets transient, BOM-friendly.

Note: use a low-ESR MLCC (X7R) with ESR < 10 mΩ and ESL < 1 nH at 2 MHz. The cap self-resonance f_res = 1/(2π√(L_ESL·C)) with L_ESL = 1 nH, C = 100 nF is 15.9 MHz — safely above f_sw.

### 2.4 Resulting LC filter parameters

```
 f_LC = 1/(2π·√(L·C)) = 1/(2π·√(22·10⁻⁶·100·10⁻⁹))
      = 1/(2π·√(2.2·10⁻¹²)) = 1/(2π·1.483·10⁻⁶) = 107.3 kHz

 Q  = R_L·√(C/L)   — load-dependent!
    at R_L = 120 Ω (10 mA):   Q = 120·√(100n/22µ) = 120·0.0674 = 8.09
    at R_L = 1.2 kΩ (1 mA):   Q = 1.2k·0.0674 = 80.9
    at R_L = 120 kΩ (10 µA):  Q = 120k·0.0674 = 8090  ← don't excite this
```

**Implication**: the plant Q skyrockets as load lightens. At 10 µA the LC is essentially undamped — **you cannot run voltage-mode PWM against this without destabilising**. This is a hard argument for **burst / PFM sleep mode** — at light loads the switcher turns off, the LC is freewheeling through the load only (no active drive), and Q doesn't matter because there's no swept-sine excitation.

---

## 3. Power FET Sizing

### 3.1 Conduction budget

For η_peak ≥ 90 % at I_L,avg = 10 mA, P_out = 12 mW, total P_loss ≤ 1.33 mW.

Proposed sub-budget at peak:

| Item | Budget | Fraction |
|---|---|---|
| P_cond | 300 µW | 22 % |
| P_sw | 300 µW | 22 % |
| P_gate | 400 µW | 30 % |
| P_dead | 200 µW | 15 % |
| P_quiescent | 130 µW | 10 % |
| **Total** | **1.33 mW** | **η = 90.0 %** |

R_eff target:
```
 P_cond = I² · R_eff  →  R_eff = 300 µW / (10 mA)² = 3.0 Ω
```

### 3.2 Device widths

From the ass-6 extraction: R_on·W_total ≈ **6.1 Ω·mm for PMOS**, **7.35 Ω·mm for NMOS** (at V_GS = V_in = 3.3 V). *These must be re-extracted at V_GS = 3.3 V instead of 5 V — lower overdrive → somewhat higher R_on·W product (~1.4× worse). Budget accordingly.*

Using ass-6 values as a starting estimate (worst-case baseline; re-measure in sim):

```
 R_on,P ≤ 6 Ω  (so it contributes ≤ 2.2 Ω to R_eff at D = 0.36)
   → W_tot,P ≈ 6.1 / 6 = 1.02 mm
 R_on,N ≤ 5 Ω  (so it contributes ≤ 3.2 Ω to R_eff at 1−D = 0.64)
   → W_tot,N ≈ 7.35 / 5 = 1.47 mm

 R_eff = 6·0.364 + 5·0.636 = 2.18 + 3.18 = 5.36 Ω   (budget 3 Ω — need tighter)
```

This doesn't meet the budget. Push wider:

```
 Target R_eff = 3 Ω with D = 0.36, match contributions: R_on,P·D = R_on,N·(1−D) = 1.5 Ω
   R_on,P = 1.5/0.364 = 4.12 Ω  →  W_tot,P = 6.1/4.12 = 1.48 mm
   R_on,N = 1.5/0.636 = 2.36 Ω  →  W_tot,N = 7.35/2.36 = 3.11 mm
```

**Chosen**:
- **Power PMOS: W_tot ≈ 1.5 mm** (e.g., W=500µm × 3 fingers/multipliers)
- **Power NMOS: W_tot ≈ 3.0 mm** (e.g., W=500µm × 6 fingers/multipliers)

These are **~70× smaller than the snapshot** power FETs. Die-area saving is huge, and:
- P_gate = C_ox·(W_P·L_P + W_N·L_N)·V² ·f_sw
       ≈ 2.9·(1500·0.5 + 3000·0.6)·(3.3)²·2·10⁶ / 10¹⁵   [units: fF/µm²·µm·µm·V²·Hz → W]
       = 2.9 · (750 + 1800) · 10.89 · 2·10⁶ · 10⁻¹⁵
       = 2.9 · 2550 · 2.178·10⁷ · 10⁻¹⁵
       = 1.61·10⁻⁴ W = **161 µW** ✔ (budget 400 µW)

- C_g,tot ≈ 7.4 pF (half of prior budget — P_gate plenty under)

### 3.3 Sanity: peak current & saturation

At peak I_L = 10 + 17.4/2 = 18.7 mA through devices sized for >> 1 A. **Current density negligible**, no saturation concern.

### 3.4 Optimisation axis — don't oversize

The 5 % conduction-loss rule from ass-6 gives *upper bound* on W. Going wider **wastes** area AND raises P_gate — which, at light load, dominates efficiency. So:

```
 Optimal W(I_L,avg) : dP_loss/dW = 0
      P_cond ∝ I² / W         (quadratic in I)
      P_gate ∝ W               (linear, load-independent)
      →  ∂/∂W[α·I²/W + β·W] = −α·I²/W² + β = 0
      →  W_opt ∝ I  (device sizes should track load for best η across range)
```

In practice, adaptive FET segmentation (parallel slices switched in/out based on load) is a technique the final-project report should discuss — even if not all of it is implemented.

---

## 4. Gate Driver Redesign

The snapshot driver is sized for 150 mm power FETs — wildly oversized for 1.5–3 mm FETs here. New sizing:

Required drive current to slew C_g = 7.4 pF through ΔV = 3.3 V in t_r = 2 ns:
```
 I_drv = C_g·ΔV/t_r = 7.4 pF · 3.3 / 2 ns = 12.2 mA
```

Driver inverter at 3.3 V GS can supply ~0.3 mA/µm at the strong-inversion operating point (5V MOS run at 3.3 V is weaker — estimate from sim). Width:
```
 W_drv ≈ 12.2 mA / 0.3 mA/µm ≈ 40 µm
```

**Chosen**: driver inverter W_tot ≈ 40 µm (both PMOS and NMOS, since 3.3 V drive isn't mobility-lopsided). Own gate cap ~0.06 pF — driver's own P_gate,self = 0.06p·10.89·2M ≈ 1.3 µW (negligible).

### 4.1 Dead-time re-tuning

The ass-6 dead-time of 10 ns was sized against 2 ns transitions at 5 V. With new 3.3 V drive and smaller FETs, transitions may be faster or slower — **re-sim the transition time and tune deadtime to 2×t_transition + small margin**. Candidate: 5 ns.

Body-diode loss (dominant dead-time cost):
```
 P_dead = V_f · I_L,avg · 2·t_d · f_sw
        = 0.7 · 10 mA · 2 · 5 ns · 2 MHz = 140 µW  ✔ (budget 200 µW)
```

---

## 5. Parasitics & Switch-Node Ringing

### 5.1 The ringing tank

Each chip↔PCB pin contributes 2 nH + 50 mΩ. The switch-node sees:
- L_par,top (PMOS drain → V_in bond)
- L_par,bot (NMOS drain → GND bond)
- L_par,sw (switch node → inductor pin)

Effective loop L_par ≈ 2·2 nH + 2 nH = 6 nH (worst case).

C at switch node = C_oss,PMOS + C_oss,NMOS ≈ 0.3·C_ox·(W_P·L_P + W_N·L_N)
= 0.3·2.9·(1500·0.5 + 3000·0.6) pF = 0.3·2.9·2550 fF = 2.22 pF

Ringing:
```
 f_ring = 1/(2π·√(L_par·C_par)) = 1/(2π·√(6n·2.22p)) = 1/(2π·√(1.33·10⁻²⁰))
        = 1/(2π·1.15·10⁻¹⁰) = 1.38 GHz
```

**Peak ringing amplitude** during a switching transition (energy in the inductor released into the tank):
```
 V_ring,pk ≈ I_L · √(L_par / C_par) = 0.019·√(6n/2.22p) = 0.019·1644 = 31 V
```

**Way above the 1.5 V spec.** Mitigations (in order of implementation ease):

1. **Slow the transition**. A longer t_r, t_f band-limits the dI/dt exciting the tank. Target f_ring/excitation_bandwidth ≫ 10.
   - Slowing to 5 ns transitions costs extra switching loss but dramatically cuts HF content.
2. **R-C snubber across V_sw to GND**. Optimal values:
   ```
    R_snub = √(L_par/C_par) = 1644 Ω   (actually this is for critical damping; pick R < this for active damping)
    C_snub ≈ 4·C_par = 8.9 pF
   ```
   Choose R_snub = 500 Ω, C_snub = 10 pF → damps tank with moderate power dissipation.
3. **Layout**: minimise physical loop area. The 2 nH baseline already assumes reasonable layout; beyond that, requires PCB-level optimisation (not a circuit-design change).
4. **Gate resistor on the fast-switching FET** to slow *only* the transition that causes the worst ringing.

**Strategy for the schematic**:
- Add explicit 2 nH + 50 mΩ pi-model per package connection (V_in pin, GND pin, switch-node pin, V_out pin).
- Start with 5 ns transitions (retune gate driver if needed).
- Add snubber (R_snub 500 Ω, C_snub 10 pF) if sim still shows > 1.5 V ringing.
- Iterate.

### 5.2 Parasitic R impact on conduction

50 mΩ × 2 (per power path, in series) = 100 mΩ added to R_eff. At I_L = 10 mA:
```
 P_parasitic_cond = I² · 0.1 Ω = 10 µW   (negligible at this current)
```

Parasitic R only matters for V_in drop under transient peak currents (ΔV = L_par·dI/dt during switching, not DC). Accounted for in the ringing analysis.

---

## 6. Control Loop

### 6.1 Architecture choice

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| Voltage-mode Type-III | Proven in ass-7, straightforward | 2nd-order plant, Q varies wildly with load | ✔ **Baseline** — port ass-7 loop with retuned corners |
| Peak current-mode + Type II | Built-in line rejection, easy burst integration, 1st-order plant | Needs current sense + slope comp for D > 0.5 (we're at 0.36, so no slope-comp needed) | **Stretch goal** — evaluate if voltage-mode fails |
| Hysteretic / COT | Fastest transient, naturally PFM-friendly | Variable f_sw, EMI concerns | Consider for burst controller sub-block |

**Primary path**: voltage-mode Type-III (reuse ass-7 skeleton).

### 6.2 Loop design for the new plant

Plant: f_LC = 107.3 kHz (from §2.4), Q = 8.1 @ 10 mA.

Specs:
- |L(2 kHz)| ≥ 40 dB   (interference rejection)
- PM > 45° (implicit — more conservative 60° if possible)
- f_UGB < f_sw / π = 636.6 kHz (Berkhout)
- R ≤ 10 MΩ, C ≤ 100 pF (carry over from ass-7)

Feedback divider (V_ref = 1.0 V, V_out = 1.2 V):
```
 R_bot/(R_top + R_bot) = 1.0/1.2 = 0.833
 R_top/R_bot = 0.2
 Pick R_bot = 10 kΩ, R_top = 2 kΩ  →  k_div = 0.833 (−1.58 dB)
```

PWM gain: V_in / V_saw,pp. Brief doesn't fix V_saw for final project — pick **V_saw = 2 V pk-pk** (clean headroom in 3.3 V rail):
```
 PWM gain = 3.3 / 2.0 = 1.65 (+4.3 dB)
```

DC loop factor (non-compensator): k_div · PWM = 0.833 · 1.65 = **1.375 (+2.8 dB)**.

Loop gain at 2 kHz — in integrator region if f_ZEA > 2 kHz:
```
 |L(2k)| = 1.375 · A_mid · (f_ZEA/2k) · 1   (H_LC ≈ 1 at 2 kHz << f_LC)
```

Target ≥ 100 (40 dB):
```
 A_mid · f_ZEA ≥ 100/1.375 · 2000 = 145.5 kHz
```

**Choice**: f_ZEA = 15 kHz, A_mid = 10 → A_mid·f_ZEA = 150 kHz → |L(2k)| = 1.375·10·(15/2) = 103.1 (40.3 dB) ✔

Boost pair around f_LC = 107.3 kHz:
- **f_FZ = 50 kHz** (below f_LC, triggers +20 dB/dec)
- **f_FP = 2 MHz** (ends boost — below f_sw to avoid coupling)
- **f_HF = 4 MHz** or higher (filter HF ripple)

Crossover prediction:
```
 |L(f_LC)| = 1.375 · (10·107.3/50) · 1 · Q ≈ 1.375 · 21.46 · 8.09 = 239 (47.6 dB)
```

From f_LC, slope is −20 dB/dec until f_FP:
```
 f_c = f_LC · 10^(47.6/20) = 107.3·10^2.38 = 107.3·240 = 25.75 MHz   ← WRONG, way above Berkhout
```

That exceeds Berkhout by 40×. Q = 8 is amplifying the crossover way too much. **Need to reduce A_mid drastically** or add damping.

Revised:
- Reduce A_mid: with A_mid = 2, f_ZEA = 50 kHz → |L(2k)| = 1.375·2·(50/2) = 68.75 (36.7 dB) ← fails the 40 dB target.
- Keep A_mid = 10, push f_ZEA lower: f_ZEA = 15 kHz still gives 47.6 dB at f_LC.

**The real issue is Q**. At heavy load (10 mA), Q = 8 causes a 18 dB peak at f_LC. The loop needs to *de-peak* the plant.

**Fix**: place an **LHP zero exactly at f_LC to counter the Q-peak**, not just bracket it. Plus reduce overall gain or add explicit damping.

Alternative cleaner approach: **current-mode control** — collapses the 2nd-order plant to 1st-order → no Q issue. Given the high-Q LC, this is looking increasingly attractive.

### 6.3 Decision point — evaluate both topologies in sim

| Metric | VM Type-III (proposed) | CM Type-II |
|---|---|---|
| Plant order | 2 | 1 (inductor is controlled current source) |
| Q concern | **Big at 10 mA: Q = 8** | None — 1st-order |
| Compensator | Type III, 5 components, 4 corners | Type II, 3 components, 2 corners |
| Line rejection | ~40 dB @ 2 kHz achievable | **~60+ dB @ 2 kHz** (built-in) |
| Slope comp needed? | No | No (D = 0.36 < 0.5) |
| Burst-mode friendliness | Moderate | Good (peak-current clamps intrinsically) |
| Complexity added | Low (port ass-7) | Current sense + comparator (new building block) |

**Recommendation**: start with the Type-III port from ass-7 as a first pass (zero-cost reuse). If the high-Q plant causes marginal PM, migrate to current-mode. Include both evaluations in the report.

### 6.4 Component values (VM Type-III, first draft)

Retargeting ass-7 values for the new plant:

```
 R_top = 2 kΩ,   R_bot = 10 kΩ
 R1 = 100 kΩ
 R2 = 1 MΩ      → A_mid = R2/R1 = 10
 C2 = 1/(2π·R2·f_ZEA) = 1/(2π·1M·15k) = 10.6 pF
 C3 = 1/(2π·R1·f_FZ) = 1/(2π·100k·50k) = 31.8 pF
 R3 = 1/(2π·C3·f_FP) = 1/(2π·31.8p·2M) = 2.5 kΩ
 C1 = 1/(2π·R2·f_HF) = 1/(2π·1M·4M) = 0.04 pF = 40 fF
```

All in bounds (R ≤ 10 MΩ, C ≤ 100 pF).

**Caveat**: these are the *first-pass* values. The Q-peak issue above means PM may be < 60°. Expect to iterate — reduce A_mid, push f_FZ earlier, or migrate to current-mode.

---

## 7. Sleep-Mode / Burst Architecture

### 7.1 Topology choice

**Pulse-skipping (PFM-like) burst mode**:
1. Hysteretic comparator watches V_out vs V_ref_hys_low and V_ref_hys_high
2. V_out falls below V_ref_hys_low → wake converter, run ~N cycles until V_out > V_ref_hys_high
3. Sleep state: disable gate drivers (clock-gate), leave only ref + hysteretic comparator live
4. I_quiescent,sleep ≈ 3 µA (ref + comparator; ideal op-amp draws 0)

### 7.2 Burst parameters

Hysteresis band ΔV_hys = 20 mV (comfortably above output ripple):
```
 V_ref_hys_high = 1.21 V
 V_ref_hys_low  = 1.19 V
```

Energy delivered per burst (to recharge cap from V_lo to V_hi at no load):
```
 E_burst = C · V_out · ΔV_hys = 100n · 1.2 · 20m = 2.4 nJ
```

Sleep duration (at I_load = 10 µA):
```
 t_sleep = C·ΔV_hys / I_load = 100n·20m / 10µ = 200 µs
 f_burst = 5 kHz
```

During burst, run for typically **1–3 switching cycles** at full duty to peak the inductor, then freewheel — this delivers more than enough energy to refill the cap. Peak I_L during burst ~ 40–50 mA (higher than active-mode peak; fine — FETs can handle).

### 7.3 Sleep-mode efficiency

```
 P_in,sleep  = V_in · (I_load + I_q) = 3.3 · 13 µA = 42.9 µW
 P_out,sleep = 1.2 · 10 µA = 12 µW
 η_sleep     = 12/42.9 = 28 %
```

Low, but absolute loss is only 31 µW — well below any continuous-PWM alternative (P_gate alone at 2 MHz = 161 µW). **This is the dominant reason to implement burst.**

### 7.4 Sleep-to-active transition

- Burst wake-up latency: 1 comparator propagation + first switching cycle ≈ 500 ns–1 µs
- Fast enough for the 10 mA load-step tolerance
- In the simulation plan, add a load-step test: 10 µA → 10 mA step, verify V_out doesn't droop below 1.15 V

---

## 8. Interference Rejection — 40 dB @ 2 kHz

Already covered in §6.2: with A_mid = 10, f_ZEA = 15 kHz, |L(2kHz)| ≈ 40.3 dB.

**In simulation**:
1. Add 1 Vpp (or spec's nominal perturbation amplitude — assume 1 Vpp) at 2 kHz to V_in
2. Transient sim, DFT V_out at 2 kHz bin
3. Expected: V_out ripple @ 2 kHz ≈ (D · V_in_pert) / |L| = 0.36 · 1 / 104 = 3.46 mVpp
4. PSRR = 20·log10(3.46m / 1) = −49.2 dB ✔ (below −40 dB)

---

## 9. Schematic Modification Roadmap (from post-ass-7 baseline)

Starting from the ass-7 working schematic (which has the compensator + PWM comparator added per `assignment7_plan.md` §7):

### 9.1 Variables — update to final-project specs

| Variable | Ass-7 value | Final value |
|---|---|---|
| V_in (V0 vdc) | 5.0 V | **3.3 V** |
| V_ref | 1.0 V | **1.0 V** (no change) |
| V_saw,pp | 4.0 V | **2.0 V** |
| L | 10 µH | **22 µH** (or retry 10 µH with DCM) |
| C | 1 µF | **100 nF** |
| RL | 4 Ω | **120 Ω** (10 mA load) |
| fsw | 2 MHz | **2 MHz** (unchanged) |
| deadtime | 10 ns | **5 ns** (retuned) |
| Feedback R_top | 8 kΩ | **2 kΩ** |
| Feedback R_bot | 10 kΩ | **10 kΩ** |
| R1 | 100 kΩ | **100 kΩ** |
| R2 | 700 kΩ | **1 MΩ** |
| R3 | 910 Ω | **2.5 kΩ** |
| C1 | 114 fF | **40 fF** |
| C2 | 45.5 pF | **10.6 pF** |
| C3 | 53 pF | **31.8 pF** |

### 9.2 Power FET resize (reduce from snapshot values)

| Inst | Ass-7 (snapshot) | Final-project |
|---|---|---|
| M0 (Power PMOS) | 500 µm × 300 = 150 mm | **500 µm × 3 = 1.5 mm** (drop totalM from 300 to 3) |
| M1 (Power NMOS) | 500 µm × 100 = 50 mm | **500 µm × 6 = 3.0 mm** (drop totalM from 100 to 6) |

### 9.3 Gate-driver resize

| Inst | Ass-7 | Final-project |
|---|---|---|
| M2, M4 (driver PMOS) | 500 µm × 300 | **W=40 µm, totalM=1** |
| M3, M5 (driver NMOS) | 500 µm × 100 | **W=40 µm, totalM=1** |

### 9.4 Add package parasitics

Insert 2 nH + 50 mΩ series models at four pins:

1. **V_in pin**: between external V_bat source and on-chip V_in rail feeding the power PMOS source
2. **GND pin**: between on-chip gnd! net and external GND
3. **Switch-node pin**: between internal V_PWM node and external inductor terminal
4. **V_out pin**: between external cap/load node and on-chip V_out sensing for feedback

Implement as:
- `analogLib ind` (L = 2 nH) in series with `analogLib res` (r = 50 mΩ)

### 9.5 Add snubber (conditional, after first ringing sim)

Across V_PWM to GND at the chip pin side of the switch-node parasitic:
- R_snub = 500 Ω (analogLib res)
- C_snub = 10 pF (analogLib cap)
- Series R-C network

Only enable if the first ringing sim shows > 1 V pk on V_PWM.

### 9.6 Add sleep-mode logic (stretch)

For a **minimal viable** sleep implementation:
- Hysteretic comparator: ahdlLib comparator with hysteresis, comparing V_out against V_ref_hys_low/high
- Output gates the gate-driver enable (add an AND between PWM comparator output and burst-enable)
- Q_quiescent reference + comparator biasing — in ideal-component mode, assume 0 µA; for realistic sim, add `I_q = 3 µA` as a current source on V_in

**Alternative**: skip sleep mode implementation in Cadence (state it as architectural) and just characterise the active-mode efficiency. Discuss sleep in the report as theory-only.

---

## 10. Simulation Plan

### 10.1 Simulations (ordered)

| # | Purpose | Analysis | Notes |
|---|---|---|---|
| 1 | Revert ass-6 specs and confirm open-loop works | tran 0–100 µs | Before adding anything final-project-specific |
| 2 | Add compensator (per ass-7), confirm closed-loop regulation at 5V/1.8V/4Ω | tran 0–1 ms | Ass-7 integration check |
| 3 | Switch to final-project vars (§9.1), confirm regulation | tran 0–1 ms | V_out → 1.2 V |
| 4 | Resize FETs (§9.2–9.3), confirm regulation | tran 0–1 ms | Verify R_on sim'd matches hand-calc |
| 5 | AC Bode with final compensator | ac 1 Hz – 100 MHz | Expect PM check, |L(2 kHz)| check |
| 6 | Efficiency sweep R_L = 12 Ω – 120 kΩ | par + tran | Generate η-vs-P_out curve |
| 7 | Add package parasitics (§9.4), check switch-node ringing | tran, maxstep 100 ps | Expect V_ring measure |
| 8 | Tune snubber (§9.5) if needed | tran | Iterate until V_ring < 1.5 V |
| 9 | 2 kHz interference rejection | tran 0 – 50 ms, DFT | V_out spectrum at 2 kHz |
| 10 | Load step (10 µA → 10 mA → 10 µA) | tran | ΔV_out < 100 mV |
| 11 | (Stretch) Sleep mode: 10 µA load, hysteretic burst | tran 0 – 10 ms | Characterise f_burst and avg P_in |
| 12 | (Stretch) Current-mode topology A/B | ac + tran | If VM shows marginal PM |

### 10.2 Critical measurements & expressions

```
# Efficiency (use direct V_in current)
  P_in  = average( IT("V_in_pin_source") ) · 3.3
  P_out = average( VT("/Vout") · IT("/R0") )  (or use dedicated monitor resistor)
  eta   = P_out / P_in

# Output ripple pk-pk (steady state window)
  dV_pk = peakToPeak(clip( VT("/Vout"), t_start, t_end ))

# Inductor ripple
  dI_L = peakToPeak(clip( IT("/L0/PLUS"), t_start, t_end ))

# Switch-node ringing peak
  V_ring = ymax(VT("/VPWM")) − V_in   (if ringing above V_in)
         + V_in − ymin(VT("/VPWM"))   (if ringing below gnd)
  V_ring_peak = max of above

# Interference rejection @ 2 kHz
  X = dft(VT("/Vout"), t1, t2, 2^N)
  bin_2k = value(X, 2 kHz)
  PSRR_dB = 20·log10(mag(bin_2k) / 0.5)   # 0.5 = amp of 1 Vpp perturbation
```

### 10.3 Convergence / numerical care

- Use `errpreset=conservative` for all transients
- `maxstep = 100 ps` when ringing is of interest, else `maxstep = 10 ns`
- Initial conditions: C0 IC = 0 V (cold start); alternatively IC = 1.2 V to skip warm-up for efficiency measurements
- For long disturbance sims (50 ms), crank maxstep up to 200 ns; use save-only signals to limit disk

---

## 11. Efficiency Target Check (assembled)

Peak-load operating point (10 mA):

| Term | Value |
|---|---|
| P_out | 12.0 mW |
| P_cond = (10 mA)²·3 Ω | 0.30 mW |
| P_sw   = ½·3.3·10 m·4 n·2 M | 0.13 mW |
| P_gate = 7.4 p·3.3²·2 M | 0.16 mW |
| P_dead = 0.7·10 m·10 n·2 M | 0.14 mW |
| P_quiescent (ideal amps assumed) | 0 — 0.1 mW |
| **P_loss_total** | **≈ 0.73–0.83 mW** |
| **η_peak** | **93.5 – 94.3 %** ✔ (target 90 %) |

Margin vs spec: +3.5 – 4.3 percentage points. Achievable.

### 11.1 Efficiency at non-peak loads

| Load | I_L,avg | P_out | P_cond | P_sw | P_gate | P_dead | η |
|---|---|---|---|---|---|---|---|
| 10 mA | 10 mA | 12 mW | 0.30 mW | 0.13 mW | 0.16 mW | 0.14 mW | **94 %** |
| 1 mA | 1 mA | 1.2 mW | 3 µW | 13 µW | 160 µW | 14 µW | 86 % |
| 100 µA | 100 µA | 120 µW | 0.03 µW | 1.3 µW | 160 µW | 1.4 µW | 42 % (active-mode) |
| **10 µA (active mode)** | 10 µA | 12 µW | ~0 | 0.13 µW | **160 µW** | 0.14 µW | **7 %** — unacceptable |
| **10 µA (sleep mode)** | 10 µA avg | 12 µW | — | — | ~f_burst/f_sw fraction = 0.25 % of 160 µW = 0.4 µW | — | **28 %** ✔ |

**→ Sleep mode is not optional**; it is the mechanism by which η stays tolerable at light loads.

---

## 12. Risk Register

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| 1 | High-Q plant destabilises loop at 10 mA | Medium | High — loop marginal | Migrate to current-mode control if VM PM < 45° in sim |
| 2 | Switch-node ringing exceeds 1.5 V | High | High — spec violation | Snubber + slow transitions; iterate in sim |
| 3 | P_gate dominates and η < 90 % | Low-Medium | Medium | Already budgeted; re-resize FETs downward if tight |
| 4 | Sleep-mode implementation in Cadence too complex | Medium | Medium — may need to theorise | Discuss architecturally in report; simulate minimal burst-pulse proxy |
| 5 | 100 nF cap insufficient for load-step transient | Low | Medium | Bump C to 220 nF; re-check f_LC and compensator |
| 6 | 22 µH + 100 nF LC resonance (107 kHz) couples with 2 kHz interference non-linearly | Very low | Low | Spectral analysis in disturbance sim |
| 7 | TSMC 5V model at V_GS = 3.3 V has higher-than-expected R_on | Medium | Medium | Re-extract R_on at 3.3 V drive; may need to widen FETs 1.5× |
| 8 | Parasitic-induced V_in drop shifts operating point during transient | Low | Low | Budget extra 50 mV V_in headroom; not a steady-state issue |

---

## 13. Deliverables Checklist

For the final-project report/presentation:

- [ ] **Architecture diagram** — block-level with control loop, sleep logic, parasitics
- [ ] **Design decision log** — why f_sw = 2 MHz, why L = 22 µH, why C = 100 nF (table)
- [ ] **Power FET sizing analysis** — W-sweep showing optimum
- [ ] **Gate driver sizing** — transition-time and P_gate trade
- [ ] **Loop design** — Type-III (or current-mode) with Bode plot + PM + 2 kHz gain
- [ ] **Efficiency curve** — η vs P_out across 10 µA → 10 mA range, showing peak and sleep-mode inflection
- [ ] **Switch-node ringing** — with and without snubber, showing < 1.5 V
- [ ] **Interference rejection** — V_out FFT with 1 Vpp @ 2 kHz perturbation, showing ≥ 40 dB attenuation
- [ ] **Sleep-mode operation** — waveforms of burst cycle (optional — theoretical discussion if sim not feasible)
- [ ] **Loss breakdown at peak** — pie chart / table of P_cond, P_sw, P_gate, P_dead, P_q
- [ ] **Parasitic model justification** — 2 nH + 50 mΩ per connection, all pins annotated
- [ ] **White-background plots, large fonts** (explicit spec)

---

## 14. Rough Timeline (assuming ass-7 is done)

| Phase | Tasks | Est. time |
|---|---|---|
| A. Retarget schematic to final specs | §9.1 – §9.3 variable swaps; first regulation sim | 1–2 h |
| B. Add parasitics, first ringing sim | §9.4; observe V_ring; add snubber if needed | 2–3 h |
| C. Retune compensator for new plant | §6 — first Bode, adjust if PM marginal | 3–5 h |
| D. Efficiency sweep across load range | Simulation #6; aggregate into η-vs-P_out plot | 2 h |
| E. Interference rejection sim | Simulation #9; 50 ms transient + DFT | 1 h (+ overnight compute) |
| F. Load step, transient verification | Simulation #10 | 1 h |
| G. (Stretch) Sleep mode / burst | Simulation #11 — hysteretic comparator + disable logic | 3–6 h |
| H. (Stretch) Current-mode evaluation | Simulation #12 — only if PM < 45° in VM | 4–6 h |
| I. Compile report + deck | Tables, plots, discussion | 4–6 h |
| **Total** | | **≈ 17 – 30 h** |

---

## 15. Summary — the "napkin version"

**Buck specifics**: 3.3 → 1.2 V @ 10 mA / 10 µA, f_sw = 2 MHz, L = 22 µH, C = 100 nF, power PMOS 1.5 mm / NMOS 3 mm.
**Loop**: voltage-mode Type-III first (port from ass-7 with new corner frequencies to match f_LC = 107 kHz); fall back to current-mode if Q = 8 destabilises.
**Sleep**: hysteretic burst at ~5 kHz with 20 mV band; disables gate drivers; yields 28 % η at 10 µA (vs 7 % in continuous PWM).
**Parasitics**: 2 nH + 50 mΩ per pin; add RC snubber (500 Ω + 10 pF) across switch node to tame the 1.4 GHz ringing tank.
**Expected peak η**: 93–94 %, comfortably above 90 % target.
**Main risk**: high-Q LC destabilising voltage-mode loop — backup is current-mode migration.
