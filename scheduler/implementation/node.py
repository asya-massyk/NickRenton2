import uuid
from typing import List

from scheduler.abstract.abstract_node import AbstractNode
from scheduler.core.action import Action
from scheduler.core.node_response import NodeResponse

from . import awerbuch
from . import sidon

# Підключаємо класи алгоритмів
AwerbuchNode = awerbuch.AwerbuchNode
SidonNode = sidon.SidonNode

# Вибір алгоритму
ALGORITHM = "awerbuch"  # або "sidon"


class Mailbox:
    """Черга для inbox та outbox"""
    def __init__(self):
        self.inbox: List[Action] = []
        self.outbox: List[Action] = []

    def add_inbox_action(self, action: Action):
        action.action_type = 'inbox'
        self.inbox.append(action)

    def add_outbox_action(self, action: Action):
        action.action_type = 'outbox'
        self.outbox.append(action)

    def get_actions(self) -> List[Action]:
        """Повертає всі дії в inbox та outbox, не видаляючи їх"""
        return self.inbox + self.outbox

    def remove_action(self, action: Action):
        if action.action_type == 'inbox' and action in self.inbox:
            self.inbox.remove(action)
        elif action.action_type == 'outbox' and action in self.outbox:
            self.outbox.remove(action)


class Node(AbstractNode):
    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID]):
        self.node_id = node_id
        self.neighbors = neighbors
        self.mailbox = Mailbox()

        # Створюємо внутрішній алгоритм
        if ALGORITHM == "awerbuch":
            self.algo = AwerbuchNode(node_id, neighbors)
        elif ALGORITHM == "sidon":
            self.algo = SidonNode(node_id, neighbors)
        else:
            raise Exception("Unknown algorithm")

        self.started = False

    def process_action(self, action: Action) -> NodeResponse:
        new_actions_list = []

        # Старт алгоритму тільки один раз (ініціатор)
        if not self.started:
            self.started = True
            if self.node_id == min(self.neighbors + [self.node_id]):
                print(f"[Node {self.node_id}] Ініціатор стартує алгоритм")
                started_actions = self.algo.start() or []

                for target, msg in started_actions:
                    act = Action(
                        data={"target": target, "message": msg, "sender": self.node_id},
                        node_id=self.node_id,
                        action_id=uuid.uuid4()
                    )
                    self.mailbox.add_inbox_action(act)
                    new_actions_list.append(act)
                    print(f"[Node {self.node_id}] Створено початкове повідомлення до {target}: {msg}")

        # Обробка вхідного Action
        if action is not None:
            sender = action.data.get("sender")
            message = action.data.get("message")

            print(f"[Node {self.node_id}] Прийнято повідомлення від {sender}: {message}")

            generated_actions = self.algo.on_receive(sender, message) or []

            for target, msg in generated_actions:
                act = Action(
                    data={"target": target, "message": msg, "sender": self.node_id},
                    node_id=self.node_id,
                    action_id=uuid.uuid4()
                )
                self.mailbox.add_inbox_action(act)
                new_actions_list.append(act)
                print(f"[Node {self.node_id}] Створено нове повідомлення до {target}: {msg}")

        return NodeResponse(new_actions_list)