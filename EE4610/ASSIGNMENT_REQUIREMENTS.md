# EE4610 Digital IC Design I - Assignment Requirements

**Group Members:**
- Daniel Tyukov (5714699)
- Senquan Zhang (6338216)
- Yaonan Hu (6573657)

**Technology:** TSMC 180nm (tsmc18)
**Tools:** Cadence Virtuoso, Calibre DRC
**Server:** ee4610.ewi.tudelft.nl

---

## **Transistor Dimensions (Calculated)**

```
PMOS Width (W_P): 2.0 μm
NMOS Width (W_N): 1.0 μm
Length (L):       0.18 μm (minimum)
```

**Calculation:** W_P = [(9+6+7) mod 3] + 1 = 2 μm

---

# Assignment 1: NAND Gate Design (Schematic + Layout)

**Deadline:** December 19th, 2025

## Part 1-1: Schematic Design

### Design Specifications

**Libraries:**
- tsmc18 (transistor models)
- analogLib (test components)

**Transistor Models:**
- PMOS: `pmos2v` (W=2.0μm, L=0.18μm)
- NMOS: `nmos2v` (W=1.0μm, L=0.18μm)

**Supply Voltage:** VDD = 1.8V

---

### Step 1: Verify NAND Gate Function

**Objective:** Prove the circuit works correctly as a NAND gate

**Tasks:**
1. Create schematic with PMOS and NMOS transistors
2. Generate symbol from schematic (Create → Cellview → FromCellview)
3. Create testbench cellview
4. Add input voltage sources from analogLib:
   - Input A: Pulse waveform
   - Input B: Pulse waveform
   - VDD: DC voltage source (1.8V)
   - VSS: Ground
5. Add output probe

**Test Input Pattern:**
```
A = alternating pulses
B = alternating pulses (different pattern)

Verify truth table:
A | B | OUT
0 | 0 | 1
0 | 1 | 1
1 | 0 | 1
1 | 1 | 0
```

**Simulation Setup:**
- Launch → ADE L
- Analysis: Transient (tran)
- Stop time: Long enough to see all input combinations
- Select outputs to plot (From Design)

**Deliverable:**
- Screenshot of schematic with clear component labels
- Screenshot of symbol
- Screenshot of testbench
- Screenshot of input/output waveforms showing NAND operation

---

### Step 2: Analyze Performance Parameters

**Objective:** Measure propagation delay, rise/fall times, and power consumption

**Input Signal Specifications:**
```
Input A:
  - Pattern: 101010... (alternating)
  - Period: 2ms
  - Pulse Width: 1ms
  - Rise/Fall Edge: 100ps
  - V1: 0V, V2: 1.8V

Input B:
  - Pattern: 111111... (constant high)
  - DC: 1.8V
```

**Timeline:**
```
Time(ms):  0    1    2    3    4    5    6
A:         0    1    0    1    0    1    0
B:         1    1    1    1    1    1    1
```

**Create New Testbench:**
- Separate testbench cellview for performance testing
- Configure voltage sources with exact specifications above

**Parameters to Measure:**

#### 1. Propagation Delay
Measure time delay from input transition to output transition:

- **t_PHL (High-to-Low):** Time from input 50% to output 50% (falling)
- **t_PLH (Low-to-High):** Time from input 50% to output 50% (rising)
- **Average Propagation Delay:** (t_PHL + t_PLH) / 2

**How to measure in Virtuoso:**
- Use marker tool in waveform viewer
- Place markers at 50% points of input and output transitions

#### 2. Rise Time & Fall Time
Measure output transition times:

- **Rise Time (t_r):** Time from 10% to 90% of rising edge
- **Fall Time (t_f):** Time from 90% to 10% of falling edge

**Reference:**
```
100% ─────────┐
 90% ──────┐   │
            │   │
 10% ──┐   │   │
  0% ──┘   └───┘
      └─t_r─┘ └─t_f─┘
```

#### 3. Quiescent Power (Static Power)
Power consumed when circuit is idle (no switching):

- Measure DC current from VDD when outputs are stable
- **P_quiescent = VDD × I_DC**

**How to measure:**
- Add current probe on VDD net
- Measure average current during stable periods (no transitions)

#### 4. Dynamic Power (Switching Power)
Power consumed during switching activity:

