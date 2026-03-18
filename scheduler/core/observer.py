import time
import random
from typing import List
from uuid import UUID
from scheduler.core.action import Action
from scheduler.implementation.node import Node

class Observer:
    def __init__(self, nodes: List[Node], tick_delay: float = 0.1):
        self.nodes = nodes
        self.tick_delay = tick_delay
        self.total_messages = 0
        self.last_tick = 0  # зберігаємо кількість тіків для підсумку

        if not nodes:
            print("[Observer] No nodes found — nothing to start")
            return

        # Знаходимо ініціатора (найменший UUID)
        initiator = min(self.nodes, key=lambda n: n.node_id)
        print(f"[Observer] Initiator selected: {initiator.node_id}")

        # Скидаємо стани всіх вузлів
        for node in self.nodes:
            node.started = False

        # Запускаємо алгоритм тільки на ініціаторі
        initiator.started = True
        initial_actions = initiator.start_algorithm() or []
        

        for act in initial_actions:
            self._send(act)
            self.total_messages += 1

    def _send(self, action: Action):
        """Надсилаємо дію до отримувача (action.node_id — це отримувач)"""
        for dest in self.nodes:
            if dest.node_id == action.node_id:
                dest.mailbox.add_inbox_action(action)
                return
        print(f"[WARNING] Recipient not found for action to {action.node_id}")

    def run(self):
        step = 0
        MAX_STEPS = 200

        while step < MAX_STEPS:
            step += 1
            print(f"\n=== Tick {step} ===")

            pending_actions = []
            has_activity = False

            for node in self.nodes:
                current_inbox = node.mailbox.inbox.copy()
                if current_inbox:
                    has_activity = True

                for action in current_inbox:
                    node.mailbox.remove_action(action)
                    response = node.process_action(action)
                    pending_actions.extend(response.actions)
                    self.total_messages += len(response.actions)

            if not has_activity and not pending_actions:
                print("\n=== Simulation finished — no more messages ===")
                break

            # Перемішуємо для імітації асинхронності
            random.shuffle(pending_actions)

            for act in pending_actions:
                self._send(act)

            time.sleep(self.tick_delay)

        self.last_tick = step  # зберігаємо кількість тіків

        if step >= MAX_STEPS:
            print("\n=== Reached max steps — possible infinite loop or very large graph ===")

        self._print_tree_summary()

    def _short(self, uid: UUID) -> str:
        """Скорочений UUID для читабельності"""
        return str(uid)[:8] + "..."

    def _print_tree_summary(self):
        print("\n=== Spanning Tree Structure ===")
        tree = {}
        root = min(self.nodes, key=lambda n: n.node_id)

        for node in self.nodes:
            # Безпечне отримання parent (різні алгоритми можуть мати різні назви)
            parent = getattr(node.algo, 'parent', None)
            if parent is None or parent == node.node_id:
                continue

            p_short = self._short(parent)
            if p_short not in tree:
                tree[p_short] = []
            tree[p_short].append(self._short(node.node_id))

        # Сортуємо дітей для кращого вигляду
        for children in tree.values():
            children.sort()

        from pprint import pprint
        pprint(tree, width=100, compact=True)

        root_short = self._short(root.node_id)
        print(f"Root: {root_short}")

        if root_short in tree:
            print(f"Root children: {', '.join(tree[root_short])}")
        else:
            print("Root has no children (single node network?)")

        # Підсумок
        print(f"\n=== Summary ===")
        algo_name = 'Awerbuch' if 'awerbuch' in str(type(root.algo)).lower() else 'Sidon'
        print(f"  Algorithm: {algo_name}")
        print(f"  Nodes: {len(self.nodes)}")
        print(f"  Total messages sent: {self.total_messages}")
        print(f"  Ticks: {self.last_tick}")
        print("  Spanning tree built successfully  ")