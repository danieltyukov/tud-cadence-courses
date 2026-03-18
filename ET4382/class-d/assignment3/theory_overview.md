# Assignment 3A Theory Overview — Class-D Output Stage

## The Big Picture

We're designing the power output stage of a Class-D amplifier — the circuit that drives a speaker (4Ω load) efficiently from a 12V supply.

---

## Parts 1-5: Single Half-Bridge

A **half-bridge** is two big NMOS power switches (nld12_g5a_nbl_mac) stacked between 12V and GND. They alternate switching, producing a square wave at the `sw` node that toggles between 0V and 12V.

### Supporting Circuitry

| Block | What it does |
|-------|-------------|
| Non-overlap generator (NAND + INV) | Ensures both switches are never ON simultaneously (prevents shoot-through) |
| Dead time (5ns) | Brief gap where both FETs are OFF during transitions |
| Gate drivers (PMOS + NMOS inverters) | Provide enough current to switch the big power FETs fast |
| Level shifters (vcvs) | High-side gate references to `sw` node (which bounces 0-12V), not ground |

### Part-by-Part Summary

- **Part 1 — PowerFET Sizing:** Find the number of fingers so R_ON ≤ 50mΩ at 150°C
- **Part 2 — V_TH and Q_G:** Extract threshold voltage (DC sweep) and total gate charge (transient with current integration)
- **Part 3 — Gate Driver Sizing:** Size the CMOS inverter drivers for ~25ns rise/fall at the power FET gate. Skew W_NMOS >> W_PMOS to prevent shoot-through from Cgd coupling
- **Part 4 — Dead Time & Level Shifting:** 5ns dead time via ahdlLib logic gates, vcvs level shifter for high-side
- **Part 5 — Half-Bridge Verification:** Run with ±2A load current, verify clean switching, no shoot-through, proper dead time

### Soft vs Hard Switching (Part 5)

| | Soft Switching (+2A out) | Hard Switching (-2A in) |
|---|---|---|
| Load current | Assists the transition | Resists the transition |
| dVsw/dt | Faster | Slower |
| Body diode | Conducts after transition | Conducts during dead time |
| Reverse recovery | No | Yes |
| VgsH during dead time | Stays low | Rises due to Cgd coupling (shoot-through risk) |

---

## Part 6: BTL (Bridge-Tied Load)

### Why BTL?

A single half-bridge gives a **single-ended** output: `sw` toggles 0↔12V with a DC average of 6V. A speaker would see 6V DC offset — bad.

**BTL** duplicates the half-bridge and drives the load **differentially:**

```
Half-bridge A: sw_A toggles 0↔12V    ──┐
                                        ├── Load sees: sw_A - sw_B
Half-bridge B: sw_B toggles 0↔12V    ──┘
```

With **AD-PWM**, when A goes HIGH, B goes LOW (and vice versa):
- A=12V, B=0V → load sees +12V
- A=0V, B=12V → load sees -12V

**Result:** Differential output swings ±12V with zero DC offset. Double the voltage swing = 4× the power compared to single-ended.

### AD-PWM Control

- Half-bridge A is driven by PWM signal
- Half-bridge B is driven by **inverted** PWM signal
- In practice: swap O+ and O- connections for the second half-bridge
- No extra non-overlap generator needed — dead time is already in both signals

### LC Filter

The `sw` nodes are square waves at 1 MHz (fsw). The speaker only wants audio (20Hz-20kHz). The LC filter (L=18μH, C=820nF from Assignment 1A) is a low-pass:
- Passes the audio content
- Blocks the 1 MHz switching frequency
- Each half-bridge gets its own LC filter before connecting to the load

### What to Test

1. **Zero modulation (mi=0):** Both sides at 50% duty, inverted. Differential output ≈ 0V after filtering. Common-mode = constant 6V (property of AD-PWM).

2. **Efficiency vs modulation index:** Sweep mi from 0 to 0.9 (0 = silence, 0.9 = loud). Efficiency = P_load / (P_VSUP + P_VREG).

---

## Power Loss Breakdown

Three loss mechanisms in Class-D:

### P_R — Conduction Loss
- I² × R_ON through the power switches
- Increases with load current (higher mi)
- P_R_sig = P_OUT × R_ON / R_LOAD
- P_R_rip = (1/3) × (V_SUP / (8 × L × f_SW))² × R_ON

### P_Q — Gate Charge Loss
- Energy to switch gates ON/OFF every cycle
- P_Q = f_SW × 2 × V_SUP × (Q_GL + Q_GH) per half-bridge
- ×2 for BTL
- Roughly constant — dominates at low output power
- Includes gate driver inverter self-consumption

### P_X — Switching (Transition) Loss
- Overlap of voltage and current during switching transitions
- P_X = f_SW × t_x × V_SUP × (I_OUT + I_RR)
- Only during hard switching
- Increases with load current

### Efficiency Formula

```
η = P_load / (P_VSUP + P_VREG)

P_VSUP = V_SUP × average(I_VSUP)
P_VREG = V_REG × average(I_VREG)    ← don't forget gate driver current
P_load = average(V_diff × I_load)    or V_out_rms² / R
```

---

## Part 7: 4× Gate Driver Size

Bigger drivers switch the power FETs faster. The tradeoff:

| | Smaller drivers (1×) | Bigger drivers (4×) |
|---|---|---|
| Switching speed | Slower | ~4× faster |
| P_X (switching loss) | Higher | Lower |
| P_Q (gate charge loss) | Lower | Higher (4× more driver capacitance) |
| P_R (conduction loss) | Same | Same (same power FETs) |

**Net effect on efficiency:**
- **Low mi** (small load current): P_Q dominates → 4× drivers = worse efficiency
- **High mi** (large load current): P_X dominates → 4× drivers = better efficiency
- There's a **crossover point** where bigger drivers become beneficial

Plot both efficiency curves and identify where they cross.

---

## Key Design Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| V_SUP | 12V | Given |
| V_REG | 5V | Given |
| f_SW | 1 MHz | Given (Assignment 1A) |
| R_LOAD | 4Ω | Given |
| L_filter | 18μH | Assignment 1A |
| C_filter | 820nF | Assignment 1A |
| R_ON target | ≤ 50mΩ at 150°C | Given |
| Dead time | 5ns | Given |
| Gate rise/fall | ~25ns | Target |
| PowerFET | nld12_g5a_nbl_mac | TSMC 0.18μm BCD |
| Gate driver | nmos5v_mac + pmos5v_mac | TSMC 0.18μm |
