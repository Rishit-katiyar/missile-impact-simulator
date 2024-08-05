import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import csv
import time

class Particle:
    def __init__(self, position, velocity, size, is_fragment=False, particle_type='normal'):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
        self.size = size
        self.is_fragment = is_fragment
        self.particle_type = particle_type

class Surface:
    def __init__(self, size, thickness, material='stealth'):
        self.size = size
        self.thickness = thickness
        self.material = material
        self.damage = np.zeros(size)
        self.deformation = np.zeros(size)

class ParticleImpactSimulation:
    def __init__(self, surface, particles, max_speed, damage_threshold, simulation_time):
        self.surface = surface
        self.particles = particles
        self.max_speed = max_speed
        self.damage_threshold = damage_threshold
        self.simulation_time = simulation_time
        self.current_time = 0
        self.start_time = time.time()

    def check_termination(self):
        total_damage = np.sum(self.surface.damage)
        return total_damage >= self.damage_threshold or self.current_time >= self.simulation_time or time.time() - self.start_time >= 5

    def calculate_deformation(self):
        # Calculate deformation based on the depth of impact and particle size
        for particle in self.particles:
            if particle.position[2] < self.surface.thickness:
                impact_x = int(particle.position[0])
                impact_y = int(particle.position[1])
                deformation = particle.size * 0.5  # Adjust deformation factor as needed
                self.surface.deformation[impact_x, impact_y] += deformation

    def analyze_damage(self):
        # Perform damage analysis, e.g., total damage, distribution, critical points, etc.
        total_damage = np.sum(self.surface.damage)
        max_damage = np.max(self.surface.damage)
        avg_damage = np.mean(self.surface.damage)
        # Additional analysis metrics and visualizations can be added here

    def save_simulation_data(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['X', 'Y', 'Z', 'Damage'])
            for x in range(self.surface.size[0]):
                for y in range(self.surface.size[1]):
                    writer.writerow([x, y, self.surface.damage[x, y]])

class ParticleImpactVisualization:
    def __init__(self, simulation):
        self.simulation = simulation
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')

    def update(self, frame):
        self.ax.clear()
        self.ax.set_xlim(0, self.simulation.surface.size[0])
        self.ax.set_ylim(0, self.simulation.surface.size[1])
        self.ax.set_zlim(0, self.simulation.surface.thickness)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Damage')

        for particle in self.simulation.particles:
            if particle.position[2] < self.simulation.surface.thickness:
                particle.position += particle.velocity
                particle.position[2] += 0.01  # Move particle along z-axis (simulating impact depth)
                if (0 <= particle.position[0] < self.simulation.surface.size[0] and 
                    0 <= particle.position[1] < self.simulation.surface.size[1]):
                    impact_x = int(particle.position[0])
                    impact_y = int(particle.position[1])
                    self.simulation.surface.damage[impact_x, impact_y] += 0.01  # Simulate damage to surface
                    
                    # Simulate fragmentation upon impact
                    if self.simulation.surface.damage[impact_x, impact_y] >= particle.size:
                        if not particle.is_fragment:
                            particle.is_fragment = True
                            # Create multiple fragments
                            for _ in range(np.random.randint(2, 5)):
                                fragment_size = max(0.01, np.random.normal(particle.size/2, 0.01))
                                fragment_velocity = np.random.normal(scale=0.05, size=3)
                                fragment_particle = Particle(position=particle.position, velocity=fragment_velocity, size=fragment_size, is_fragment=True)
                                self.simulation.particles.append(fragment_particle)
                        # Skip drawing fragments, as they will be drawn in black
                        continue
               
            color = 'r' if not particle.is_fragment else 'k'
            marker = 'o' if particle.particle_type == 'normal' else '^'
            self.ax.scatter(particle.position[0], particle.position[1], particle.position[2], s=particle.size*100, c=color, marker=marker)

        self.ax.plot_surface(*np.meshgrid(np.arange(self.simulation.surface.size[0]), np.arange(self.simulation.surface.size[1])), 
                             self.simulation.surface.damage, cmap='viridis', alpha=0.5)  # Show surface damage
        self.ax.plot_surface(*np.meshgrid(np.arange(self.simulation.surface.size[0]), np.arange(self.simulation.surface.size[1])), 
                             self.simulation.surface.deformation, cmap='coolwarm', alpha=0.5)  # Show surface deformation

