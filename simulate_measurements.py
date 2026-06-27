import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import plotly.graph_objects as go

#Measurement noise standard deviation (km) - realistic ground radar
NOISE_STD = 0.3 # 300 meters

# Read TLE file
with open("gnss.txt", "r") as f:
    raw = f.read()

lines = [line.strip() for line in raw.splitlines() if line.strip()]
satellites = []

for i in range(0, len(lines) - 2, 3):
    name = lines[i]
    line1 = lines[i+1]
    line2 = lines[i+2]
    sat = Satrec.twoline2rv(line1, line2)
    satellites.append((name, sat))

# Pick the first satellite
name, sat = satellites[0]

# Propage true orbit and simulate noisy measurements
start_time = datetime.utcnow()
true_positions = []
noisy_measurements = []

for minutes in range(0, 12 * 60, 5):
    t = start_time + timedelta(minutes=minutes)
    jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second)
    error, position, velocity = sat.sgp4(jd, fr)

    true_pos = np.array(position)

    # Add Gaussian noise to simulate radar measurement
    noise = np.random.normal(0, NOISE_STD, size=3)
    noisy_pos = true_pos + noise

    true_positions.append(true_pos)
    noisy_measurements.append(noisy_pos)

true_positions = np.array(true_positions)
noisy_measurements = np.array(noisy_measurements)

# Print first few to sanity check
print(f"Simulated measurements for {name}\n")
print(f"{'Time (min)':<12} {'True X (km)':<16} {'Measured X (km)':<18} {'Error (km)'}")
print("-" * 65)
for i in range(5):
    t = i * 5
    true_x = true_positions[i, 0]
    meas_x = noisy_measurements[i, 0]
    error = abs(true_x - meas_x)
    print(f"{t:<12} {true_x:<16.3f} {meas_x:<18.3f} {error:.4f}")

# Plot true orbit and noisy measurements
fig = go.Figure()

# True Orbit
fig.add_trace(go.Scatter3d(
    x=true_positions[:,0],
    y=true_positions[:,1],
    z=true_positions[:,2],
    mode='lines',
    line=dict(color='royalblue', width=4),
    name='True Orbit'
))

# Noisy Measurements
fig.add_trace(go.Scatter3d(
    x=noisy_measurements[:,0],
    y=noisy_measurements[:,1],
    z=noisy_measurements[:,2],
    mode='markers',
    marker=dict(color='red', size=2),
    name="Radar measurements"
))

fig.update_layout(
    title=f"True orbit vs noisy radar measurements - {name}",
    scene=dict(
        xaxis_title='X (km)',
        yaxis_title='Y (km)',
        zaxis_title='Z (km)',
        aspectmode='data'   
    ),
    width=900,
    height=700
)

fig.show()