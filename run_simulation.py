import uuid
from scheduler.core.observer import Observer
from scheduler.implementation.node import Node

# Створюємо вузли
node_ids = [uuid.uuid4() for _ in range(3)]
# Сусіди для прикладу (кільце)
neighbors_list = [
    [node_ids[1]],       # вузол 0 -> вузол 1
    [node_ids[2]],       # вузол 1 -> вузол 2
    [node_ids[0]]        # вузол 2 -> вузол 0
]

nodes = [Node(node_id=node_ids[i], neighbors=neighbors_list[i]) for i in range(3)]

# Запускаємо спостерігача
observer = Observer(nodes, tick_delay=0.2)
observer.run()