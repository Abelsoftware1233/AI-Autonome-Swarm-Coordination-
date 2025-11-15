# main.py

from swarm_simulator import SwarmSimulator
import time
import random

def main():
    """ Hoofdloop van de zwermsimulatie. """
    
    # 1. Initialisatie
    SIMULATION_STEPS = 500
    simulator = SwarmSimulator(num_drones=15, area_size=100)
    print(f"--- Gestart: Zwermsimulatie met {simulator.num_drones} drones ---")
    print("Regels: Separation (hoog), Alignment (middel), Cohesion (laag)")
    
    # 2. Simulatie Loop
    for step in range(SIMULATION_STEPS):
        
        # Voeg af en toe een nieuwe taak toe
        if step > 0 and step % 50 == 0:
            simulator.add_new_task((
                random.uniform(-40, 40), 
                random.uniform(-40, 40), 
                random.uniform(5, 20)
            ))
            
        active_count = simulator.run_simulation_step()
        
        if step % 10 == 0:
            print(f"\n[STAP {step}] Actief: {active_count}/{simulator.num_drones}. Taken in wachtrij: {len(simulator.task_pool)}")
            
            # Print de status van de eerste 3 drones als voorbeeld
            for i in range(3):
                status = simulator.agents[i].get_status()
                print(f"  ID {status['id']}: Pos {status['position']}, Batterij {status['battery']}%, Status: {status['state']}")
        
        # Simulatie 'snelheid'
        time.sleep(0.01)

    # 3. Einde van de simulatie
    print("\n--- Simulatie Voltooid ---")
    low_power_drones = sum(1 for agent in simulator.agents if agent.state == "low_power")
    print(f"Totaal {low_power_drones} drones zijn uitgevallen door lage batterij.")

if __name__ == "__main__":
    main()
