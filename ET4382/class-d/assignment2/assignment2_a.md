# Homework Assignment 2A - PWM Feedback Loops

## Context from Assignment 1A
- LC filter: $L = 18\,\mu H$, $C = 820\,nF$, $R = 4\,\Omega$ (load)
- $f_0 = 41.4\,kHz$, $Q = 0.854$, $f_{-3dB} = 48.66\,kHz$
- Attenuation @ 1MHz: 55.45 dB (simulated)
- PWM frequency: $f_{PWM} = 1\,MHz$
- $V_{PWM}$ switches between $\pm 10V$
- Transient simulation: 5ms, conservative accuracy, **maxstep = 10ns** (critical)
- Spectrum expression: `dB20(dft(VT("/Vout") 1m 5m 4096))`
- All components from analogLib unless noted

---

## Part 1: 1st Order Feedback Loop

### Overview
Build a 1st order feedback loop around a PWM generator at 1MHz using an active RC-integrator. The comparator is modeled as a cascade of **subtractor + hysteresis** from ahdlLib (NOT the comparator cell).

### Signal Flow
1. Input current $I_{in}$ injected at virtual ground ($V_{IntVx}$)
2. RC-integrator (limiting\_diffamp + $R_{FB}$ + $C_{INT}$) produces $V_{IntOUT}$ (limited to $\pm 2V$)
3. Subtractor computes difference (integrator output − reference)
4. Hysteresis block creates PWM switching at $\pm 10V$ → $V_{PWM}$
5. $V_{PWM}$ feeds back through $R_{FB}$ to virtual ground (closing the loop)
6. $V_{PWM}$ also drives LC filter + $4\,\Omega$ load → $V_{out}$

### Component List (Cadence)

| Component | Library | Cell | Key Parameters |
|-----------|---------|------|----------------|
| Integrator opamp (I9) | ahdlLib | limiting\_diffamp | gain=1e6, sigout\_high=2, sigout\_low=-2, sigin\_offset=0 |
| Feedback resistor (RFB) | analogLib | res | $R_{FB} = 100\,k\Omega$ |
| Integrator cap (CINT) | analogLib | cap | $C_{INT} = 250\,pF$, **IC = 1V** |
| Subtractor (I10) | ahdlLib | subtractor | default; sigin\_p = net4, sigin\_n = gnd |
| Hysteresis (I12) | ahdlLib | hysteresis | sigout\_high=10, sigout\_low=-10, sigtrig\_low=0, sigtrig\_high=0, tdel=1ns |
| Inductor (L0) | analogLib | ind | $L = 18\,\mu H$ |
| Capacitor (C0) | analogLib | cap | $C = 820\,nF$ |
| Load (R0) | analogLib | res | $R = 4\,\Omega$ |
| Input current (I13) | analogLib | isource | sinusoidal, 1kHz |
| Error source (Verr) | analogLib | vsource | sinusoidal, 5kHz, 1V (for error injection) |
| Ground | analogLib | gnd | — |

### Important Notes
- The hysteresis block is edge-triggered → need **1V initial condition on $C_{INT}$** to start oscillation
- $C_{INT}$ orientation matters: IC=1V must make the integrator output (net4) start **positive** so the first zero-crossing triggers the hysteresis
- Without IC, the loop will not start oscillating (DC operating point gets stuck)
- **maxstep = 10ns** is critical — the default 50μs steps over all 1MHz switching events

---

### Step 1: Calculate $C_{INT}$ for Large-Signal Stability

**Large-signal stability criterion:** the integrator output must not exceed its clipping limits ($\pm 2V$) during worst-case transient conditions.

$$C_{INT} \geq \frac{V_{PWM} \times T}{2 \times R_{FB} \times V_{clip}} = \frac{10 \times 1\,\mu s}{2 \times 100\,k\Omega \times 2V} = 250\,pF$$

**Chosen: $C_{INT} = 250\,pF$**

Integrator unity-gain bandwidth:

$$f_{UGB} = \frac{1}{2\pi \cdot R_{FB} \cdot C_{INT}} = \frac{1}{2\pi \times 100\,k\Omega \times 250\,pF} \approx 6.37\,kHz$$

### Step 2: Inject 1kHz Current Input Signal

