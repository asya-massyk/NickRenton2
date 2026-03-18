import uuid
from typing import List, Dict

from scheduler.abstract.abstract_network import AbstractNetwork
from scheduler.core.node_response import NodeResponse   
import scheduler.implementation.node

class CurrentNetwork(AbstractNetwork):
    NUMBER_OF_NODES = 8

    def __init__(self) -> None:
        self.nodes = []
        ids = [uuid.uuid4() for _ in range(self.NUMBER_OF_NODES)]

        self.__get_edges(ids)

        for node_id in ids:
            node = scheduler.implementation.node.Node(node_id, self.edges[node_id])
            self.nodes.append(node)

        super().__init__(self.nodes)


        initiator = min(self.nodes, key=lambda n: n.node_id)
        initial_acts = initiator.start_algorithm() or []
        initiator.started = True
        response = NodeResponse(initial_acts)

        
        for act in response.actions:
            if act.node_id != initiator.node_id:          
                for node in self.nodes:
                    if node.node_id == act.node_id:
                        node.mailbox.add_inbox_action(act)

    def __iter__(self):
        return iter(self.nodes)

    def __get_edges(self, ids: List[uuid.UUID]) -> Dict[uuid.UUID, List[uuid.UUID]]:
        # Статична топологія мережі
        self.edges = {
            ids[0]: [ids[1], ids[2]],
            ids[1]: [ids[0], ids[3], ids[4]],
            ids[2]: [ids[0], ids[5], ids[6], ids[7]],
            ids[3]: [ids[1]],
            ids[4]: [ids[1]],
            ids[5]: [ids[2]],
            ids[6]: [ids[2]],
            ids[7]: [ids[2]]
        }
        return self.edges