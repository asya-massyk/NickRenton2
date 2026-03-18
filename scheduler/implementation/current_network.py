import uuid
from typing import List, Dict

from scheduler.abstract.abstract_network import AbstractNetwork
import scheduler.implementation.node


class CurrentNetwork(AbstractNetwork):
    NUMBER_OF_NODES = 8

    def __init__(self) -> None:
        # 1️⃣ Генеруємо унікальні ID вузлів
        self.nodes = []
        ids = [uuid.uuid4() for _ in range(self.NUMBER_OF_NODES)]

        # 2️⃣ Створюємо ребра мережі
        self.__get_edges(ids)

        # 3️⃣ Створюємо всі вузли з mailbox та edges
        for node_id in ids:
            node = scheduler.implementation.node.Node(node_id, self.edges[node_id])
            self.nodes.append(node)

        # 4️⃣ Ініціалізуємо AbstractNetwork
        super().__init__(self.nodes)

        # 5️⃣ Старт алгоритму для вузла-ініціатора
        initiator = min(self.nodes, key=lambda n: n.node_id)  # вузол з найменшим ID
        response = initiator.process_action(None)  # стартовий виклик

        # 6️⃣ Додаємо стартові дії у mailbox тільки для інших вузлів
        for act in response.actions:
    # додаємо тільки іншим вузлам
            if act.data['target'] != initiator.node_id:
                for node in self.nodes:
                    if node.node_id == act.data['target']:
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