def main_menu():
    print("Welcome to Particle Impact Simulation")
    print("----------------------------------------------------------")
    print("1. Start Simulation")
    print("2. Customize Simulation Parameters")
    print("3. Exit")
    choice = input("Enter your choice: ")
    return choice

def customize_parameters():
    surface_width = int(input("Enter surface width [10]: ") or "10")
    surface_height = int(input("Enter surface height [10]: ") or "10")
    surface_thickness = float(input("Enter surface thickness [1]: ") or "1")
    num_particles = int(input("Enter number of particles [500]: ") or "500")  # Reduced number of particles
    max_speed = float(input("Enter maximum particle speed [0.1]: ") or "0.1")
    particle_size_mean = float(input("Enter mean particle size [0.05]: ") or "0.05")
    particle_size_std = float(input("Enter particle size standard deviation [0.02]: ") or "0.02")
    particle_velocity_mean = float(input("Enter mean particle velocity [0.05]: ") or "0.05")
    particle_velocity_std = float(input("Enter particle velocity standard deviation [0.02]: ") or "0.02")
    damage_threshold = float(input("Enter damage threshold [500]: ") or "500")  # Termination threshold
    simulation_time = int(input("Enter simulation time [1000]: ") or "1000")  # Simulation time limit
    return surface_width, surface_height, surface_thickness, num_particles, max_speed, particle_size_mean, particle_size_std, particle_velocity_mean, particle_velocity_std, damage_threshold, simulation_time

def initialize_simulation(surface_width=10, surface_height=10, surface_thickness=1, num_particles=500, max_speed=0.1,
                          particle_size_mean=0.05, particle_size_std=0.02, particle_velocity_mean=0.05, particle_velocity_std=0.02, damage_threshold=500, simulation_time=1000):
    surface = Surface(size=(surface_width, surface_height), thickness=surface_thickness)
    particles = []
    # Creating missile particle
    missile_position = np.array([np.random.uniform(surface.size[0]*0.2, surface.size[0]*0.8), np.random.uniform(surface.size[1]*0.2, surface.size[1]*0.8), 0])
    missile_velocity = np.array([np.random.normal(0, max_speed/2), np.random.normal(0, max_speed/2), max_speed])
    missile_size = 0.05
    missile_particle = Particle(position=missile_position, velocity=missile_velocity, size=missile_size)
    particles.append(missile_particle)
    # Adding additional smaller particles
    for _ in range(num_particles - 1):
        particle_position = np.random.rand(3) * surface.size[0]
        particle_velocity = np.random.normal(particle_velocity_mean, particle_velocity_std, size=3)
        particle_size = max(0.01, np.random.normal(particle_size_mean, particle_size_std))
        particle_type = 'normal' if np.random.rand() < 0.8 else 'special'  # 80% normal particles, 20% special particles
        particle = Particle(position=particle_position, velocity=particle_velocity, size=particle_size, particle_type=particle_type)
        particles.append(particle)
    simulation = ParticleImpactSimulation(surface, particles, max_speed, damage_threshold, simulation_time)
    return simulation

def start_simulation(simulation, save_data=False):
    visualization = ParticleImpactVisualization(simulation)
    ani = animation.FuncAnimation(visualization.fig, visualization.update, frames=100, interval=50)
    plt.show()

    if save_data:
        simulation.save_simulation_data('simulation_data.csv')

if __name__ == "__main__":
    surface_width, surface_height, surface_thickness, num_particles, max_speed = 10, 10, 1, 500, 0.1  # Reduced number of particles
    particle_size_mean, particle_size_std, particle_velocity_mean, particle_velocity_std = 0.05, 0.02, 0.05, 0.02
    damage_threshold = 500  # Termination threshold
    simulation_time = 1000  # Simulation time limit

    while True:
        choice = main_menu()
        if choice == "1":
            simulation = initialize_simulation(surface_width, surface_height, surface_thickness, num_particles, max_speed,
                                               particle_size_mean, particle_size_std, particle_velocity_mean, particle_velocity_std, damage_threshold, simulation_time)
            start_simulation(simulation, save_data=True)
            if simulation.check_termination():
                print("Simulation terminated. Damage threshold reached or simulation time limit exceeded.")
                simulation.analyze_damage()  # Perform post-simulation analysis
                break
        elif choice == "2":
            surface_width, surface_height, surface_thickness, num_particles, max_speed, \
            particle_size_mean, particle_size_std, particle_velocity_mean, particle_velocity_std, damage_threshold, simulation_time = customize_parameters()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
