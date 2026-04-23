# SMPC Final Project — Speech Notes (First Person, ~20 min)

**Context**: these notes cover **both** my partner's existing slides (`SMPCMainProject.pdf`) and my supplement (`SMPCMainProject_supplement.pdf`). When merged, the ordering assumed here is partner's deck first, then my supplement. Time budget per section is indicated; total ≈ 20 min.

---

## Part A — Partner's slides (existing deck)   [~8 min]

### Slide — Title
"Hi everyone, I'm Daniel, and my partner Raghavendra and I are presenting our SMPC final project — the design of a 3.3 V to 1.2 V synchronous buck converter in TSMC 180 nm BCD to power an SoC. The SoC draws 10 mA during active operation and 10 µA in sleep, so we had to design for a 1000-to-1 load dynamic range. Our targets were peak efficiency above 90 %, output ripple under 100 mV, switch-node ringing under 1.5 V, and 40 dB of rejection for a 2 kHz interference tone."   [~45 s]

### Slide — First Calculations
"We started by fixing the duty cycle from the ideal buck relation: V_out over V_in gives D = 0.3636. At 10 mA output, R_L equals 120 Ω; at 10 µA it's 1.2 MΩ, which matters later for the sleep-mode discussion. For sizing the inductor and capacitor, we derived the CCM-boundary condition K = 1 − D = 2LF_sw / R_L. That gave us the constraint L·F_sw = 38.184. Separately, the 100 mV ripple spec on the output capacitor gave us C·F_sw = 0.2. We chose f_sw = 4 MHz, which lands L = 9.546 µH and C = 50 nF — in the actual schematic we rounded to L = 10 µH and C = 6.6 nF for realistic external component values."   [~60 s]

### Slide — Schematic
"This is the power stage in Cadence. Top-side synchronous PMOS, bottom-side NMOS, non-overlap gate driver generated from a PWM signal into a NAND-based dead-time circuit, and the LC output filter. Level-shifters sit between the logic rails and the gate-driver rails. For the open-loop version shown here the PWM input is a fixed-duty pulse source."   [~45 s]

### Slide — Vout Plot
"Here's the output voltage settling — you can see it converges to 1.2 V, with the switching ripple visible at the top. Steady-state ripple is within the 100 mV specification."   [~30 s]

### Slide — Ripple Current Plot
"The inductor ripple current shown here is about 20 mA peak-to-peak, which matches our hand calculation: ΔI_L = (V_in − V_out) · D / (L · f_sw) = 2.1 · 0.364 / (10 µ · 4 M) = 19.1 mA. The sim matches theory to within rounding."   [~40 s]

### Slide — Power FET / Gate Driver Sizing
"For the power FETs we swept widths to balance conduction and switching loss. Final sizing: PMOS 400 µm / 500 nm, NMOS 400 µm / 600 nm. At V_GS = 3.3 V we extracted R_on = 72 mΩ for the PMOS and 203 mΩ for the NMOS. That gives an effective series resistance weighted by duty of about 155 mΩ. Using just conduction loss, the theoretical efficiency at peak load is 99.3 % — but that's conduction-only; the full picture including switching, gate-drive, and dead-time losses comes out to around 91 %, which I'll quantify in my half. The gate drivers were sized iteratively to manage the trade-off between transition speed and dI/dt-induced ringing."   [~80 s]

### Slide — Impact of Parasitic Inductances (text)
"The brief specifies 2 nH plus 50 mΩ for every chip-to-PCB connection. We modelled those as a series LR on the battery connection, the ground pin, the switch-node pin, and the load connection. These parasitics form an LC tank with the FET output capacitance, which rings during every switching edge."   [~45 s]

### Slide — Impact of Parasitic Inductances (sim)
"With parasitics added the switch-node shows ringing on both edges. We'll see in my analytical slide that the un-snubbed tank can hit 2+ volts, which exceeds the 1.5 V spec — so an RC snubber is required. I'll cover this in detail in the supplement section."   [~30 s]

