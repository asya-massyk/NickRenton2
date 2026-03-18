import uuid
from typing import List
from abc import ABC, abstractmethod

from scheduler.core.action import Action
from scheduler.core.node_response import NodeResponse


class AbstractNode(ABC):
    node_id: uuid.UUID
    neighbors: List[uuid.UUID]

    @abstractmethod
    def process_action(self, action: Action) -> NodeResponse:
        """Обробка дії та повернення NodeResponse"""
        pass