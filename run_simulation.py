# run_simulation.py
from scheduler.core.observer import Observer
from scheduler.implementation.current_network import CurrentNetwork

if __name__ == "__main__":
    network = CurrentNetwork()                  # створюємо мережу
    observer = Observer(network.nodes)          # ← передаємо network.nodes (це список Node)
    observer.run()