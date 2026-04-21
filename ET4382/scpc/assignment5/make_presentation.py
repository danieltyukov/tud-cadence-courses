#!/usr/bin/env python3
"""Generate PDF presentation for SCPC Assignment 5 - Homework Exercise 2"""

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
    pdf.cell(0, 20, "SCPC Homework - Exercise 2", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 24)
    pdf.cell(0, 15, "Switched-Capacitor Power Converters", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "ET4382 - Digital IC Design", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, "Daniel Tyukov - 5714699", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, "Raghavendra Joshi - 6438180", align="C", new_x="LMARGIN", new_y="NEXT")
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
        max_h = H - 45
        scale_w = max_w / img_w_px
        scale_h = max_h / img_h_px
        scale = min(scale_w, scale_h)
        disp_w = img_w_px * scale
        disp_h = img_h_px * scale
        x = 15 + (max_w - disp_w) / 2
        pdf.image(img_path, x=x, y=22, w=disp_w, h=disp_h)
    else:
        pdf.set_xy(15, 80)
        pdf.cell(0, 10, f"[Image not found: {os.path.basename(img_path)}]", align="C")
    if caption:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_xy(15, H - 18)
        pdf.cell(0, 8, caption, align="C")

def table_slide(title, headers, rows, col_widths=None, font_size=10):
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
    pdf.set_font("Helvetica", "B", font_size)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, border=1, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", "", font_size)
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

# ===== PART (a): Blocking Voltages =====
section_slide("Part (a)", "Blocking Voltages of Power Switches")

text_slide("Part (a): Circuit A - Series-Parallel 4:1", [
    "**Topology: 3 flying caps (C1, C2, C3), output cap C4, 10 switches",
    "**Conversion ratio: M = 1/4",
    "",
    "**Phase 1 (series): S1, S2, S3, S4 ON",
    "Caps in series from Vin to Vout: Vin -> C1 -> C2 -> C3 -> Vout",
    "Each cap voltage: Vc = Vin/4",
    "Node voltages (phi1): [1, 3/4, 3/4, 1/2, 1/2, 1/4] x Vin",
    "",
    "**Phase 2 (parallel): S5-S10 ON",
    "Each cap connected between Vout and GND",
    "Node voltages (phi2): [1/4, 0, 1/4, 0, 1/4, 0] x Vin",
    "",
    "**Blocking voltage = |V_terminal1 - V_terminal2| when switch is OFF",
    "Max blocking voltage: 3/4 x Vin (S1, S5, S8)",
])

table_slide("Part (a): Circuit A - Switch Blocking Voltages",
    ["Switch", "Phase", "Blocking Voltage", "Switch", "Phase", "Blocking Voltage"],
    [
        ["S1", "phi1", "3/4 x Vin", "S6",  "phi2", "1/2 x Vin"],
        ["S2", "phi1", "1/4 x Vin", "S7",  "phi2", "1/4 x Vin"],
        ["S3", "phi1", "1/4 x Vin", "S8",  "phi2", "3/4 x Vin"],
        ["S4", "phi1", "1/4 x Vin", "S9",  "phi2", "1/2 x Vin"],
        ["S5", "phi2", "3/4 x Vin", "S10", "phi2", "1/4 x Vin"],
    ],
    col_widths=[25, 25, 80, 25, 25, 80],
    font_size=11)

text_slide("Part (a): Circuit B - Ladder/Dickson 4:1", [
    "**Topology: 3 flying caps (C1, C2, C3), output cap C4, 8 switches",
    "**Conversion ratio: M = 1/4",
    "",
    "**Cap voltages: V_C1 = V_C2 = Vin/2, V_C3 = Vin/4",
    "",
    "**Phase 1: S1, S2, S3 ON",
    "Node voltages (phi1): [1, 1/2, 1/2, 1/4, 0, 1/4] x Vin",
    "",
    "**Phase 2: S4-S8 ON",
    "Node voltages (phi2): [1, 0, 1, 0, 1/2, 1/4] x Vin",
    "",
    "**More uniform blocking voltage distribution than Circuit A",
    "Most switches: 1/2 x Vin blocking voltage",
])

table_slide("Part (a): Circuit B - Switch Blocking Voltages",
    ["Switch", "Phase", "Blocking Voltage", "Switch", "Phase", "Blocking Voltage"],
    [
        ["S1", "phi1", "1/2 x Vin", "S5", "phi2", "1/4 x Vin"],
        ["S2", "phi1", "1/2 x Vin", "S6", "phi2", "3/4 x Vin"],
        ["S3", "phi1", "1/2 x Vin", "S7", "phi2", "1/2 x Vin"],
        ["S4", "phi2", "1/4 x Vin", "S8", "phi2", "1/4 x Vin"],
    ],
    col_widths=[25, 25, 80, 25, 25, 80],
    font_size=11)