- Measure average current from VDD during transitions
- **P_dynamic = VDD × I_avg (during switching)**
- Can also calculate: P_dynamic = C_L × VDD² × f
  - C_L: load capacitance
  - f: switching frequency (500 Hz for 2ms period)

**How to measure:**
- Use Calculator in ADE L
- Measure average power: `avgPower(VT("/VDD"))`
- P_dynamic = P_total - P_quiescent

**Deliverables:**
- Screenshot of testbench with input signal configurations
- Screenshot of transient simulation waveforms
- Screenshot showing measurement markers for timing
- Table of measured values:
  | Parameter | Value | Unit |
  |-----------|-------|------|
  | t_PHL | | ps |
  | t_PLH | | ps |
  | t_propagation | | ps |
  | Rise Time | | ps |
  | Fall Time | | ps |
  | P_quiescent | | μW |
  | P_dynamic | | μW |
  | P_total | | μW |
- Brief analysis explaining the results

---

## Part 1-2: Layout Design

**Objective:** Create physical layout of NAND gate and verify with DRC

### Prerequisites Setup

**Calibre Integration:**
1. Exit Virtuoso
2. Copy CalibreSetup files from Brightspace:
   - `.cdsinit` (hidden file)
   - `sourceme`
3. Place in tsmcBCD directory (replace existing)
4. Run: `source sourceme`
5. Start Virtuoso: `virtuoso &`
6. Verify "Calibre" appears in menu bar

---

### Step 1: Start Layout

**From Schematic:**
1. Open your NAND schematic (not testbench, not symbol)
2. Launch → Layout XL
3. Check left panel shows all technology layers

**Display Settings:**
- Press `E` (Options → Display)
- Set X/Y Snap Spacing: 0.005 (5nm) - foundry requirement
- Set Grid Spacing as needed
- Click OK

---

### Step 2: Import Components

**Import Transistors:**
1. Connectivity → Update → Components And Nets
2. Settings:
   - ✓ Update Net Signal Type
   - ✓ Update Net Min/MaxV
   - ✓ Update Instance Masters by: Replacing the Old
   - ✓ Generate: Instances, I/O Pins, PR Boundary
3. Click OK

**Result:** PMOS and NMOS will appear in layout window

---

### Step 3: Draw Metal Layers

**Layout Structure:**
- PMOS transistors (top)
- NMOS transistors (bottom)
- Metal1 connections between components
- Poly gates (shared inputs A, B)
- Metal1 for VDD (top rail)
- Metal1 for VSS (bottom rail)
- Metal1 for output

**Keyboard Shortcuts:**
```
r  - Create Rectangle
m  - Move
s  - Stretch (be careful - deselect first)
p  - Create Path
c  - Copy
u  - Undo
q  - Show properties
k  - Ruler (measure distances)
i  - Add instance
f  - Fit view
```

**Layer Selection:**
- Select layer from LSW palette (left panel)
- Common layers:
  - POLY (polysilicon - gates)
  - METAL1 (first metal layer)
  - METAL2 (second metal layer)
  - CONT (contacts between layers)
  - VIA (vias between metal layers)
  - NWELL (n-well for PMOS)
  - PIMP/NIMP (p/n implants)

**Important Layout Rules (refer to DRC rules):**
- Minimum METAL1 width: 0.23 μm
- Minimum METAL1 spacing: 0.23 μm
- Minimum POLY width: 0.18 μm
- Use ruler (press `k`) to verify dimensions
- Follow design rules to minimize DRC errors

**Drawing Process:**
1. Press `r` for rectangle
2. Select layer (e.g., METAL1) from LSW
3. Left-click to start, drag, click to finish
4. Press `Esc` to exit drawing mode

**Connections:**
- Connect source/drain to metal with CONT
- Connect different metal layers with VIA
- Add labels with `l` key for net names (VDD, VSS, A, B, OUT)

---

### Step 4: Add Labels and Pins

**Add Wire Labels:**
- Press `l`
- Type name (VDD, VSS, A, B, OUT)
- Place on corresponding metal

**Create I/O Pins:**
- Press `p`
- Set pin properties (input/output)
- Place on layout

**Save Regularly:**
- Click "Check and Save" icon

---

### Step 5: Design Rule Check (DRC)

