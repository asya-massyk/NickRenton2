from enum import Enum

class MsgType(Enum):
    EXPLORE = "EXPLORE"
    ECHO = "ECHO"
    LEADER = "LEADER"


class EchoElectionNode:
    def __init__(self, node_id, neighbors):
        self.id = node_id
        self.neighbors = neighbors

        self.parent = None
        self.known_max = node_id

        self.waiting_echo = set()
        self.children = set()

        self.leader = None
        self.election_completed = False

        # 🔥 новий прапорець — щоб не було дублювання
        self.echo_sent = False

    def start(self):
        self.parent = self.id
        self.known_max = self.id

        self.children.clear()
        self.waiting_echo = set(self.neighbors)

        self.leader = None
        self.election_completed = False
        self.echo_sent = False   # 🔥 reset

        actions = []
        print(f"[Node {self.id}] START ELECTION (max ID wins). Sending EXPLORE({self.id}) to all neighbors")

        for n in self.neighbors:
            print(f"[Node {self.id}] → EXPLORE({self.id}) to {n}")
            actions.append((n, (MsgType.EXPLORE, self.id)))

        return actions

    def on_receive(self, sender, message):
        actions = []
        msg_type, data = message

        # =====================
        # EXPLORE
        # =====================
        if msg_type == MsgType.EXPLORE:
            incoming_id = data
            print(f"[Node {self.id}] Received EXPLORE({incoming_id}) from {sender}")

            if incoming_id > self.known_max:
                self.known_max = incoming_id
                self.parent = sender

                self.children.clear()
                self.waiting_echo = set(n for n in self.neighbors if n != sender)

                self.election_completed = False
                self.echo_sent = False   # 🔥 важливо

                print(f"[Node {self.id}] HIGHER ID! New max = {self.known_max}, parent = {sender}")

                if self.waiting_echo:
                    for n in self.waiting_echo:
                        print(f"[Node {self.id}] → EXPLORE({self.known_max}) to {n}")
                        actions.append((n, (MsgType.EXPLORE, self.known_max)))
                else:
                    print(f"[Node {self.id}] Leaf → ECHO({self.known_max}) to {sender}")
                    actions.append((sender, (MsgType.ECHO, self.known_max)))
                    self.echo_sent = True  # 🔥 щоб не повторити

            else:
                print(f"[Node {self.id}] Lower/equal ID → ECHO back")
                actions.append((sender, (MsgType.ECHO, self.known_max)))

        # =====================
        # ECHO
        # =====================
        elif msg_type == MsgType.ECHO:
            subtree_max = data

            if sender in self.waiting_echo:
                self.waiting_echo.remove(sender)
                self.children.add(sender)

                self.known_max = max(self.known_max, subtree_max)

                print(f"[Node {self.id}] ECHO from {sender} (subtree_max={subtree_max}). "
                      f"Waiting left: {len(self.waiting_echo)}. New known_max={self.known_max}")

            # 🔥 ГОЛОВНИЙ ФІКС
            if not self.waiting_echo and not self.echo_sent:
                self.echo_sent = True

                if self.parent != self.id:
                    print(f"[Node {self.id}] All echoes received → sending aggregated max {self.known_max} to parent {self.parent}")
                    actions.append((self.parent, (MsgType.ECHO, self.known_max)))

                else:
                    if not self.election_completed and self.known_max == self.id:
                        self.election_completed = True
                        self.leader = self.known_max

                        print(f"\n[Node {self.id}] ELECTION COMPLETE! Global Leader = {self.leader}")

                        for child in self.children:
                            print(f"[Node {self.id}] → LEADER {self.leader} to child {child}")
                            actions.append((child, (MsgType.LEADER, self.leader)))

        # =====================
        # LEADER
        # =====================
        elif msg_type == MsgType.LEADER:
            if self.leader != data:
                self.leader = data

                print(f"[Node {self.id}] Received LEADER = {self.leader}. Forwarding to children...")

                for child in self.children:
                    print(f"[Node {self.id}] → LEADER {self.leader} to {child}")
                    actions.append((child, (MsgType.LEADER, self.leader)))

        return actions