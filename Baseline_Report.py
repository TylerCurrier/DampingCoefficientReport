# Baseline_report.py
# Tyler Currier
# March 23, 2026
# 49ers Racing IC - Vehicle Dynamics

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
from datetime import datetime
import os

# File picker
Tk().withdraw()

initial_csv_folder = r"E:\FSAE\24 Car Damper Baselines\csv_out\O6" #filepath to be manually changed per test
file_path = filedialog.askopenfilename(
    title="Select CSV File",
    initialdir=initial_csv_folder,
    filetypes=[("CSV files", "*.csv"), ("all files", "*.*")]
)

if not file_path:
    print("No file selected.")
    exit()

data_filename = os.path.splitext(os.path.basename(file_path))[0]

# Detect header row
with open(file_path, 'r') as f:
    lines = f.readlines()

header_row = None
for i, line in enumerate(lines):
    if "vel" in line.lower() and "force" in line.lower():
        header_row = i
        break

if header_row is None:
    print("Could not detect velocity/force header row.")
    exit()

# Load data
data = pd.read_csv(file_path, skiprows=header_row)

velocity_col = None
force_col = None

for col in data.columns:
    if "vel" in col.lower():
        velocity_col = col
    if "force" in col.lower():
        force_col = col

if velocity_col is None or force_col is None:
    print("Velocity or Force column not found.")
    exit()

velocity = data[velocity_col].to_numpy()
force = data[force_col].to_numpy()

# Remove NaNs
valid = ~(np.isnan(velocity) | np.isnan(force))
velocity = velocity[valid]
force = force[valid]

# Split rebound/compression
rebound_mask = velocity > 0
compression_mask = velocity < 0

vel_rebound = velocity[rebound_mask]
force_rebound = force[rebound_mask]

vel_compression = np.abs(velocity[compression_mask])
force_compression = np.abs(force[compression_mask])

# Sort data
sort_r = np.argsort(vel_rebound)
vel_rebound = vel_rebound[sort_r]
force_rebound = force_rebound[sort_r]

sort_c = np.argsort(vel_compression)
vel_compression = vel_compression[sort_c]
force_compression = force_compression[sort_c]

# Smooth forces
window = 5
force_rebound = np.convolve(force_rebound, np.ones(window)/window, mode='same')
force_compression = np.convolve(force_compression, np.ones(window)/window, mode='same')

# -----------------------------
# Fit Line (1–2.5 in/s ONLY)
# -----------------------------

fit_min_velocity = 1.0
fit_max_velocity = 2.5

mask_fit_r = (vel_rebound >= fit_min_velocity) & (vel_rebound <= fit_max_velocity)
mask_fit_c = (vel_compression >= fit_min_velocity) & (vel_compression <= fit_max_velocity)

# Quadratic fit: F = a*v^2 + b*v + c
coef_r = np.polyfit(vel_rebound[mask_fit_r], force_rebound[mask_fit_r], 2)
coef_c = np.polyfit(vel_compression[mask_fit_c], force_compression[mask_fit_c], 2)

# Evaluate at 3 in/s
v_target = 3.0

force_r_3 = np.polyval(coef_r, v_target)
force_c_3 = np.polyval(coef_c, v_target)

c_rebound_3 = abs(force_r_3 / v_target)
c_compression_3 = abs(force_c_3 / v_target)

# -----------------------------
# Plot (same-axis)
# -----------------------------

v_plot = np.linspace(0, max(np.max(vel_rebound), np.max(vel_compression)), 300)

fit_curve_r = np.polyval(coef_r, v_plot)
fit_curve_c = np.polyval(coef_c, v_plot)

plt.figure(figsize=(10,7))

# Raw data
plt.scatter(vel_rebound, force_rebound, s=5, alpha=0.3, label="Rebound Raw")
plt.scatter(vel_compression, force_compression, s=5, alpha=0.3, label="Compression Raw")

# Fit curves
plt.plot(v_plot, fit_curve_r, linewidth=2, linestyle='-', label="Rebound Fit (1–2.5 in/s)")
plt.plot(v_plot, fit_curve_c, linewidth=2, linestyle='--', label="Compression Fit (1–2.5 in/s)")

# Highlight 3 in/s
plt.scatter([v_target], [force_r_3], s=80)
plt.scatter([v_target], [force_c_3], s=80)

plt.xlabel("Velocity (in/s)")
plt.ylabel("Force (lb)")
plt.grid(True)
plt.legend()

# Move graph up to make room for text
plt.subplots_adjust(bottom=0.35)

# -----------------------------
# Metadata
# -----------------------------

damper_used = input("Enter damper used: ")
test_type = input("Enter test type: ")
tester = input("Enter tester name: ")
#d_lsC = input("Enter low speed compression valve setting: ")
#d_hsC = input("Enter high speed compression valve setting: ")
#d_lsR = input("Enter low speed rebound valve setting: ")
#d_hsR = input("Enter high speed rebound valve setting: ")

now = datetime.now()
date_time_string = now.strftime("%m/%d/%Y %H:%M:%S")
timestamp = now.strftime("%m-%d-%Y_%M%S")

title = f"DC_Report_[{data_filename}]"
plt.title(title)

subtitle = f"{date_time_string}\nDamper: {damper_used} | Test: {test_type} | Tester: {tester}"
plt.figtext(0.5, 0.92, subtitle, ha="center")

#valving = f"Valving {d_lsC},{d_hsC},{d_lsR},{d_hsR}"
#plt.figtext(0.7, 0.12, valving, ha="center")

# Lowered report text
report = (
    f"Damping Coefficients @ 3 in/s\n\n"
    f"Rebound: {c_rebound_3:.2f} lb*s/in\n"
    f"Compression: {c_compression_3:.2f} lb*s/in"
)

plt.figtext(0.1, 0.12, report)

# Save
output_folder = r"E:\FSAE\24 Car Damper Baselines\DC_Reports\O6" #filepath to be manually changed per test
os.makedirs(output_folder, exist_ok=True)

filename = f"DC_Report_[{data_filename}]_{timestamp}.jpg"
save_path = os.path.join(output_folder, filename)

plt.savefig(save_path, dpi=300, bbox_inches='tight')
plt.close()

os.startfile(save_path)

print("Report generated:")
print(save_path)