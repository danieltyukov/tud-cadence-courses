#!/usr/bin/env python3
"""Generate PDF presentation for Assignment 3A - Power Stage Design"""

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
    pdf.cell(0, 20, "Homework Assignment 3A", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 24)
    pdf.cell(0, 15, "Power Stage Design", align="C", new_x="LMARGIN", new_y="NEXT")
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

# ===== Overview =====
image_slide("Circuit Overview: NMOS Half-Bridge", img("OutputStage.png"),
    "Class-D output stage with TSMC 0.18um BCD process (nld12_g5a_nbl_mac PowerFETs)")

# ===== PART 1: PowerFET Sizing =====
section_slide("Part 1", "PowerFET Sizing (R_ON <= 50 mOhm at 150C)")

text_slide("Part 1: PowerFET Sizing", [
    "**Goal: Size the nld12_g5a_nbl_mac PowerFET for R_ON <= 50 mOhm at 150C",
    "",
    "**Method:",
    "DC sweep of total gate width W",
    "VGS = 5V, VDS = 100mV, T = 150C",
    "R_ON = VDS / ID = 100mV / ID",
    "",
    "**Result:",
    "At W = 103mm (nf = 400 fingers): R_ON = 50.02 mOhm",
    "ID = 1.9992A at the target operating point",
    "",
    "**Key formula:",
    "N_fingers = ceil(R_ON,single / R_ON,target)",
    "W_total = N x W_finger",
])

image_slide("Part 1: R_ON vs Width", img("50mOhm_Ron.png"),
    "Top: ID vs W, Bottom: R_ON vs W. Marker at W=103mm, R_ON=50.02 mOhm")

# ===== PART 2: V_TH and Q_G =====
section_slide("Part 2", "Threshold Voltage & Gate Charge")

text_slide("Part 2: V_TH Extraction & Gate Charge", [
    "**V_TH Extraction:",
    "DC sweep: VGS from 0 to 5V, VDS = 100mV, T = 27C",
    "V_TH ~ 0.75V (where drain current starts flowing)",
    "",
    "**Gate Charge Q_G:",
    "Transient simulation: gate driven 0 to 5V",
    "Gate current integrated over time: Q_G = integral(I_G dt)",
    "Q_G = 1.247 nC",
    "",
    "**Gate charge power loss (per half-bridge):",
    "P_Q = f_SW x 2 x V_SUP x (Q_GL + Q_GH)",
    "",
    "**Observations:",
    "Gate current peaks at ~450mA during turn-on",
    "Miller plateau visible in gate voltage ramp",
    "Drain voltage collapses from 20V to ~1mV as FET turns on",
])

image_slide("Part 2: V_TH Extraction", img("Vth_extraction.png"),
    "DC sweep of ID vs VGS. V_TH ~ 0.75V at onset of conduction")

image_slide("Part 2: Gate Charge Q_G", img("GateCharge.png"),
    "Gate current, integrated charge (Q_G=1.247nC), gate voltage, drain voltage")

# ===== PART 3: Gate Driver Sizing =====
section_slide("Part 3", "Gate Driver Sizing")

text_slide("Part 3: Gate Driver Sizing", [
    "**Target: ~25ns rise/fall time at PowerFET gate",
    "",
    "**Driver sizing:",
    "PMOS: pmos5v_mac, W = 3u, L = 500n",
    "NMOS: nmos5v_mac, W = pmos_w x 4 = 12u, L = 600n",
    "",
    "**Skewed design (W_NMOS >> W_PMOS):",
    "Fast turn-OFF (strong NMOS pull-down) prevents shoot-through",
    "Slower turn-ON (weaker PMOS pull-up) is acceptable with dead time",
    "",
    "**Measured results:",
    "Rise time (Vgl: 0 to 5V): 19.19ns",
    "Fall time (VgsH: 5V to 0V): 2.61ns",
    "",
    "**Average gate drive current:",
    "I_avg = Q_G / t_rise = 1.247nC / 25ns ~ 50mA",
])

image_slide("Part 3: Rise Time", img("RiseTime.png"),
    "Vgl rise time = 19.19ns (turn-ON of low-side FET)")

image_slide("Part 3: Fall Time", img("FallTime.png"),
    "VgsH fall time = 2.61ns (fast turn-OFF via strong NMOS pull-down)")

