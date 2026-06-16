import numpy as np
import plotly.graph_objects as go
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta

# Read TLE file from disk
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

# Propagate over one full orbital period (~12 hours for GPS), one point per minute
start_time = datetime.utcnow()
positions = []

for minutes in range(0, 12 * 60, 5):
    t = start_time + timedelta(minutes=minutes)
    jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second)
    error, position, velocity = sat.sgp4(jd, fr)
    positions.append(position)

positions = np.array(positions)

# Plot the orbit path
fig = go.Figure()

fig.add_trace(go.Scatter3d(
    x=positions[:,0], y=positions[:,1], z=positions[:,2],
    mode='lines',
    line=dict(color='royalblue', width=4),
    name=name
))

# Add earth as a sphere for reference
earth_radius = 6371 #km
u = np.linspace(0, 2 * np.pi, 50)
v = np.linspace(0, np.pi, 50)
x_earth = earth_radius * np.outer(np.cos(u), np.sin(v))
y_earth = earth_radius * np.outer(np.sin(u), np.sin(v))
z_earth = earth_radius * np.outer(np.ones(np.size(u)), np.cos(v))

fig.add_trace(go.Surface(
    x=x_earth, y=y_earth, z=z_earth,
    colorscale=[[0, 'lightblue'], [1, 'lightblue']],
    showscale=False,
    opacity=0.7,
    name='Earth'
))

fig.update_layout(
    title=f"Orbit of {name}",
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