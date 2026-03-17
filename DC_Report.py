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


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
from datetime import datetime
import os

# ---------------------------
# Select CSV file
# ---------------------------
Tk().withdraw()
file_path = filedialog.askopenfilename(title="Select Damper Dyno CSV")

if not file_path:
    print("No file selected.")
    exit()

data_filename = os.path.splitext(os.path.basename(file_path))[0]

# ---------------------------
# Load CSV
# ---------------------------
data = pd.read_csv(file_path)

# Change column names here if needed
velocity = data.iloc[:,0].to_numpy()
force = data.iloc[:,1].to_numpy()

# ---------------------------
# Sort data by velocity
# ---------------------------
sort_index = np.argsort(velocity)
velocity = velocity[sort_index]
force = force[sort_index]

# ---------------------------
# Compute derivative (dF/dv)
# ---------------------------
damping_coeff = np.gradient(force, velocity)

# ---------------------------
# Significant velocities
# ---------------------------
sig_velocities = [1,2,4,6,8,10]

# interpolate coeffs
sig_coeffs = np.interp(sig_velocities, velocity, damping_coeff)

# report velocities
report_velocities = [1,5,10]
report_coeffs = np.interp(report_velocities, velocity, damping_coeff)

# ---------------------------
# Collect metadata
# ---------------------------
damper_used = input("Enter damper used: ")
test_type = input("Enter test type: ")
tester = input("Enter tester name: ")

now = datetime.now()
date_time_string = now.strftime("%Y-%m-%d %H:%M:%S")
timestamp = now.strftime("%Y%m%d_%H%M%S")

# ---------------------------
# Plot
# ---------------------------
plt.figure(figsize=(10,6))

plt.plot(velocity, damping_coeff, label="Damping Coefficient")

# mark significant points
plt.scatter(sig_velocities, sig_coeffs)
for v,c in zip(sig_velocities, sig_coeffs):
    plt.text(v,c,f"{v} in/s", fontsize=8)

plt.xlabel("Velocity (in/s)")
plt.ylabel("Damping Coefficient (lb*s/in)")
plt.xlim(0, max(velocity))
plt.grid(True)

# ---------------------------
# Title + subtitles
# ---------------------------
title = f"DC_Report_{data_filename}"
plt.title(title)

subtitle = f"{date_time_string}\nDamper: {damper_used} | Test: {test_type} | Tester: {tester}"
plt.figtext(0.5,0.92,subtitle, ha="center")

# ---------------------------
# Report values below graph
# ---------------------------
report_text = (
    f"Low Speed (1 in/s): {report_coeffs[0]:.2f} lb*s/in\n"
    f"Mid Speed (5 in/s): {report_coeffs[1]:.2f} lb*s/in\n"
    f"High Speed (10 in/s): {report_coeffs[2]:.2f} lb*s/in"
)

plt.figtext(0.5,0.02, report_text, ha="center", fontsize=11)

# ---------------------------
# Save report
# ---------------------------
report_filename = f"DC_Report_{data_filename}_{timestamp}.jpg"
save_path = os.path.join(os.path.dirname(file_path), report_filename)

plt.savefig(save_path, dpi=300, bbox_inches='tight')
plt.close()

print("Report generated:")
print(save_path)