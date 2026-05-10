import uuid
from typing import List, Dict
from scheduler.abstract.abstract_network import AbstractNetwork
import scheduler.implementation.node


class CurrentNetwork(AbstractNetwork):
    NUMBER_OF_NODES = 8

    def __init__(self):
        self.nodes = []
        ids = [uuid.uuid4() for _ in range(self.NUMBER_OF_NODES)]

        self.edges = self.__edges(ids)

        for i in ids:
            self.nodes.append(
                scheduler.implementation.node.Node(i, self.edges[i])
            )

        super().__init__(self.nodes)

    def __edges(self, ids: List[uuid.UUID]) -> Dict:
        return {
            ids[0]: [ids[1], ids[2]],
            ids[1]: [ids[0], ids[3], ids[4]],
            ids[2]: [ids[0], ids[5], ids[6]],
            ids[3]: [ids[1]],
            ids[4]: [ids[1]],
            ids[5]: [ids[2]],
            ids[6]: [ids[2], ids[7]],
            ids[7]: [ids[6]],
        }