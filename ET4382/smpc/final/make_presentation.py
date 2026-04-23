#!/usr/bin/env python3
"""Generate the NEW/extra slides for the SMPC Final Project presentation.

These slides are meant to be combined (after the partner's existing
SMPCMainProject.pdf) to form the complete 20-minute deck. Same fpdf2
Helvetica style as assignment 7.
"""

from fpdf import FPDF
import os

DIR = os.path.dirname(os.path.abspath(__file__))
A7 = os.path.join(DIR, "..", "assignment7")


class Presentation(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


pdf = Presentation("L", "mm", "A4")
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=False)
W, H = 297, 210


def section_slide(title, subtitle=""):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_y(75)
    pdf.cell(0, 18, title, align="C", new_x="LMARGIN", new_y="NEXT")
    if subtitle:
        pdf.set_font("Helvetica", "", 16)
        pdf.cell(0, 12, subtitle, align="C", new_x="LMARGIN", new_y="NEXT")


def text_slide(title, bullets, font_size=12):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(15, 10)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
    pdf.line(15, 23, W - 15, 23)
    pdf.set_font("Helvetica", "", font_size)
    pdf.set_xy(20, 28)
    for b in bullets:
        if b == "":
            pdf.ln(3)
        elif b.startswith("**"):
            pdf.set_font("Helvetica", "B", font_size)
            pdf.cell(0, 7, b.replace("**", ""),
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_x(20)
            pdf.set_font("Helvetica", "", font_size)
        else:
            pdf.cell(0, 7, f"  {b}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_x(20)


def image_slide(title, img_path, caption=""):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(15, 8)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.line(15, 19, W - 15, 19)
    if os.path.exists(img_path):
        from PIL import Image as PILImage
        pil_img = PILImage.open(img_path)
        img_w_px, img_h_px = pil_img.size
        max_w = W - 30
        max_h = H - 45 - (10 if caption else 0)
        scale = min(max_w / img_w_px, max_h / img_h_px)
        disp_w = img_w_px * scale
        disp_h = img_h_px * scale
        x = 15 + (max_w - disp_w) / 2
        pdf.image(img_path, x=x, y=22, w=disp_w, h=disp_h)
    else:
        pdf.set_xy(15, 80)
        pdf.cell(0, 10, f"[Image not found: {os.path.basename(img_path)}]",
                 align="C")
    if caption:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_xy(15, H - 18)
        pdf.multi_cell(W - 30, 5, caption, align="C")


def image_text_slide(title, img_path, bullets, img_width_ratio=0.55,
                     font_size=11):
    """Image on the left, bullet text on the right."""
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(15, 8)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.line(15, 19, W - 15, 19)
    left_w = (W - 30) * img_width_ratio
    if os.path.exists(img_path):
        from PIL import Image as PILImage
        pil_img = PILImage.open(img_path)
        img_w_px, img_h_px = pil_img.size
        max_h = H - 40
        scale = min(left_w / img_w_px, max_h / img_h_px)
        disp_w = img_w_px * scale
        disp_h = img_h_px * scale
        pdf.image(img_path, x=15, y=24, w=disp_w, h=disp_h)
    text_x = 15 + left_w + 5
    text_w = W - 15 - text_x
    pdf.set_xy(text_x, 24)
    pdf.set_font("Helvetica", "", font_size)
    for b in bullets:
        pdf.set_x(text_x)
        if b == "":
            pdf.ln(3)
        elif b.startswith("**"):
            pdf.set_font("Helvetica", "B", font_size)
            pdf.multi_cell(text_w, 6, b.replace("**", ""))
            pdf.set_font("Helvetica", "", font_size)
        else:
            pdf.multi_cell(text_w, 6, f"  {b}")


def table_slide(title, headers, rows, col_widths=None, font_size=11,
                row_h=7):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(15, 8)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.line(15, 19, W - 15, 19)
    ncols = len(headers)
    if col_widths is None:
        cw = (W - 30) / ncols
        col_widths = [cw] * ncols
    pdf.set_xy(15, 24)
    pdf.set_font("Helvetica", "B", font_size)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], row_h + 1, h, border=1, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", "", font_size)
    for row in rows:
        pdf.set_x(15)
        for i, val in enumerate(row):
            pdf.cell(col_widths[i], row_h, str(val), border=1, align="C")
        pdf.ln()


img = lambda name: os.path.join(DIR, name)
img7 = lambda name: os.path.join(A7, name)

# =================== NEW SLIDES ONLY ===================
# These are appended AFTER the partner's existing SMPCMainProject.pdf
# when the two PDFs are combined.

# --- Slide A: Project Requirements ---
table_slide("Project Requirements (from the brief)", [
    "Requirement", "Target", "Notes"
], [
    ["V_in",                     "3.3 V",           "Battery / source"],
    ["V_out",                    "1.2 V",           "SoC supply"],
    ["Output ripple (pk-pk)",    "< 100 mV",        "Supply quality"],
    ["Switch-node ringing peak", "< 1.5 V above rail", "Pkg parasitics 2nH + 50mOhm per pin"],
    ["Peak load current",        "10 mA",           "Active mode"],
    ["Sleep load current",       "10 uA",           "3 orders of magnitude lower"],
    ["Peak efficiency",          ">= 90 %",         "Optimise over output power"],
    ["Line interference rej.",   "~ 40 dB @ 2 kHz", "Nearby aggressor source"],
    ["Process",                  "TSMC 180 nm BCD", "pch_5 / nch_5 devices"],
], col_widths=[70, 60, 137], font_size=11)

# --- Slide B: System-level design summary ---
text_slide("System-Level Design Choices", [
    "**Switching frequency  f_sw = 4 MHz",
    "  High enough to use small (inductor ~ 10 uH, cap ~ 50 nF)",
    "  Low enough that gate-drive / switching losses stay bounded",
    "",
    "**Filter:  L = 9.55 uH,  C = 50 nF",
    "  From ripple-current + ripple-voltage constraints (slide 3)",
    "",
    "**Power stage: synchronous buck, pch_5 HS + nch_5 LS",
    "  Open-loop PWM from vpulse V1 for ass-6 characterisation",
    "  Closed loop added using Type-III compensator (ass-7 work - reused here)",
    "",
    "**Gate driver: 2-stage tapered CMOS inverter chain",
    "  Non-overlap NAND + dead-time tdel = 10 ns prevents shoot-through",
    "",
    "**Parasitics: each chip-to-PCB connection modelled as 2 nH + 50 mOhm",
    "  Impacts switch-node ringing and efficiency (see efficiency slide)",
    "",
    "**Sleep mode: future-scope PFM / burst, see dedicated slide",
])

# --- Slide C: Measured scalars ---
table_slide("Measured Results (Open-loop, 10 mA Load)", [
    "Quantity",             "Measured",   "Spec / Target", "Margin"
], [
    ["V_out avg",           "1.009 V",    "1.2 V (ideal)",   "-191 mV (open-loop droop)"],
    ["V_out ripple pk-pk",  "11.24 mV",   "< 100 mV",        "9x margin - PASS"],
    ["I_L avg",             "8.406 mA",   "~10 mA",          "scaled with V_out droop"],
    ["I_L ripple pk-pk",    "18.84 mA",   "-",               "ratio 2.24x -> DCM boundary"],
    ["V_PWM max",           "3.741 V",    "< V_in + 1.5 V",  "+441 mV - PASS"],
    ["V_PWM min",           "-545 mV",    "-",               "LS body-diode conduction"],
    ["I_bat (from V_in)",   "3.903 mA",   "-",               "open-loop"],
    ["P_in",                "12.88 mW",   "-",               "= 3.3 V x 3.903 mA"],
    ["P_out",               "8.48 mW",    "-",               "= V_out x I_L_avg"],
    ["Efficiency (meas.)",  "65.8 %",     ">= 90 %",         "FAIL (open-loop, FETs oversized)"],
], col_widths=[60, 55, 65, 87], font_size=10, row_h=7)

# --- Slide D: Transient image 10 mA ---
image_slide("Open-Loop Transient - 10 mA Load (R_L = 120 Ohm)",
            img("01_transient_10mA.png"),
            "V_out (red) settles at 1.009 V - 191 mV below 1.2 V target due to 8% duty loss "
            "from dead-time and conduction drops. V_PWM (green) switches cleanly 0->3.3 V with "
            "peak 3.74 V. I_L (magenta) 8.4 mA average, 18.8 mA pk-pk - near DCM boundary.")

# --- Slide E: Switch-node ringing & parasitics ---
text_slide("Switch-Node Ringing under Package Parasitics", [
    "**Brief: each chip-to-PCB wire = 2 nH + 50 mOhm",
    "",
    "**Measured V_PWM extremes (with open-loop PWM):",
    "  V_PWM_max = 3.741 V   -> +441 mV above V_bat (3.3 V)",
    "  V_PWM_min = -545 mV  -> LS body-diode forward conduction during dead-time",
    "",
    "**Ringing peak well under the 1.5 V over-rail limit  ->  PASS",
    "",
    "**Origin of the positive spike:",
    "  When LS turns off, the parasitic L stores energy proportional to I_L * L",
    "  Energy dumps into SW-node parasitic C -> L-C ring at ~ 1/(2pi*sqrt(L_par*C_par))",
    "  Amplitude scales with di/dt -> our 500 um drivers are fast (large dI/dt)",
    "",
    "**Mitigations considered (not all implemented):",
    "  Slow the gate driver (trade with switching losses)",
    "  Snubber (R-C) at switch node (added BOM)",
    "  Bond-wire parallelisation -> reduce L_par",
    "",
    "**Worst case over load, V_in, temp: still < 1 V over-rail in simulation",
])

# --- Slide F: 10 uA sleep case ---
image_slide("Open-Loop Transient - 10 uA Sleep Load (R_L = 120 kOhm)",
            img("02_transient_10uA.png"),
            "At 10 uA load the converter enters deep DCM. Open-loop duty is unchanged "
            "(D=0.3636) so V_out rises toward V_in - visible as ~1.6 V here. This is "
            "exactly the pathology that motivates a PFM / burst-mode controller for "
            "the sleep state (discussed on sleep-mode slide).")

# --- Slide G: Light-load over-voltage analysis ---
text_slide("Why Open-Loop Fails at 10 uA: DCM Over-voltage", [
    "**K = 2*L*f_sw / R_L determines CCM vs DCM:",
    "  At 10 mA:  K = 2*10u*4M / 120  = 6.67e-4    (DCM boundary - barely)",
    "  At 10 uA:  K = 2*10u*4M / 120k = 6.67e-7    (deep DCM)",
    "",
    "**Fixed-duty buck in DCM cannot regulate V_out:",
    "  Inductor fully discharges, output cap charges toward V_in on average",
    "  Open-loop V_out climbs well above 1.2 V (sim: ~1.6 V)",
    "",
    "**Implications for the SoC at 10 uA:",
    "  Supply would exceed its 1.2 V rating - unacceptable",
    "  Linear regulation alone wastes current (cannot make 3.3 V into 1.2 V at 10 uA efficiently)",
    "",
    "**Solution approach (see Sleep-Mode slide):",
    "  Burst / PFM: deliver short pulses, sleep between them, average V_out = 1.2 V",
    "  Gate driver OFF during sleep window -> near-zero quiescent dissipation",
    "",
    "**Conclusion from this measurement:",
    "  Closed-loop + light-load handling is NOT optional for the brief's 10 uA spec",
    "  -> Next slides: feedback architecture + Type-III loop we have already closed (ass-7)",
])

# --- Slide H: Efficiency measured vs theoretical ---
text_slide("Efficiency Analysis - Measured vs Theoretical", [
    "**Measured @ 10 mA load (open-loop):",
    "  P_in  = V_in * |I_bat| = 3.3 V * 3.903 mA = 12.88 mW",
    "  P_out = V_out * I_L    = 1.009 * 8.406 mA = 8.48 mW",
    "  eta_meas = 65.8 %",
    "",
    "**Theoretical conduction-only (Appendix-2 hand-calc):",
    "  R_on,PMOS = 72 mOhm, R_on,NMOS = 203 mOhm (from Ron extraction)",
    "  P_cond = I^2 * R_eff = (8.57 mA)^2 * 0.155 = 1.14 uW (avg) + ripple term",
    "  -> eta_cond_only ~ 99.3 %",
    "",
    "**Where does the ~33 % efficiency gap go?",
    "  1) Gate-drive charge: P_gate = Q_g * V_dd * f_sw",
    "     Power FETs W=400 um, driver FETs also ~400 um -> large C_g * V * f",
    "     ** FETs sized for much larger currents - dominant loss at 10 mA **",
    "  2) Switching loss: 0.5*V*I*t_sw*f_sw in overlap intervals",
    "  3) Body-diode conduction during 10 ns dead-time (V_PWM = -545 mV)",
    "  4) Parasitic L-C ringing dissipation",
    "",
    "**Optimisation path (not all executed):",
    "  Shrink driver + power FETs for 10 mA load -> projected eta >= 90 %",
    "  Scale gate width with load (segmented power stage) for peak eta vs load",
    "  See 'What We Did Not Do' doc for the path to meeting the 90 % spec",
])

# --- Slide I: Gate driver design ---
text_slide("Gate Driver Design Considerations", [
    "**Topology: 2-stage tapered CMOS inverter chain per HS / LS path",
    "  Stage A (M2/M3 - from schematic): drives stage B",
    "  Stage B (M4/M5): drives the power FET gate",
    "  Taper ratio chosen to balance propagation delay vs per-stage Q_g",
    "",
    "**Non-overlap generator:  NAND (I0/I1) + inverter (I2) with tdel = 10 ns",
    "  Prevents shoot-through (HS+LS both ON)",
    "  tdel chosen > worst-case driver tr/tf spread",
    "",
    "**Observed consequence of dead-time:",
    "  During tdel, LS body diode carries inductor current -> V_PWM = -0.55 V",
    "  Duty-cycle loss: 2 x 10 ns / 250 ns = 8 %",
    "  Equivalent effective duty: D_eff = 0.36 x (1 - 0.08) = 0.33 -> V_out_ideal = 1.1 V",
    "  Plus conduction drops: measured V_out = 1.01 V (consistent with above)",
    "",
    "**Trade-off dials (explored via simM multipliers):",
    "  Larger driver -> faster edge, lower switching loss, MORE gate-drive power, MORE ringing",
    "  Smaller driver -> slower edge, more switching loss, LESS gate-drive power, LESS ringing",
    "",
    "**Iteratively sized for the 10 mA operating point - see FET-sizing slide for values",
    "  Not yet re-optimised for the 10 uA sleep point",
])

# --- Slide J: Feedback loop architecture (image + bullets) ---
image_text_slide("Closed-Loop Architecture - Feedback Loop",
                 img("04_feedback_loop_schematic.png"),
                 [
                     "**Feedback divider:",
                     "R7 = 8 kOhm / R8 = 10 kOhm",
                     "k_div = R8/(R7+R8) = 0.556",
                     "",
                     "**Error amp: ideal op-amp",
                     "Compares V_fb to V_ref = 1.0 V",
                     "Output = V_comp (compensator node)",
                     "",
                     "**PWM generator:",
                     "E0 VCVS with egain = 1e4 acts as",
                     "ideal comparator between V_comp",
                     "and sawtooth V2 (tvpairs:2 source)",
                     "",
                     "**Controller:",
                     "Type-III C(s) - fully designed and",
                     "verified in Assignment 7",
                     "(pole/zero frequencies on next slides)",
                     "",
                     "**Final-project adaptation:",
                     "V_ref = 1.0 V, divider 8k/10k chosen",
                     "to give V_out = V_ref/k_div = 1.8 V",
                     "Needs re-scaling for 1.2 V target",
                     "(e.g. R_top=4k, R_bot=10k -> 1.4 V;",
                     "or lower V_ref to 0.666 V for 1.2 V)",
                 ],
                 img_width_ratio=0.58, font_size=10)

# --- Slide K: Compensator Bode (from ass-7) ---
image_slide("Type-III Compensator C(s) - Standalone Bode (from ass-7)",
            img7("03_compensator_Cs_bode.png"),
            "Type-III shape verified: integrator below f_ZEA=5 kHz, mid-band ~17 dB, "
            "+20 dB/dec boost between f_FZ=30 kHz and f_FP=3.3 MHz peaking ~50 dB, "
            "HF pole f_HF=2 MHz for switching-ripple rejection. Phase: 90 -> 250 -> 90 deg.")

# --- Slide L: Loop gain measured ---
image_slide("Closed-Loop Gain L(s) - Measured (stb, from ass-7)",
            img7("04_loop_gain_Ls_bode.png"),
            "M1 @ 200 Hz: |L| = +40.36 dB -> loop rejects 200 Hz line by 100x "
            "|  M2 @ 316 kHz: |L| = 0 dB -> f_c crossover "
            "|  M3 @ 316 kHz: phase = +51.2 deg -> PM. "
            "For the final-project 2 kHz target, the same loop gives ~20 dB at 2 kHz "
            "(integrator roll-off 20 dB/decade), so compensator re-tune needed (see gaps doc).")

# --- Slide M: Corner frequencies ---
image_slide("Measured Corner Frequencies (ADE Outputs, from ass-7)",
            img7("04b_corner_freqs_measured.png"),
            "fZEA = 4.997 kHz, fFZ = 30.03 kHz, fFP = 3.300 MHz, fHF = 1.994 MHz. "
            "All four corners within 0.3 % of target - compensator component values are correct.")

# --- Slide N: Closed-loop steady state ---
image_slide("Closed-Loop Steady-State V_out (from ass-7)",
            img7("05b_Vout_steadystate_ripple.png"),
            "Closed-loop buckvoltagemode @ 2 MHz. V_PWM clean 0-5 V switching, "
            "V_comp active (ideal-amp artifact), V_out settles 1.80 V +/- 20 mV - "
            "stable, no sub-harmonic oscillation. Confirms PM of ~ 51 deg is healthy.")

# --- Slide O: Interference rejection ---
text_slide("Interference Rejection - Brief Target 40 dB @ 2 kHz", [
    "**Closed-loop line-to-output transfer:",
    "    V_out / dV_bat  =  D / (1 + L(jw))",
    "",
    "**Using the ass-7 Type-III loop:",
    "  |L(200 Hz)|  = 40.36 dB   (measured, slide L)",
    "  |L(2 kHz)|   ~ 20 dB      (-20 dB/dec integrator roll-off from 200 Hz)",
    "",
    "**Predicted PSRR at the two frequencies (D = 0.36):",
    "  PSRR(200 Hz) = 20*log10(0.36 / (1 + 100))  = -49 dB      (ass-7 result)",
    "  PSRR(2 kHz)  = 20*log10(0.36 / (1 + 10))   ~ -30 dB      (ass-7 loop reused)",
    "",
    "**To reach -40 dB @ 2 kHz we need |L(2 kHz)| >= 40 dB.  Options:",
    "  a) Push f_ZEA from 5 kHz up to ~50 kHz",
    "      -> PM drops; may need f_FZ/f_FP re-placement to compensate",
    "  b) Raise A_mid (currently 7; need ~25)",
    "      -> larger R2, same C2",
    "  c) Hybrid: f_ZEA = 20 kHz with A_mid = 15",
    "      -> |L(2 kHz)| = A_mid * f_ZEA / 2 kHz = 15 * 10 = 150x = 43 dB   PASS",
    "",
    "**Status: re-tune path is understood but NOT yet executed; see gaps doc",
    "  Ass-7 PSRR screenshot (next slide) shows the mechanism works - number needs scaling",
])

# --- Slide P: PSRR evidence (ass-7 screenshot) ---
image_slide("Line-Disturbance Response - Evidence (from ass-7)",
            img7("07_line_step_PSRR.png"),
            "Transient with 0.5 V sinusoid on V_bat (1 Vpp @ 200 Hz). V_out envelope stays "
            "1.72-1.82 V - consistent with switching ripple + small ~3 mV component at 200 Hz "
            "(-49 dB PSRR). Same mechanism scales to 2 kHz with the compensator re-tune above.")

# --- Slide Q: Sleep mode strategy ---
text_slide("Sleep-Mode Strategy - 10 uA Case", [
    "**Problem (demonstrated on light-load slide):",
    "  Fixed-duty PWM in DCM at 10 uA lets V_out rise to ~1.6 V",
    "  Continuous switching at f_sw = 4 MHz also wastes gate-drive power",
    "",
    "**Proposed architecture - Pulse-Frequency Modulation (PFM) / burst mode:",
    "  1) Sleep-detect: comparator flags when I_load drops (or when V_out overshoots)",
    "  2) Gate of driver -> high-Z, power stage idles; output cap holds V_out",
    "  3) When V_out droops below V_ref - hysteresis, deliver a SHORT burst of PWM",
    "  4) Return to idle; repeat",
    "",
    "**Expected duty of burst cycles:",
    "  P_out_sleep = 1.2 V * 10 uA = 12 uW",
    "  Burst period T_b ~ C * dV / I_load = 50n * 10m / 10u = 50 ms",
    "  -> very long idle intervals -> negligible gate-drive cost",
    "",
    "**Control-loop integration:",
    "  Type-III bypassed during sleep (loop disabled to save quiescent amp current)",
    "  Hysteretic comparator only; wake-up triggers full loop restart",
    "",
    "**Efficiency projection in sleep:",
    "  If quiescent current reduced to ~2 uA -> eta_sleep ~ 70 % at 10 uA",
    "  Current fixed-PWM design would fail this target by orders of magnitude",
    "",
    "**Status: architecture defined, NOT implemented in silicon sim (see gaps doc)",
])

# --- Slide R: Summary ---
table_slide("Summary - Final-Project Brief Compliance", [
    "Topic", "Status", "Evidence / Notes"
], [
    ["System-level design (f_sw, L, C)", "DONE",
     "f_sw=4 MHz, L=9.55 uH, C=50 nF; ripple 11 mV << 100 mV spec"],
    ["Power FET sizing",                 "DONE",
     "W/L = 400u/500n (P), 400u/600n (N); R_on 72m/203m"],
    ["Gate driver",                      "DONE (baseline)",
     "2-stage tapered + 10 ns non-overlap; over-sized for 10 mA - see gaps"],
    ["Efficiency analysis",              "PARTIAL",
     "measured 65.8% @ 10 mA; path to 90% in gaps doc"],
    ["Parasitic impact",                 "DONE",
     "V_ring peak = 441 mV << 1.5 V limit with 2nH+50mOhm model"],
    ["Control loop",                     "DONE via ass-7 reuse",
     "Type-III: |L(200 Hz)|=40 dB, f_c=316 kHz, PM=51.2 deg"],
    ["Interference rejection (40dB@2kHz)","PARTIAL",
     "ass-7 loop gives 20 dB @ 2 kHz; re-tune path documented"],
    ["Sleep mode (10 uA)",               "ARCHITECTURE",
     "PFM/burst concept defined; not implemented in sim"],
    ["Peak efficiency >= 90 %",          "NOT MET",
     "open-loop 66%; blocked by FET over-sizing - analysis on eta slide"],
], col_widths=[60, 55, 152], font_size=10, row_h=8)

# Save
out_path = os.path.join(DIR, "SMPC_Final_NewSlides.pdf")
pdf.output(out_path)
print(f"Saved: {out_path}")
print(f"New slides: {pdf.page_no()}")
