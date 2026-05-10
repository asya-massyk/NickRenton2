class SafraNode:
    def __init__(self, node_id, neighbors):
        self.id = node_id
        self.neighbors = neighbors

        self.counter = 0
        self.color = "WHITE"
        self.active = False

        self.next_node = None
        self.is_initiator = False
        self.terminated = False

    def on_send(self):
        self.counter += 1

    def on_basic(self, sender):
        self.counter = max(self.counter - 1, 0)
        self.color = "BLACK"
        self.active = True

        return [
            (n, ("BASIC", None))
            for n in self.neighbors
            if n != sender
        ]

    def on_ack(self, sender):
        return []

    def on_token(self, token):
        if self.terminated:
            return []

        token["counter"] += self.counter

        if self.color == "BLACK":
            token["color"] = "BLACK"

        self.counter = 0
        self.color = "WHITE"
        self.active = False

        if self.is_initiator:
            if token["counter"] == 0 and token["color"] == "WHITE":
                print("\n✅ SAFRA TERMINATED\n")
                self.terminated = True
                return []

        return [(self.next_node, ("TOKEN", token))]