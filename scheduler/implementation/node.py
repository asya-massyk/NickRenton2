import os
from scheduler.core.mailbox import Mailbox
from scheduler.core.action import Action
from scheduler.core.node_response import NodeResponse

from . import safra
from . import rana

# 🔥 перемикання алгоритму через env
ALGORITHM = os.getenv("ALGORITHM", "rana")


class Node:
    def __init__(self, node_id, neighbors):
        self.node_id = node_id
        self.neighbors = neighbors
        self.mailbox = Mailbox()

        if ALGORITHM == "safra":
            self.algo = safra.SafraNode(node_id, neighbors)
        else:
            self.algo = rana.RanaNode(node_id, neighbors)

    def start_algorithm(self):
        return [
            Action(
                data={"sender": self.node_id, "message": ("BASIC", None)},
                node_id=n
            )
            for n in self.neighbors
        ]

    def process(self, action):
        sender = action.data["sender"]
        msg_type, payload = action.data["message"]

        out = []

        if msg_type == "BASIC":
            if hasattr(self.algo, "on_send"):
                self.algo.on_send()

            out = self.algo.on_basic(sender)

        elif msg_type == "ACK":
            out = self.algo.on_ack(sender)

        elif msg_type == "TOKEN":
            out = self.algo.on_token(payload)

        return NodeResponse([
            Action(
                data={"sender": self.node_id, "message": msg},
                node_id=tgt
            )
            for tgt, msg in out
        ])