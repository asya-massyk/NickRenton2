from typing import List
from scheduler.core.action import Action


class Mailbox:
    def __init__(self):
        self.inbox: List[Action] = []

    def add_inbox_action(self, action: Action):
        self.inbox.append(action)

    def pop(self):
        return self.inbox.pop(0) if self.inbox else None