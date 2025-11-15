# drone_run.py - Start de echte vlucht en coördinator

from swarm_coordinator import SwarmCoordinator
import time

def main():
    """ Hoofdloop van de coördinatie. """
    
    # 1. Initialisatie
    SIMULATION_STEPS = 500
    # Aantal drones en de gewenste opstijghoogte
    coordinator = SwarmCoordinator(num_drones=3, takeoff_alt=5) 
    
    print(f"--- Gestart: Coördinatie met {coordinator.num_drones} fysieke/gesimuleerde drones ---")

    # 2. Vluchtvoorbereiding en Opstijgen
    try:
        coordinator.run_initialisation()
    except Exception as e:
        print(f"FATALE FOUT bij opstijgen/verbinding: {e}")
        return

    # 3. Coördinatie Loop (Swarm Control)
    for step in range(SIMULATION_STEPS):
        
        # Voeg af en toe een nieuwe taak toe
        if step > 0 and step % 100 == 0:
            # Nieuwe GPS-coördinaten van een willekeurige locatie
            coordinator.add_new_task((47.397000 + random.uniform(-0.0005, 0.0005), 
                                      8.545000 + random.uniform(-0.0005, 0.0005), 
                                      15))
            
        active_count = coordinator.run_step()
        
        if step % 5 == 0:
            print(f"\n[STAP {step}] Actief: {active_count}/{coordinator.num_drones}. Taken: {len(coordinator.task_pool)}")
            
            for agent in coordinator.agents:
                status = agent.get_status()
                print(f"  ID {status['id']}: Pos {status['position']}, Batterij {status['battery']}%, Status: {status['state']}")
        
        time.sleep(0.5) # Korte vertraging tussen commando's

    # 4. Einde van de operatie
    print("\n--- Operatie Voltooid. Landen wordt geïnitieerd. ---")
    for agent in coordinator.agents:
        agent.land()

if __name__ == "__main__":
    main()