# ===== PART (b): PMOS/NMOS Selection =====
section_slide("Part (b)", "PMOS/NMOS Switch Implementation")

text_slide("Part (b): Switch Type Selection", [
    "**Constraint: gate drive voltage in range [Vin, 0]",
    "",
    "**Selection rule:",
    "Switches closer to Vin (high rail) -> PMOS",
    "  Gate driven to 0V to turn ON (Vsg = Vnode > |Vtp|)",
    "Switches closer to GND (low rail) -> NMOS",
    "  Gate driven to Vin to turn ON (Vgs = Vin - Vnode > Vtn)",
    "",
    "**Circuit A (10 switches):",
    "PMOS: S1, S5, S6, S7 (top rail switches, connected near Vin)",
    "NMOS: S8, S9, S10 (bottom rail switches, connected to GND)",
    "S2, S3, S4: intermediate nodes, either type possible",
    "",
    "**Circuit B (8 switches):",
    "PMOS: S1, S2, S3, S5, S7, S8 (near high rail)",
    "NMOS: S4, S6 (near low rail)",
])

# ===== PART (c): Component Sizing =====
section_slide("Part (c)", "Ron, C1, C2, C3 Design for Rout = 20 Ohm")

text_slide("Part (c): Design Approach", [
    "**Target: Rout = 20 Ohm at corner frequency fc = 10 MHz",
    "",
    "**Output impedance model:",
    "Rout = sqrt(R_SSL^2 + R_FSL^2)",
    "",
    "**At corner frequency: R_SSL = R_FSL",
    "Rout = sqrt(2) x R_FSL  =>  R_FSL = 20/sqrt(2) = 14.14 Ohm",
    "",
    "**FSL (Fast Switching Limit):",
    "R_FSL = sum(a_i^2) x 2 x Ron  (switch charge multipliers)",
    "",
    "**SSL (Slow Switching Limit):",
    "R_SSL = m / (fs x CT)  (capacitor charge multipliers)",
    "",
    "**Capacitance density (for area):",
    "C_1V8 = 6 nF/mm^2 (Vc < 1.8V)",
    "C_5V = 2.5 nF/mm^2 (Vc < 5V)",
])

text_slide("Part (c): Circuit A Sizing", [
    "**Charge multiplier analysis:",
    "FSL factor p = 5/4 => R_FSL = (5/4) x Ron",
    "SSL factor m = 9/16",
    "",
    "**Ron calculation:",
    "14.14 = (5/4) x Ron  =>  Ron = 14.14 x 4/5 = 11.31 Ohm",
    "",
    "**Capacitor sizing:",
    "R_SSL = m / (fs x CT) => CT = (9/16) / (10^7 x 14.14) = 3.977 nF",
    "Equal distribution: C1 = C2 = C3 = CT/3 = 1.33 nF",
    "",
    "**Voltage across each cap: Vc = Vin/4 = 1V < 1.8V",
    "Use C_1V8 density => Area = CT / 6 = 3.977/6 = 0.663 mm^2",
    "",
    "**Note: all caps are floating (C_INV type)",
])

text_slide("Part (c): Circuit B Sizing", [
    "**Charge multiplier analysis:",
    "FSL factor p = 17/8 => R_FSL = (17/8) x Ron",
    "SSL factor m = 1",
    "",
    "**Ron calculation:",
    "14.14 = (17/8) x Ron  =>  Ron = 14.14 x 8/17 = 6.655 Ohm",
    "",
    "**Capacitor sizing:",
    "R_SSL = m / (fs x CT) => CT = 1 / (10^7 x 14.14) = 7.07 nF",
    "Optimal distribution: C3 = 2 x C1 = 2 x C2",
    "C1 = C2 = 1.77 nF, C3 = 3.54 nF",
    "",
    "**All caps floating (C_INV), voltage < 1.8V for given Vin",
    "Use C_1V8 density => Area = CT / 6 = 7.07/6 = 1.18 mm^2",
])

table_slide("Part (c): Circuit A vs Circuit B Comparison",
    ["Parameter", "Circuit A", "Circuit B"],
    [
        ["Topology", "Series-Parallel", "Ladder/Dickson"],
        ["Ron", "11.31 Ohm", "6.655 Ohm"],
        ["CT (total)", "3.977 nF", "7.07 nF"],
        ["C1", "1.33 nF", "1.77 nF"],
        ["C2", "1.33 nF", "1.77 nF"],
        ["C3", "1.33 nF", "3.54 nF"],
        ["Cap distribution", "Equal", "C3 = 2 x C1"],
        ["Total area", "0.663 mm^2", "1.18 mm^2"],
        ["Max blocking V", "3/4 Vin", "3/4 Vin"],
    ],
    col_widths=[90, 89, 89])

