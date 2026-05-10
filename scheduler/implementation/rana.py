class RanaNode:
    def __init__(self, node_id, neighbors):
        self.id = node_id
        self.neighbors = neighbors

        self.parent = None
        self.waiting = set()

    def on_basic(self, sender):
        if self.parent is None:
            self.parent = sender
            self.waiting = set(self.neighbors) - {sender}

            if not self.waiting:
                return [(self.parent, ("ACK", None))]

            return [(n, ("BASIC", None)) for n in self.waiting]

        return [(sender, ("ACK", None))]

    def on_ack(self, sender):
        self.waiting.discard(sender)

        if not self.waiting and self.parent is not None:
            return [(self.parent, ("ACK", None))]

        return []

    def on_token(self, token):
        return []