**Setup DRC:**
1. Calibre → Run nmDRC
2. If first time, click "Cancel" at Load Runset File
3. Click "Rules" tab
4. Set DRC Rules File:
   ```
   /opt/ei/DK/tsmc/oa180/mini018BCDG2/216A/Calibre/drc/calibre.drc
   ```
5. Click "Run DRC" tab
6. Set DRC Run Directory (create your own):
   ```
   /home/xinlingyue/tsmcBCD/DRC
   ```
   (use your netid)

**Run DRC:**
1. Click "Run DRC" button
2. Wait for completion
3. Review results in:
   - Calibre - DRC RVE window (violations viewer)
   - DRC Summary Report window

**Fix DRC Errors:**
- Click on errors in RVE window
- Error location highlights in layout
- Read error description at bottom
- Modify layout to fix
- Re-run DRC

**Acceptable Errors:**
You can ignore these R-category errors:
- "LV device must be isolated by NBL combine with HVNW"
- "Min poly area coverage < 14%"
- "Minimum density across full chip >= 0.14"

**Goal:** Clean DRC or only R-category errors remaining

**Deliverables:**
- Screenshot of completed layout with ruler showing transistor dimensions
- Screenshot of metal/poly wire routing
- Screenshot of Calibre setup process
- Screenshot of final DRC clean window showing:
  - 0 errors (or only R-category)
  - Summary report
- Brief description of layout strategy

---

## Assignment 1 Submission Requirements

**Report Format:** PDF

**Content Checklist:**
- [ ] Cover page with group members and student IDs
- [ ] NAND schematic with labels
- [ ] NAND symbol
- [ ] Testbench 1 (function verification) with input/output waveforms
- [ ] Testbench 2 (performance) with signal specifications
- [ ] Performance measurement results (table format)
- [ ] Analysis of timing and power results
- [ ] Layout screenshots:
  - [ ] Full layout view
  - [ ] Transistor dimensions (with ruler)
  - [ ] Metal/poly connections
- [ ] Calibre setup screenshots
- [ ] DRC clean results
- [ ] Conclusion

**Example Reports Available:**
- Report_Example_Schematic.pdf
- Report_Example_Layout.pdf

**Submission:**
- Brightspace → Assignments → Assignment 1
- One submission per group
- Deadline: **December 19th, 2025**

---

# Assignment 2: Full Adder Design (Schematic Only)

**Deadline:** January 12th, 2025

## Overview

**Objective:** Design a 1-bit Full Adder from transistor level

**Full Adder Function:**
```
Inputs:  A, B, Cin (carry in)
Outputs: S (sum), Cout (carry out)

Truth Table:
A | B | Cin | S | Cout
0 | 0 | 0   | 0 | 0
0 | 0 | 1   | 1 | 0
0 | 1 | 0   | 1 | 0
0 | 1 | 1   | 0 | 1
1 | 0 | 0   | 1 | 0
1 | 0 | 1   | 0 | 1
1 | 1 | 0   | 0 | 1
1 | 1 | 1   | 1 | 1

Logic:
S = A ⊕ B ⊕ Cin
Cout = AB + BCin + ACin
```

---

## Design Approach

**Bottom-Up Design Strategy:**

### Level 1: Basic Gates (Transistor Level)
Design and create symbols for:
1. **NAND Gate** (already from Assignment 1)
2. **NOR Gate**
3. **Inverter (NOT)**
4. **AND Gate** (NAND + NOT)
5. **OR Gate** (NOR + NOT)
6. **XOR Gate** (can build from NAND/NOR/NOT)

**Requirements:**
- Design each gate at transistor level
- Use pmos2v and nmos2v models
- Follow proper sizing (you can use same as Assignment 1 or optimize)
- Generate symbol for each gate
- Test each gate individually (optional but recommended)

### Level 2: Intermediate Blocks
Build larger blocks using your gates:
1. **Half Adder:**
   ```
   Inputs: A, B
   Outputs: S = A ⊕ B, C = AB
   ```
2. **2-Input Multiplexer** (if using mux-based design)

### Level 3: Full Adder
Combine blocks to create full adder

