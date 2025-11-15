# swarm_coordinator.py - Centrale server die taken en status beheert

import random
import math
from drone_agent import DroneAgent

class SwarmCoordinator:
    """
    Simuleert de centrale coördinator/server die de zwerm beheert.
    In een pure zwerm zou dit gedecentraliseerd zijn.
    """
    def __init__(self, num_drones=3, takeoff_alt=10):
        self.agents = []
        self.num_drones = num_drones
        self.takeoff_alt = takeoff_alt
        self.task_pool = []
        self.next_task_id = 1
        
        # Belangrijk: De connectiestring moet uniek zijn voor elke drone
        # Voor simulatie (SITL): 'tcp:127.0.0.1:5760' of 'udp:127.0.0.1:14550'
        # Voor echte drone: '/dev/ttyACM0' (USB) of 'udp:0.0.0.0:14550' (Wifi)
        for i in range(num_drones):
            # Gebruik hier de echte of gesimuleerde connectie!
            connection = f'udp:127.0.0.1:1455{i}' # Voor meerdere SITL drones
            self.agents.append(DroneAgent(i, connection))
            
        self.add_new_task((47.397742, 8.545594, 50)) # Voorbeeld: Zürich
        
    def add_new_task(self, target_pos_lat_lon_alt):
        """ Voegt een nieuwe taak toe. """
        self.task_pool.append({'id': self.next_task_id, 'target': target_pos_lat_lon_alt})
        self.next_task_id += 1
        print(f"\n--- Nieuwe Taak ({self.next_task_id - 1}) gecreëerd: {target_pos_lat_lon_alt} ---\n")

    def get_all_drone_statuses(self):
        """ Vraagt de status van alle fysieke drones op. """
        return [agent.get_status() for agent in self.agents]

    def perform_autonomous_task_allocation(self):
        """ Autonome toewijzing op basis van afstand en batterij. """
        # ... (Logica blijft hetzelfde, maar gebruikt nu echte GPS/Batterij data) ...
        # (Let op: Afstandsberekening tussen GPS-coördinaten is complexer dan euclidisch!)

        if self.task_pool:
            task = self.task_pool[0]
            # Voorbeeld: wijs de taak toe aan de eerste beschikbare drone
            best_agent = next((a for a in self.agents if a.state in ["flocking", "idle"]), None)
            
            if best_agent:
                best_agent.update_task(task['id'], task['target'])
                best_agent.target = task['target'] # Set target op de agent
                self.task_pool.pop(0)

    def run_initialisation(self):
        """ Brengt alle drones in de lucht. """
        for agent in self.agents:
            agent.arm_and_takeoff(self.takeoff_alt)
            
    def run_step(self):
        """ Voert één coördinatiestap uit. """
        all_statuses = self.get_all_drone_statuses()
        
        # Probeer taken toe te wijzen
        if random.random() < 0.2:
            self.perform_autonomous_task_allocation()
        
        active_drones = 0
        for agent in self.agents:
            # Haal de echte snelheid op van de drone (nodig voor Boids-berekening)
            current_vel_ned = agent.get_real_velocity()
            
            agent.update_movement(all_statuses, current_vel_ned)
            
            if agent.state not in ["low_power", "landing"]:
                active_drones += 1
                
        return active_drones