# ===== PART (d): Maximum Theoretical Efficiency =====
section_slide("Part (d)", "Maximum Theoretical Efficiency")

text_slide("Part (d): Efficiency Calculation", [
    "**Given: Vin = 4V, Vout = 0.8V",
    "**Both circuits: M = 1/4 (ideal conversion ratio)",
    "",
    "**Maximum theoretical efficiency:",
    "eta_max = Vout / (M x Vin)",
    "eta_max = 0.8 / (1/4 x 4)",
    "eta_max = 0.8 / 1.0",
    "eta_max = 0.8 = 80%",
    "",
    "**Both Circuit A and Circuit B have the same ideal ratio M = 1/4",
    "=> Same maximum theoretical efficiency: 80%",
    "",
    "**Note: actual efficiency will be lower due to:",
    "- Switch conduction losses (R_on x I^2)",
    "- Bottom-plate parasitic losses",
    "- Gate drive losses",
    "- Other parasitic effects",
])

# ===== PART (e): Circuit A Simulation (SSL & FSL) =====
section_slide("Part (e)", "Circuit A Simulation: SSL vs FSL")

text_slide("Part (e): Simulation Setup", [
    "**Circuit A only (series-parallel, M = 1/4)",
    "**Component values from part (c):",
    "C1 = C2 = C3 = 1.33 nF, Cout = 80 nF, Ron = 11.31 Ohm",
    "",
    "**Two simulations at different switching frequencies:",
    "",
    "**Sim 1 - SSL regime (fs = fc/20 = 500 kHz):",
    "Slow switching limit: fs << fc => Rout dominated by R_SSL",
    "Iout reduced by 20x (0.5 mA) to keep Vout ~ M x Vin",
    "",
    "**Sim 2 - FSL regime (fs = 20fc = 200 MHz):",
    "Fast switching limit: fs >> fc => Rout dominated by R_FSL",
    "Iout = 10 mA (nominal load)",
])

text_slide("Part (e): SSL Results (fs = 500 kHz)", [
    "**Rout ~ 282 Ohm (dominated by R_SSL ~ 1/fs)",
    "",
    "**Vout ~ 860 mV with large sawtooth ripple (~15 mV p-p)",
    "",
    "**Waveform characteristics:",
    "Caps fully settle each phase (slow switching)",
    "Charge transfers are impulsive: all charge dumps into Cout at once",
    "Causes visible voltage steps in output waveform",
    "",
    "**Iout reduced by 20x to keep Vout ~ M x Vin",
    "because Vout = M x Vin - Rout x Iout",
    "With 20x higher Rout, need 20x lower Iout to maintain Vout",
])

image_slide("Part (e): SSL Simulation (fs = 500 kHz)", img("parte-sim1_SSL_fs500kHz_Vout_Rout.png"),
    "SSL regime: Vout ~ 860 mV, large sawtooth ripple, Rout ~ 282 Ohm")

text_slide("Part (e): FSL Results (fs = 200 MHz)", [
    "**Rout ~ 14.8 Ohm (dominated by R_FSL = p x Ron, independent of fs)",
    "",
    "**Vout ~ 852 mV with virtually no ripple (< 1 mV)",
    "",
    "**Waveform characteristics:",
    "Caps barely change voltage each phase (fast switching)",
    "Current is quasi-constant => Cout sees smooth, continuous charging",
    "Smooth exponential settling, no visible switching artifacts",
    "",
    "**At FSL, increasing fs further does NOT reduce Rout",
    "Only reducing Ron can improve performance",
])

image_slide("Part (e): FSL Simulation (fs = 200 MHz)", img("parte-sim2_FSL_fs200MHz_Vout_Rout.png"),
    "FSL regime: Vout ~ 852 mV, virtually no ripple, Rout ~ 14.8 Ohm")

text_slide("Part (e): SSL vs FSL Key Takeaways", [
    "**SSL (fs << fc): capacitance-limited losses",
    "Rout ~ R_SSL = m / (fs x CT)",
    "Increase C or fs to reduce Rout",
    "Large sawtooth ripple from impulsive charge transfer",
    "",
    "**FSL (fs >> fc): resistance-limited losses",
    "Rout ~ R_FSL = p x Ron (independent of fs)",
    "Only reducing Ron helps",
    "Negligible ripple from continuous charge transfer",
    "",
    "**Comparison:",
    "SSL: Rout ~ 282 Ohm, ripple ~ 15 mV p-p",
    "FSL: Rout ~ 14.8 Ohm, ripple < 1 mV",
    "",
    "**Fundamentally different charge transfer mechanisms:",
    "SSL = impulsive (all charge at once) vs FSL = continuous (smooth current)",
])

# ===== PART (f): Bottom-Plate Losses =====
section_slide("Part (f)", "Bottom-Plate Parasitic Losses")

