#!/usr/bin/env python3
"""Plot peak-to-peak ripple current vs modulation index for single-phase and two-phase PWM"""

import numpy as np
import matplotlib.pyplot as plt

# Parameters
Vdd = 10        # V (comparator output ±10V)
L = 18e-6       # H
T = 1e-6        # s (fPWM = 1MHz)

mi = np.linspace(0, 0.95, 200)

# Single-phase: ΔI = 2*Vdd * D*(1-D) * T / L, where D = (1+mi)/2
# Simplifies to: ΔI = 5*(1 - mi²) / 18
dI_single = 2 * Vdd * ((1 + mi)/2) * ((1 - mi)/2) * T / L  # in Amps
dI_single_mA = dI_single * 1000

# Two-phase combined (D >= 0.5): ΔI = 10*mi*(1-mi) / 18
dI_two = 2 * (Vdd - Vdd*mi) / L * (((1+mi)/2) - 0.5) * T  # in Amps
dI_two_mA = dI_two * 1000

# Discrete points for table verification
mi_pts = np.arange(0, 1.0, 0.1)
dI_single_pts = 2 * Vdd * ((1+mi_pts)/2) * ((1-mi_pts)/2) * T / L * 1000
dI_two_pts = 2 * (Vdd - Vdd*mi_pts) / L * (((1+mi_pts)/2) - 0.5) * T * 1000

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(mi, dI_single_mA, 'b-', linewidth=2.5, label='Single-phase')
ax.plot(mi, dI_two_mA, 'r-', linewidth=2.5, label='Two-phase (interleaved)')

# Mark discrete points
ax.plot(mi_pts, dI_single_pts, 'bo', markersize=7)
ax.plot(mi_pts, dI_two_pts, 'rs', markersize=7)

ax.set_xlabel('Modulation Index (mi)', fontsize=14)
ax.set_ylabel('Peak-to-Peak Ripple Current (mA)', fontsize=14)
ax.set_title('Inductor Ripple Current: Single-Phase vs Two-Phase PWM\n'
             r'($V_{dd}$ = ±10V, L = 18µH, $f_{PWM}$ = 1MHz)', fontsize=15)
ax.legend(fontsize=13, loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 0.95)
ax.set_ylim(0, 300)
ax.tick_params(labelsize=12)

# Annotate key points
ax.annotate('Max single-phase\n278 mA', xy=(0, 278), xytext=(0.12, 260),
            fontsize=10, arrowprops=dict(arrowstyle='->', color='blue'), color='blue')
ax.annotate('Max two-phase\n139 mA', xy=(0.5, 139), xytext=(0.62, 160),
            fontsize=10, arrowprops=dict(arrowstyle='->', color='red'), color='red')
ax.annotate('Perfect cancellation\nat mi = 0', xy=(0, 0), xytext=(0.1, 30),
            fontsize=10, arrowprops=dict(arrowstyle='->', color='red'), color='red')

plt.tight_layout()
plt.savefig('/home/danieltyukov/workspace/tud/tud-digital-ic-design/ET4382/part3_ripple_vs_mi.png', dpi=150, bbox_inches='tight')
print("Saved: part3_ripple_vs_mi.png")
plt.close()
