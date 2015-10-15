from queue import Queue
import time
import pdb 

import itertools # for bidirectional

"""This is where the problem is defined. Initial state, goal state and other information that can be got from the problem"""

class Problem(object):

    def __init__(self, initial, goal=None):
        """This is the constructor for the Problem class. It specifies the initial state, and possibly a goal state, if there is a unique goal.  You can add other arguments if the need arises"""
        self.initial = initial  # Lists of Lists
        
        if goal is not None:
            self.goal = goal
        else: 
            # goal state is the initial state 1st peg on another peg, sort it just in case
            self.goal = sorted(self.initial[0], reverse=True)

        assert(len(initial) == 3)  # Can't have more than 3 pegs
        self.pegs = [i for i in range(0, len(initial))]
        # Get number of disks
        self.numberOfDisks = len(self.initial[0])
        # Make sentinel value
        self.sentinel = self.initial[0][0] + 1

        for peg in self.initial:
            peg.insert(0, self.sentinel)

        self.goal.insert(0, self.sentinel)

        self.visited = dict() #keep visited states

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""

        def check(action):
            """Check to see if we'll end up in a loop by applying the action.
            """
            result = [peg[:] for peg in state]
            value = result[action.src].pop()
            # if value < result[action.dest][-1] or result[action.dest] == self.sentinel:
            #     return True
            result[action.dest].append(value)
            if str(result) in self.visited:
                return False
            return True

        actions = []
        tops = [peg[-1] for peg in state]
        idxSmallest = tops.index(1) #Since smallest(1) is always on top, this will always be true
        moveSmallTo = list(self.pegs) 
        moveSmallTo.remove(idxSmallest) #Empty move if move to itself

        nextSmall = min(tops[moveSmallTo[0]], tops[moveSmallTo[1]])
        idxNextSmall = tops.index(nextSmall)
        for move in moveSmallTo:
            action = Action(idxSmallest, move, 1)
            if check(action):
                actions.append(action)

        if nextSmall is self.sentinel:
            # 1 disk to move only (cannot move sentinel)
            return actions
        else:
            moveSmallTo.remove(idxNextSmall)
            assert(len(moveSmallTo) == 1)
            action = Action(idxNextSmall, moveSmallTo[0], nextSmall)
            if check(action):
                actions.append(action)
            return actions        

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        result = [peg[:] for peg in state]   # Make a copy - fixed
        value = result[action.src].pop()
        assert(value == action.value)
        if value is self.sentinel:
            raise(ValueError,"Attempted to Move Sentinel Value")
        result[action.dest].append(value)
        # print(action, end=" ")
        # print(result)
        return result

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal, as specified in the constructor. Override this
        method if checking against a single self.goal is not enough.
        This must be written by students"""
        # if state == self.initial:
        #     raise(ValueError, "Back to Square 1")
        # if state ==  [[4], [4], [4, 3, 2, 1]]:
        #     pdb.set_trace()
        if state[0][-1] != self.sentinel:
            return False
        if state[1] == self.goal or state[2] == self.goal:
            return True
        return False

"""Similar Problem to the original class, but handles which side to arrange disks to."""
"""Inherits from Problem other than Action and Goal Test"""
class BiDirectionalProblem(Problem):

    def __init__(self, initial, goal=None):
        """This is the constructor for the Problem class. It specifies the initial state, and possibly a goal state, if there is a unique goal.  You can add other arguments if the need arises"""
        super().__init__(initial)

        if goal is not None:
            self.goal = goal
        else: 
        #    # goal state is the initial state 1st peg on another peg, sort it just in case
             self.goal = [peg[:] for peg in self.initial]
             self.goal.reverse() # in place hence the copy

        self.StartVisited = dict()
        self.GoalVisited = dict()
#        self.visited = dict() #keep visited states

    def actions(self, state, fromStart):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""

        """FromEnd is a boolean that will perform a separate action if starting from the end
        Exact code other than use of fromState routines. 
        Makes code more efficient without having to check for fromStart existence even on BFS.
        """

        def check(action):
            """Check to see if we'll end up in a loop by applying the action.
            """
            result = [peg[:] for peg in state]
            value = result[action.src].pop()
            # if value < result[action.dest][-1] or result[action.dest] == self.sentinel:
            #     return True
            result[action.dest].append(value)
            if fromStart:
                if self.StartVisited.get(str(result), None) is not None:
                    return False
            else:
                if self.GoalVisited.get(str(result), None) is not None:
                    return False
            return True

        actions = []
        tops = [peg[-1] for peg in state]
        idxSmallest = tops.index(1) #Since smallest(1) is always on top, this will always be true
        moveSmallTo = list(self.pegs) 
        moveSmallTo.remove(idxSmallest) #Empty move if move to itself

        nextSmall = min(tops[moveSmallTo[0]], tops[moveSmallTo[1]])
        idxNextSmall = tops.index(nextSmall)
        for move in moveSmallTo:
            action = Action(idxSmallest, move, 1)
            if check(action):
                actions.append(action)

        if nextSmall is self.sentinel:
            # 1 disk to move only (cannot move sentinel)
            return actions
        else:
            moveSmallTo.remove(idxNextSmall)
            assert(len(moveSmallTo) == 1)
            action = Action(idxNextSmall, moveSmallTo[0], nextSmall)
            if check(action):
                actions.append(action)
            return actions

class Action:
    def __init__(self, src, dest, value):
        self.src = src
        self.dest = dest
        self.value = value # TODO: Can also remove this one dev is stable.

    def __str__(self):
        return "Move " + str(self.value) + " from peg " + str(self.src) + " to peg " + str(self.dest)

    def __cmp__(self, other): # not used
        return (self.src == other.src) and (self.dest == other.dest) and (self.value and other.value)


class Node:

    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state"""

    def __init__(self, state, parent=None, action=None):
        """Create a search tree Node, derived from a parent by an action.
        Update the node parameters based on constructor values"""
        # update(self, state=state, parent=parent, action=action, depth=0)
        # If depth is specified then depth of node will be 1 more than the
        # depth of parent
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def expand(self, problem, fromStart=None):
        # List the nodes reachable in one step from this node.
        if fromStart is None:
            return [self.child_node(problem, action)
                    for action in problem.actions(self.state)]
        else:
            return [self.child_node(problem, action)
                    for action in problem.actions(self.state, fromStart)]

    def child_node(self, problem, action):
        next = problem.result(self.state, action)
        # print("Depth ", self.depth)
        return Node(next, self, action)


