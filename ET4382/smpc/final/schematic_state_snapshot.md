# SMPC1_partB — Schematic State Snapshot (pre-ass-7 rewind)

**Purpose**: Record the current state of the `ClassDMiniProject1 / SMPC1_partB` cell so it can be restored verbatim after Assignment 7 is complete. Assignment 7 requires reverting the buck to its ass-6 specs (5 V / 1.8 V / 4 Ω / 2 MHz / 1 µF); this document captures every variable, device multiplier, and analysis setting that must be put back afterward for final-project work.

**Taken on**: 2026-04-22 (pre-ass-7 start).

---

## 1. Design Variables (ADE "Design Variables" pane)

| Variable | Value | Unit | Meaning / where used |
|---|---|---|---|
| `Von` | 3.3 | V | Logic/PWM "high" level and battery voltage |
| `C` | 6.6 | nF | Output filter cap (C0, small BOM exploration) |
| `L` | 10 | µH | Output filter inductor (L0) |
| `RL` | 120 | Ω | Load resistor (R0) → 10 mA @ 1.2 V |
| `D` | 0.37 | — | Open-loop duty cycle (≈ 1.2 / 3.3 with loss margin) |
| `fsw` | 4 | MHz | PWM switching frequency |
| `deadtime` | 10 | ns | Non-overlap generator dead-time (`tdel` on NAND) |
| `PowerPmosW` | 500 | µm | Power PMOS finger width (M0) |
| `PowerPmosL` | 500 | nm | Power PMOS channel length (M0) |
| `PowerNmosW` | 500 | µm | Power NMOS finger width (M1) |
| `PowerNmosL` | 600 | nm | Power NMOS channel length (M1) |
| `PmosW` | 500 | µm | Gate-driver PMOS per-finger width (M2, M4) |
| `PmosL` | 500 | nm | Gate-driver PMOS length |
| `NmosW` | 500 | µm | Gate-driver NMOS per-finger width (M3, M5) |
| `NmosL` | 600 | nm | Gate-driver NMOS length |

## 2. Power & Gate-Driver Transistor Instances

All use TSMC 180 nm BCD 5 V models (`pmos5v` / `nmos5v`, models `pch_5` / `nch_5`). `fingers:1`; full device width = `w × totalM`.

| Inst | Role | Model | w | l | simM | totalM | Effective W |
|---|---|---|---|---|---|---|---|
| M0 | Power PMOS (HS) | pch_5 | PowerPmosW = 500 µm | 500 nm | 300 | 300 | 150 mm |
| M1 | Power NMOS (LS) | nch_5 | PowerNmosW = 500 µm | 600 nm | 100 | 100 | 50 mm |
| M2 | Gate-drv PMOS (driver stage A) | pch_5 | PmosW = 500 µm | 500 nm | 300 | 300 | 150 mm |
| M3 | Gate-drv NMOS (driver stage A) | nch_5 | NmosW = 500 µm | 600 nm | 100 | 100 | 50 mm |
| M4 | Gate-drv PMOS (driver stage B) | pch_5 | PmosW = 500 µm | 500 nm | 300 | 300 | 150 mm |
| M5 | Gate-drv NMOS (driver stage B) | nch_5 | NmosW = 500 µm | 600 nm | 100 | 100 | 50 mm |

**Note**: Driver here is sized similar to the power FETs — this is oversized for final-project 10 mA loads (will be shrunk during final-project sizing pass).

## 3. Passive / Source Instances

| Inst | Type | Value / Parameters |
|---|---|---|
| L0 | analogLib ind | L = L = 10 µH |
| C0 | analogLib cap | c = C = 6.6 nF |
| R0 | analogLib res | r = RL = 120 Ω |
| V0 | analogLib vdc | vdc = 3.3 V (battery, drives Vss rail) |
| V1 | analogLib vpulse | v1 = Von = 3.3, v2 = 0, tr = 100 p, tf = 100 p, td = 0, period = 1/fsw = 250 ns (4 MHz), open-loop PWM input |
| E0, E1 | analogLib vcvs | egain = 1.0 (level translators between logic and gate-driver rails) |
| I0, I1 | ahdlLib nand_gate | tdel = deadtime = 10 ns (non-overlap pair) |
| I2 | ahdlLib not_gate | input inverter for generating complementary signal |

## 4. Analyses (ADE Explorer "Analyses")

- **Simulator**: spectre
- **Analysis**: `tran` 0 → 320 µs, conservative errpreset
- **Temperature**: 27 °C

## 5. Outputs / Measurements

From the ADE "Outputs" pane:

