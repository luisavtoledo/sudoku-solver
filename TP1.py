from queue import Queue
from queue import LifoQueue
import sys
import time
import heapq

class Node:

    def __init__(self, state, parent=None, cost=0):

        self.state = state
        self.parent = parent
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost

    def expand(self):

        children = []
        size = len(self.state)
        aux = 0

        for i in range(size):
            for j in range(size):
                if self.state[i][j] == 0:
                    aux = 1
                    for n in range(1, 10):
                        if valid_play(self.state, i, j, n) == 0:
                            child_state = [row[:] for row in self.state]
                            child_state[i][j] = n
                            child = Node(child_state, parent=self, cost=self.cost+1)
                            children.append(child)
                    break
            if aux == 1:
                break
        return children
    
    def goal_test(self):

        for row in self.state:
            if sorted(row) != list(range(1, 10)):
                return 1
            
        for col in range(0, 9):
            if sorted([self.state[row][col] for row in range(0, 9)]) != list(range(1, 10)):
                return 1
            
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                square = [self.state[x][y] for x in range(i, i+3) for y in range(j, j+3)]
                if sorted(square) != list(range(1, 10)):
                    return 1
                
        return 0
    
#verifica se colocar n no espaço específico é uma jogada válida
def valid_play(state, row, col, n):

    for i in range(len(state)):
        if state[row][i] == n or state[i][col] == n:
            return 1
    
    square_row = row - (row % 3)
    square_col = col - (col % 3)

    for i in range(square_row, square_row + 3):
        for j in range(square_col, square_col + 3):
            if state[i][j] == n:
                return 1
            
    return 0

def bfs(initial_node):

    frontier = Queue()
    frontier.put(initial_node)
    explored = set()

    if initial_node.goal_test() == 0:
        return 0, initial_node.state
    
    while not frontier.empty():
        node = frontier.get()
        explored.add(node)

        children = node.expand()
        for child in children:
            if child not in frontier.queue and child not in explored:
                if child.goal_test() == 0:
                    return len(explored), child.state
                frontier.put(child)
        
    return 0

def dls(initial_node, depth):

    frontier = LifoQueue()
    frontier.put(initial_node)
    explored = set()
    result = 'failure'

    while not frontier.empty():
        node = frontier.get()

        if node.goal_test() == 0:
            return len(explored), node.state
        
        explored.add(node)

        if node.cost > depth:
            result = 'cutoff'

        else:
            children = node.expand()
            for child in children:
                frontier.put(child)

    return len(explored), result

def ids(initial_node):

    depth = 0

    while(1):
        expanded, solution = dls(initial_node, depth)
        if solution != 'cutoff' and solution != 'failure':
            return expanded, solution
        depth += 1

def ucs(initial_node):

    frontier = []
    heapq.heappush(frontier, (0, initial_node))
    explored = set()

    while frontier:
        cost, node = heapq.heappop(frontier)

        if node.goal_test() == 0:
            return len(explored), node.state
        
        explored.add(node)

        children = node.expand()
        for child in children:
            if child not in explored and child not in frontier:
                heapq.heappush(frontier, (cost + 1, child))

    return 'failure'

#heurística 1: quantidade de espaços em branco
def blank_spaces(state):
    return sum(row.count(0) for row in state)

#heurística 2: relaxacao do problema onde olhamos só as linhas, quantidade de valores possíveis
def unique_values(state):
    count = 0
    for row in state:
        empty = [cell for cell in row if cell == 0]
        values = set(range(1, 10)) - set(row)
        count += len(empty) * len(values)
    
    return count

#greedy
def greedy(initial_node):

    frontier = []
    heapq.heappush(frontier, (0, initial_node))
    explored = set()

    while frontier:
        _, node = heapq.heappop(frontier)

        if node.goal_test() == 0:
            return len(explored), node.state
        
        explored.add(node)

        children = node.expand()
        for child in children:
            if child not in explored and child not in frontier:
                heapq.heappush(frontier, (unique_values(child.state), child))

    return 'failure'

#a_star
def a_star(initial_node):

    g = 0
    h = blank_spaces(initial_node.state)
    f = g + h

    count = 0
    open = []
    heapq.heappush(open, (f, count, initial_node))
    closed = set() 

    while open:
        _, _, node = heapq.heappop(open)

        if node.goal_test() == 0:
            return len(closed), node.state
    
        closed.add(node)

        children = node.expand()
        count -= 1
        for child in children:
            if child not in closed:
                if child not in open:
                    g += 1
                    h -= 1
                    heapq.heappush(open, (f, count, child))

    return 'failure'

def parse_input():

    algorithm = sys.argv[1]
    sudoku_lines = sys.argv[2:]

    initial_state = []
    for line in sudoku_lines:
        row = []
        for n in line:
            row.append(int(n))
        initial_state.append(row)

    return algorithm, initial_state

def run_algorithm(algorithm, initial_state):

    initial_node = Node(initial_state, None, 0)

    if algorithm == 'B':
        num_expanded, solution = bfs(initial_node)

    elif algorithm == 'I':
        num_expanded, solution = ids(initial_node)

    elif algorithm == 'U':
        num_expanded, solution = ucs(initial_node)

    elif algorithm == 'A':
        num_expanded, solution = a_star(initial_node)

    elif algorithm == 'G':
        num_expanded, solution = greedy(initial_node)

    return num_expanded, solution

def main():

    algorithm, initial_state = parse_input()
    start = time.time()
    num_expanded, solution = run_algorithm(algorithm, initial_state)
    end = time.time()

    execution_time = (end - start) * 1000

    print(f"{num_expanded} {execution_time:.0f}")
    for line in solution:
        print(" ".join(map(str, line)), end="   ")
    print()

main()