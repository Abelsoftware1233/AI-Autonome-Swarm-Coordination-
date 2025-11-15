# swarm_simulator.py

import random
from drone_agent import DroneAgent

class SwarmSimulator:
    """
    Beheert de verzameling DroneAgents en de simulatie-logica.
    Voert de AI Autonome Taaktoewijzing uit.
    """
    def __init__(self, num_drones=10, area_size=50):
        self.agents = []
        self.num_drones = num_drones
        self.area_size = area_size
        self._initialize_swarm()
        self.next_task_id = 1
        self.task_pool = []
        
        # Voeg een paar initiële taken toe
        self.add_new_task((random.uniform(-20, 20), random.uniform(-20, 20), 10))
        self.add_new_task((random.uniform(-20, 20), random.uniform(-20, 20), 10))

    def _initialize_swarm(self):
        """ Creëert de drones op willekeurige posities. """
        for i in range(self.num_drones):
            pos = (
                random.uniform(-self.area_size/2, self.area_size/2),
                random.uniform(-self.area_size/2, self.area_size/2),
                random.uniform(5, 15)  # Initiele Z-hoogte
            )
            self.agents.append(DroneAgent(i, position=pos))
            
    def add_new_task(self, target_pos):
        """ Voegt een nieuwe taak toe aan de wachtrij. """
        self.task_pool.append({'id': self.next_task_id, 'target': target_pos})
        self.next_task_id += 1
        print(f"\n--- Nieuwe Taak ({self.next_task_id - 1}) gecreëerd op: {target_pos} ---\n")

    # --- AUTONOME TAAKTOEWIJZING (AI) ---

    def perform_autonomous_task_allocation(self):
        """
        Gedecentraliseerd beslissingsalgoritme om de beste drone voor een taak te vinden.
        (Gebruikt een simpele 'Greedy' toewijzing op basis van afstand en batterij)
        """
        if not self.task_pool:
            return

        task = self.task_pool[0]  # Neem de oudste taak
        best_agent = None
        min_cost = float('inf')

        for agent in self.agents:
            if agent.state in ["idle", "flocking"]:
                # Bereken de kosten (Cost Function): afstand * batterijfactor
                distance = math.sqrt(sum((agent.position[i] - task['target'][i])**2 for i in range(3)))
                
                # Batterijfactor: de kosten zijn lager als de batterij vol is
                battery_factor = 100 / (agent.battery + 1) # Batterij laag = factor hoog
                
                cost = distance * battery_factor

                if cost < min_cost:
                    min_cost = cost
                    best_agent = agent
        
        if best_agent:
            # Wijs de taak toe en verwijder deze uit de pool
            best_agent.update_task(task['id'], task['target'])
            self.task_pool.pop(0)
        
    def run_simulation_step(self):
        """ Voert één simulatiestap uit voor alle drones. """
        
        # 1. Probeer een autonome toewijzing uit te voeren
        if random.random() < 0.2: # Slechts 20% kans per stap om een nieuwe taak toe te wijzen (optimalisatie)
            self.perform_autonomous_task_allocation()
        
        # 2. Update de beweging van alle drones
        active_drones = 0
        for agent in self.agents:
            agent.update_movement(self.agents)
            if agent.state != "low_power":
                active_drones += 1
        
        # 3. Controleer de taakvoltooiing
        for agent in self.agents:
            if agent.state == "executing_task" and agent.target:
                distance_to_target = math.sqrt(sum((agent.position[i] - agent.target[i])**2 for i in range(3)))
                
                if distance_to_target < 1.0: # Doel bereikt
                    print(f"Drone {agent.id} heeft taak voltooid op {agent.target}")
                    agent.target = None
                    agent.state = "idle" # Keer terug naar de zwerm/wachtstatus
                    
        return active_drones