| Name | Type | Expression | Purpose |
|---|---|---|---|
| `/O+`, `/O-` | signal | — | Non-overlap generator outputs (pre-level-shift) |
| `/VPWM` | signal | — | Switch-node voltage (before L) |
| `/Vout` | signal | — | Regulated output |
| `/net10`, `/net12`, `/net14`, `/net16` | signal | — | Gate-driver internal nodes |
| `/Vss` | signal | — | Battery rail (= 3.3 V) |
| `/gnd!` | signal | — | Reference ground |
| `Iout` | signal | `/L0/PLUS` | Inductor current |
| `Id_Pmos` | signal | `/M0/D` | Power PMOS drain current |
| `Id_Nmos` | signal | `/M1/D` | Power NMOS drain current |
| `VSD_Pmos` | expr | `VT("/Vss") − VT("/VPWM")` | PMOS source-drain voltage (for Ron extraction) |
| `VDS_Nmos` | expr | `VT("/VPWM") − VT("/gnd!")` | NMOS drain-source voltage |
| `IL_avg` | expr | `average(IT("/L0/PLUS"))` | Inductor average current |
| `IL_p2p` | expr | `peakToPeak(clip(IT("/L0/PLUS") …))` | Inductor ripple Δ I_L |
| `Ron_Pmos` | expr | `VSD_Pmos / IT("/M0/D")` | Extracted PMOS on-resistance |
| `Ron_Nmos` | expr | `VDS_Nmos / IT("/M1/D")` | Extracted NMOS on-resistance |
| `Duty` | expr | `VAR("D")` | Passed-through variable for logging |
| `/R0/PLUS` | signal | — | Voltage across load (sanity) |

## 6. Sim Results Observed at Snapshot Time

These values correspond to the state captured in the screenshots. Some are likely stale from a prior run with different R_L (see §7).

| Metric | Reported Value | Comment |
|---|---|---|
| IL_avg | 405.087 mA | ⚠ Stale — inconsistent with R_L = 120 Ω (expected ≈ 10 mA). Matches a prior sim with R_L ≈ 3 Ω. |
| IL_p2p | 56.65 mA | Ripple — consistent with V_in = 3.3 V, V_out ≈ 1.2 V, L = 10 µH, f_sw = 4 MHz. |

## 7. Restoration Procedure (after ass-7)

To bring the schematic back to the snapshot state for final-project exploration:

1. **Design Variables** — copy values from §1 verbatim.
2. **Transistor multipliers** — copy `simM` / `totalM` from §2 into instance property sheets for M0–M5.
3. **Passive/source values** — copy §3 (in particular, V0 vdc = 3.3 V, V1 vpulse parameters, L0 / C0 / R0 values).
4. **Analyses** — restore `tran 0 320 µ conservative` per §4.
5. **Outputs** — §5 expressions (most should persist; re-verify after any net renaming).
6. **Sanity check**: run a fresh transient; expect V_out ≈ 1.22 V, I_L,avg ≈ 10 mA (not 405 mA — the stale result from §6 will be overwritten).

## 8. Stale Data Warning

At snapshot time, the `IL_avg = 405 mA` result does **not** match R_L = 120 Ω and should not be cited. It is left in the ADE output pane because re-running the sim was deferred until after ass-7. When restoration completes (§7), the first action is to re-run the sim and verify I_L,avg ≈ 10 mA.

---

## Quick-copy reference card (paste into Cadence after ass-7)

```
Von        = 3.3
C          = 6.6n
L          = 10u
RL         = 120
D          = 0.37
fsw        = 4M
deadtime   = 10n
PowerPmosW = 500u   PowerPmosL = 500n
PowerNmosW = 500u   PowerNmosL = 600n
PmosW      = 500u   PmosL      = 500n
NmosW      = 500u   NmosL      = 600n

M0 simM/totalM = 300/300   (Power PMOS, pch_5)
M1 simM/totalM = 100/100   (Power NMOS, nch_5)
M2 simM/totalM = 300/300   (Gate-drv PMOS, pch_5)
M3 simM/totalM = 100/100   (Gate-drv NMOS, nch_5)
M4 simM/totalM = 300/300   (Gate-drv PMOS, pch_5)
M5 simM/totalM = 100/100   (Gate-drv NMOS, nch_5)

V0  vdc         = 3.3
V1  vpulse      v1=3.3, v2=0, tr=100p, tf=100p, td=0, period=250n
I0, I1 nand_gate  tdel = deadtime
E0, E1 vcvs       egain = 1.0

tran 0 320u conservative, T = 27 °C
```
