# Autonomous Orbit Determination

Real-time satellite state estimation using TLE data and the SGP4 propagation model, 
built toward a full Extended Kalman Filter implementation for orbit determination.

## What this project does

- Parses real GNSS satellite TLE data from Celestrak
- Propagates satellite positions and velocities in the ECI frame using SGP4
- Computes real-time orbital state vectors (position, velocity, distance from Earth)
- **In progress:** Extended Kalman Filter for state estimation from noisy measurements

## Why it matters

Orbit determination is a core GNC problem — every spacecraft navigation system needs 
to estimate its true state from imperfect measurements. The Kalman filter implemented 
here is the same foundational algorithm used in GPS receivers, spacecraft GNC, and 
autonomous vehicle navigation.

## Stack

- Python, NumPy
- sgp4 — industry-standard orbital propagation
- Plotly — 3D orbit visualization (coming soon)

## Background

Built as part of a summer portfolio project targeting GNC and autonomy roles in the 
eVTOL and space industry. Aerospace Engineering senior at CU Boulder.