def breadth_first_search(problem):
    # Start from first node of the problem Tree
    node = Node(problem.initial)
    # Check if current node meets Goal_Test criteria
    if problem.goal_test(node.state):
        return node
    # Create a Queue to store all nodes of a particular level.
    frontier = Queue()
    frontier.put(node)

    # Loop until all nodes are explored(frontier queue is empty) or Goal_Test
    # criteria are met
    while not frontier.empty():
        # Remove from frontier, for analysis
        node = frontier.get()
        # Loop over all children of the current node
        # Note: We consider the fact that a node can have multiple child nodes
        # here
        problem.visited[str(node.state)] = 1 # add to visited nodes
        for child in node.expand(problem):
            # If child node meets Goal_Test criteria
            if problem.goal_test(child.state):
                return child
            # Add every new child to the frontier
            frontier.put(child)
    return None


"""
- What to return for bidirectional? Since we have to stitch, can get lowest node first, then stitch
-- nodeFromEnd.parent recurse to get 'lowest'
-- pointer to nodeFromStart
-- pointer to hold the next node from nodeFromEnd (next = nodeFromEnd.parent)
-- current node flips it's parent to point to (pointer of nodeFromStart)
-- set pointer of nodeFromStart to this node.

- Having a node from start and another from end to check frontier from each side, 
    isn't this bad. 
- Do we need 2 visited dictionaries? doesn't seem like it?? test 
- Memory profiler? guppy? or pympler? 
"""

