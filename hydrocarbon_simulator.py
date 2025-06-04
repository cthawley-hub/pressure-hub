import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math


st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .top-right {
        position: absolute;
        top: 10px;
        right: 20px;
        font-size: 0.9em;
        color: gray;
    }
    </style>
    <div class="top-right">© 2025 Created by Charles Hawley</div>
""", unsafe_allow_html=True)
   

# Input fields for triangular distributions
def triangular_input(label, default_min, default_mode, default_max):
    col1, col2, col3 = st.columns(3)
    with col1:
        min_val = st.number_input(f"{label} Min", value=default_min)
    with col2:
        mode_val = st.number_input(f"{label} Mode", value=default_mode)
    with col3:
        max_val = st.number_input(f"{label} Max", value=default_max)
    return (min_val, mode_val, max_val)

# Input fields for triangular distributions
def uniform_input(label, default_min, default_max):
    col1, col2 = st.columns(2)
    with col1:
        min_val = st.number_input(f"{label} Min", value=default_min, format= "%.3f")
    with col2:
        max_val = st.number_input(f"{label} Max", value=default_max, format= "%.3f")
    return (min_val, max_val)



# Create two columns: left for input, right for output
spacer1, left_col, spacer2, right_col, spacer3 = st.columns([0.5,2,0.5,2,0.5])

with left_col:
    st.title("Hydrocarbon Column Height Monte Carlo Simulation")
    st.subheader("Reservoir / fracture pressure at the apex")

    reservoir_pressure_range = triangular_input("Reservoir Pressure (bar)", 760, 770, 780)
    fracture_pressure_range = triangular_input("Fracture Pressure (bar)", 795, 806, 820)

    st.subheader("Fluid parameters")

    water_density_range = uniform_input("Water Density (g/cm³)", 1.035, 1.035)               
    hydrocarbon_density_range = uniform_input("Hydrocarbon Density (g/cm³)", 0.3268, 0.3268)

    st.subheader("Top seal displacement pressure parameters")

    contact_angle_degrees_range = (st.number_input("Contact Angle(°)", value=0))
    interfacial_tension_range = triangular_input("Interfacial Tension (N/m)", 0.03, 0.04, 0.05)                             
    pore_throat_radius_range = triangular_input("Pore Throat Radius (nm)", 10.0, 20.0, 30.0)

    st.subheader("Simulation set up")

    num_simulations = st.number_input("Number of Simulations", min_value=1000, max_value=50000, value=10000)
    # Seed input for reproducibility
    seed_value = st.number_input("Seed", value=42)

# Convert nm to meters
pore_throat_radius_range = tuple(r * 1e-9 for r in pore_throat_radius_range)
water_density_range  = tuple(r * 1000 for r in water_density_range)
hydrocarbon_density_range  = tuple(r * 1000 for r in hydrocarbon_density_range)

def calculate_capillary_limited_height(interfacial_tension, contact_angle_degrees, water_density, hydrocarbon_density, pore_throat_radius):
    contact_angle_radians = math.radians(contact_angle_degrees)
    return (2 * interfacial_tension * math.cos(contact_angle_radians)) / (
        (water_density - hydrocarbon_density) * 9.81 * pore_throat_radius
    )

def calculate_fracture_pressure_limited_height(fracture_pressure, reservoir_pressure, water_density, hydrocarbon_density):
    fracture_pressure_pa = fracture_pressure * 1e5
    reservoir_pressure_pa = reservoir_pressure * 1e5
    max_buoyancy_pressure = fracture_pressure_pa - reservoir_pressure_pa
    return max_buoyancy_pressure / ((water_density - hydrocarbon_density) * 9.81)






# Simulation logic remains unchanged...

if left_col.button("Run Simulation"):

    np.random.seed(seed_value)  # Set the seed here

    max_heights = []
    limiting_factors = {"Capillary pressure": 0, "Fracture pressure": 0}
    interfacial_tensions = []
    contact_angles = []
    water_densities = []
    hydrocarbon_densities = []
    pore_throat_radii = []
    fracture_pressures = []
    reservoir_pressures = []

    for _ in range(num_simulations):
        interfacial_tension = np.random.triangular(*interfacial_tension_range)
        contact_angle_degrees = contact_angle_degrees_range
        water_density = np.random.uniform(*water_density_range)
        hydrocarbon_density = np.random.uniform(*hydrocarbon_density_range)
        pore_throat_radius = np.random.triangular(*pore_throat_radius_range)
        fracture_pressure = np.random.triangular(*fracture_pressure_range)
        reservoir_pressure = np.random.triangular(*reservoir_pressure_range)

        interfacial_tensions.append(interfacial_tension)
        contact_angles.append(contact_angle_degrees)
        water_densities.append(water_density)
        hydrocarbon_densities.append(hydrocarbon_density)
        pore_throat_radii.append(pore_throat_radius)
        fracture_pressures.append(fracture_pressure)
        reservoir_pressures.append(reservoir_pressure)

        capillary_height = calculate_capillary_limited_height(
            interfacial_tension, contact_angle_degrees, water_density, hydrocarbon_density, pore_throat_radius
        )
        fracture_height = calculate_fracture_pressure_limited_height(
            fracture_pressure, reservoir_pressure, water_density, hydrocarbon_density
        )

        max_height = min(capillary_height, fracture_height)
        max_heights.append(max_height)

        if capillary_height < fracture_height:
            limiting_factors["Capillary pressure"] += 1
        else:
            limiting_factors["Fracture pressure"] += 1

    p10 = np.percentile(max_heights, 90)
    mean = np.mean(max_heights)
    p90 = np.percentile(max_heights, 10)

    with right_col:
        st.write("") 
        st.write("") 
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("") 
        tab1, tab2, tab3 = st.tabs(["Hydrocarbon Column Heights", "Limiting Factors", "Input Distributions"])

        with tab1:
            st.write("")
            st.write("")
            st.subheader("Distribution of Maximum Safe Hydrocarbon Column Heights")
            fig, ax = plt.subplots()
            ax.hist(max_heights, bins=50, edgecolor='k', alpha=0.7)
            ax.axvline(p10, color='r', linestyle='dashed', linewidth=1, label=f'P10: {p10:.2f} m')
            ax.axvline(mean, color='g', linestyle='dashed', linewidth=1, label=f'Mean: {mean:.2f} m')
            ax.axvline(p90, color='b', linestyle='dashed', linewidth=1, label=f'P90: {p90:.2f} m')
            ax.set_xlabel('Height (meters)')
            ax.set_ylabel('Frequency')
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

        with tab2:
            st.write("")
            st.write("")
            st.subheader("Percentage of Realizations Controlled by Capillary vs Fracture Pressure")
            fig, ax = plt.subplots()
            labels = list(limiting_factors.keys())
            values = [limiting_factors[label] / num_simulations * 100 for label in labels]
            ax.bar(labels, values, color=['blue', 'orange'])
            ax.set_ylabel('Percentage (%)')
            ax.grid(True, axis='y')
            st.pyplot(fig)

        with tab3:
            st.write("")
            st.write("")
            st.subheader("Input Distributions")
            fig, axs = plt.subplots(4, 2, figsize=(12, 18))
            axs[0, 0].hist(interfacial_tensions, bins=50)
            axs[0, 0].set_title("Interfacial Tension")
            axs[0, 1].hist(contact_angles, bins=50)
            axs[0, 1].set_title("Contact Angle")
            axs[1, 0].hist(water_densities, bins=50)
            axs[1, 0].set_title("Water Density")
            axs[1, 1].hist(hydrocarbon_densities, bins=50)
            axs[1, 1].set_title("Hydrocarbon Density")
            axs[2, 0].hist(pore_throat_radii, bins=50)
            axs[2, 0].set_title("Pore Throat Radius")
            axs[2, 1].hist(fracture_pressures, bins=50)
            axs[2, 1].set_title("Fracture Pressure")
            axs[3, 0].hist(reservoir_pressures, bins=50)
            axs[3, 0].set_title("Reservoir Pressure")
            fig.tight_layout()
            st.pyplot(fig)





