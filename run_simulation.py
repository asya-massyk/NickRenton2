import uuid
import os
import time

from scheduler.core.observer import Observer
from scheduler.implementation.ly_node import LaiYangNode
from scheduler.implementation.current_network import CurrentNetwork
from scheduler.settings.network_settings import settings
from scheduler.core.action import Action


class LaiYangNetwork(CurrentNetwork):
    def __init__(self):
        super().__init__()
        new_nodes = []
        for old_node in self.nodes:
            ly_node = LaiYangNode(old_node.node_id, old_node.neighbors)
            ly_node.mailbox = old_node.mailbox
            new_nodes.append(ly_node)
        self.nodes = new_nodes


settings.EXTERNAL_REQUEST_MODE = False

if __name__ == '__main__':
    os.makedirs("test_results", exist_ok=True)

    network = LaiYangNetwork()
    observer = Observer(network)

    initiator = network.nodes[0]
    snapshot_id = uuid.uuid4()

    start_action = Action(
        data={"type": "START_SNAPSHOT", "snapshot_id": snapshot_id, "color": "RED"},
        node_id=initiator.node_id,
        action_id=uuid.uuid4()
    )
    initiator.mailbox.add_inbox_action(start_action)

    print("=== Симуляція Lai-Yang запущена ===")
    print(f"Ініціатор: {initiator.node_id}")
    print("Ctrl + C — зупинити вручну\n")

    iteration = 0
    max_iterations = 300   

    try:
        while iteration < max_iterations:
            action = observer.network.get_action()
            if action:
                observer.process_action(action)
                observer.nodes.get(action.node_id).mailbox.remove_action(action)
            else:
                time.sleep(0.1)
            iteration += 1

            if iteration % 50 == 0:
                print(f"... оброблено {iteration} ітерацій ...")

    except KeyboardInterrupt:
        pass
    finally:
        print("\n\n=== Симуляція зупинена ===")
        print("=== Зібрані snapshot'и ===")
        for node in network.nodes:
            if isinstance(node, LaiYangNode):
                snap = node.get_snapshot()
                print(f"\nNode {node.node_id}:")
                print(f"   Local snapshot: {snap.get('local_state')}")
                channel = snap.get('channel_state')
                print("   Channel state :")
                if channel:
                    for k, v in channel.items():
                        print(f"      from {k[:8]}: {len(v)} msgs")
                else:
                    print("      empty")
                print(f"   Current app   : {snap.get('current_app_state')}")
                print("-" * 60)