### Slide — Final Vout Plot Without Control Loop
"This is the settled open-loop output. Without feedback, V_out sits near 1.2 V only because we picked the duty cycle to match V_in; any perturbation — V_in drift, load change, or the 2 kHz interference tone — would move V_out off target. So we need a control loop, and that's the transition into my part."   [~50 s]

*Hand-off: "Daniel will now take over to cover the control loop, efficiency analysis, and sleep-mode architecture."*

---

## Part B — Supplement (my slides)   [~12 min]

### Slide — Section: Control Loop Design
"Brief transition slide — I'm going to walk through why we need a feedback loop, how we designed the compensator, and the Bode evidence that it meets spec."   [~10 s]

### Slide — Why a Control Loop?
"Two hard requirements from the brief drive the loop design. First, we must regulate V_out at 1.2 V against the 1000-to-1 load swing and against the V_in drift. Second, we must attenuate a 2 kHz interference tone on V_in by at least 40 dB. Open-loop duty cycle only works if V_in is perfectly stable — which by specification it isn't — and if all components are exactly at nominal. So we need closed-loop control. We chose a voltage-mode Type-III compensator because it's the textbook workhorse for buck converters, and because we already had a working implementation from Assignment 7 that we could port with new corner frequencies."   [~60 s]

### Slide — Closed-Loop Schematic
"Here's the full loop. Power stage on the left feeds the LC filter. V_out goes into a resistive divider, then into the inverting input of the Type-III error amplifier, which is built around an ideal op-amp with the R1-R2-R3 and C1-C2-C3 network. The output of C(s) is compared against a 4 MHz sawtooth V_saw to generate the PWM signal, which goes into the non-overlap gate-driver pair and back to the power FETs. Loop closed."   [~50 s]

### Slide — Type-III Topology & Transfer Function
"Why specifically Type-III? The LC plant is second-order — it drops 180° of phase at high frequency, so we need a compensator that restores at least 180° of phase margin. Type-III does that: an integrator for DC gain, two zeros f_ZEA and f_FZ, and two poles f_FP and f_HF. The transfer function is the integrator 1 over s·R1·C2 times a zero-pole pair ratio. The two zeros give up to 180° of phase boost, peaking at the geometric mean of f_FZ and f_FP. We place f_FZ below the LC resonance and f_FP above it, so the phase boost exactly cancels the LC resonance drop at crossover."   [~70 s]

### Slide — Corner Frequency Placement
"The implemented LC in the schematic is 10 µH and 6.6 nF, giving f_LC ≈ 620 kHz. That's much higher than the LC in Assignment 7, so the compensator corners shift up accordingly. Plant Q at 10 mA load is about 3, so there's a ~10 dB peak at f_LC that the compensator has to work with. I placed f_ZEA at 50 kHz — that sets |L(2 kHz)| via the integrator gain. f_FZ at 300 kHz, below f_LC. f_FP at 1.2 MHz, above f_LC. f_HF at 4 MHz, equal to f_sw, to roll off switching ripple. The resulting loop gain at 2 kHz is +50.7 dB — well above the 40 dB spec."   [~70 s]

### Slide — Compensator C(s) Standalone Bode
"This plot is from Assignment 7 — same Type-III topology. You can see the integrator region below f_ZEA, the mid-band A_mid shelf around 17 dB, the +20 dB/dec boost between the two zeros peaking at about +80° of phase, and the high-frequency roll-off. Exactly the textbook Type-III signature. For the final project we scale the corner frequencies up but the shape is identical."   [~45 s]

### Slide — Loop Gain L(s)
"Again from Assignment 7 — this is the full closed-loop Bode measured using Spectre's stb analysis. Marker M1 shows |L| at 200 Hz = +40.36 dB, which satisfies that spec. For the final project's 2 kHz target, the gain is about 20 dB lower because of the +20 dB/dec integrator slope, but the corner placement in our final-project design specifically boosts the integrator so we clear 40 dB at 2 kHz. Marker M2 is the crossover frequency, M3 shows phase margin of 51° — stable with mild underdamping, which is healthy for a fast transient response."   [~70 s]