**Example Topology:**
```
         ┌─────────┐
    A ───┤         │
         │  Half   │─── S1
    B ───┤  Adder  │
         │   #1    │─── C1
         └─────────┘
              │
              │ S1
              │
         ┌────▼────┐
    Cin ─┤         │
         │  Half   │─── S (final sum)
         │  Adder  │
         │   #2    │─── C2
         └─────────┘
              │
              │ C2
         ┌────▼────┐
    C1 ──┤   OR    │─── Cout (final carry)
    C2 ──┤         │
         └─────────┘
```

**Alternative Topologies:**
You can use any valid full adder implementation:
- Transmission gate based
- CMOS logic based
- Multiplexer based
- Your own optimized design

---

## Step 1: Verify Full Adder Function

**Objective:** Prove the circuit correctly implements full adder logic

**Testbench Setup:**
1. Create testbench cellview
2. Add your full adder symbol
3. Add three input voltage sources (A, B, Cin)
4. Add VDD and VSS
5. Add probes on S and Cout outputs

**Input Test Pattern:**
Design input pulses to cover all 8 combinations of truth table

**Example Pattern:**
```
Time(ms):  0    1    2    3    4    5    6    7    8
A:         0    1    0    1    0    1    0    1    (toggles fastest)
B:         0    0    1    1    0    0    1    1    (toggles medium)
Cin:       0    0    0    0    1    1    1    1    (toggles slowest)
```

**Simulation:**
- Transient analysis
- Stop time: 8ms (to see all combinations)
- Plot A, B, Cin, S, Cout

**Verification:**
- Manually check each time interval against truth table
- Annotate waveforms showing expected vs actual

**Deliverables:**
- Schematic of each basic gate (transistor level)
- Symbol for each gate
- Full adder schematic (showing hierarchy)
- Full adder symbol
- Testbench schematic
- Waveform screenshot with all 8 input combinations
- Verification table comparing expected vs simulated outputs

---

## Step 2: Analyze Performance Parameters

**Objective:** Measure timing and power characteristics

**Input Signal Specifications:**
```
Input A:
  - Pattern: 101010... (alternating)
  - Period: 2ms
  - Pulse Width: 1ms
  - Rise/Fall Edge: 100ps
  - V1: 0V, V2: 1.8V

Input B:
  - Pattern: 111111... (constant high)
  - DC: 1.8V

Input Cin:
  - Pattern: 101010... (alternating, same as A)
  - Period: 2ms
  - Pulse Width: 1ms
  - Rise/Fall Edge: 100ps
  - V1: 0V, V2: 1.8V
```

**Timeline:**
```
Time(ms):  0    1    2    3    4    5
A:         0    1    0    1    0    1
B:         1    1    1    1    1    1
Cin:       0    1    0    1    0    1
```

**Create Performance Testbench:**
- New testbench cellview
- Configure voltage sources with exact specs above

**Parameters to Measure:**

### 1. Propagation Delay

Measure for both outputs:

**Sum Output (S):**
- t_PHL (S): Input 50% → S 50% (falling)
- t_PLH (S): Input 50% → S 50% (rising)
- Average: (t_PHL + t_PLH) / 2

**Carry Output (Cout):**
- t_PHL (Cout): Input 50% → Cout 50% (falling)
- t_PLH (Cout): Input 50% → Cout 50% (rising)
- Average: (t_PHL + t_PLH) / 2

**Critical Path:**
- Identify longest delay path (A/B/Cin → S or Cout)
- This determines maximum operating frequency

### 2. Rise Time & Fall Time

Measure for both outputs:
- **S Rise Time:** 10% to 90% of S rising edge
- **S Fall Time:** 90% to 10% of S falling edge
- **Cout Rise Time:** 10% to 90% of Cout rising edge
- **Cout Fall Time:** 90% to 10% of Cout falling edge

### 3. Quiescent Power
- Measure DC current from VDD during stable state
- P_quiescent = VDD × I_DC (no switching)

### 4. Dynamic Power
- Measure average current during switching activity
- P_dynamic = VDD × I_avg (during transitions)
- P_dynamic = P_total - P_quiescent

**Deliverables:**
- Screenshot of performance testbench
- Waveforms showing measurements
- Measurement table:
  | Parameter | Value | Unit |
  |-----------|-------|------|
  | t_PHL (S) | | ps |
  | t_PLH (S) | | ps |
  | t_prop (S) | | ps |
  | t_PHL (Cout) | | ps |
  | t_PLH (Cout) | | ps |
  | t_prop (Cout) | | ps |
  | Rise Time (S) | | ps |
  | Fall Time (S) | | ps |
  | Rise Time (Cout) | | ps |
  | Fall Time (Cout) | | ps |
  | Critical Path Delay | | ps |
  | P_quiescent | | μW |
  | P_dynamic | | μW |
  | P_total | | μW |
