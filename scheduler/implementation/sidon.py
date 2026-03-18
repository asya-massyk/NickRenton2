class SidonNode:
    def __init__(self, node_id, neighbors):
        self.id = node_id
        self.neighbors = neighbors
        self.visited_edges = set()
        self.path_history = set()

    def start(self):
        actions = []
        print(f"[Node {self.id}] Start Sidon algorithm. Sending to neighbors...")

        for n in self.neighbors:
            edge = tuple(sorted((self.id, n)))
            self.visited_edges.add(edge)
            print(f"[Node {self.id}] -> sending path [{self.id}] to {n}")
            actions.append((n, (self.id, [self.id])))

        return actions

    def on_receive(self, sender, message):
        actions = []
        origin, path = message

        edge = tuple(sorted((self.id, sender)))

        if edge in self.visited_edges:
            return []

        self.visited_edges.add(edge)
        new_path = path + [self.id]
        signature = tuple(new_path)

        if signature in self.path_history:
            return []

        self.path_history.add(signature)
        print(f"[Node {self.id}] Received path from {sender}: {path} -> new path {new_path}")

        for n in self.neighbors:
            if n != sender:
                next_edge = tuple(sorted((self.id, n)))
                if next_edge not in self.visited_edges:
                    print(f"[Node {self.id}] -> forwarding path {new_path} to {n}")
                    actions.append((n, (origin, new_path)))

        return actions