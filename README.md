# Autonomous Orbit Determination

Real-time satellite state estimation using TLE data and the SGP4 propagation model,
with a Kalman filter for fusing noisy radar measurements with orbital mechanics.

## What this project does

- Parses real GNSS satellite TLE data from Celestrak
- Propagates satellite positions and velocities in the ECI frame using SGP4
- Simulates realistic ground radar measurements with Gaussian noise (~300m error)
- Kalman filter fuses SGP4 predictions with noisy measurements — 89% improvement over raw sensor data
- 3D interactive orbit visualization comparing true orbit, radar measurements, and filter estimate

## Why it matters

Orbit determination is a core GNC problem — every spacecraft navigation system needs
to estimate its true state from imperfect measurements. The Kalman filter implemented
here is the same foundational algorithm used in GPS receivers, spacecraft GNC, and
autonomous vehicle navigation.

## Stack

- Python, NumPy
- sgp4 — industry-standard orbital propagation
- Plotly — interactive 3D orbit visualization

## Background

Built as part of a summer portfolio project targeting GNC and autonomy roles in the
eVTOL and space industry. Aerospace Engineering senior at CU Boulder.
