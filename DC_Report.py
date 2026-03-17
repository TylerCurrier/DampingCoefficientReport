"""
#psuedo
import libraries
load csv from system files
parse velocity and force into arrays
sort forces by velocity
take differentials
plot onto single graph
    range - o inches per second, max velocity from run
grab coeffs at significant points and add a point on the graph to denote them
    significant points - 1,2,4,6,8,10
    report sig points - 1(low speed), 5(medium Speed), 10(high Speed) *these will be called out below the graph
Create Title for the report = DC_Report_["data filename"]
Create Filename for report = DC_Report_["data filename"]_date+time
ask for = damper used, test type, tester
Generate Subtitles below title = date + time, damper used, test type, tester
create .jpg report and save to files
"""

#DC_Report
#Tyler Currier
#March 16, 2026
#49ers Racing IC - Vehicle Dynamics

#import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
from datetime import datetime
import os

#open filepicker
Tk().withdraw()
file_path = filedialog.askopenfilename(title="Select Damper Dyno CSV")

if not file_path:
    print("No file selected.")
    exit()

data_filename = os.path.splitext(os.path.basename(file_path))[0]

#-------------------------------------------------
# Detect header row
#-------------------------------------------------
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

#-------------------------------------------------
# load csv
#-------------------------------------------------
data = pd.read_csv(file_path, skiprows=header_row)

#-------------------------------------------------
# detect velocity and force columns
#-------------------------------------------------
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

#-------------------------------------------------
# remove NaN values
#-------------------------------------------------
valid = ~(np.isnan(velocity) | np.isnan(force))
velocity = velocity[valid]
force = force[valid]

#-------------------------------------------------
# Split compression and rebound
#-------------------------------------------------
rebound_mask = velocity > 0
compression_mask = velocity < 0

vel_rebound = velocity[rebound_mask]
force_rebound = force[rebound_mask]

vel_compression = np.abs(velocity[compression_mask])
force_compression = np.abs(force[compression_mask])

#-------------------------------------------------
# Function to bin dyno data
#-------------------------------------------------
def bin_data(vel, force, bin_width=0.05):

    bins = np.arange(0, np.max(vel), bin_width)
    bin_index = np.digitize(vel, bins)

    binned_vel = []
    binned_force = []

    for i in range(1, len(bins)):
        mask = bin_index == i

        if np.sum(mask) > 5:
            binned_vel.append(np.mean(vel[mask]))
            binned_force.append(np.mean(force[mask]))

    return np.array(binned_vel), np.array(binned_force)

vel_rebound, force_rebound = bin_data(vel_rebound, force_rebound)
vel_compression, force_compression = bin_data(vel_compression, force_compression)

#-------------------------------------------------
# Smooth forces slightly
#-------------------------------------------------
window = 5

force_rebound = np.convolve(force_rebound, np.ones(window)/window, mode='same')
force_compression = np.convolve(force_compression, np.ones(window)/window, mode='same')

#-------------------------------------------------
# Compute damping coefficient  c = F/v
#-------------------------------------------------
min_velocity = 0.05

c_rebound = np.abs(force_rebound / np.maximum(vel_rebound, min_velocity))
c_compression = np.abs(force_compression / np.maximum(vel_compression, min_velocity))

#-------------------------------------------------
# Significant velocities
#-------------------------------------------------
sig_velocities = [1,2,4,6,8,10]

max_v = max(np.max(vel_rebound), np.max(vel_compression))
sig_velocities = [v for v in sig_velocities if v <= max_v]

sig_rebound = np.interp(sig_velocities, vel_rebound, c_rebound)
sig_compression = np.interp(sig_velocities, vel_compression, c_compression)

#-------------------------------------------------
# metadata
#-------------------------------------------------
damper_used = input("Enter damper used: ")
test_type = input("Enter test type: ")
tester = input("Enter tester name: ")

now = datetime.now()
date_time_string = now.strftime("%Y-%m-%d %H:%M:%S")
timestamp = now.strftime("%Y%m%d_%H%M%S")

#-------------------------------------------------
# Plot
#-------------------------------------------------
plt.figure(figsize=(10,7))

plt.plot(vel_rebound, c_rebound, label="Rebound")
plt.plot(vel_compression, c_compression, label="Compression")

plt.scatter(sig_velocities, sig_rebound)
plt.scatter(sig_velocities, sig_compression)

plt.xlabel("Velocity (in/s)")
plt.ylabel("Damping Coefficient (lb*s/in)")
plt.grid(True)
plt.legend()

plt.xlim(0, max_v)

plt.subplots_adjust(bottom=0.30)

#-------------------------------------------------
# Title
#-------------------------------------------------
title = f"DC_Report_[{data_filename}]"
plt.title(title, fontsize=14)

subtitle = f"{date_time_string}\nDamper: {damper_used} | Test: {test_type} | Tester: {tester}"
plt.figtext(0.5, 0.93, subtitle, ha="center", fontsize=10)

#-------------------------------------------------
# Report text
#-------------------------------------------------
report_lines = ["Significant Damping Coefficients\n"]

for v,r,c in zip(sig_velocities, sig_rebound, sig_compression):
    report_lines.append(f"{v} in/s  | Rebound: {r:.2f}  Compression: {c:.2f}")

report_text = "\n".join(report_lines)

plt.figtext(0.15, 0.02, report_text, ha="left", fontsize=11)

#-------------------------------------------------
# Save Report
#-------------------------------------------------
report_filename = f"DC_Report_{data_filename}_{timestamp}.jpg"
save_path = os.path.join(os.path.dirname(file_path), report_filename)

plt.savefig(save_path, dpi=300, bbox_inches='tight')
plt.close()

print("Report generated:")
print(save_path)