text_slide("Part (f): Bottom-Plate Loss Analysis", [
    "**Given: Vin = 4V, caps sized as in part (c)",
    "**Parasitic capacitance:",
    "Positive (top) plate: 0.1% of C",
    "Negative (bottom) plate: 3% of C",
    "",
    "**Loss mechanism:",
    "Parasitic caps charge/discharge as node voltages change between phases",
    "P_bp = fs x sum(Cpar_i x delta_V_i^2)",
    "",
    "**Per-node parasitic (top + bottom plate at each node):",
    "Cpar = C x (0.1% + 3%) = C x 3.1%",
    "",
    "**Key driver: node voltage swings between phi1 and phi2",
    "Larger voltage swings at nodes => more bottom-plate loss",
    "Circuit A has larger voltage swings at internal nodes",
])

text_slide("Part (f): Circuit A - Bottom-Plate Losses", [
    "**Node voltage swings (normalized by Vin):",
    "C1+: |1 - 1/4| = 3/4       C1-: |3/4 - 0| = 3/4",
    "C2+: |3/4 - 1/4| = 1/2     C2-: |1/2 - 0| = 1/2",
    "C3+: |1/2 - 1/4| = 1/4     C3-: |1/4 - 0| = 1/4",
    "",
    "**Sum of squared swings:",
    "(3/4)^2 + (3/4)^2 + (1/2)^2 + (1/2)^2 + (1/4)^2 + (1/4)^2",
    "= 9/16 + 9/16 + 4/16 + 4/16 + 1/16 + 1/16 = 28/16",
    "",
    "**Cpar per node = 1.33 nF x 3.1% = 41.23 pF",
    "",
    "**P_bp = 10 MHz x 6 nodes x Vin^2 x Cpar x 28/16",
    "",
    "**P_bp = 69.3 mW  =>  more lossy",
])

text_slide("Part (f): Circuit B - Bottom-Plate Losses", [
    "**Different parasitic caps (unequal C1,C2 vs C3):",
    "Cpar_C1,C2 = 1.77 nF x 3.1% = 54.87 pF",
    "Cpar_C3 = 3.54 nF x 3.1% = 109.7 pF",
    "",
    "**C1,C2 node voltage swing sum:",
    "sum(delta_V^2) for C1,C2 plates = 7/16",
    "",
    "**C3 node voltage swing sum:",
    "sum(delta_V^2) for C3 plates = 1",
    "(C3+ swings full Vin, C3- stays at Vout)",
    "",
    "**P_bp = fs x Vin^2 x [7/16 x Cpar_C1C2 + 1 x Cpar_C3]",
    "",
    "**P_bp = 22.5 mW  =>  less lossy",
    "",
    "**Circuit B has ~3x lower bottom-plate losses than Circuit A",
])

table_slide("Part (f): Bottom-Plate Loss Comparison",
    ["Parameter", "Circuit A", "Circuit B"],
    [
        ["C1 = C2", "1.33 nF", "1.77 nF"],
        ["C3", "1.33 nF", "3.54 nF"],
        ["Cpar (3.1%)", "41.23 pF (all)", "54.87 / 109.7 pF"],
        ["Max node swing", "3/4 x Vin", "1 x Vin (C3+)"],
        ["Sum(dV^2)", "28/16", "7/16 + 1"],
        ["P_bp", "69.3 mW", "22.5 mW"],
        ["", "More lossy", "Less lossy"],
    ],
    col_widths=[90, 89, 89])

# ===== Summary =====
text_slide("Summary", [
    "**Part (a): Blocking Voltages",
    "Circuit A: max 3/4 x Vin (non-uniform distribution, 10 switches)",
    "Circuit B: mostly 1/2 x Vin (more uniform, 8 switches)",
    "",
    "**Part (b): Switch Implementation",
    "PMOS for switches near Vin, NMOS for switches near GND",
    "",
    "**Part (c): Component Sizing (Rout = 20 Ohm, fc = 10 MHz)",
    "Circuit A: Ron = 11.31 Ohm, CT = 3.977 nF, Area = 0.663 mm^2",
    "Circuit B: Ron = 6.655 Ohm, CT = 7.07 nF, Area = 1.18 mm^2",
    "",
    "**Part (d): Max Theoretical Efficiency",
    "eta_max = 80% for both (M = 1/4, Vin = 4V, Vout = 0.8V)",
    "",
    "**Part (f): Bottom-Plate Losses",
    "Circuit A: 69.3 mW (more lossy due to larger voltage swings)",
    "Circuit B: 22.5 mW (less lossy, ~3x improvement)",
])

# Save
out_path = os.path.join(DIR, "Assignment5_SCPC_Presentation.pdf")
pdf.output(out_path)
print(f"Saved: {out_path}")
print(f"Pages: {pdf.page_no()}")
