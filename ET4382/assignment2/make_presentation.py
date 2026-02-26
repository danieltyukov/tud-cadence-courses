#!/usr/bin/env python3
"""Generate PDF presentation for Assignment 2A - PWM Feedback Loops"""

from fpdf import FPDF
import os

DIR = os.path.dirname(os.path.abspath(__file__))

class Presentation(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

pdf = Presentation("L", "mm", "A4")  # landscape
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=False)
W, H = 297, 210  # A4 landscape

def title_slide():
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_y(50)
    pdf.cell(0, 20, "Homework Assignment 2A", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 24)
    pdf.cell(0, 15, "PWM Feedback Loops", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "ET4382 - Digital IC Design", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, "Daniel Tyukov - 5714699", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, "TU Delft", align="C", new_x="LMARGIN", new_y="NEXT")

def section_slide(title, subtitle=""):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_y(70)
    pdf.cell(0, 20, title, align="C", new_x="LMARGIN", new_y="NEXT")
    if subtitle:
        pdf.set_font("Helvetica", "", 18)
        pdf.cell(0, 12, subtitle, align="C", new_x="LMARGIN", new_y="NEXT")

def text_slide(title, bullets, font_size=13):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(15, 10)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
    pdf.line(15, 23, W-15, 23)
    pdf.set_font("Helvetica", "", font_size)
    pdf.set_xy(20, 28)
    for b in bullets:
        if b.startswith("**"):
            pdf.set_font("Helvetica", "B", font_size)
            pdf.cell(0, 8, b.replace("**",""), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", font_size)
        else:
            pdf.cell(0, 8, f"  {b}", new_x="LMARGIN", new_y="NEXT")

def image_slide(title, img_path, caption=""):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(15, 8)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.line(15, 19, W-15, 19)
    if os.path.exists(img_path):
        from PIL import Image as PILImage
        pil_img = PILImage.open(img_path)
        img_w_px, img_h_px = pil_img.size
        max_w = W - 30
        max_h = H - 45  # room for title (22) + caption (18) + margins
        # scale to fit both width and height
        scale_w = max_w / img_w_px
        scale_h = max_h / img_h_px
        scale = min(scale_w, scale_h)
        disp_w = img_w_px * scale
        disp_h = img_h_px * scale
        x = 15 + (max_w - disp_w) / 2  # center horizontally
        pdf.image(img_path, x=x, y=22, w=disp_w, h=disp_h)
    else:
        pdf.set_xy(15, 80)
        pdf.cell(0, 10, f"[Image not found: {os.path.basename(img_path)}]", align="C")
    if caption:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_xy(15, H - 18)
        pdf.cell(0, 8, caption, align="C")

def table_slide(title, headers, rows, col_widths=None):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(15, 8)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.line(15, 19, W-15, 19)

    ncols = len(headers)
    if col_widths is None:
        cw = (W - 30) / ncols
        col_widths = [cw] * ncols

    pdf.set_xy(15, 24)
    pdf.set_font("Helvetica", "B", 11)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, border=1, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", "", 10)
    for row in rows:
        x = 15
        pdf.set_x(x)
        for i, val in enumerate(row):
            pdf.cell(col_widths[i], 7, str(val), border=1, align="C")
        pdf.ln()

# ===== BUILD PRESENTATION =====

img = lambda name: os.path.join(DIR, name)

# Title
title_slide()

# ===== PART 1: 1st Order Feedback Loop =====
section_slide("Part 1", "1st Order Feedback Loop")

text_slide("Part 1: Circuit Description", [
    "**1st order self-oscillating PWM feedback loop at ~1MHz",
    "",
    "**Signal flow:",
    "Input current Iin injected at virtual ground of RC-integrator",
    "Integrator (limiting_diffamp, gain=1e6, output limited to +/-2V)",
    "Subtractor computes: integrator output - reference (gnd)",
    "Hysteresis block creates PWM switching at +/-10V",
    "VPWM feeds back through RFB to virtual ground (closing the loop)",
    "VPWM drives LC filter + 4 Ohm load",
    "",
    "**Key components:",
    "RFB = 100 kOhm, CINT = 250 pF (IC = 1V)",
    "Hysteresis: sigout_high=10, sigout_low=-10, tdel=1ns",
    "LC filter: L = 18 uH, C = 820 nF, R = 4 Ohm",
])

text_slide("Part 1: CINT Calculation & Transimpedance", [
    "**Large-signal stability criterion:",
    "CINT >= VPWM * T / (2 * RFB * Vclip)",
    "CINT >= 10 * 1us / (2 * 100k * 2V) = 250 pF",
    "",
    "**Integrator unity-gain bandwidth:",
    "fUGB = 1 / (2*pi * RFB * CINT) = 6.37 kHz",
    "",
    "**Step 2: 1kHz current input (10 uA):",
    "Vout = Iin * RFB = 10 uA * 100 kOhm = 1V (confirmed by simulation)",
    "Clean sinusoidal output, 1kHz peak at ~0 dB in spectrum",
    "",
    "**IC = 1V on CINT is critical:",
    "Hysteresis is edge-triggered, needs initial condition to start oscillation",
    "Without IC, loop will not start (DC operating point gets stuck)",
])

image_slide("Part 1: Schematic", img("part1_schematic.png"),
    "1st order feedback loop with limiting_diffamp, subtractor, hysteresis")

image_slide("Part 1: Vout Waveform (1kHz, 10uA)", img("part1_vout_1kHz_10uA.png"),
    "Clean 1V sine at output, transimpedance = Iin * RFB")

image_slide("Part 1: VPWM Zoomed", img("part1_vpwm_zoomed.png"),
    "PWM switching at ~1MHz with duty cycle modulated by input signal")

image_slide("Part 1: Spectrum (1kHz, 10uA)", img("part1_spectrum_1kHz_10uA.png"),
    "Dominant 1kHz peak at ~0 dB, PWM harmonics attenuated by LC filter")

text_slide("Part 1: Maximum Current Amplitude", [
    "**Theoretical: IIN,MAX = Vout,max / RFB = 10V / 100k = 100 uA",
    "",
    "**Simulated: IIN,MAX = 74 uA",
    "",
    "**Why lower than theoretical:",
    "Integrator needs headroom for PWM triangle ripple on output (net4)",
    "At 74 uA: Vout = +/-7.4V, loop operates cleanly",
    "At 75 uA: integrator output clips at +/-2V, VPWM loses switching, loop dies",
    "",
    "**Sweep results:",
    "40 uA: +/-4V (clean)    |  70 uA: +/-7V (clean)",
    "74 uA: +/-7.4V (max)    |  75 uA: saturated (loop dies)",
])

image_slide("Part 1: IIN,MAX = 74 uA", img("part1_step3_74uA_max.png"),
    "Maximum clean operation at 74 uA")

image_slide("Part 1: Clipping at 75 uA", img("part1_step3_75uA_clipping.png"),
    "Loop saturates: VPWM stuck, Vout drifts")

text_slide("Part 1: 5kHz Error Injection", [
    "**Setup:",
    "Verr (vsource, sine, 5kHz, 1V) placed between I12 sigout and VPWM node",
    "Both LC filter and feedback path see the error",
    "I13 amplitude = 0 (no input signal)",
    "",
    "**Result: 5kHz peak at -73.1 dB in output spectrum",
    "Error suppression = 73 dB",
    "",
    "**Theoretical loop gain @ 5kHz:",
    "KPWM = VPWM / (pi * Vclip) = 10 / (pi * 2) = 1.59",
    "|Hint(5kHz)| = fUGB / f = 6.37k / 5k = 1.27",
    "|L(5kHz)| = 1.27 * 1.59 = 2.02 (~6 dB)",
    "Predicted suppression: 1 + |L| = 3 -> 9.5 dB",
    "",
    "**Measured 73 dB >> predicted 9.5 dB:",
    "Self-oscillating loop has much higher effective KPWM",
    "Triangle ripple is only ~0.2V pp (not +/-2V clipping limits)",
    "Effective KPWM = 10 / (pi * 0.1) = 31.8",
])

image_slide("Part 1: Error Injection Schematic", img("part1_step4_error_schematic.png"),
    "Verr placed between hysteresis output and VPWM node")

image_slide("Part 1: Error Waveform", img("part1_step4_error_waveform.png"),
    "VPWM with 5kHz envelope, Vout settled near 0V")

image_slide("Part 1: Error Spectrum", img("part1_step4_error_spectrum.png"),
    "5kHz error suppressed to -73.1 dB at output")

# ===== PART 2: 2nd Order Feedback Loop =====
section_slide("Part 2", "2nd Order Feedback Loop")

text_slide("Part 2: Circuit Description", [
    "**Added to 1st order loop:",
    "2nd integrator I14 (limiting_diffamp, same settings as I9)",
    "RFB2 = 100 kOhm from VPWM to I14 virtual ground (net03)",
    "CINT2 = 250 pF (IC = 1V) on I14",
    "RZERO = 500 kOhm in series with CINT on I9 (stabilizing zero)",
    "10 pF cap on net03 to gnd (convergence fix)",
    "",
    "**Signal chain:",
    "I9 sigout (net013) -> I10 subtractor sigin_p",
    "I14 sigout (net04) -> I10 subtractor sigin_n (triangle reference)",
    "Subtractor -> hysteresis -> VPWM",
    "VPWM -> RFB -> I9, VPWM -> RFB2 -> I14, VPWM -> LC filter",
    "",
    "**Zero frequency: fz = 1/(2*pi * 500k * 250p) = 1.27 kHz",
    "",
    "**Observation: loop self-oscillates at ~50 kHz (not 1 MHz)",
    "Both integrators have identical time constants (RFB*CINT = 25 us)",
    "This causes the integrator poles to cancel in the loop transfer",
])

image_slide("Part 2: Schematic", img("part2_schematic.png"),
    "2nd order feedback loop with two integrators and stabilizing zero")

image_slide("Part 2: Waveforms", img("part2_waveforms.png"),
    "VPWM, net013 (I9 out), Vout, net04 (I14 out / triangle reference)")

text_slide("Part 2: 5kHz Error Injection", [
    "**Setup: same as Part 1 Step 4",
    "Verr (5kHz, 1V) between I12 sigout and VPWM node",
    "I13 amplitude = 0",
    "",
    "**Result: 5kHz peak at -6.4 dB in output spectrum",
    "Error suppression = 6.4 dB",
    "",
    "**Much lower than Part 1's 73 dB because:",
    "Identical integrator time constants (CINT = CINT2 = 250 pF)",
    "cause the frequency-dependent terms to cancel",
    "Loop acts as constant gain: L = KPWM * RZERO/RFB = 1.59 * 5 = 8",
    "No integrating behavior -> minimal error suppression",
    "",
    "**Theoretical suppression:",
    "|L| = KPWM * RZERO/RFB = 7.95 (~18 dB)",
    "Predicted: 20*log10(1 + 7.95) = 19 dB",
    "Measured: 6.4 dB (lower due to chaotic loop operation)",
])

image_slide("Part 2: Error Injection Schematic", img("part2_error_schematic.png"),
    "Verr placed between hysteresis output and VPWM node")

image_slide("Part 2: Error Spectrum", img("part2_error_spectrum.png"),
    "5kHz error at -6.4 dB (only 6 dB suppression vs Part 1's 73 dB)")

# ===== PART 3: Clipping Comparison =====
section_slide("Part 3", "Clipping Comparison (FS + 10%)")

text_slide("Part 3: Setup & Results", [
    "**Drive both loops at FS+10%:",
    "Iin = 1.1 * IIN,MAX = 1.1 * 74 uA = 81 uA",
    "I13: sine, 1kHz, 81 uA",
    "",
    "**1st order loop result:",
    "Vout saturates to -10V and stays there permanently",
    "Integrator clips at -2V, VPWM locks to -10V, loop dies",
    "Clean but fatal saturation - output locks to one rail",
    "Once overdriven past IIN,MAX, the loop cannot recover",
    "",
    "**2nd order loop result:",
    "Vout oscillates chaotically between +/-12V with erratic swings",
    "Both integrators clip and fight each other (integrator wind-up)",
    "LC filter ringing causes overshoot beyond +/-10V (peaks to +/-14V)",
    "Loop never settles but also never fully locks up",
    "",
    "**Key difference:",
    "1st order: fails gracefully (locks to rail, silent failure)",
    "2nd order: fails chaotically (wind-up, unstable oscillation with overshoot)",
])

image_slide("Part 3: 1st Order Clipping (81 uA)", img("part3_1st_order_clipping.png"),
    "1st order loop: Vout saturates to -10V permanently")

image_slide("Part 3: 2nd Order Clipping (81 uA)", img("part3_2nd_order_clipping.png"),
    "2nd order loop: chaotic oscillation +/-12V with integrator wind-up")

# ===== Summary =====
text_slide("Summary", [
    "**Part 1: 1st Order Feedback Loop",
    "Self-oscillating PWM at ~1MHz, CINT = 250 pF, RFB = 100 kOhm",
    "IIN,MAX = 74 uA, transimpedance = RFB = 100 kOhm",
    "Error suppression @ 5kHz = 73 dB (self-oscillating gain >> naturally-sampled)",
    "",
    "**Part 2: 2nd Order Feedback Loop",
    "Added 2nd integrator (I14) + RZERO = 500 kOhm stabilizing zero",
    "Self-oscillation at ~50 kHz (lower due to 2nd integrator dynamics)",
    "Error suppression @ 5kHz = 6.4 dB (identical time constants limit performance)",
    "",
    "**Part 3: Clipping at FS+10% (81 uA)",
    "1st order: Vout locks to -10V (clean, silent saturation)",
    "2nd order: chaotic +/-12V oscillation (integrator wind-up)",
    "2nd order harder to recover from clipping due to two integrators",
])

# Save
out_path = os.path.join(DIR, "Assignment2A_5714699.pdf")
pdf.output(out_path)
print(f"Saved: {out_path}")
print(f"Pages: {pdf.page_no()}")
