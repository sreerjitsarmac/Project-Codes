import numpy as np
import plotly.graph_objects as go

# Constants
moon_radius = 1737.4       # km (Moon's radius)
altitude = 2000            # km (satellite altitude)
satellite_fov = 90         # degrees (field of view for each satellite)
moon_diameter = 2 * moon_radius
inclination = float(input("Enter the inclination angle (in degrees): "))

# Calculate number of satellites (simple coverage-based estimate)
def calculate_satellites(altitude, inclination, moon_diameter, satellite_fov):
    total_surface_area = 4 * np.pi * moon_radius**2
    r_orbit = moon_radius + altitude
    coverage_area = satellite_fov / 360 * np.pi * r_orbit**2
    satellites = int(np.ceil(total_surface_area / coverage_area))
    return satellites

satellites_needed = calculate_satellites(altitude, inclination, moon_diameter, satellite_fov)
print(f"Number of Satellites Needed for Inclination {inclination}°: {satellites_needed}")

# Prepare static traces (they will be repeated in every frame)
def create_static_traces(inclination):
    traces = []
    # Moon surface as a sphere
    u = np.linspace(0, 2*np.pi, 200)
    v = np.linspace(0, np.pi, 100)
    u_mesh, v_mesh = np.meshgrid(u, v)
    x_sphere = moon_radius * np.sin(v_mesh) * np.cos(u_mesh)
    y_sphere = moon_radius * np.sin(v_mesh) * np.sin(u_mesh)
    z_sphere = moon_radius * np.cos(v_mesh)
    # Offset entire system upward by 500 km
    z_sphere += 500  
    moon_surface = go.Surface(
        x=x_sphere, y=y_sphere, z=z_sphere,
        colorscale='Gray', opacity=0.6, showscale=False,
        name="Moon"
    )
    traces.append(moon_surface)
    
    # Equator lines
    equator_x = np.linspace(-moon_radius, moon_radius, 100)
    equator_y = np.sqrt(moon_radius**2 - equator_x**2)
    eq_z = np.zeros_like(equator_x) + 500
    equator_line1 = go.Scatter3d(
        x=equator_x, y=equator_y, z=eq_z,
        mode='lines', line=dict(color='yellow', width=3),
        opacity=0.3, name="Equator"
    )
    equator_line2 = go.Scatter3d(
        x=equator_x, y=-equator_y, z=eq_z,
        mode='lines', line=dict(color='yellow', width=3),
        opacity=0.3, showlegend=False
    )
    traces.append(equator_line1)
    traces.append(equator_line2)
    
    # Orbital path for given inclination
    r_orbit = moon_radius + altitude
    theta = np.deg2rad(inclination)
    phi_path = np.linspace(0, 2*np.pi, 200)
    x_path = r_orbit * np.cos(phi_path)
    y_path = r_orbit * np.sin(phi_path) * np.cos(theta)
    z_path = r_orbit * np.sin(phi_path) * np.sin(theta) + 500
    orbit_path = go.Scatter3d(
        x=x_path, y=y_path, z=z_path,
        mode='lines', name=f"Inclination {inclination}° Orbit",
        line=dict(color='red', width=3)
    )
    traces.append(orbit_path)
    
    return traces

static_traces = create_static_traces(inclination)

# Initial satellite positions (for frame 0)
def satellite_positions(inclination, satellites_needed, phase_offset=0):
    r_orbit = moon_radius + altitude
    theta = np.deg2rad(inclination)
    phi_positions = np.linspace(0, 2*np.pi, satellites_needed, endpoint=False)
    positions = []
    for phi in phi_positions:
        phi_new = phi + phase_offset
        x_sat = r_orbit * np.cos(phi_new)
        y_sat = r_orbit * np.sin(phi_new) * np.cos(theta)
        z_sat = r_orbit * np.sin(phi_new) * np.sin(theta) + 500
        positions.append((x_sat, y_sat, z_sat))
    return positions

initial_sat_positions = satellite_positions(inclination, satellites_needed, phase_offset=0)
satellite_traces = []
for j, pos in enumerate(initial_sat_positions):
    x_sat, y_sat, z_sat = pos
    sat_trace = go.Scatter3d(
        x=[x_sat], y=[y_sat], z=[z_sat],
        mode='markers', marker=dict(size=10, color='blue'),
        name=f"Satellite {j+1}"
    )
    satellite_traces.append(sat_trace)

# Combine static traces and initial satellite traces for initial data
initial_data = static_traces + satellite_traces

# Create frames for animation (update only satellite positions)
num_frames = 100
frames = []
for i in range(num_frames):
    phase_offset = np.deg2rad(i * 360 / num_frames)
    sat_positions = satellite_positions(inclination, satellites_needed, phase_offset)
    frame_sat_traces = []
    for j, pos in enumerate(sat_positions):
        x_sat, y_sat, z_sat = pos
        frame_sat_traces.append(go.Scatter3d(
            x=[x_sat], y=[y_sat], z=[z_sat],
            mode='markers', marker=dict(size=10, color='blue'),
            name=f"Satellite {j+1}",
            showlegend=False
        ))
    # Each frame includes all static traces and the updated satellite traces
    frame_data = static_traces + frame_sat_traces
    frames.append(go.Frame(data=frame_data, name=str(i)))

# Build figure and add frames
fig = go.Figure(data=initial_data, frames=frames)

# Add animation controls
fig.update_layout(
    title=f"3D Lunar Satellite Orbit at {inclination}° Inclination",
    scene=dict(
        xaxis_title="X (km)",
        yaxis_title="Y (km)",
        zaxis_title="Z (km)",
        aspectmode='data'
    ),
    updatemenus=[{
        "type": "buttons",
        "showactive": True,
        "buttons": [
            {
                "label": "Play",
                "method": "animate",
                "args": [None, {"frame": {"duration": 100, "redraw": True}, "mode": "immediate", "fromcurrent": True}]
            },
            {
                "label": "Pause",
                "method": "animate",
                "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}]
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "x": 0.1,
        "xanchor": "right",
        "y": 0,
        "yanchor": "top"
    }]
)

fig.show()
