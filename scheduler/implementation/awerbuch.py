from enum import Enum

class MsgType(Enum):
    EXPLORE = "EXPLORE"
    ACK = "ACK"


class AwerbuchNode:
    def __init__(self, node_id, neighbors):
        self.id = node_id
        self.neighbors = neighbors

        self.parent = None
        self.visited = False
        self.waiting_ack = set()
        self.children = set()

    def start(self):
        actions = []
        self.visited = True
        self.parent = self.id

        print(f"[Node {self.id}] Start algorithm. Sending EXPLORE to neighbors...")

        for n in self.neighbors:
            print(f"[Node {self.id}] -> EXPLORE to {n}")
            actions.append((n, (MsgType.EXPLORE, self.id)))
            self.waiting_ack.add(n)

        return actions

    def on_receive(self, sender, message):
        actions = []
        msg_type, data = message

        if msg_type == MsgType.EXPLORE:
            if not self.visited:
                self.visited = True
                self.parent = sender
                print(f"[Node {self.id}] Received EXPLORE from {sender}. Mark parent={sender}")

                for n in self.neighbors:
                    if n != sender:
                        print(f"[Node {self.id}] -> EXPLORE to {n}")
                        actions.append((n, (MsgType.EXPLORE, self.id)))
                        self.waiting_ack.add(n)

                if not self.waiting_ack:
                    print(f"[Node {self.id}] No neighbors to wait. Sending ACK to parent {self.parent}")
                    actions.append((self.parent, (MsgType.ACK, self.id)))
            else:
                print(f"[Node {self.id}] Already visited. Sending ACK back to {sender}")
                actions.append((sender, (MsgType.ACK, self.id)))

        elif msg_type == MsgType.ACK:
            if sender in self.waiting_ack:
                self.waiting_ack.remove(sender)
                self.children.add(sender)
                print(f"[Node {self.id}] Received ACK from {sender}. Remaining: {self.waiting_ack}")

            if not self.waiting_ack and self.parent != self.id:
                print(f"[Node {self.id}] All ACKs received. Sending ACK to parent {self.parent}")
                actions.append((self.parent, (MsgType.ACK, self.id)))

        return actions