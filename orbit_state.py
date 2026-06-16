import numpy as np

#Earth's gravitational parameter (km^3/s^2)
mu_earth = 398600.4418

def orbital_state(position, velocity):
    r_vec = np.array(position)
    v_vec = np.array(velocity)

    # finding magnitude of pos and vel vec
    r = np.linalg.norm(r_vec) #linalg means linear algebra
    v = np.linalg.norm(v_vec)

    # specific orbital energy (km^2/s^2)
    energy = (v**2) / 2 - mu_earth / r

    #specific angular momentum vector (km^2/s)
    h_vec = np.cross(r_vec, v_vec)
    h = np.linalg.norm(h_vec)

    # semi-major axis from energy (km)
    a = -mu_earth / (2 * energy)

    # orbital period (sec)
    period_sec = 2 * np.pi * np.sqrt(a**3 / mu_earth)
    period_hr = period_sec / 3600

    return {
        "energy": energy,
        "angular_momentum": h,
        "semi_major_axis": a,
        "period_hours": period_hr
    }

