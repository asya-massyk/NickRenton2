class SidonNode:
    def __init__(self, node_id, neighbors):
        self.id = node_id
        self.neighbors = neighbors
        self.parent = None
        self.expected_echo = set()          # від кого чекаємо echo
        self.received_echo = set()
        self.visited = False

    def start(self):
        actions = []
        print(f"[Node {self.id}] Start Sidon algorithm. Sending to neighbors...")

        self.visited = True
        for n in self.neighbors:
            print(f"[Node {self.id}] -> sending token to {n}")
            actions.append((n, ("token", [self.id])))  

        self.expected_echo = set(self.neighbors)   # чекаємо echo від усіх сусідів

        return actions

    def on_receive(self, sender, message):
        actions = []

        msg_type, path = message if isinstance(message, tuple) else (message, [])

        if msg_type == "token":
            if self.visited:
                # вже відвідали → одразу echo назад
                print(f"[Node {self.id}] Already visited. Sending echo back to {sender}")
                actions.append((sender, ("echo", None)))
                return actions

            # перший раз
            self.visited = True
            self.parent = sender
            print(f"[Node {self.id}] Received token from {sender}. Parent = {sender}")

            new_path = path + [self.id]

            # надсилаємо далі всім крім parent
            for n in self.neighbors:
                if n != sender:
                    print(f"[Node {self.id}] -> forwarding token to {n}")
                    actions.append((n, ("token", new_path)))
                    self.expected_echo.add(n)

            # якщо немає дітей → одразу echo назад
            if not self.expected_echo:
                print(f"[Node {self.id}] Leaf node. Sending echo back to parent {self.parent}")
                actions.append((self.parent, ("echo", None)))

        elif msg_type == "echo":
            print(f"[Node {self.id}] Received echo from {sender}")
            self.received_echo.add(sender)

            if sender in self.expected_echo:
                self.expected_echo.remove(sender)

            if not self.expected_echo and self.parent is not None:
                # всі echo отримані → відправляємо echo батькові
                print(f"[Node {self.id}] All echoes received. Sending echo to parent {self.parent}")
                actions.append((self.parent, ("echo", None)))

        return actions