# scheduler/core/observer.py
import time
from typing import List
from scheduler.core.action import Action
from scheduler.implementation.node import Node

class Observer:
    def __init__(self, nodes: List[Node], tick_delay: float = 0.1):
        self.nodes = nodes
        self.tick_delay = tick_delay

        # Стартова фаза: ініціатор розсилає EXPLORE
        for node in self.nodes:
            if not node.started:
                node.started = True
                if node.is_initiator():
                    actions = node.start_algorithm()
                    for a in actions:
                        self._send(a)

    def _send(self, action: Action):
        for dest in self.nodes:
            if dest.node_id == action.data["target"]:
                dest.mailbox.add_inbox_action(action)

    def run(self):
        active = True
        step = 0

        while active:
            step += 1
            active = False
            print(f"\n=== Tick {step} ===")

            for node in self.nodes:
                inbox_copy = node.mailbox.inbox.copy()
                for action in inbox_copy:
                    node.mailbox.remove_action(action)
                    responses = node.process_action(action)

                    for act in responses.actions:
                        self._send(act)

                if node.mailbox.get_actions():
                    active = True

            time.sleep(self.tick_delay)