from typing import List
from scheduler.core.action import Action


class Mailbox:
    def __init__(self):
        self.inbox: List[Action] = []
        self.outbox: List[Action] = []

    def add_inbox_action(self, action: Action):
        action.action_type = "inbox"
        self.inbox.append(action)

    def add_outbox_action(self, action: Action):
        action.action_type = "outbox"
        self.outbox.append(action)

    def get_actions(self):
        return self.inbox[:] + self.outbox[:]

    def remove_action(self, action: Action):
        if action.action_type == "inbox" and action in self.inbox:
            self.inbox.remove(action)
        elif action.action_type == "outbox" and action in self.outbox:
            self.outbox.remove(action)