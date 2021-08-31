class Node:
    def __init__(self):
        self.bObstacle = False
        self.bVisited = False
        self.fGlobalGoal = 0
        self.fLocalGoal = 0
        self.x = 0
        self.y = 0
        self.neighbours = []
        self.parent = None
    
    
    def __eq__(self, o):
        if o is None:
            return False
        if self is o:
            return True
        return self.fGlobalGoal == o.fGlobalGoal

    
    def __lt__(self, o: object) -> bool:
        return self.fGlobalGoal < o.fGlobalGoal


    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"