- Analysis discussing:
  - Which path is critical (slowest)
  - Comparison with Assignment 1 NAND gate
  - Power breakdown
  - Potential optimizations

---

## Assignment 2 Submission Requirements

**Report Format:** PDF

**Content Checklist:**
- [ ] Cover page with group members and student IDs
- [ ] Design approach explanation
- [ ] Schematics of all basic gates (transistor level):
  - [ ] NAND, NOR, NOT, AND, OR, XOR
  - [ ] With transistor sizing specified
- [ ] Symbol for each gate
- [ ] Half adder schematic (if used)
- [ ] Full adder schematic showing hierarchy
- [ ] Full adder symbol
- [ ] Testbench 1 (function verification):
  - [ ] Schematic
  - [ ] Input/output waveforms for all 8 combinations
  - [ ] Verification table
- [ ] Testbench 2 (performance):
  - [ ] Schematic with signal specs
  - [ ] Waveforms with measurement markers
- [ ] Performance results table
- [ ] Analysis and discussion:
  - [ ] Critical path identification
  - [ ] Comparison with NAND gate
  - [ ] Power analysis
  - [ ] Potential improvements
- [ ] Conclusion

**Submission:**
- Brightspace → Assignments → Assignment 2
- One submission per group
- Deadline: **January 12th, 2025**

---

## Additional Resources

**References:**
- EE4610_Instruction_Manual_2025.pdf
- EE4610_Assignment_Guide_2025.pdf
- EE4610_Assignment_Slides_2025.pdf
- Report_Example_Schematic.pdf
- Report_Example_Layout.pdf

**Propagation Delay Reference:**
https://en.wikipedia.org/wiki/Signal_propagation_delay

**Rise/Fall Time Reference:**
https://www.nutsvolts.com/magazine/article/understanding_digital_logic_ics_part_1

**Q&A Forums:**
- Course Materials: Brightspace → Collaboration → Discussions → Course Materials Q&A Forum
- Assignments: Brightspace → Collaboration → Discussions → Cadence Assignments Q&A Forum

**TA Sessions (On-site):**
- Session 1: December 10th, 11:30-12:30
- Session 2: January 7th, 11:30-12:30

**Teaching Assistants:**
- Yunzhe Yang: y.yang-16@tudelft.nl (Assignments)
- Haoyu Cai: H.Cai-2@tudelft.nl (Assignments)
- Shunmin Jiang: s.jiang-12@student.tudelft.nl (Course Q&A)

---

## Tips for Success

### General
- Start early - layout and DRC take time
- Save frequently (Ctrl+S)
- Test each component before integrating
- Use hierarchy - build small blocks first
- Keep organized naming conventions

### Schematic Design
- Label all nets clearly
- Use proper symbols for readability
- Check connections before simulation
- Verify transistor sizes match specifications

### Layout Design
- Follow DRC rules from start
- Use ruler (k) constantly to check dimensions
- Keep layout compact but DRC-clean
- Run DRC frequently (after major changes)
- Document your layout strategy

### Simulation
- Always check simulation convergence
- Use appropriate time steps
- Zoom in on transitions for accurate measurements
- Use calculator functions for precise values
- Save simulation states for different tests

### Debugging
- If simulation doesn't converge:
  - Check for floating nodes
  - Verify VDD/VSS connections
  - Check transistor models
- If DRC errors are confusing:
  - Read error description carefully
  - Check layer selections
  - Verify minimum widths/spacings
  - Ask on Brightspace forum

### Report Writing
- Include clear, high-resolution screenshots
- Label all figures
- Explain methodology
- Show calculations
- Discuss results - don't just present data
- Compare with expected behavior
- Be honest about limitations/errors

---

## Good Luck!

Remember: These assignments are designed to give you hands-on experience with IC design flow. Focus on understanding the process, not just completing tasks. The skills you learn here are fundamental to VLSI design.

**Questions?** Post on Brightspace or attend TA sessions!
