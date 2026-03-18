from time import sleep
from random import choice
from scheduler.core.action import Action
from scheduler.settings.network_settings import settings


class Observer:
    def __init__(self, network):
        self.network = network
        self.nodes = {node.node_id: node for node in network.nodes}

    def process_action(self, action: Action):
        print(f"Processing Action: {action}")
        response = self.nodes[action.node_id].process_action(action)

        for incoming_action in response.actions:
            self.nodes[incoming_action.node_id].mailbox.add_inbox_action(incoming_action)
            print(f"--> New message for node {incoming_action.node_id}: {incoming_action.data}")

        # прибираємо оброблену дію
        self.nodes[action.node_id].mailbox.remove_action(action)

    def run(self):
        while True:
            # збираємо всі доступні дії
            actions = [a for node in self.network.nodes for a in node.mailbox.get_actions()]
            if actions:
                action = choice(actions)
                self.process_action(action)
            else:
                print("No available action found")
            sleep(settings.ACTION_SLEEP_TIME_SECONDS)