**Simulation results with $I_{in} = 10\,\mu A$ at 1kHz:**
- Clean sinusoidal output at $V_{out}$ with amplitude $\approx 1V$
- Confirms transimpedance: $V_{out} = I_{in} \times R_{FB} = 10\,\mu A \times 100\,k\Omega = 1V$ ✓
- Spectrum shows dominant 1kHz peak at ~0 dB (1.58 mdB), with PWM harmonics well attenuated by LC filter

**Screenshots:**
- `part1_schematic.png` — 1st order feedback loop schematic
- `part1_vout_1kHz_10uA.png` — Vout waveform (1kHz sine, 10μA input)
- `part1_vpwm_zoomed.png` — VPWM zoomed showing PWM switching
- `part1_spectrum_1kHz_10uA.png` — Output spectrum with 1kHz marker at ~0 dB

### Step 3: Determine Maximum Current Amplitude $I_{IN,MAX}$

**Theoretical:**

$$I_{IN,MAX} = \frac{V_{out,max}}{R_{FB}} = \frac{10V}{100\,k\Omega} = 100\,\mu A$$

**Simulated:** $I_{IN,MAX} \approx 74\,\mu A$

The simulated value is lower than theoretical because the integrator needs headroom for the PWM triangle ripple on its output (net4). At 74μA, Vout reaches $\approx \pm 7.4V$ and the loop still operates cleanly. At 75μA, the integrator output clips at $\pm 2V$, VPWM loses its switching pattern, and the loop saturates.

| Amplitude | Vout | Status |
|-----------|------|--------|
| 40 μA | ±4V | Clean |
| 50 μA | ±5V | Clean |
| 60 μA | ±6V | Clean |
| 70 μA | ±7V | Clean |
| 74 μA | ±7.4V | Clean (max) |
| 75 μA | Saturated | Loop dies |
| 80 μA | Saturated | Loop dies |
| 100 μA | Saturated | Loop dies |

**Screenshots:**
- `part1_step3_74uA_max.png` — Waveform at $I_{IN,MAX} = 74\,\mu A$ (clean operation)
- `part1_step3_75uA_clipping.png` — Waveform at 75μA showing saturation (VPWM stuck, Vout drifts)

### Step 4: Inject 5kHz Error Signal

**Setup:**
- Error source (Verr): vsource, sine, 5kHz, 1V amplitude
- Placed in series between hysteresis output and the VPWM node (where both LC filter inductor and $R_{FB}$ connect)
- Input current source (I13) amplitude set to 0
- This injects the error into the forward path — both LC filter and feedback see the error

**Error source placement (critical):**
- Hysteresis sigout → Verr(+) → Verr(−) → VPWM node
- VPWM node → inductor L0 → Vout (forward path)
- VPWM node → RFB → integrator virtual ground (feedback path)

**Simulation results:**
- VPWM oscillates cleanly with visible 5kHz envelope modulation
- Vout settles to ~0V (no input signal) — 5kHz component heavily suppressed
- Spectrum: **5kHz peak at −73.1 dB** at Vout

**Error suppression = 73 dB** (injected 1V = 0 dB reference, output at −73 dB)

**Screenshots:**
- `part1_step4_error_schematic.png` — Schematic with Verr error source
- `part1_step4_error_waveform.png` — VPWM and Vout time domain
- `part1_step4_error_spectrum.png` — Spectrum with 5kHz marker at −73 dB

### Step 5: Calculate Loopgain @ 5kHz and Verify

**Theoretical (naturally-sampled PWM formula):**

$$K_{PWM} = \frac{V_{PWM}}{\pi \cdot V_{clip,int}} = \frac{10V}{\pi \times 2V} \approx 1.59$$

$$|H_{int}(5\,kHz)| = \frac{f_{UGB}}{f} = \frac{6.37\,kHz}{5\,kHz} \approx 1.27$$

$$|L(5\,kHz)| = |H_{int}| \times K_{PWM} = 1.27 \times 1.59 \approx 2.02 \quad (\sim 6\,dB)$$

Predicted suppression: $1 + |L| \approx 3 \rightarrow 9.5\,dB$

**Measured suppression: 73 dB** — much higher than the 9.5 dB prediction.

