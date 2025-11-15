# drone_agent.py

import random

class DroneAgent:
    """
    Vertegenwoordigt een individuele drone in de zwerm.
    """
    def __init__(self, agent_id, position=(0, 0, 0), battery_level=100):
        self.id = agent_id
        self.position = list(position)
        self.battery = battery_level
        self.target = None
        self.state = "idle"

    def move_randomly(self):
        """ Simuleert een basisbeweging. """
        if self.battery > 5:
            self.position[0] += random.uniform(-1, 1)
            self.position[1] += random.uniform(-1, 1)
            # De hoogte (Z-as) blijft hier voorlopig constant
            self.battery -= 1
            print(f"Drone {self.id} beweegt naar {self.position[:2]}, batterij: {self.battery}%")
            return True
        else:
            self.state = "low_power"
            print(f"Drone {self.id} heeft te weinig stroom ({self.battery}%)")
            return False

    def update_task(self, new_task_id, target_pos):
        """
        Dynamische Taaktoewijzing: Ontvangt een nieuwe taak.
        In een echt systeem zou dit via een licht communicatieprotocol gebeuren.
        """
        self.target = target_pos
        self.state = "executing_task"
        print(f"Drone {self.id} heeft taak {new_task_id} ontvangen, doel: {target_pos}")

    def get_status(self):
        """ Rapporteert de status van de drone. """
        return {
            'id': self.id,
            'position': tuple(round(p, 2) for p in self.position),
            'battery': self.battery,
            'state': self.state
        }