def bidirectional_BFS(problem): # where problem is biDirectionalProblem instance 
    startNode = Node(problem.initial)
    goalNode = Node(problem.goal)

    if startNode.state == goalNode.state:
        raise(ValueError,"SOLN NODES FOUND ON FIRST")

    frontierFromStart = []
    frontierFromGoal = []

    frontierFromStart.append(startNode)
    frontierFromGoal.append(goalNode)

    while frontierFromStart and frontierFromGoal: # Both must not be empty
        nodeFromStart = frontierFromStart.pop(0)
        nodeFromGoal = frontierFromGoal.pop(0)

        # print("Node from start ", nodeFromStart.state, end="")
        # print(" Node from goal ", nodeFromGoal.state)

        #Hold references so we can grab it out in O(1)
        problem.StartVisited[str(nodeFromStart.state)] = nodeFromStart
        problem.GoalVisited[str(nodeFromGoal.state)] = nodeFromGoal

        listFromStart = nodeFromStart.expand(problem, True)
        listFromGoal = nodeFromGoal.expand(problem, False)

        for childFromStart in listFromStart:
            # See if they are at same level
            for childFromGoal in listFromGoal:
                if childFromStart.state == childFromGoal.state:
                    raise(ValueError, "SOLN NODE FOUND ON SAME LEVEL")

                for node in frontierFromStart: # Happens more
                    if childFromGoal.state ==  node.state:
                        raise(ValueError, "GoalNode found in start frontier")

                for node in frontierFromGoal:
                    if childFromStart.state == node.state:
                        return childFromStart
                        raise(ValueError, "StartNode found in goal frontier")

            if problem.GoalVisited.get(str(childFromStart.state), None) is not None:
                raise(ValueError, "FOUND")
        frontierFromStart += listFromStart
        frontierFromGoal += listFromGoal

    return None


class Hanoi:
    """Hanoi object based on number of disks. Makes Problem object with a list of lists"""
    def __init__(self,numberOfDisks):
        self.problem = Problem([ [i for i in range(numberOfDisks, 0, -1)], list(), list() ])
        self.minSteps = 2**numberOfDisks - 1
        self.sentinel = numberOfDisks + 1
        self.numberOfDisks = numberOfDisks
        self.solnNode = None

    def stripSentinel(self, board):
        return [[i for i in peg 
                    if i != self.sentinel] 
                    for peg in board]

    def printHanoi(self, board, strip=False):
        if strip: 
            board = self.stripSentinel(board)
        for peg in board:
            print(peg, end=" ")
        if self.sentinel in peg:
            print("","Sentinel Value:", self.sentinel)
        else:
            print("")

    def printProblem(self):
        self.printHanoi(self.problem.initial, True)

    def solveProblemBFS(self):
        print('Solving Hanoi Puzzle with ', self.numberOfDisks, ' disks.')
        self.solnNode = breadth_first_search(self.problem)
        if self.solnNode is not None:
            print("Solving Complete")
        else:
            raise(ValueError, "Solution Not Found")

    def printSolution(self):
        self.printHanoi(self.solnNode.state, True)

    
def runTests():
    # print("START BFS SOLVE")
    # t = time.process_time()
    # x = Hanoi(8)
    # x.printProblem()
    # x.solveProblemBFS()
    # # x.printSolution()
    # print("\nElapsed time for soln: ", time.process_time() - t)
    # print("COMPLETE BFS")

    print("START BDP Solve")
    t = time.process_time()
    y = BiDirectionalProblem([[8,7,6,5,4,3,2,1],[],[]])
    z = bidirectional_BFS(y)
    print("\nElapsed time for soln: ", time.process_time() - t)

if(__name__ == '__main__'):
    runTests()