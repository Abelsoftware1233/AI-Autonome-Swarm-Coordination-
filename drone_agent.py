# drone_agent.py - Aangepast voor echte vluchtcommando's (DroneKit/MAVLink)

import math
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative

class DroneAgent:
    """
    Vertegenwoordigt de besturingslogica voor een fysieke drone.
    Vereist een DroneKit-verbinding.
    """
    def __init__(self, agent_id, connection_string, max_speed=0.5):
        self.id = agent_id
        self.max_speed = max_speed
        self.perception_radius = 5.0
        self.target = None
        
        # 1. Connectie met de vluchtcontroller via DroneKit
        print(f"Drone {self.id}: Verbinden met de vluchtcontroller op {connection_string}...")
        self.vehicle = connect(connection_string, wait_ready=True)
        print(f"Drone {self.id}: Verbonden!")
        
        self.state = "initialising"
        
        # Voor lokale Boids-berekeningen (wordt elke stap bijgewerkt met GPS)
        self._current_velocity = [0, 0, 0] 

    def get_real_position(self):
        """ Haalt de huidige GPS-positie op van de drone. """
        # We gebruiken lat, lon, alt (GPS-coördinaten)
        loc = self.vehicle.location.global_relative_frame
        return [loc.lat, loc.lon, loc.alt] # Z-as is hoogte

    def get_real_velocity(self):
        """ Haalt de snelheid op van de drone. """
        # Let op: Snelheid is hier in m/s (NED - North, East, Down)
        return [
            self.vehicle.velocity[0],  # North (m/s)
            self.vehicle.velocity[1],  # East (m/s)
            -self.vehicle.velocity[2]  # Up (m/s)
        ]

    def get_status(self):
        """ Rapporteert de status van de drone. """
        loc = self.vehicle.location.global_relative_frame
        return {
            'id': self.id,
            'position': (round(loc.lat, 6), round(loc.lon, 6), round(loc.alt, 2)),
            'battery': round(self.vehicle.battery.level, 1),
            'state': self.state,
            'mode': str(self.vehicle.mode.name)
        }

    # --- HULPFUNCTIES (BIJVOORBEELD Blijft hetzelfde, maar nu toegepast op MAVLink data) ---
    def _limit_vector(self, vector, limit):
        # ... (deze logica blijft hetzelfde als in de simulatie)
        magnitude = math.sqrt(sum(v**2 for v in vector))
        if magnitude > limit:
            return [v * limit / magnitude for v in vector]
        return vector

    def _separation(self, neighbors):
        # ... (logica voor separation) ...
        return [0, 0, 0] # Vereist geavanceerde positionering

    def _alignment(self, neighbors):
        # ... (logica voor alignment) ...
        return [0, 0, 0]

    def _cohesion(self, neighbors):
        # ... (logica voor cohesion) ...
        return [0, 0, 0]

    # --- VLUGT- EN SWARM-COMMANDO'S ---

    def arm_and_takeoff(self, aTargetAltitude):
        """ Arm de drone en stijg op naar een bepaalde hoogte. """
        print(f"Drone {self.id}: Basiscontroles voorbereiden...")
        
        while not self.vehicle.is_armable:
            print(f"Drone {self.id}: Wachten op initialisatie...")
            time.sleep(1)

        # Toezicht op veiligheid en ARM
        # ... (Hier komen veiligheidschecks zoals GPS-lock) ...
        
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        
        while not self.vehicle.armed:
            print(f"Drone {self.id}: Wachten op arming...")
            time.sleep(1)

        print(f"Drone {self.id}: Opstijgen naar {aTargetAltitude} meter!")
        self.vehicle.simple_takeoff(aTargetAltitude)  # Neem af met de standaard home locatie.

        while True:
            print(f" Hoogte: {self.vehicle.location.global_relative_frame.alt}")
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print(f"Drone {self.id}: Opgestegen!")
                break
            time.sleep(1)
        
        self.state = "flocking"


    def send_global_velocity(self, velocity_north, velocity_east, velocity_up):
        """ Stuur de MAVLink commando's voor snelheid. Dit is de kern van de beweging. """
        # Dit is de DroneKit-methode om in GUIDED_NOGPS (of gewoon GUIDED) te bewegen
        # Latere implementaties zouden MAVSDK of geavanceerdere VFR_HUD commando's gebruiken.
        msg = self.vehicle.message_factory.set_position_target_global_int_encode(
            0,       # time_boot_ms (niet gebruikt)
            0, 0,    # target system, target component
            7,       # MAV_FRAME_BODY_OFFSET_NED (of GLOBAL_RELATIVE_FRAME)
            0b0000111111000111, # type_mask (alleen snelheid gebruiken)
            0, 0, 0, # lat, lon, alt
            velocity_north, velocity_east, -velocity_up, # vx, vy, vz (m/s)
            0, 0, 0, # afx, afy, afz (niet gebruikt)
            0, 0)    # yaw, yaw_rate (niet gebruikt) 

        self.vehicle.send_mavlink(msg)
        
    def land(self):
        """ Zet de drone in land-modus. """
        print(f"Drone {self.id}: Schakelen naar LAND modus.")
        self.vehicle.mode = VehicleMode("LAND")
        self.state = "landing"

    def update_movement(self, all_agents_status, current_velocity_ned):
        """ 
        Berekent de gewenste snelheidsvector op basis van zwermregels
        en stuurt dit naar de vluchtcontroller.
        """
        if self.vehicle.battery.level <= 10:
            self.state = "low_power"
            self.land()
            return
            
        # 1. Bepaal de 'buren' (hier gesimuleerd op basis van gedeelde status)
        neighbors = [s for s in all_agents_status if s['id'] != self.id]
        
        # 2. Boids berekening (simpel gehouden om de code compact te houden)
        # In een echte toepassing zou de Boids-berekening veel complexer zijn
        # omdat het werkt met GPS/Local coördinaten.
        
        # Simpele test: Als er een doel is, beweeg ernaartoe. Anders, drift.
        
        if self.state == "executing_task" and self.target:
            # Opdracht: Stuur naar het doel met een constante snelheid
            # (In de echte wereld moet dit via PID-controllers gebeuren)
            V_N = 0.5  # Snelheid Noord
            V_E = 0.5  # Snelheid Oost
            V_U = 0.0  # Snelheid Omhoog
            
            # TODO: Converteer GPS-doel (target) naar een snelheid in m/s 
            # (Dit is de lastigste stap in de overgang van sim naar echt)
            
            self.send_global_velocity(V_N, V_E, V_U)

        elif self.state == "flocking":
            # Houd de drone in een lichte 'flocking' mode (d.w.z. beweeg langzaam)
            V_N = 0.1
            V_E = 0.1
            V_U = 0.0
            self.send_global_velocity(V_N, V_E, V_U)
            
        return True