# ===== PART 4: Dead Time =====
section_slide("Part 4", "Dead Time Verification")

text_slide("Part 4: Dead Time", [
    "**Dead time = 5ns (break-before-make)",
    "",
    "**Implementation:",
    "ahdlLib nand_gate + not_gate with tdel = 5ns",
    "Non-overlap generator ensures both FETs are never ON simultaneously",
    "",
    "**Measurement:",
    "Zoomed to rising edge of /input at ~1.0us",
    "O- falls first, then after 5.04ns, O+ rises",
    "During this gap, both gate drive signals are LOW",
    "Both PowerFETs are OFF (prevents shoot-through)",
])

image_slide("Part 4: Dead Time Verification", img("Deadtime.png"),
    "O- falls first, O+ rises 5.04ns later. Both FETs OFF during dead time.")

# ===== PART 5: Half-Bridge Verification =====
section_slide("Part 5", "Half-Bridge Verification (+/-2A)")

text_slide("Part 5: Soft vs Hard Switching", [
    "**Soft Switching (iload = +2A):",
    "Load current assists the transition",
    "Faster dVsw/dt, body diode conducts after transition",
    "VgsH stays low during dead time (no shoot-through risk)",
    "",
    "**Hard Switching (iload = -2A):",
    "Load current resists the transition",
    "Slower dVsw/dt, body diode conducts during dead time",
    "VgsH rises to ~3V due to Cgd coupling (shoot-through risk)",
    "Skewed driver keeps VgsH below V_TH",
    "",
    "**Cgd coupling formula:",
    "I_GD = C_GD x dV_sw/dt",
    "This current pulls V_GS of OFF FET above V_TH -> shoot-through",
])

image_slide("Part 5: All Signals (+2A, Soft Switching)", img("a3a_p1_all.png"),
    "Vinput, O+/O-, Vgh, Vgl, Vsw, VgsH/VgsL, Isupply. Clean switching.")

image_slide("Part 5: All Signals (-2A, Hard Switching)", img("a3a_p1_all_neg2A.png"),
    "VgsH rises to ~3V during dead time due to Cgd coupling. No shoot-through.")

image_slide("Part 5: Switching Node Zoomed", img("Vsw (switching node) zoomed.png"),
    "Vsw transition from ~-1V to 12V in ~5ns. Clean, no ringing.")

image_slide("Part 5: Shoot-Through Check", img("shoot_through_check.png"),
    "Brief capacitive spike (~2.79A, ~5ns) during transition. No sustained overlap.")

image_slide("Part 5: Load Current at Turn-On", img("LoadCurrent.png"),
    "Initial inrush: spikes to ~3.2A, settles to 2A. Normal behavior.")

# ===== PART 6: BTL Configuration =====
section_slide("Part 6", "BTL Configuration with LC Filter")

text_slide("Part 6: BTL Architecture", [
    "**Why BTL (Bridge-Tied Load)?",
    "Single half-bridge: sw toggles 0-12V, DC average = 6V offset",
    "BTL: two half-bridges drive load differentially",
    "V_diff = sw_A - sw_B, swings +/-12V with zero DC offset",
    "",
    "**AD-PWM (Analog Double-Edge):",
    "Half-bridge A: O+ to high-side, O- to low-side",
    "Half-bridge B: O- to high-side, O+ to low-side (swapped)",
    "When A=HIGH, B=LOW and vice versa",
    "",
    "**LC Filter:",
    "L = 18uH, C = 820nF per side",
    "f0 = 1/(2*pi*sqrt(L*C)) = 41.4 kHz",
    "Passes audio (20Hz-20kHz), blocks 1MHz switching",
    "",
    "**Load: 4 Ohm connected differentially (out_A to out_B)",
])

image_slide("Part 6: BTL Schematic", img("btl_schematic.png"),
    "Two half-bridges with swapped O+/O- for AD-PWM, LC filters, differential load")

image_slide("Part 6: BTL at mi=0 (Settling)", img("btl_mi0_settling.png"),
    "Full 100us: sw_A/sw_B inverted, out_A/out_B settle to ~6V, V_diff -> 0V")

image_slide("Part 6: BTL at mi=0 (Settled)", img("btl_mi0_settled.png"),
    "Steady state: V_diff = -24.5mV (~0V), V_cm = 6.0V (constant, AD-PWM property)")

