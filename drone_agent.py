# drone_agent.py

import random
import math

class DroneAgent:
    """
    Vertegenwoordigt een individuele drone in de zwerm.
    Geüpdatet met Boids (zwermintelligentie) logica.
    """
    def __init__(self, agent_id, position=(0, 0, 0), battery_level=100):
        self.id = agent_id
        self.position = list(position)
        self.battery = battery_level
        self.target = None
        self.state = "idle"
        # Snelheid en maximale kracht (voor Boids)
        self.velocity = [random.uniform(-0.1, 0.1) for _ in range(3)]
        self.max_speed = 0.5
        self.perception_radius = 5.0  # Hoever de drone kan 'kijken'

    def update_task(self, new_task_id, target_pos):
        """
        Dynamische Taaktoewijzing: Ontvangt een nieuwe taak.
        """
        self.target = target_pos
        self.state = "executing_task"
        print(f"Drone {self.id} heeft taak {new_task_id} ontvangen, doel: {target_pos}")

    # --- SWARM INTELLIGENCE LOGIC (BOIDS) ---

    def _limit_vector(self, vector, limit):
        """ Beperk de lengte van de vector tot een maximum. """
        magnitude = math.sqrt(sum(v**2 for v in vector))
        if magnitude > limit:
            return [v * limit / magnitude for v in vector]
        return vector

    def _separation(self, neighbors):
        """ Regel 1: Vermijd botsingen. Stuur weg van dichtstbijzijnde buren. """
        steer = [0, 0, 0]
        count = 0
        for other in neighbors:
            distance = math.sqrt(sum((self.position[i] - other.position[i])**2 for i in range(3)))
            if 0 < distance < 1.0: # Kleinere afstand, sterkere afstoting
                diff = [(self.position[i] - other.position[i]) / distance**2 for i in range(3)] # Omgekeerd evenredig met afstand^2
                steer = [steer[i] + diff[i] for i in range(3)]
                count += 1
        
        if count > 0:
            steer = [s / count for s in steer]
            steer = self._limit_vector(steer, self.max_speed)
        return steer

    def _alignment(self, neighbors):
        """ Regel 2: Pas de snelheid aan aan het gemiddelde van de buren. """
        avg_velocity = [0, 0, 0]
        if neighbors:
            for other in neighbors:
                avg_velocity = [avg_velocity[i] + other.velocity[i] for i in range(3)]
            
            avg_velocity = [v / len(neighbors) for v in avg_velocity]
            # Sturen naar het gemiddelde
            steer = [(avg_velocity[i] - self.velocity[i]) * 0.1 for i in range(3)] # Factor 0.1 voor zachte sturing
            return self._limit_vector(steer, self.max_speed)
        return [0, 0, 0]

    def _cohesion(self, neighbors):
        """ Regel 3: Beweeg naar het gemiddelde centrum van de buren. """
        center_of_mass = [0, 0, 0]
        if neighbors:
            for other in neighbors:
                center_of_mass = [center_of_mass[i] + other.position[i] for i in range(3)]
            
            center_of_mass = [c / len(neighbors) for c in center_of_mass]
            # Vector van huidige positie naar middelpunt
            steer = [(center_of_mass[i] - self.position[i]) * 0.005 for i in range(3)] # Kleine factor voor zachte aantrekking
            return self._limit_vector(steer, self.max_speed)
        return [0, 0, 0]

    def update_movement(self, all_agents):
        """ Berekent de nieuwe positie op basis van zwermregels en taken. """
        if self.battery <= 5:
            self.state = "low_power"
            return False

        # 1. Bepaal buren binnen de perception_radius
        neighbors = []
        for agent in all_agents:
            if agent is not self:
                distance = math.sqrt(sum((self.position[i] - agent.position[i])**2 for i in range(3)))
                if distance < self.perception_radius:
                    neighbors.append(agent)
        
        # 2. Bereken de Boids krachten
        sep_force = self._separation(neighbors)
        align_force = self._alignment(neighbors)
        coh_force = self._cohesion(neighbors)

        # 3. Combineer de krachten (gewichten bepalen het gedrag)
        final_acceleration = [
            sep_force[i] * 3.0 +   # Sterke nadruk op botsingsvermijding
            align_force[i] * 1.0 + # Matige uitlijning
            coh_force[i] * 0.5     # Zachte aantrekking
            for i in range(3)
        ]

        # 4. Voeg taaksturing toe als er een doel is
        if self.state == "executing_task" and self.target:
            target_vector = [self.target[i] - self.position[i] for i in range(3)]
            target_steer = self._limit_vector(target_vector, 0.5) # Zachte sturing naar het doel
            final_acceleration = [
                final_acceleration[i] + target_steer[i] * 2.0
                for i in range(3)
            ]
        
        # 5. Update snelheid en positie (Integratie)
        self.velocity = [self.velocity[i] + final_acceleration[i] for i in range(3)]
        self.velocity = self._limit_vector(self.velocity, self.max_speed)

        self.position = [self.position[i] + self.velocity[i] for i in range(3)]
        
        # Batterijverbruik
        self.battery -= 0.1
        self.state = "flocking" if self.state != "executing_task" else "executing_task"
        return True

    def get_status(self):
        """ Rapporteert de status van de drone. """
        return {
            'id': self.id,
            'position': tuple(round(p, 2) for p in self.position),
            'battery': round(self.battery, 1),
            'state': self.state
        }
