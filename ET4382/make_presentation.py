#!/usr/bin/env python3
"""Generate PDF presentation for Assignment 1A - Class-D Amplifier"""

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
    pdf.cell(0, 20, "Homework Assignment 1A", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 24)
    pdf.cell(0, 15, "Class-D Amplifier", align="C", new_x="LMARGIN", new_y="NEXT")
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
        # fit image in remaining space
        max_w, max_h = W - 30, H - 35
        pdf.image(img_path, x=15, y=22, w=max_w, h=0, keep_aspect_ratio=True)
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
    # header
    pdf.set_font("Helvetica", "B", 11)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, border=1, align="C")
    pdf.ln()
    # rows
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

# ===== PART 1 =====
section_slide("Part 1", "LC Lowpass Filter Design")

text_slide("Part 1: Specifications & Design", [
    "**Specifications:",
    "Load: R = 4 Ohm",
    "Attenuation @ 1MHz: > 50 dB",
    "Quality factor: 0.7 < Q < 1.0",
    "E12 series components, L +/-10%, C +/-20%",
    "",
    "**Topology: 2nd-order LC lowpass",
    "L in series, C in parallel with R (shunt to GND)",
    "",
    "**Formulas:",
    "f0 = 1 / (2*pi*sqrt(LC))",
    "Q = R * sqrt(C/L)",
    "Attenuation (f >> f0) = 40 * log10(f/f0) dB",
    "",
    "**Selected E12 values: L = 18 uH, C = 820 nF",
])

text_slide("Part 1: Nominal Performance", [
    "**Component values:",
    "L = 18 uH (E12, +/-10%)",
    "C = 820 nF (E12, +/-20%)",
    "R = 4 Ohm (load)",
    "",
    "**Calculated performance:",
    "f0 = 1/(2*pi*sqrt(18u * 820n)) = 41.4 kHz",
    "Q = 4 * sqrt(820n / 18u) = 0.854",
    "Attenuation @ 1MHz = 40 * log10(1e6/41430) = 55.3 dB",
    "",
    "**Simulated (Cadence AC analysis):",
    "f_-3dB = 48.66 kHz",
    "Attenuation @ 1MHz = 55.45 dB",
    "Q confirmed by Bode shape (no peaking)",
])

table_slide("Part 1: Worst-Case Tolerance Analysis",
    ["Corner", "L", "C", "f0 (kHz)", "Q", "Atten @1MHz (dB)"],
    [
        ["Nominal", "18 uH", "820 nF", "41.4", "0.854", "55.3"],
        ["L-10% C-20%", "16.2 uH", "656 nF", "48.8", "0.986", "52.4"],
        ["L+10% C+20%", "19.8 uH", "984 nF", "36.2", "0.728", "58.9"],
        ["L-10% C+20%", "16.2 uH", "984 nF", "39.9", "0.986", "55.0"],
        ["L+10% C-20%", "19.8 uH", "656 nF", "44.1", "0.728", "53.1"],
        ["", "", "", "", "", ""],
        ["All corners", "", "", "", "0.73-0.99", ">52.4"],
    ],
    [50, 40, 40, 40, 40, 57]
)

image_slide("Part 1: Schematic", img("part1_schematic.png"), "LC lowpass filter in Cadence Virtuoso")
image_slide("Part 1: Bode Plot", img("part1_bode_plot.png"), "AC analysis: magnitude & phase, markers at f_-3dB and 1MHz")

# ===== PART 2 =====
section_slide("Part 2", "Double-Sided PWM Generator")

text_slide("Part 2: Circuit Description", [
    "**Components:",
    "Comparator (ahdlLib): sigout_high = +10V, sigout_low = -10V",
    "Triangle carrier (vpulse): V1=-1, V2=+1, Rise=499n, Fall=499n, Period=1us",
    "Sine input (vsin): variable amplitude and frequency",
    "LC filter + 4 Ohm load (same as Part 1)",
    "",
    "**Double-sided (naturally-sampled) PWM:",
    "Input sine compared with triangle carrier at fPWM = 1 MHz",
    "Output switches between +10V and -10V",
    "LC filter recovers the audio-frequency content",
    "",
    "**Simulation: transient 5ms, conservative accuracy",
    "Spectrum: dB20(dft(VT(\"/Vout\") 1m 5m 4096))",
])

text_slide("Part 2: Simulation Results", [
    "**1 kHz, 0.1 FS:",
    "Clean ~+/-1V sine at output, strong 1kHz spectral peak",
    "",
    "**1.001 MHz (fPWM + 1kHz), 0.1 FS:",
    "Almost no output - LC filter attenuates carrier-frequency content by >50dB",
    "",
    "**2.001 MHz (2*fPWM + 1kHz), 0.1 FS:",
    "A 1kHz sine appears! Signal aliases back through double-sided PWM",
    "Sidebands around 2*fPWM fold into baseband - key PWM property",
    "",
    "**1 kHz, 0.9 FS:",
    "Large ~+/-9V sine wave, near full modulation",
    "PWM pulse widths vary from very narrow to very wide",
])

