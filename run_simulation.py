from scheduler.core.observer import Observer
from scheduler.implementation.current_network import CurrentNetwork

if __name__ == "__main__":
    network = CurrentNetwork()
    observer = Observer(network)
    observer.run()