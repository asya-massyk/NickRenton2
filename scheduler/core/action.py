import uuid
from typing import Any, Dict


class Action:
    def __init__(self, data: Dict[Any, Any], node_id: uuid.UUID, action_id: uuid.UUID = None):
        self.data = data
        self.node_id = node_id
        self.action_id = action_id or uuid.uuid4()
        self.action_type = "inbox"

    def __repr__(self):
        return f"{self.action_type.capitalize()} action for Node {self.node_id} with Data: {self.data}"