image_slide("Part 2: Schematic", img("part2_schematic.png"), "PWM generator + LC filter")
image_slide("Part 2: 1kHz, 0.1 FS", img("part2_spectrum_1kHz_01FS.png"), "Time domain + spectrum")
image_slide("Part 2: 1.001 MHz, 0.1 FS", img("part2_spectrum_1001kHz_01FS.png"), "fPWM + 1kHz: attenuated by LC filter")
image_slide("Part 2: 2.001 MHz, 0.1 FS", img("part2_spectrum_2001kHz_01FS.png"), "2*fPWM + 1kHz: aliasing back to 1kHz")
image_slide("Part 2: 1kHz, 0.9 FS", img("part2_spectrum_1kHz_09FS.png"), "Near full modulation")

# ===== PART 3 =====
section_slide("Part 3", "Two-Phase Interleaved PWM")

text_slide("Part 3: Circuit & Theory", [
    "**Two-phase interleaved Class-D:",
    "Phase 1: comparator + L1 (18uH) + R1 (1m Ohm), carrier delay = 0",
    "Phase 2: comparator + L0 (18uH) + R2 (1m Ohm), carrier delay = 500ns (T/2)",
    "Shared output: C = 820nF || R = 4 Ohm",
    "DC input: vdc = mi (modulation index, swept 0 to 0.9)",
    "",
    "**Single-phase ripple:",
    "dI_1ph = 5*(1 - mi^2) / 18  [A]",
    "",
    "**Two-phase combined ripple (D >= 0.5):",
    "dI_2ph = 10*mi*(1 - mi) / 18  [A]",
    "",
    "**Reduction factor: dI_2ph / dI_1ph = 2*mi / (1 + mi)",
    "At mi=0: perfect cancellation. At mi=1: no benefit.",
])

table_slide("Part 3: Ripple Current Comparison",
    ["mi", "D", "dI_1ph (mA)", "dI_2ph (mA)", "Reduction"],
    [
        ["0.0", "0.500", "278", "0", "100%"],
        ["0.1", "0.550", "275", "50", "82%"],
        ["0.2", "0.600", "267", "89", "67%"],
        ["0.3", "0.650", "253", "117", "54%"],
        ["0.4", "0.700", "233", "133", "43%"],
        ["0.5", "0.750", "208", "139", "33%"],
        ["0.6", "0.800", "178", "133", "25%"],
        ["0.7", "0.850", "142", "117", "18%"],
        ["0.8", "0.900", "100", "89", "11%"],
        ["0.9", "0.950", "53", "50", "5%"],
    ],
    [30, 30, 55, 55, 55]
)

text_slide("Part 3: Key Observations", [
    "**Single-phase ripple: max at mi=0 (278 mA), decreases with mi",
    "",
    "**Two-phase combined ripple: ZERO at mi=0 (perfect cancellation)",
    "  Peaks at mi=0.5 (139 mA), then decreases",
    "",
    "**Two-phase always <= single-phase ripple",
    "  Max single-phase (278 mA) = 2x max two-phase (139 mA)",
    "",
    "**Greatest benefit at low modulation (idle/low-power):",
    "  At mi=0: 100% reduction",
    "  At mi=0.5: 33% reduction",
    "",
    "**Simulation confirms analytical predictions:",
    "  Combined current at mi=0 shows near-zero ripple",
    "  Ripple increases with mi as expected",
])

image_slide("Part 3: Schematic", img("part3_schematic.png"), "Two-phase interleaved PWM + LC filter")
image_slide("Part 3: Parametric Sweep Results", img("part3_inductor_currents.png"), "Inductor currents: Phase 1, Phase 2, and combined (mi = 0 to 0.9)")

# Summary
text_slide("Summary", [
    "**Part 1: LC Lowpass Filter",
    "L = 18 uH, C = 820 nF, f0 = 41.4 kHz, Q = 0.854",
    "55.3 dB attenuation @ 1MHz (>50dB in all tolerance corners)",
    "",
    "**Part 2: Double-Sided PWM",
    "Comparator-based PWM at 1MHz, +/-10V output",
    "LC filter recovers audio signal, attenuates carrier",
    "Aliasing at 2*fPWM confirmed (key property of double-sided PWM)",
    "",
    "**Part 3: Two-Phase Interleaved PWM",
    "180-degree phase shift between two PWM channels",
    "Ripple cancellation: up to 100% at mi=0",
    "Two-phase max ripple (139 mA) = half of single-phase max (278 mA)",
])

# Save
out_path = os.path.join(DIR, "Assignment1A_Presentation.pdf")
pdf.output(out_path)
print(f"Saved: {out_path}")
print(f"Pages: {pdf.page_no()}")
