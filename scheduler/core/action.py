import uuid
from typing import Any, Dict


class Action:
    def __init__(self, data: Dict[Any, Any], node_id, action_id=None):
        self.data = data
        self.node_id = node_id
        self.action_id = action_id or uuid.uuid4()
        self.action_type = "inbox"