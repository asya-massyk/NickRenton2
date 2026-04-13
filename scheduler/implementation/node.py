# scheduler/implementation/node.py
from scheduler.core.mailbox import Mailbox
import uuid
from typing import List
from scheduler.abstract.abstract_node import AbstractNode
from scheduler.core.action import Action
from scheduler.core.node_response import NodeResponse

from . import awerbuch
from . import sidon
from . import echo_election   # ← має бути

ALGORITHM = "echo_election"   # ← залиш

class Node(AbstractNode):
    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID]):
        self.node_id = node_id
        self.neighbors = neighbors
        self.mailbox = Mailbox()
        self.started = False

        if ALGORITHM == "awerbuch":
            self.algo = awerbuch.AwerbuchNode(node_id, neighbors)
        elif ALGORITHM == "sidon":
            self.algo = sidon.SidonNode(node_id, neighbors)
        elif ALGORITHM == "echo_election":
            self.algo = echo_election.EchoElectionNode(node_id, neighbors)
        else:
            raise ValueError(f"Unknown algorithm: {ALGORITHM}")

    def start_algorithm(self):
        # ← ВИПРАВЛЕННЯ: для echo_election ігноруємо прапорець started
        if ALGORITHM != "echo_election" and self.started:
            return []

        self.started = True
        acts = self.algo.start() or []

        result = []
        for tgt, msg in acts:
            act = Action(
                data={"target": tgt, "message": msg, "sender": self.node_id},
                node_id=tgt,
                action_id=uuid.uuid4()
            )
            result.append(act)
        return result

    def process_action(self, action: Action) -> NodeResponse:
        sender = action.data["sender"]
        msg = action.data["message"]

        acts = self.algo.on_receive(sender, msg) or []
        result = []
        for tgt, message in acts:
            act = Action(
                data={"target": tgt, "message": message, "sender": self.node_id},
                node_id=tgt,
                action_id=uuid.uuid4()
            )
            result.append(act)

        return NodeResponse(result)