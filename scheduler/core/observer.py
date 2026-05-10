import time
import random
from scheduler.core.action import Action
import os

ALGORITHM = os.getenv("ALGORITHM", "rana")


class Observer:
    def __init__(self, nodes):
        self.nodes = nodes
        self.total_messages = 0

        self.initiator = min(nodes, key=lambda n: str(n.node_id))
        print("[INIT]", self.initiator.node_id)

        # старт BASIC
        initial = self.initiator.start_algorithm()
        for a in initial:
            self.send(a)
            self.total_messages += 1

        # кільце для Safra
        nodes_sorted = sorted(self.nodes, key=lambda n: str(n.node_id))

        for i, n in enumerate(nodes_sorted):
            nxt = nodes_sorted[(i + 1) % len(nodes_sorted)]
            n.algo.next_node = nxt.node_id

        nodes_sorted[0].algo.is_initiator = True

        self.token_started = False

    def send(self, action):
        for n in self.nodes:
            if str(n.node_id) == str(action.node_id):
                n.mailbox.add_inbox_action(action)

    def run(self):
        step = 0

        while step < 100:
            step += 1
            print("\nTick", step)

            pending = []
            active = False

            for n in self.nodes:
                while n.mailbox.inbox:
                    a = n.mailbox.inbox.pop(0)
                    active = True
                    r = n.process(a)
                    pending.extend(r.actions)
                    self.total_messages += len(r.actions)

            # 🔥 запускаємо токен ТІЛЬКИ для Safra і тільки після старту
            if ALGORITHM == "safra" and step == 2 and not self.token_started:
                token = {"counter": 0, "color": "WHITE"}

                self.send(Action(
                    data={
                        "sender": self.initiator.node_id,
                        "message": ("TOKEN", token)
                    },
                    node_id=self.initiator.node_id
                ))

                self.token_started = True

            # зупинка Safra
            if ALGORITHM == "safra":
                if any(getattr(n.algo, "terminated", False) for n in self.nodes):
                    print("\nSAFRA GLOBAL STOP")
                    break

            if not pending and not active:
                print("\nFINISHED")
                break

            random.shuffle(pending)

            for p in pending:
                self.send(p)

            time.sleep(0.05)

        print("\nMESSAGES:", self.total_messages)
        print("Ticks:", step)