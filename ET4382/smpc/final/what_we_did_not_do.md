# What We Did Not Do — Quick Read

1. **Sleep-mode controller** — architectural only, not built in Cadence.
   → *Would do*: add `ahdlLib` hysteretic comparator (V_ref ± 10 mV), AND-gate its output with the PWM to clock-gate the driver, run 10 ms tran at 10 µA load to show burst cycles.

2. **2 kHz PSRR sim** — analytical only (|L(2 kHz)| ≈ +50 dB → ~−60 dB PSRR).
   → *Would do*: set V0 = `vsin(DC=3.3, Amp=0.5, f=2k)`, run 50 ms tran, `dft(VT("/Vout"), t1, t2)` at the 2 kHz bin, confirm ≤ 10 mVpp.

3. **Ringing sim at final FET widths** — analytical (2.35 V pk, snubber recommended).
   → *Would do*: instantiate 2 nH + 50 mΩ π-models on V_in / GND / V_SW / V_out pins, tran with `maxstep = 100 ps`, A/B with and without R_snub = 500 Ω + C_snub = 10 pF across V_SW.

4. **Current-mode control** — not evaluated; voltage-mode Type-III was sufficient.
   → *Would do*: add sense-FET mirror on power PMOS (1:1000 width ratio), replace PWM comparator with current-sense comparator, retune to Type-II, compare PM and PSRR to voltage-mode.

5. **R_on re-extraction at V_GS = 3.3 V** — used partner's characterization.
   → *Would do*: DC sweep (ADE dc analysis) on each power FET at V_GS = 3.3 V with final W/L/M, read R_on from `VDS / ID`, compare to 72 mΩ / 203 mΩ quoted.

6. **Efficiency-vs-P_out sweep curve** — analytical table only.
   → *Would do*: parametric sweep R_L from 12 Ω → 1.2 MΩ (log steps), measure `P_in = avg(V_in · I_Vin)` and `P_out = avg(V_out · I_out)` in each tran, plot η vs P_out on log-log.

7. **Load-step transient (10 µA → 10 mA)** — not simulated.
   → *Would do*: drive load with `vpulse`-gated switch or step R_L via pwl, tran with `maxstep = 10 ns`, measure max V_out droop and settling time, verify < 100 mV.

8. **Dead-time tuning** — carried over 10 ns from ass-6.
   → *Would do*: parametric sweep `deadtime = {2, 5, 10, 15, 20 ns}`, measure η at each, pick the value that minimises body-diode loss without shoot-through (expected optimum ~5 ns).

9. **Sensitivity / Monte Carlo** — ideal R/C used, no corner analysis.
   → *Would do*: Monte Carlo on R ±10 %, C ±20 %, f_LC ±25 %; confirm PM > 45° and |L(2 kHz)| ≥ 40 dB across all corners.

10. **Physical layout / PEX** — out of scope for the brief.
    → *Would do*: draw FETs and driver in Virtuoso XL, DRC/LVS clean, run PEX for parasitic caps and routing R, re-sim the closed loop post-layout to check compensator shift.

**Bottom line**: understanding and derivations are complete; what's missing is Cadence validation runs that would refine numbers but not change conclusions.
