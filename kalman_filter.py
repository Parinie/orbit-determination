import numpy as np
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta

# Constants
MU_EARTH = 398600.4418  # km^3/s^2
NOISE_STD = 0.3         # measurement noise, km
DT = 60                # timestep in seconds (1 minutes)

# @ means matrix multiplication in python

def predict(x, P, F, Q):
    """
    Kalman predict step.
    x = state vectore [x, y, z, vx, vy, vz]
    P = state covariance matrix (our uncertainty)
    F = state transition matrix (physics model)
    Q = process noise covariance (how much we distrust the physics)
    """

    x_pred = F @ x           # predict state
    P_pred = F @ P @ F.T + Q # predict covariance
    return x_pred, P_pred

def update(x_pred, P_pred, z, H, R):
    """
    Kalman update step.
    z = measurement vector [x, y, z]
    H = measurement matrix (maps state to measurement space)
    R = measurement noise covariance (how much we distrust the sensor)
    """ 

    S = H @ P_pred @ H.T + R           # innovation covariance
    K = P_pred @ H.T @ np.linalg.inv(S) # Kalman gain
    innovation = z - H @ x_pred         # difference between measurement and prediction
    x_updated = x_pred + K @ innovation
    P_updated = (np.eye(6) - K @ H) @ P_pred
    return x_updated, P_updated, K

print("Kalman filter functions defined successfully")

# State transition matrix — linear motion model
# State vector: [x, y, z, vx, vy, vz]
F = np.array([
    [1, 0, 0, DT, 0,  0 ],
    [0, 1, 0, 0,  DT, 0 ],
    [0, 0, 1, 0,  0,  DT],
    [0, 0, 0, 1,  0,  0 ],
    [0, 0, 0, 0,  1,  0 ],
    [0, 0, 0, 0,  0,  1 ]
])

# Measurement matrix — we only measure position, not velocity
H = np.array([
    [1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0]
])

# Measurement noise covariance matrix
R = np.eye(3) * NOISE_STD**2

# Process noise covariance - how much we distrust the linear motion model
Q = np.eye(6) * 1e-3

print("F matrix:")
print(F)
print("\nH matrix:")
print(H)

# Read TLE and propagate true orbit + simulate measurements
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

true_positions = []
noisy_measurements = []
filtered_positions = []

# Initialize filter state from first SGP4 reading
jd, fr = jday(start_time.year, start_time.month, start_time.day,
                start_time.hour, start_time.minute, start_time.second)
_, pos0, vel0 = sat.sgp4(jd, fr)

x = np.array([pos0[0], pos0[1], pos0[2],
               vel0[0], vel0[1], vel0[2]]) # initial state

P = np.eye(6) * 100 # initial uncertainty - we're not very confident yet

# Run filter
for minutes in range(0, 12 * 60, 1):
    t = start_time + timedelta(minutes=minutes)
    jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second)
    _, position, velocity = sat.sgp4(jd, fr)

    true_pos = np.array(position)
    noise = np.random.normal(0, NOISE_STD, size=3)
    z = true_pos + noise

    # Use SGP4 as the physics prediction instead of linear F
    x_pred = np.array([position[0], position[1], position[2],
                       velocity[0], velocity[1], velocity[2]])
    P_pred = P + Q

    # Just run the update step with SGP4 prediction
    x, P, K = update(x_pred, P_pred, z, H, R)

    true_positions.append(true_pos)
    noisy_measurements.append(z)
    filtered_positions.append(x[:3])

true_positions = np.array(true_positions)
noisy_measurements = np.array(noisy_measurements)
filtered_positions = np.array(filtered_positions)

# Compute errors
noisy_errors = np.linalg.norm(noisy_measurements - true_positions, axis=1)
filtered_errors = np.linalg.norm(filtered_positions - true_positions, axis=1)

print(f"\nResults for {name}:")
print(f"  Average measurement error: {noisy_errors.mean():.4f} km")
print(f"  Average filter error:      {filtered_errors.mean():.4f} km")
print(f"  Improvement: {((noisy_errors.mean() - filtered_errors.mean()) / noisy_errors.mean() * 100):.1f}%")

