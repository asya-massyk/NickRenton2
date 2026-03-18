import time
import uuid
from typing import List
from scheduler.implementation.node import Node
from scheduler.core.action import Action

class Observer:
    """Спостерігач, який крок за кроком обробляє всі вузли"""
    def __init__(self, nodes: List[Node], tick_delay: float = 0.1):
        self.nodes = nodes
        self.tick_delay = tick_delay  # час між кроками в секундах

        # 🔹 Відправляємо стартові дії від ініціаторів відразу сусідам
        for node in self.nodes:
            if not node.started:
                node.started = True
                if node.node_id == min(node.neighbors + [node.node_id]):  # ініціатор
                    print(f"[Node {node.node_id}] Ініціатор стартує алгоритм")
                    started_actions = node.algo.start()  # список (target, message)
                    if started_actions is None:
                        started_actions = []

                    for target, msg in started_actions:
                        action_data = {
                            "target": target,
                            "message": msg,
                            "sender": node.node_id
                        }
                        act = Action(
                            data=action_data,
                            node_id=node.node_id,
                            action_id=uuid.uuid4()
                        )
                        # Відправляємо одразу до цільового вузла
                        for dest_node in self.nodes:
                            if dest_node.node_id == target:
                                dest_node.mailbox.add_inbox_action(act)
                                print(f"[Observer] Стартова action від {node.node_id} до {dest_node.node_id} додано")
                                break

    def run(self):
        """Основний цикл спостереження"""
        active = True
        step = 0
        while active:
            step += 1
            active = False  # перевіряємо, чи є ще дії
            print(f"\n=== Tick {step} ===")

            for node in self.nodes:
                inbox_actions = node.mailbox.inbox.copy()
                for action in inbox_actions:
                    target = action.data.get("target")

                    # Обробляємо дію
                    response = node.process_action(action)
                    node.mailbox.remove_action(action)

                    # Додаємо нові дії до inbox відповідних вузлів
                    for new_action in response.actions:
                        for dest_node in self.nodes:
                            if dest_node.node_id == new_action.data['target']:
                                dest_node.mailbox.add_inbox_action(new_action)
                                print(f"[Observer] Action від {node.node_id} до {dest_node.node_id} додано в inbox")
                                break

                # Перевіряємо чи залишились дії
                if node.mailbox.get_actions():
                    active = True

            time.sleep(self.tick_delay)