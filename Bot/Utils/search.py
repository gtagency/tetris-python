

def orderChildren(piecePositions):
    #need to ensure that the up state is returned first if applicable

def dfs (piecePositions, goalPositions):
    if piecePositions == goalPositions:
        return piecePositions
    horizon = []
    closed = []
    currentPosition = (piecePositions, [])
    while (currentPosition != goalPositions):
        if currentPosition[0] not in closed:
            children = orderChildren(currentPosition)
            for i in children:
                if i[0] == goalPositions:
                    return i
                if i[0] not in closed:
                    horizon.append(i)
            closed.append(currentPosition[0])
        if len(horizon) == 0:
            return False
        currentPosition = horizon.pop()


def aStarSearch(game, heuristic):
    path_map = {}
    state_map = {}
    queue = PriorityQueue()
    visited = set()
    state = (game.piece, game.piecePosition)
    queue.push((state,None,None,0), 1)
    while not(queue.isEmpty()):
        state,action,parent,cost = queue.pop()
        if state not in visited:
            visited.add(state)
            path_map[state] = action
            state_map[state] = parent
            for successor in :
                if successor[0] not in visited:
                    queue.push((successor[0],successor[1],state,cost + successor[2]), cost + successor[2] + heuristic(successor[0],problem))
    path = []
    if problem.isGoalState(state):
        while state != problem.getStartState():
            path.insert(0, path_map[state])
            state = state_map[state]
    return path

class PriorityQueue:
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        # entry = (priority, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        #  (_, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

def depthFirstSearch(game):
    path_map = {}
    state_map = {}
    stack =
    visited = set()
    state = problem.getStartState()
    stack.push(problem.getStartState())
    while not(stack.isEmpty()):
        state = stack.pop()
        if problem.isGoalState(state):
            break
        if state not in visited:
            visited.add(state)
            for successor in problem.getSuccessors(state):
                if successor[0] not in visited:
                    stack.push(successor[0])
                    path_map[successor[0]] = successor[1]
                    state_map[successor[0]] = state
    path = []
    if problem.isGoalState(state):
        while state != problem.getStartState():
            path.insert(0, path_map[state])
            state = state_map[state]
    return path

class Stack:
    "A container with a last-in-first-out (LIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Push 'item' onto the stack"
        self.list.append(item)

    def pop(self):
        "Pop the most recently pushed item from the stack"
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the stack is empty"
        return len(self.list) == 0