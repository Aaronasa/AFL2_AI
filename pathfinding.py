import heapq

class Node:
    """
    A node class for A* Pathfinding
    """
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
      return self.f < other.f

    def __repr__(self):
      return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"


def a_star(grid, start, end):
    """
    Returns a list of tuples as a path from the given start to the given end in the given grid
    """
    start_node = Node(None, start)
    end_node = Node(None, end)

    open_list = []
    closed_list = set()

    heapq.heappush(open_list, (start_node.f, start_node))

    while len(open_list) > 0:
        current_node = heapq.heappop(open_list)[1]
        closed_list.add(current_node.position)

        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            if node_position[0] > (len(grid) - 1) or node_position[0] < 0 or node_position[1] > (len(grid[0]) - 1) or node_position[1] < 0:
                continue

            if grid[node_position[0]][node_position[1]] != 0:
                continue
            
            if node_position in closed_list:
                continue

            new_node = Node(current_node, node_position)
            children.append(new_node)

        for child in children:
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            is_in_open_list = False
            for open_node_f, open_node in open_list:
                if child == open_node and child.g >= open_node.g:
                    is_in_open_list = True
                    break
            
            if is_in_open_list:
                continue

            heapq.heappush(open_list, (child.f, child))

    return None