text_slide("Part 6: Efficiency Measurement", [
    "**Comparator-based PWM for mi sweep:",
    "Triangle carrier (1MHz) + DC signal (mi) + ahdlLib comparator",
    "Duty cycle proportional to modulation index mi",
    "",
    "**Efficiency formula:",
    "eta = P_load / (P_sup + P_reg)",
    "P_sup = V_SUP x average(I_SUP)    [12V supply]",
    "P_reg = V_REG x average(I_REG)    [5V gate driver supply]",
    "P_load = average(V_diff x I_load)",
    "",
    "**Parametric sweep: mi = 0 to 0.9 (10 steps)",
    "",
    "**Power loss breakdown:",
    "P_R (conduction) = I^2 x R_ON  -- increases with mi",
    "P_Q (gate charge) = f_SW x 2 x V_SUP x Q_G  -- constant",
    "P_X (switching) = f_SW x t_x x V_SUP x I_OUT  -- hard switching only",
])

image_slide("Part 6: PWM Input Stage", img(" btl_efficiency_input_stage.png"),
    "Triangle carrier + DC signal (mi) + comparator generates variable-duty PWM")

image_slide("Part 6: Efficiency vs mi (1x Drivers)", img("btl_efficiency_vs_mi.png"),
    "P_su, P_reg, P_load, eta vs mi. Efficiency increases with output power.")

# ===== PART 7: 4x Driver Comparison =====
section_slide("Part 7", "4x Gate Driver Comparison")

text_slide("Part 7: 1x vs 4x Gate Drivers", [
    "**Tradeoff:",
    "Larger driver -> faster switching -> less P_X (switching loss)",
    "Larger driver -> more driver capacitance -> more P_Q (gate charge loss)",
    "",
    "**1x Drivers: pmos_w = 3u, nmos_w = 12u",
    "**4x Drivers: pmos_w = 12u, nmos_w = 48u",
    "",
    "**Expected behavior:",
    "Low mi: P_Q dominates -> 4x drivers = worse efficiency",
    "High mi: P_X dominates -> 4x drivers = better efficiency",
    "Crossover point where bigger drivers become beneficial",
    "",
    "**Simulation result:",
    "1x and 4x efficiency curves are very similar",
    "P_reg difference only ~0.3mW (20.2 vs 20.5mW)",
    "Due to ideal components (vcvs level shifters, ahdlLib gates)",
    "Real implementation would show larger differences",
])

image_slide("Part 7: Efficiency vs mi (4x Drivers)", img("btl_efficiency_vs_mi_4x.png"),
    "4x drivers (pmos_w=12u): nearly identical efficiency to 1x drivers")

table_slide("Part 7: 1x vs 4x Comparison",
    ["Parameter", "1x (pmos_w=3u)", "4x (pmos_w=12u)"],
    [
        ["P_reg (gate driver)", "~20.2 mW", "~20.5 mW"],
        ["P_load at mi=0.9", "~28 W", "~28 W"],
        ["Switching speed", "Baseline", "~4x faster"],
        ["Efficiency curve", "Baseline", "Nearly identical"],
    ],
    col_widths=[90, 89, 89])

# ===== Summary =====
text_slide("Summary", [
    "**Part 1: PowerFET Sizing",
    "nf=400 fingers, W=103mm, R_ON=50.02 mOhm at 150C",
    "",
    "**Part 2: V_TH = 0.75V, Q_G = 1.247 nC",
    "",
    "**Part 3: Gate Driver - Rise=19ns, Fall=2.6ns (skewed: W_N=4xW_P)",
    "",
    "**Part 4: Dead Time = 5.04ns (break-before-make verified)",
    "",
    "**Part 5: Half-Bridge verified at +/-2A",
    "Soft switching: clean. Hard switching: VgsH rises to 3V but no shoot-through",
    "",
    "**Part 6: BTL with LC Filter",
    "V_diff~0V at mi=0, V_cm=6V constant (AD-PWM property)",
    "Efficiency increases with modulation index (output power)",
    "",
    "**Part 7: 4x drivers show similar efficiency (ideal component limitation)",
])

# Save
out_path = os.path.join(DIR, "Assignment3A_5714699.pdf")
pdf.output(out_path)
print(f"Saved: {out_path}")
print(f"Pages: {pdf.page_no()}")
