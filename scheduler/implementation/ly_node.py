import uuid
from typing import List, Dict, Any
from collections import defaultdict

from scheduler.abstract.abstract_node import AbstractNode
from scheduler.core.action import Action
from scheduler.core.node_response import NodeResponse
from scheduler.core.mailbox import Mailbox


class LaiYangNode(AbstractNode):
    WHITE = "WHITE"
    RED = "RED"

    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID]):
        self.node_id = node_id
        self.neighbors = neighbors
        self.mailbox = Mailbox()

        self.color = self.WHITE
        self.local_snapshot = None
        self.channel_state: Dict[str, List[Dict]] = defaultdict(list)
        self.has_recorded = False
        self.snapshot_id = None

        # Application state
        self.application_state = {"value": 0, "messages_processed": 0}

        # Snapshot delay
        self.messages_processed_before_record = 0
        self.min_messages_for_snapshot = 10

    def take_local_snapshot(self, snapshot_id: uuid.UUID) -> None:
        if self.has_recorded:
            return

        self.has_recorded = True
        self.snapshot_id = snapshot_id
        self.local_snapshot = self.application_state.copy()
        self.color = self.RED

        print(
            f"[Node {self.node_id}] === LOCAL SNAPSHOT TAKEN AFTER "
            f"{self.messages_processed_before_record} msgs === {self.local_snapshot}"
        )

    def record_in_transit(self, sender_id: uuid.UUID, payload: Dict) -> None:
        sender_str = str(sender_id)
        sender_short = sender_str[:8]

        self.channel_state[sender_str].append(payload.copy())

        print(
            f"[Node {self.node_id}] Recorded in-transit from {sender_short}: "
            f"+{payload.get('increment', 0)}"
        )

    def process_action(self, message: Action) -> NodeResponse:
        data = message.data
        sender_id = message.node_id
        out_actions = []

        msg_type = data.get("type")
        payload = data.get("payload", {})
        color = data.get("color", self.WHITE)
        snap_id = data.get("snapshot_id")

        # ====================== LAI-YANG ======================

        # Якщо отримали RED повідомлення і були WHITE
        if color == self.RED and self.color == self.WHITE:
            self.messages_processed_before_record = self.application_state["messages_processed"]

            if self.messages_processed_before_record >= self.min_messages_for_snapshot:
                self.take_local_snapshot(snap_id)
            else:
                # стаємо RED, але snapshot ще не беремо
                self.color = self.RED
                self.snapshot_id = snap_id

        # Якщо ми RED і прийшло WHITE повідомлення → це in-transit
        if self.color == self.RED and color == self.WHITE:
            self.record_in_transit(sender_id, payload)

        # ====================== APPLICATION ======================

        if msg_type == "COMPUTATION":
            self.application_state["value"] += payload.get("increment", 0)
            self.application_state["messages_processed"] += 1

            # Можемо взяти snapshot пізніше
            if self.color == self.RED and not self.has_recorded:
                if (
                    self.application_state["messages_processed"]
                    - self.messages_processed_before_record
                    >= self.min_messages_for_snapshot
                ):
                    self.take_local_snapshot(self.snapshot_id or snap_id)

        # ====================== SENDING ======================

        # Трохи хаосу для симуляції "повідомлень у польоті"
        import random
        send_color = self.RED if self.color == self.RED and random.random() > 0.3 else self.WHITE

        for neigh in self.neighbors:
            new_data = {
                "type": "COMPUTATION",
                "payload": {"increment": 1},
                "color": send_color,
                "snapshot_id": self.snapshot_id or snap_id,
            }
            out_actions.append(Action(new_data, neigh, uuid.uuid4()))

        # Ініціація snapshot
        if msg_type == "START_SNAPSHOT" and self.color == self.WHITE:
            self.take_local_snapshot(data.get("snapshot_id"))

        return NodeResponse(out_actions)

    def get_snapshot(self) -> Dict[str, Any]:
        if not self.has_recorded:
            return {"status": "not_recorded"}

        return {
            "local_state": self.local_snapshot,
            "channel_state": dict(self.channel_state),
            "color": self.color,
            "current_app_state": self.application_state.copy(),
        }