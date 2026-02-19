# Homework Assignment 1A - Class-D Amplifier

## Part 1: LC Lowpass Filter Design

### Specifications
- Load impedance: R = 4Ω
- Attenuation @ 1MHz: >50dB
- Quality factor: 0.7 < Q < 1.0
- Component values: E12 series
- Tolerances: ±10% (inductor), ±20% (capacitor)

### Circuit Topology
```
Vac ──── L (series) ──── Vout
                           |
                      C ║ R=4Ω  (both shunt to GND)
                           |
                          GND
```
- L is in SERIES with the signal path
- C is in PARALLEL with R (both shunt to GND)

### Formulas
- Corner frequency: f₀ = 1 / (2π√(LC))
- Quality factor: Q = R√(C/L)
- Attenuation (f >> f₀): ≈ 40·log10(f/f₀) dB

### Calculation
- Target f₀ ≈ 41 kHz (margin for tolerances, need f₀ ≤ 56 kHz nominally)
- L = R / (2πf₀Q)
- C = Q / (2πf₀R)

### Selected E12 Values
| Component | Value |
|-----------|-------|
| L         | 18 μH |
| C         | 820 nF (0.82 μF) |
| R (load)  | 4 Ω   |

### Nominal Performance
- f₀ = 1/(2π√(18μ × 820n)) = **41.4 kHz**
- Q = 4√(820n/18μ) = **0.854**
- Attenuation @ 1MHz = 40·log10(1e6/41430) = **55.3 dB**

### Worst-Case Tolerance Analysis
| Corner | L | C | f₀ (kHz) | Q | Atten @ 1MHz (dB) |
|--------|------|-------|----------|-------|---------------------|
| Nominal | 18μH | 820nF | 41.4 | 0.854 | 55.3 |
| L-10%, C-20% | 16.2μH | 656nF | 48.8 | 0.986 | 52.4 |
| L+10%, C+20% | 19.8μH | 984nF | 36.2 | 0.728 | 58.9 |
| L-10%, C+20% | 16.2μH | 984nF | 39.9 | 0.986 | 55.0 |
| L+10%, C-20% | 19.8μH | 656nF | 44.1 | 0.728 | 53.1 |

- Q range: **0.73 – 0.99** → within 0.7–1.0 ✓
- Min attenuation: **52.4 dB** → >50 dB ✓

### Cadence Components (all from analogLib)
| Component | Cell | Value |
|-----------|------|-------|
| AC source | vsource | AC mag = 1 |
| Inductor | ind | 18u |
| Capacitor | cap | 820n |
| Resistor | res | 4 |
| Ground | gnd | — |

### Simulation Results (AC Analysis)
- Analysis: AC, 10 Hz – 10 MHz, logarithmic, 100 pts/decade
- Output expression: `dB20(VF("/Vout"))` (magnitude), `phase(VF("/Vout"))` (phase)

| Parameter | Calculated | Simulated |
|-----------|-----------|-----------|
| f₀ (natural frequency) | 41.4 kHz | — |
| f₋₃dB | ~48.3 kHz | 48.66 kHz |
| Q | 0.854 | confirmed by Bode shape (no peaking) |
| Attenuation @ 1MHz | 55.3 dB | 55.45 dB |

Note: f₋₃dB > f₀ because Q > 0.707 (Butterworth). Both are valid corner frequency definitions.

### Screenshots (Part 1)
- `part1_schematic.png` — LC filter schematic in Cadence Virtuoso
- `part1_bode_plot.png` — Bode plot (magnitude + phase) with markers at f₋₃dB and 1MHz

---

## Part 2: Double-Sided PWM Generator

### Circuit
- Comparator (`comparator` from ahdlLib): sigout_high=10, sigout_low=-10
- Triangle carrier (`vpulse` from analogLib): V1=-1, V2=1, Rise=499n, Fall=499n, Width=1p, Period=1u
- Sine input (`vsin` from analogLib): variable amplitude and frequency
- LC filter + 4Ω load (same as Part 1)
- Transient analysis: 5ms, conservative accuracy
- Spectrum expression: `dB20(dft(VT("/Vout") 1m 5m 4096))`

### Simulation Results

#### 1kHz, 0.1 FS
- Vout: ~±1V sine (0.1 × 10V), clean after initial transient
- Spectrum: strong peak at 1kHz, higher frequencies attenuated by LC filter
- LC filter passes 1kHz signal within passband as expected

#### 1.001 MHz (fPWM + 1kHz), 0.1 FS
- Vout: almost no output — nearly flat
- The input frequency is right at the PWM carrier frequency
- The LC filter attenuates everything near 1MHz by >50dB
- Demonstrates the filter effectively removing carrier-frequency content

#### 2.001 MHz (2fPWM + 1kHz), 0.1 FS
- Vout: a 1kHz sine appears in the output!
- The signal aliases back to 1kHz through the double-sided PWM process
- Double-sided PWM (triangle carrier) creates sidebands around even harmonics (2fPWM)
- These fold back into baseband, producing a 1kHz component that passes through the LC filter
- This is a key property of double-sided (naturally-sampled) PWM