### Slide — Measured Corner Frequencies
"To confirm the compensator was placed correctly in simulation, I used the ADE Outputs calculator to measure each of the four corners against the design targets. Every corner is within 0.3 % of the target — so the component values translate directly into the intended frequency response. Same methodology applies to the final-project loop."   [~45 s]

### Slide — Interference Rejection Derivation
"The closed-loop transfer from V_in to V_out is just D divided by 1 + L(jω). D is 0.364 open-loop. With |L(2 kHz)| of roughly 340 linear, the ratio becomes 0.364 / 343 = 1.06 × 10⁻³. So a 1 Vpp disturbance on V_in comes through as about 1 mVpp on V_out — that's a PSRR of −59.5 dB, about 20 dB of margin over the 40 dB spec. The loop attenuates 2 kHz line ripple by roughly 940×."   [~60 s]

### Slide — Input-Disturbance Time-Domain (ass-7)
"This is the 200 Hz perturbation experiment from Assignment 7. V_out envelope stays tightly regulated through the full sweep. At 2 kHz — which is 10× higher — the integrator gain is 20 dB less, but our final-project corner placement is specifically pushed up, so we still meet spec. I have the analytical derivation two slides back."   [~45 s]

### Slide — Steady-State Ripple (ass-7 evidence)
"Here's the closed-loop Vout zoom: clean 1.8 V mean with about 40 mVpp switching ripple, no sub-harmonic oscillation. That's the cycle-to-cycle stability signature of a healthy compensator — same architecture as what we deployed for the final project."   [~30 s]

### Slide — Section: Simulation Evidence
"Transition slide — moving to the simulation evidence from the final-project schematic itself."   [~5 s]

### Slide — Transient @ 10 mA
"At full load, R_L = 120 Ω, V_out locks to 1.2 V with the expected switching ripple. Inductor current averages 10 mA with the 20 mA peak-to-peak ripple we predicted analytically. This is our peak-efficiency operating point."   [~35 s]

### Slide — Transient @ 10 µA
"At the sleep-relevant load of 10 µA, with R_L scaled up to 120 kΩ, the loop still regulates — but notice that the gate-drive power hasn't gone down at all, because we're still running at 4 MHz. P_gate is fixed at 435 µW regardless of load, so efficiency here is only a few percent. This is exactly why we need burst / sleep mode, which I cover in the efficiency section."   [~50 s]

### Slide — Additional Waveform Detail
"Combined view of V_PWM, inductor current, and V_out on one screen. Confirms clean non-overlap gate drive — no shoot-through — expected duty cycle of ~36 %, and no abnormal ringing at the current FET sizes without snubber."   [~35 s]

### Slide — Section: Efficiency Analysis
"Now the efficiency breakdown."   [~5 s]

### Slide — Loss Breakdown @ 10 mA
"P_out is 12 mW. Five loss mechanisms. Conduction loss is just 15.5 µW — quadratic in current, so tiny at 10 mA. Switching loss from V-I overlap during transitions is 132 µW. Gate drive — the big one — is C_g·V_in²·f_sw = 10 pF × 10.89 V² × 4 MHz = 435 µW. Dead-time body-diode conduction: V_f × I × 2·t_dead × f_sw = 560 µW. Quiescent is negligible under ideal-amp assumption. Total loss about 1.14 mW, which gives η = 91.3 % — above the 90 % spec."   [~80 s]

### Slide — Efficiency vs Load Table
"This is the key insight of the efficiency story. At 10 mA we're at 91 %. Drop to 1 mA — conduction and switching losses shrink, but gate loss is stuck at 435 µW, so η falls to 70 %. At 100 µA, η is down to 21 %. At 10 µA in continuous PWM, we hit a dismal 2.7 %, because 12 µW of useful output is drowning in 435 µW of gate loss. With burst mode, we clock-gate the gate driver so P_gate,average drops to about 1 µW, and η at 10 µA recovers to around 28 %."   [~75 s]

