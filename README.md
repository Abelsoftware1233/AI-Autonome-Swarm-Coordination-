# AI-Autonome-Swarm-Coordination-
Repository for the AI drones software for military purpose.

# 🤖 AI Autonome Zwerm Coördinatie (Drone Swarm)

Dit project simuleert een gedecentraliseerde zwerm van drones (**Swarm Intelligence**) die autonoom taken coördineren. Het systeem gebruikt lokale communicatieregels (geïnspireerd door het **Boids**-algoritme) om coherentie te behouden terwijl individuele agenten beslissen over taaktoewijzing op basis van afstand en batterijstatus.

## ✨ Kenmerken

* **Gedecentraliseerde Beweging:** De drones gebruiken de drie Boids-regels (**Separation**, **Alignment**, **Cohesion**) om botsingen te vermijden en de zwermstructuur te behouden zonder centrale controle.
* **Autonome Taaktoewijzing:** Drones in `idle` of `flocking` status bepalen de 'kosten' van een taak op basis van hun **afstand tot het doel** en hun **batterijniveau**, waardoor de meest efficiënte agent de taak krijgt (**Greedy Task Allocation**).
* **Energiebeheer:** Batterijniveaus dalen bij beweging, en drones gaan in de status `low_power` wanneer hun energie op is, wat de robuustheid test.

### Vereisten

Dit project heeft geen externe bibliotheken nodig en draait op standaard **Python 3**.

### De Simulatie Draaien

1. Zorg ervoor dat de drie bestanden (`drone_agent.py`, `swarm_simulator.py`, `main.py`) in dezelfde map staan.
2. Voer het `main.py` script uit in uw terminal:

    ```bash
    python3 main.py
    ```

3. De terminal zal de simulatiestappen, taaktoewijzingen en de status van de eerste drie drones tonen.

## 📁 Projectstructuur

Het project bestaat uit drie hoofdscripts:

├── drone_agent.py          # De kernklasse met lokale AI-logica (Boids-regels).
├── swarm_simulator.py      # Beheert de verzameling van drones, taakwachtrij en het toewijzingsalgoritme.
└── main.py                 # Het uitvoerbare bestand dat de simulatie start en de stappen loopt.


