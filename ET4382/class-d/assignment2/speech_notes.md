# Assignment 2A - Speech Notes

## Title
- Assignment 2A, PWM Feedback Loops

## Part 1 Section
- 1st order self-oscillating feedback loop

## Circuit Description
- Active RC-integrator with output clipping at ±2V acts as the loop filter
- Subtractor and hysteresis together form the comparator — hysteresis is edge-triggered so we need an initial condition on CINT to kick-start switching
- No external carrier — the loop generates its own PWM at roughly 1MHz through the integrator ramp hitting the comparator threshold

## CINT & Transimpedance
- CINT sized for large-signal stability — ensures the integrator never rails during worst-case switching transients
- With 10μA in we see a clean 1V sine out, confirming the closed-loop transimpedance equals RFB
- maxstep must be 10ns otherwise the simulator steps right over the MHz switching and you get garbage

## Schematic
- Standard topology: current in at virtual ground, integrator, comparator, output stage feeding back through RFB

## Vout 1kHz 10μA
- Textbook result — smooth sine, no distortion, loop is regulating properly

## VPWM Zoomed
- Duty cycle clearly modulated by the input — wider pulses on positive half, narrower on negative

## Spectrum
- Single clean tone at 1kHz, everything else pushed down by the LC filter

## IIN,MAX
- Swept the input amplitude until the loop lost regulation
- At 74μA the output is still a clean ±7.4V sine
- At 75μA the integrator hits its ±2V rail, can't maintain proper PWM switching, loop collapses
- The gap from the theoretical 100μA comes from needing headroom for the switching ripple on the integrator output

## 74μA waveform
- Last clean operating point — output sinusoid fills most of the ±10V range

## 75μA clipping
- Integrator saturated, VPWM stuck at one rail, output drifts — loop is dead

## Error Injection
- Placed Verr in series right at the switching node so both the forward path and feedback path see the disturbance
- Got 73dB suppression at 5kHz — far more than the 9.5dB you'd predict from the standard naturally-sampled KPWM formula
- The reason: in a self-oscillating loop the effective triangle amplitude is just the tiny ripple on the integrator output (~0.2Vpp), not the full ±2V clip range, so the actual modulator gain is roughly 20× higher than the textbook formula gives

## Error screenshots
- Schematic shows Verr placement, waveform shows the 5kHz modulation on VPWM barely reaching the output, spectrum confirms -73dB

## Part 2 Section
- Extending to a 2nd order loop with a second integrator

## Part 2 Circuit
- Second integrator I14 added in parallel — VPWM feeds through RFB2 into I14 which should produce a triangle reference
- RZERO in series with CINT on the first integrator provides the stabilizing zero
- Needed a 10pF parasitic cap on net03 to get past convergence issues with the Verilog-A models
- **Main issue:** we used CINT = CINT2 = 250pF, giving both integrators the same time constant — this causes the frequency-dependent terms to cancel in the subtractor, collapsing the loop transfer to a flat gain instead of a proper integrating 2nd order response
- Loop oscillates at ~50kHz in a somewhat chaotic manner rather than clean 1MHz PWM
- Tried several alternatives (different RZERO values, different CINT2) but couldn't find a combination that both converged for 5ms and gave proper 2nd order behavior — the Verilog-A convergence issues were the main blocker

## Part 2 Schematic
- Two integrators feeding the subtractor, RZERO visible in series with CINT, convergence cap on I14's virtual ground

## Part 2 Waveforms
- Both integrator outputs clipping at ±2V — they're acting more like comparators than integrators
- VPWM switching is irregular, Vout swings wildly — this is the degenerate constant-gain mode

## Part 2 Error Injection
- Same Verr setup as Part 1
- Only 6.4dB suppression — barely any rejection
- Confirms the loop has no real integrating action at 5kHz — just a flat gain of about RZERO/RFB = 5
- A properly functioning 2nd order loop should give even more suppression than the 1st order's 73dB

## Error screenshots
- Spectrum clearly shows the 5kHz component sitting near 0dB — almost no suppression

## Part 3 Section
- Clipping comparison, driving both loops 10% beyond full scale

## Part 3 Results
- 1st order: output ramps to -10V and stays there — integrator saturated, loop is gone, silent failure
- 2nd order: output goes chaotic with ±12-14V swings — both integrators are clipped and fighting each other, LC filter rings with overshoot beyond the supply rails
- The takeaway: 1st order fails cleanly and predictably, 2nd order fails noisily with integrator wind-up making recovery much harder

## 1st order clipping
- Flat line at -10V — the loop gave up after one half-cycle of the input

## 2nd order clipping
- Wild oscillation filling the entire voltage range — this is what integrator wind-up looks like in practice

## Summary
- 1st order loop works well: 73dB error suppression, clean operation up to 74μA
- 2nd order loop was limited by the identical time constant issue — needs CINT ≠ CINT2 for proper operation, but convergence problems prevented us from fully exploring that
- Clipping behavior shows fundamentally different failure modes: silent lockup vs chaotic oscillation