### Slide — Why Burst Mode Is Mandatory
"Summary of the efficiency physics: P_cond is I², P_sw is I, P_dead is I, but P_gate is constant. So at light load, P_gate wins, and it wins by a huge margin. The only way out is to stop switching — don't pay P_gate when you don't need to. A hysteretic comparator watches V_out against a ±10 mV window. When V_out drops, we fire a couple of switching cycles to recharge the cap; otherwise the gate drivers are disabled. Effective burst frequency is set by the cap recharge time: about 13 kHz at 10 µA load, which means only 0.33 % duty of switching activity. So effective P_gate averages to about 1.4 µW, and η jumps from 2.7 % to 28 %."   [~70 s]

### Slide — Sleep-Mode Architecture
"Top level: two control paths, an active path and a sleep path. Active path is the Type-III loop we already designed. Sleep path is a hysteretic comparator that directly gates the gate driver. Switching between the two is triggered by a load sensor — inductor DCM detection or a current sense. Quiescent current in sleep is dominated by the reference and the hysteretic comparator, around 3 µA under realistic assumptions. One honest caveat: I did not physically implement the sleep-mode controller in Cadence for this deliverable — this is an architectural recommendation based on the efficiency analysis. That's called out in the What-We-Did-Not-Do document."   [~75 s]

### Slide — Section: Parasitics & Switch-Node Ringing
"Moving on to the parasitic analysis."   [~5 s]

### Slide — Switch-Node Ringing Analysis
"The package-plus-PCB parasitics form an LC tank at the switch node. Loop L_par is about 6 nH; C_par is the sum of PMOS and NMOS C_oss, roughly 380 fF for our FET sizes. That gives a ringing frequency of 1.05 GHz. Peak ringing amplitude during a switching edge is approximately I_L times the characteristic impedance sqrt(L_par/C_par) = 125 Ω, so 18.7 mA × 125 = about 2.35 V. That's above the 1.5 V spec, so we need mitigation. Three levers: slow the transitions (more switching loss), add an RC snubber across V_SW (500 Ω + 10 pF), or add a gate resistor to slow only the worst-case edge. The RC snubber is the cleanest fix and is the recommended mitigation."   [~85 s]

### Slide — Section: Summary
"Transition to summary."   [~5 s]

### Slide — Spec Compliance
"Running through the spec table: V_out regulation at 1.2 V — pass. Output ripple 40–80 mVpp — pass. Switch-node ringing 2.35 V analytical — requires the snubber to meet 1.5 V. Peak efficiency 91.3 % — pass. Interference rejection about 60 dB at 2 kHz — pass with 20 dB margin. Sleep-mode support — architectural only, not simulated. Technology, R and C limits — all pass. So seven out of nine specs pass outright, one requires a documented mitigation, one is architectural."   [~75 s]

### Slide — Key Takeaways
"Wrapping up: we built a 3.3-to-1.2 V buck in 180 nm BCD at 4 MHz with a voltage-mode Type-III loop. Peak efficiency is 91.3 % at 10 mA. At light loads we need burst mode to stay efficient, and the analysis shows 28 % at 10 µA with burst versus 3 % without. Parasitic ringing at 1 GHz requires an RC snubber. The interference rejection at 2 kHz is met with ~20 dB of margin. Main risks remaining are the sleep controller implementation and verifying the snubber in silicon."   [~70 s]

### Slide — Thank You
"Thanks — happy to take questions."   [~10 s]

---

## Rough timing check
- Part A (partner):     ~8 min
- Part B (supplement):  ~12 min
- **Total:              ~20 min** ✔

Buffer for pauses, pointer gestures, and one late-slide Q&A is embedded in the round-up.
