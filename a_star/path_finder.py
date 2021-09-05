import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from math import sqrt
from a_star.node import Node
from game_map import GameMap, Cell


class PathFinder:
    def __init__(self, width, height):
        self.mapWidth = width
        self.mapHeight = height
        self.nodes = []
        self.node_start = None
        self.node_end = None
        self.initialize_nodes()


    def initialize_nodes(self):
        self.nodes = []
        # Fill the array
        for y in range(self.mapHeight):
            for x in range(self.mapWidth):
                node = Node()
                node.x = x
                node.y = y
                node.bObstacle = False
                node.bVisited = False
                node.parent = None
                self.nodes.append(node)
        # Create nodes' connections
        for y in range(self.mapHeight):
            for x in range(self.mapWidth):
                # North
                if y > 0:
                    # print("x", x, "y", y)
                    self.nodes[y * self.mapWidth + x].neighbours.append(self.nodes[(y - 1) * self.mapWidth + (x + 0)])
                # South
                if y < self.mapHeight - 1:
                    self.nodes[y * self.mapWidth + x].neighbours.append(self.nodes[(y + 1) * self.mapWidth + (x + 0)])
                # West
                if x > 0:
                    self.nodes[y * self.mapWidth + x].neighbours.append(self.nodes[(y - 0) * self.mapWidth + (x - 1)])
                # East
                if x < self.mapWidth - 1:
                    self.nodes[y * self.mapWidth + x].neighbours.append(self.nodes[(y + 0) * self.mapWidth + (x + 1)])


    def set_start_end(self, start_pos, end_pos):
        self.node_start = self.nodes[start_pos[1] * self.mapWidth + start_pos[0]]
        self.node_end = self.nodes[end_pos[1] * self.mapWidth + end_pos[0]]


    def set_obstacle(self, obstacle_pos):
        self.nodes[obstacle_pos[1] * self.mapWidth + obstacle_pos[0]].bObstacle = True 


    def get_shortest_path_node_iterator(self):
        # def yield_from_start(node):
        #     if node != None:
        #         yield_from_start(node.parent)
        #     else:
        #         return
        #     yield node
        # yield_from_start(self.node_end)
        path = []
        node = self.node_end
        while node is not None:
            path.insert(0, node)
            node = node.parent
        return path


    def get_shortest_path_next_node(self):
        node = self.node_end
        while node is not None:
            node = node.parent
        return node


    def solve_astar(self):
        # Clear the array
        for y in range(self.mapHeight):
            for x in range(self.mapWidth):
                self.nodes[y * self.mapWidth + x].bVisited = False
                self.nodes[y * self.mapWidth + x].fGlobalGoal = float('inf')
                self.nodes[y * self.mapWidth + x].fLocalGoal = float('inf')
                self.nodes[y * self.mapWidth + x].parent = None
        
        def distance(node_a, node_b):
            return sqrt((node_a.x - node_b.x)**2 + (node_a.y - node_b.y)**2)

        def distance_manhattan(node_a, node_b):
            return abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)
                
        def heuristic(node_a, node_b):
            return distance_manhattan(node_a, node_b)                

        # Init current node
        node_cur = self.node_start
        self.node_start.fLocalGoal = 0.0
        self.node_start.fGlobalGoal = heuristic(self.node_start, self.node_end)

        nodes_not_tested = []
        nodes_not_tested.append(self.node_start)

        while len(nodes_not_tested) != 0:
            # Sort untested nodes by global goal, so lower is first
            nodes_not_tested = sorted(nodes_not_tested)

            # Front of the list is potentially the lowest distance
            # Our list may also contains nodes that have been visited, so ditch these
            while len(nodes_not_tested) != 0 and nodes_not_tested[0].bVisited:
                nodes_not_tested.pop(0)
            
            # Abort because there are no valid nodes left to test
            if len(nodes_not_tested) == 0:
                break
            
            # Now the node of the front of the list is the best candidate
            node_cur = nodes_not_tested[0]
            node_cur.bVisited = True    # We only explore a node once

            # Iterate on the node's neighbours
            for node_neighbour in node_cur.neighbours:
                # and only if the neighbour is not visited
                # and is not an obstacle, add it to the NotTested list
                if not node_neighbour.bVisited and not node_neighbour.bObstacle:
                    nodes_not_tested.append(node_neighbour)

                # Calculate the neighbours potential lowest parent distance
                fPossibilityLowerGoal = node_cur.fLocalGoal + distance(node_cur, node_neighbour)

                # If choosing to path through this node is a lower distance than what 
                # the neighbour currently has set, update the neighbour to use this node
                # as the path source, and set its distance scores as necessary
                if fPossibilityLowerGoal < node_neighbour.fLocalGoal:
                    node_neighbour.parent = node_cur
                    node_neighbour.fLocalGoal = fPossibilityLowerGoal

                    # The best path length to the neighbour being tested has changed
                    # so update the neighbour's score.
                    # The heuristic is used to globally bias the path algorithm
                    # so it knows if it's getting better or worse.
                    # At some points the algorithm will realize this path is worse and abandon it,
                    # and then go and search along the next best path
                    node_neighbour.fGlobalGoal = node_neighbour.fGlobalGoal + heuristic(node_neighbour, self.node_end)


if __name__ == "__main__":
    print("test")
    path_finder = PathFinder(10, 10)
    start = (0, 0)
    end = (9, 9)
    path_finder.set_start_end(start, end)
    osbtacles = [(0, 1), (1, 1), (2, 3), (3, 3), (4, 2), (5, 1), (6, 0)]
    for obs in osbtacles:
        path_finder.set_obstacle(obs)
    path_finder.solve_astar()
    game = GameMap(10, 10)
    for node in path_finder.get_shortest_path_node_iterator():
        print(node)
        game.setCell((node.x, node.y), Cell.CHARACTER)
    game.setCell(start, Cell.CHARACTER)
    game.setCell(end, Cell.DOWNSTAIRS)
    for obs in osbtacles:
       game.setCell(obs, Cell.WALL) 
    print(game)