#### 1kHz, 0.9 FS
- Vout: large ~±9V sine wave (0.9 × 10V)
- Clean sinusoidal shape visible in time domain
- Near full modulation — PWM pulse widths vary from very narrow to very wide
- Spectrum shows dominant 1kHz fundamental

### Screenshots (Part 2)
- `part2_schematic.png` — PWM + LC filter schematic
- `part2_spectrum_1kHz_01FS.png` — 1kHz input, 0.1 FS (time + spectrum)
- `part2_spectrum_1001kHz_01FS.png` — fPWM+1kHz input, 0.1 FS
- `part2_spectrum_2001kHz_01FS.png` — 2fPWM+1kHz input, 0.1 FS
- `part2_spectrum_1kHz_09FS.png` — 1kHz input, 0.9 FS

## Part 3: Two-Phase PWM

### Circuit
- Two comparators (`comparator` from ahdlLib): sigout_high=10, sigout_low=-10
- Two triangle carriers (`vpulse`): same parameters as Part 2, but Phase 2 delayed by 500ns (T/2)
- DC input (`vdc` from analogLib): voltage = `mi` (design variable for modulation index)
- Two inductors: L1 = L0 = 18μH, each with 1mΩ series resistor (to avoid rigid branch loop)
- Shared LC output: C = 820nF, R = 4Ω
- Parametric sweep: `mi` from 0 to 0.9, 10 linear steps
- Transient analysis: 5ms, conservative accuracy

### Circuit Topology
```
        Phase 1                         Phase 2
vdc(mi) ─┬─ comparator ─ VPWM1         vdc(mi) ─┬─ comparator ─ VPWM2
vpulse ──┘  (±10V)     │               vpulse ──┘  (±10V)     │
   (delay=0)           │              (delay=500n)             │
                   L1=18μH                                L0=18μH
                       │                                       │
                   R1=1mΩ                                  R2=1mΩ
                       │                                       │
                       └───────────┬───────────────────────────┘
                                   │ (Vout)
                              C=820nF ║ R=4Ω
                                   │
                                  GND
```

### Analytical Ripple Calculation

**Parameters:**
- Supply: Vdd = 10V (comparator outputs ±10V)
- PWM frequency: fPWM = 1MHz → T = 1μs
- Inductor: L = 18μH per phase
- Duty cycle: D = (1 + mi) / 2
- Output voltage: Vout = mi × Vdd = 10 × mi

**Single-phase peak-to-peak inductor ripple:**

ΔI_1ph = 2 × Vdd × D × (1−D) × T / L = 20 × (1−mi²)/4 × T / L = **5(1−mi²) / 18** [A]

**Two-phase combined peak-to-peak ripple (D ≥ 0.5):**

With 180° interleaving, during each half-period there is an overlap interval (D−0.5)×T where both phases are HIGH, and a non-overlap interval (1−D)×T where one is HIGH and one is LOW. The combined current rises during overlap and falls during non-overlap, giving:

ΔI_2ph = 2 × (Vdd − Vout) / L × (D − 0.5) × T = **10 × mi × (1−mi) / 18** [A]

**Ripple reduction factor:**

ΔI_2ph / ΔI_1ph = 2mi / (1+mi)

At mi = 0: perfect cancellation (ratio = 0). At mi = 1: no benefit (ratio = 1).

### Peak-to-Peak Ripple vs Modulation Index

| mi | D | ΔI_1ph (mA) | ΔI_2ph (mA) | Reduction |
|----|-------|-------------|-------------|-----------|
| 0.0 | 0.500 | 278 | 0 | 100% |
| 0.1 | 0.550 | 275 | 50 | 82% |
| 0.2 | 0.600 | 267 | 89 | 67% |
| 0.3 | 0.650 | 253 | 117 | 54% |
| 0.4 | 0.700 | 233 | 133 | 43% |
| 0.5 | 0.750 | 208 | 139 | 33% |
| 0.6 | 0.800 | 178 | 133 | 25% |
| 0.7 | 0.850 | 142 | 117 | 18% |
| 0.8 | 0.900 | 100 | 89 | 11% |
| 0.9 | 0.950 | 53 | 50 | 5% |

### Key Observations
- Single-phase ripple is maximum at mi = 0 (278 mA) and decreases with mi
- Two-phase combined ripple is **zero at mi = 0** (perfect cancellation) and peaks at mi = 0.5 (139 mA)
- Two-phase always has equal or lower ripple than single-phase
- Maximum single-phase ripple (278 mA) is 2× the maximum two-phase ripple (139 mA)
- The benefit of interleaving is greatest at low modulation indices (idle/low-power operation)

### Simulation Results
- Parametric sweep confirms analytical predictions
- IT("/L1/PLUS"): individual phase current with triangular ripple, DC level = mi×Vdd/(2R)
- IT("/L0/PLUS"): similar to Phase 1 but shifted by T/2
- IT("/L1/PLUS") + IT("/L0/PLUS"): combined load current showing reduced ripple
- At mi = 0: combined ripple visually near zero ✓
- Ripple increases for higher mi values as expected ✓

### Screenshots (Part 3)
- `part3_schematic.png` — Two-phase PWM schematic
- `part3_inductor_currents.png` — Parametric sweep: individual + combined inductor currents vs mi
