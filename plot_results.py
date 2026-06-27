import numpy as np
import plotly.graph_objects as go
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
from kalman_filter import predict, update

NOISE_STD = 0.3
DT = 60
Q = np.eye(6) * 1e-3
H = np.array([
    [1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0]
])
R = np.eye(3) * NOISE_STD**2

with open("gnss.txt", "r") as f:
    raw = f.read()

lines = [line.strip() for line in raw.splitlines() if line.strip()]
satellites = []
for i in range(0, len(lines) - 2, 3):
    name  = lines[i]
    line1 = lines[i + 1]
    line2 = lines[i + 2]
    sat = Satrec.twoline2rv(line1, line2)
    satellites.append((name, sat))

name, sat = satellites[0]
start_time = datetime.utcnow()

jd, fr = jday(start_time.year, start_time.month, start_time.day,
              start_time.hour, start_time.minute, start_time.second)
_, pos0, vel0 = sat.sgp4(jd, fr)
x = np.array([pos0[0], pos0[1], pos0[2],
               vel0[0], vel0[1], vel0[2]])
P = np.eye(6) * 100

true_positions = []
noisy_measurements = []
filtered_positions = []

for minutes in range(0, 12 * 60, 1):
    t = start_time + timedelta(minutes=minutes)
    jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second)
    _, position, velocity = sat.sgp4(jd, fr)

    true_pos = np.array(position)
    noise = np.random.normal(0, NOISE_STD, size=3)
    z = true_pos + noise

    x_pred = np.array([position[0], position[1], position[2],
                       velocity[0], velocity[1], velocity[2]])
    P_pred = P + Q
    x, P, K = update(x_pred, P_pred, z, H, R)

    true_positions.append(true_pos)
    noisy_measurements.append(z)
    filtered_positions.append(x[:3])

true_positions = np.array(true_positions)
noisy_measurements = np.array(noisy_measurements)
filtered_positions = np.array(filtered_positions)

# 3D plot
fig = go.Figure()

fig.add_trace(go.Scatter3d(
    x=true_positions[:, 0], y=true_positions[:, 1], z=true_positions[:, 2],
    mode='lines',
    line=dict(color='royalblue', width=4),
    name='True orbit'
))

fig.add_trace(go.Scatter3d(
    x=noisy_measurements[:, 0], y=noisy_measurements[:, 1], z=noisy_measurements[:, 2],
    mode='markers',
    marker=dict(color='red', size=1.5),
    name='Radar measurements'
))

fig.add_trace(go.Scatter3d(
    x=filtered_positions[:, 0], y=filtered_positions[:, 1], z=filtered_positions[:, 2],
    mode='lines',
    line=dict(color='green', width=3),
    name='Kalman filter estimate'
))

fig.update_layout(
    title=f"Orbit determination — {name}",
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