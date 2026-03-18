# scheduler/implementation/node.py
from mailbox import Mailbox
import uuid
from typing import List
from scheduler.abstract.abstract_node import AbstractNode
from scheduler.core.action import Action
from scheduler.core.node_response import NodeResponse

from . import awerbuch
from . import sidon

# Обираємо алгоритм
ALGORITHM = "awerbuch"  # або "sidon"

class Node(AbstractNode):
    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID]):
        self.node_id = node_id
        self.neighbors = neighbors
        self.mailbox = Mailbox()
        self.started = False

        if ALGORITHM == "awerbuch":
            self.algo = awerbuch.AwerbuchNode(node_id, neighbors)
        else:
            self.algo = sidon.SidonNode(node_id, neighbors)

    def is_initiator(self) -> bool:
        # Ініціатор — вузол з мінімальним UUID
        return self.node_id == min(self.neighbors + [self.node_id])

    def start_algorithm(self):
        acts = self.algo.start() or []
        result = []
        for tgt, msg in acts:
            act = Action(
                data={"target": tgt, "message": msg, "sender": self.node_id},
                node_id=self.node_id,
                action_id=uuid.uuid4()
            )
            result.append(act)
        return result

    def process_action(self, action: Action) -> NodeResponse:
        sender = action.data["sender"]
        msg = action.data["message"]

        # Обробка через алгоритм
        acts = self.algo.on_receive(sender, msg) or []
        result = []
        for tgt, message in acts:
            act = Action(
                data={"target": tgt, "message": message, "sender": self.node_id},
                node_id=self.node_id,
                action_id=uuid.uuid4()
            )
            result.append(act)

        return NodeResponse(result)