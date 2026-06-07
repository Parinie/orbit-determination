from sgp4.api import Satrec
from sgp4.api import jday
from datetime import datetime

# Read TLE file from disk
with open("gnss.txt", "r") as f:
    raw = f.read()

# Parse into groups of 3 lines
lines = [line.strip() for line in raw.splitlines() if line.strip()]
satellites = []

for i in range(0, len(lines) - 2, 3):
    name  = lines[i]
    line1 = lines[i + 1]
    line2 = lines[i + 2]
    sat = Satrec.twoline2rv(line1, line2)
    satellites.append((name, sat))

# Print first 5 satellites to verify
print(f"Loaded {len(satellites)} satellites\n")
print("First 5 satellites:")
for name, sat in satellites[:5]:
    print(f"  {name}")
    print(f"    Inclination: {sat.inclo:.4f} rad")
    print(f"    Eccentricity: {sat.ecco:.6f}")
    print(f"    Mean motion: {sat.no:.6f} rad/min\n")

# Pick the first satellite
name, sat = satellites[0]

# Get current time
now = datetime.utcnow()
jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)

# Propagate - gives position and velocity in the ECI frame (km and km/s)
error, position, velocity = sat.sgp4(jd, fr)

print(f"\n{name} right now:")
print(f" Position (ECI): x={position[0]:.1f} km, y={position[1]:.1f} km, z={position[2]:.1f} km")
print(f" Velocity (ECI): vx={velocity[0]:.3f} km/s, vy={velocity[1]:.3f} km/s, vz={velocity[2]:.3f} km/s")

distance = (position[0]**2 + position[1]**2 + position[2]**2) ** 0.5
print(f" Distance from Earth center: {distance:.1f} km")