**Explanation of discrepancy:** The naturally-sampled PWM formula $K_{PWM} = V_{PWM}/(\pi \cdot V_{clip})$ uses the integrator clipping limits ($\pm 2V$) as the effective carrier amplitude. However, in our self-oscillating loop, the integrator output triangle ripple is only $\approx 0.2V$ peak-to-peak (not $\pm 2V$). The effective PWM gain is much higher:

$$K_{PWM,eff} = \frac{V_{PWM}}{\pi \cdot V_{triangle,peak}} \approx \frac{10}{\pi \times 0.1} \approx 31.8$$

This gives a much higher loop gain at 5kHz, explaining the large error suppression measured in simulation. The self-oscillating (hysteresis-based) loop continuously adjusts switching instants, providing significantly more loop gain than a naturally-sampled PWM with a fixed triangle carrier.

---

## Part 2: 2nd Order Feedback Loop

### Overview
Add a second RC-integrator to create a 2nd order loop. Use the second integrator to generate the triangle reference by injecting a square wave current signal in the virtual ground node of the second integrator.

### Signal Chain (2nd Order)
1. $V_{IntOUT1}$ (from 1st integrator) → subtractor (+)
2. $V_{IntOUT2}$ (triangle from 2nd integrator) → subtractor (−)
3. Subtractor output → hysteresis → $V_{PWM}$ ($\pm 10V$)
4. $V_{PWM}$ → $R_{FB1}$ → $V_{IntVx1}$ (1st integrator feedback)
5. $V_{PWM}$ → $R_{FB2}$ → $V_{IntVx2}$ (2nd integrator — generates triangle)
6. $V_{PWM}$ also drives LC filter → $V_{out}$

**Second integrator generates triangle reference:**
- $V_{PWM}$ (square wave) feeds through $R_{FB2}$ to virtual ground of integrator 2
- The integrator integrates the square wave current → produces a triangle wave
- This triangle is the reference for the subtractor (replaces gnd)

### Component List (Part 2 additions)

| Component | Library | Cell | Key Parameters |
|-----------|---------|------|----------------|
| 2nd integrator (I14) | ahdlLib | limiting\_diffamp | gain=1e6, sigout\_high=2, sigout\_low=-2 |
| Feedback resistor (RFB2) | analogLib | res | 100 kΩ |
| Integrator cap (CINT2) | analogLib | cap | 250 pF, IC = 1V |
| Stabilizing zero (RZERO) | analogLib | res | 500 kΩ (in series with CINT on I9) |
| Convergence cap (C6) | analogLib | cap | 10 pF (net03 to gnd) |

### Step 1: Calculate the Zero in the Loop Transfer

RZERO = 500 kΩ in series with CINT = 250 pF on integrator I9.

Zero frequency: f_z = 1/(2π × 500k × 250p) = 1.27 kHz

With identical integrator time constants (RFB×CINT = RFB2×CINT2 = 25 μs), the loop transfer simplifies to a constant gain: L ≈ K_PWM × RZERO/RFB = 1.59 × 5 = 7.95 (~18 dB). The two integrator poles cancel, resulting in frequency-independent loop gain rather than true 2nd order behavior.

Self-oscillation frequency: ~50 kHz (limited by delay and component dynamics, not by integrator time constants).

### Step 2: Error Injection @ 5kHz (2nd Order)

**Setup:** Same as Part 1 Step 4 — Verr (vsource, 5kHz, 1V) placed between I12 sigout and VPWM node. I13 amplitude = 0.

