import time
import random
from typing import List
from uuid import UUID
from scheduler.core.action import Action
from scheduler.implementation.node import Node, ALGORITHM   

class Observer:
    def __init__(self, nodes: List[Node], tick_delay: float = 0.1):
        self.nodes = nodes
        self.tick_delay = tick_delay
        self.total_messages = 0
        self.last_tick = 0

        if not nodes:
            print("[Observer] No nodes found — nothing to start")
            return

        print("[Observer] ALL NODES start election simultaneously (max ID wins)")

        for node in self.nodes:
            node.started = True
            initial_actions = node.start_algorithm() or []
            for act in initial_actions:
                self._send(act)
                self.total_messages += 1

    def _send(self, action: Action):
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

            random.shuffle(pending_actions)

            for act in pending_actions:
                self._send(act)

            time.sleep(self.tick_delay)

        self.last_tick = step

        if step >= MAX_STEPS:
            print("\n=== Reached max steps — possible infinite loop or very large graph ===")

        self._print_tree_summary()

    def _short(self, uid: UUID) -> str:
        return str(uid)[:8] + "..."

    def _print_tree_summary(self):
        print("\n=== Spanning Tree Structure ===")
        tree = {}

        # 🔥 правильний root
        root_node = next((n for n in self.nodes if n.algo.parent == n.node_id), None)

        for node in self.nodes:
            parent = getattr(node.algo, 'parent', None)
            if parent is None or parent == node.node_id:
                continue

            p_short = self._short(parent)
            if p_short not in tree:
                tree[p_short] = []
            tree[p_short].append(self._short(node.node_id))

        for children in tree.values():
            children.sort()

        from pprint import pprint
        pprint(tree, width=100, compact=True)

        if root_node:
            root_short = self._short(root_node.node_id)
            print(f"Root: {root_short}")

            if root_short in tree:
                print(f"Root children: {', '.join(tree[root_short])}")
            else:
                print("Root has no children")
        else:
            print("Root not found")

        print(f"\n=== Summary ===")
        algo_map = {
            "awerbuch": "Awerbuch",
            "sidon": "Sidon",
            "echo_election": "Echo Election (Spanning Tree + Leader)"
        }
        algo_name = algo_map.get(ALGORITHM, ALGORITHM.capitalize())
        print(f"  Algorithm: {algo_name}")
        print(f"  Nodes: {len(self.nodes)}")
        print(f"  Total messages sent: {self.total_messages}")
        print(f"  Ticks: {self.last_tick}")
        print("  Spanning tree built successfully")