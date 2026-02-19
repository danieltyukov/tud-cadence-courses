# Speech Notes — Assignment 1A: Class-D Amplifier

## Slide 1: Title
Hello everyone, I'm Daniel Tyukov, student number 5714699. Today I'll present homework 1A on the Class-D amplifier, covering LC filter design, PWM generation, and two-phase interleaving.

## Slide 2: Part 1 Section Title
Let's start with Part 1 — the LC lowpass filter design.

## Slide 3: Specifications & Design
We need a second-order LC lowpass filter for a 4 ohm speaker load. The requirements are over 50 dB attenuation at 1 MHz, a quality factor between 0.7 and 1, and we must use E12 series components with realistic tolerances — plus or minus 10% on the inductor, 20% on the capacitor. The topology is simple: inductor in series, capacitor in parallel with the load to ground. I chose L = 18 microhenry and C = 820 nanofarad from the E12 series.

## Slide 4: Nominal Performance
With these values, the natural frequency comes out to 41.4 kHz, Q is 0.854, and attenuation at 1 MHz is 55.3 dB. The Cadence AC simulation confirms this nicely — the simulated minus 3 dB point is 48.66 kHz and the attenuation at 1 MHz is 55.45 dB, very close to the hand calculation.

## Slide 5: Tolerance Analysis
Here's the worst-case tolerance analysis across all four corners. The Q stays within 0.73 to 0.99, comfortably inside the 0.7 to 1.0 spec. The minimum attenuation is 52.4 dB, still above the 50 dB requirement. So the design is robust against component tolerances.

## Slide 6: Part 1 Schematic
This is the schematic in Cadence Virtuoso — a simple AC voltage source, the 18 microhenry inductor in series, and the 820 nanofarad capacitor in parallel with the 4 ohm resistor.

## Slide 7: Part 1 Bode Plot
Here's the Bode plot from the AC analysis. You can see the flat passband, the rolloff starting around 40 kHz, and the second-order slope of minus 40 dB per decade. The markers show the minus 3 dB frequency at about 49 kHz and the attenuation at 1 MHz of about 55 dB.

## Slide 8: Part 2 Section Title
Now Part 2 — the double-sided PWM generator.

## Slide 9: Circuit Description
I built a naturally-sampled double-sided PWM using a comparator from the ahdlLib library. The triangle carrier is a vpulse at 1 MHz with amplitude plus or minus 1 volt. The sine input represents the audio signal. The comparator outputs plus or minus 10 volts, and the LC filter from Part 1 recovers the audio content. I used a transient simulation of 5 milliseconds and computed the spectrum with a DFT.

## Slide 10: Simulation Results
Four test cases. At 1 kHz, 0.1 full scale, we get a clean 1 volt sine — the filter passes the audio signal. At 1.001 MHz, which is the carrier plus 1 kHz, almost nothing comes through — the filter kills anything near the carrier frequency. At 2.001 MHz, which is twice the carrier plus 1 kHz, a 1 kHz sine reappears — this is aliasing through the double-sided PWM process, where sidebands around even harmonics fold back to baseband. At 1 kHz, 0.9 full scale, we get a large 9 volt sine at near-full modulation.

## Slide 11: Part 2 Schematic
Here's the PWM schematic — the comparator comparing the sine input against the triangle wave, feeding through the LC filter to the 4 ohm load.

## Slide 12: 1kHz, 0.1 FS
The time domain shows a clean low-amplitude sine. The spectrum has a strong peak at 1 kHz with everything else well attenuated.

## Slide 13: 1.001 MHz, 0.1 FS
Almost flat output — the input frequency is right at the PWM carrier and the LC filter removes it completely. This confirms the filter is doing its job.

## Slide 14: 2.001 MHz, 0.1 FS
This is the interesting one. Even though the input is at 2 MHz, we see a 1 kHz component in the output. This is because double-sided PWM creates sidebands around even multiples of the carrier, and these alias back into the audio band.

## Slide 15: 1kHz, 0.9 FS
Near full modulation — a large clean sine wave. The PWM pulses go from very narrow to very wide as the modulation index approaches 1.

## Slide 16: Part 3 Section Title
Finally, Part 3 — two-phase interleaved PWM.

## Slide 17: Circuit & Theory
I added a second PWM channel with its own comparator and inductor, with the triangle carrier delayed by half a period — 500 nanoseconds. Both phases share the same output capacitor and load. The key formulas: single-phase ripple is proportional to 1 minus mi squared, while the two-phase combined ripple is proportional to mi times 1 minus mi. The reduction factor is 2 mi over 1 plus mi — at zero modulation index you get perfect cancellation, while at full modulation there's no benefit.

## Slide 18: Ripple Comparison Table
This table shows the numbers. Single-phase ripple is highest at mi equals zero — 278 milliamps — and decreases with modulation index. Two-phase combined ripple is zero at mi equals zero and peaks at mi equals 0.5 at only 139 milliamps. The reduction ranges from 100% at idle to just 5% at mi equals 0.9.

## Slide 19: Key Observations
The main takeaway: two-phase interleaving always gives equal or lower ripple compared to single-phase. The maximum benefit is at low power, which is actually where audio amplifiers spend most of their time. The maximum two-phase ripple is exactly half the maximum single-phase ripple.

## Slide 20: Part 3 Schematic
Here's the two-phase schematic — two comparators, two inductors with small series resistors to avoid simulation issues, feeding into the shared LC output stage.

## Slide 21: Parametric Sweep Results
These are the simulation results from the parametric sweep of mi from 0 to 0.9. Top left is phase 1 current, top right is phase 2 current — both show triangular ripple increasing in DC level with mi. The bottom plot is the combined current — you can see the ripple is very small, especially at low modulation indices, confirming the analytical predictions.

## Slide 22: Ripple Current vs Modulation Index Plot
This is the key plot the assignment asks for — peak-to-peak ripple current versus modulation index for both single-phase and two-phase. The blue curve is single-phase, highest at mi equals zero and monotonically decreasing. The red curve is two-phase, starting at zero thanks to perfect cancellation, peaking at mi equals 0.5 at 139 milliamps, then decreasing again. Two-phase is always below single-phase. The dots are the discrete simulation points which match the analytical curves. Note that the single-phase data comes from the individual inductor current in our two-phase simulation, since each phase sees the same waveform as a standalone single-phase amplifier.

## Slide 23: Summary
To summarize: the LC filter meets all specs with margin across tolerances. The double-sided PWM correctly generates the modulated signal and the aliasing behavior at 2 times the carrier frequency was confirmed. Two-phase interleaving provides significant ripple reduction, especially at low modulation, cutting the maximum ripple in half. Thank you.