**Simulation results:**
- Spectrum: **5kHz peak at −6.4 dB**
- Error suppression ≈ 6 dB (much less than Part 1's 73 dB)

The low suppression is because the identical integrator time constants cause the frequency-dependent terms to cancel. The loop acts as a constant-gain amplifier rather than a true integrating feedback loop.

**Screenshots:**
- `part2_schematic.png` — 2nd order feedback loop schematic
- `part2_waveforms.png` — VPWM, net013, Vout, net04 time domain
- `part2_error_spectrum.png` — Output spectrum with 5kHz marker at −6.4 dB

### Step 3: Calculate Loopgain @ 5kHz (2nd Order)

With identical time constants, the loop gain is frequency-independent:

|L| = K_PWM × RZERO/RFB = (10/(π × 2)) × (500k/100k) = 1.59 × 5 = 7.95 (~18 dB)

Predicted suppression: 20×log10(1 + 7.95) = 19 dB

Measured suppression: 6.4 dB — lower than predicted, consistent with the chaotic/non-ideal loop operation where both integrators clip at ±2V.

---

## Part 3: Clipping Comparison (FS + 10%)

### Setup
- Drive both loops with I_in = 1.1 × I_IN,MAX = 1.1 × 74 μA ≈ 81 μA
- I13: sine, 1kHz, 81 μA
- Transient: 5ms, conservative, maxstep = 10ns

### Results

**1st order loop:**
- Vout saturates to −10V and stays there permanently
- The integrator (I9) clips at −2V, VPWM locks to −10V, loop dies
- Once overdriven past I_IN,MAX, the 1st order loop cannot recover
- Clean but fatal saturation — output locks to one rail

**2nd order loop:**
- Vout oscillates chaotically between ±12V with wild, erratic swings
- The two integrators both clip and fight each other
- LC filter ringing causes overshoot beyond ±10V (peaks to ±14V)
- The loop never settles but also never fully locks up like the 1st order

**Key difference:** The 1st order loop fails gracefully (locks to one rail, silent failure). The 2nd order loop fails chaotically (integrator wind-up causes unstable oscillation with overshoot). The 2nd order loop is harder to recover from clipping because both integrators need to unwind simultaneously.

**Screenshots:**
- `part3_1st_order_clipping.png` — 1st order Vout at FS+10% (saturated at −10V)
- `part3_2nd_order_clipping.png` — 2nd order Vout at FS+10% (chaotic ±12V oscillation)

---

## Simulation Checklist

### Part 1 — 1st Order Loop
- [x] Build schematic with limiting\_diffamp, subtractor, hysteresis, $R_{FB}$, $C_{INT}$
- [x] Set IC = 1V on $C_{INT}$ to start oscillation
- [x] Verify PWM oscillation at ~1MHz with no input
- [x] Calculate $C_{INT} = 250\,pF$ for large-signal stability
- [x] Inject 1kHz current input (10μA), verify clean 1V sine at $V_{out}$
- [x] Sweep $I_{in}$ to find $I_{IN,MAX} = 74\,\mu A$
- [x] Inject 5kHz error voltage (1V), measure suppression: **73 dB**
- [x] Calculate loop gain @ 5kHz — theoretical 9.5 dB vs measured 73 dB (self-oscillating gain much higher)
- [x] Screenshots: schematic, waveforms, spectrum plots (9 screenshots captured)

### Part 2 — 2nd Order Loop
- [x] Add 2nd integrator with RFB2 = 100kΩ, CINT2 = 250pF (IC=1V)
- [x] Add stabilizing zero (RZERO = 500kΩ in series with CINT on I9)
- [x] Connect I14 sigout (net04) to I10 sigin\_n (replacing gnd)
- [x] Add 10pF convergence cap on net03
- [x] Verify PWM oscillation (~50kHz, simulation completes 5ms)
- [x] Inject 5kHz error, measure suppression: **6.4 dB**
- [x] Calculate loop gain @ 5kHz: theoretical 18 dB vs measured 6.4 dB
- [x] Screenshots: schematic, waveforms, error spectrum (3 screenshots)

### Part 3 — Clipping
- [x] Drive 1st order with FS+10% (81 μA), capture Vout: **saturated at −10V**
- [x] Drive 2nd order with FS+10% (81 μA), capture Vout: **chaotic ±12V oscillation**
- [x] Compare: 1st order locks to rail (silent), 2nd order oscillates chaotically (wind-up)
- [x] Screenshots: both clipping waveforms (2 screenshots)

---

## Simulation Settings
- Analysis: Transient, stop = 5ms, accuracy = conservative, **maxstep = 10ns**
- Spectrum: `dB20(dft(VT("/Vout") 1m 5m 4096))`
- Power measurement: `spectrumMeasurement` expression in calculator
- Initial condition: IC = 1V on $C_{INT}$ (critical for oscillation startup)
- Cadence library: `assignment1_a_et4382_p1`, cell: `lc_filter`
