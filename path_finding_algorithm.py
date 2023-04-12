import pygame
from queue import PriorityQueue
from Colors import color

pygame.init()

class Grid:
    WIDTH = 800
    ROWS = 50
    
    def __init__(self):
        self.grid_width = self.WIDTH // self.ROWS
        self.grid = self.gen_grid()

    def gen_grid(self):
        grid = []
        for i in range(self.ROWS):
            grid.append([])
            for j in range(self.ROWS):
                grid[i].append(Node(i * self.grid_width, j * self.grid_width, i, j))
        
        for i in range(self.ROWS):
            grid[0][i].make_wall()
            grid[self.ROWS-1][i].make_wall()
            grid[i][0].make_wall()
            grid[i][self.ROWS-1].make_wall()
        
        return grid

    def update_grid(self):
        for row in self.grid:
            for node in row:
                node.update(self)
    
    def draw(self, window):
        window.fill(color.WHITE)
        # drawing all the nodes
        for col in self.grid:
            for node in col:
                node.draw(window)

        # vertical grid lines
        for i in range(self.ROWS): 
            pygame.draw.line(window, color.BLACK, (i * self.grid_width, 0), (i * self.grid_width, self.WIDTH), 3)
        # horizontal grid lines
        for i in range(self.ROWS):
            pygame.draw.line(window, color.BLACK, (0, i * self.grid_width), (self.WIDTH, i * self.grid_width), 3)
    
        pygame.display.update()
    

class Node:

    def __init__(self, x, y, row, col):
        self.neighbors = []
        self.color = color.WHITE
        self.width = Grid.WIDTH // Grid.ROWS
        self.x = x
        self.y = y
        self.row = row 
        self.col = col

    # getter methods:
    def is_closed(self):
        return self.color == color.RED
    
    def is_wall(self):
        return self.color == color.BLACK
    
    def is_goal(self):
        return self.color == color.GREEN
    
    def is_start(self):
        return self.color == color.BLUE

    # setter methods
    def reset(self):
        self.color = color.WHITE

    def open(self):
        self.color = color.YELLOW

    def close(self):
        self.color = color.RED
    
    def make_start(self):
        self.color = color.BLUE
    
    def make_goal(self):
        self.color = color.GREEN
    
    def make_path(self):
        self.color = color.VIOLET
    
    def make_wall(self):
        self.color = color.BLACK

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    def update(self, grid):
        self.neighbors = []
        
        if self.row < grid.ROWS - 1:
            node = grid.grid[self.row + 1][self.col] # neighbor to the right
            if not node.is_wall():
                self.neighbors.append((1, node)) #distance is 1
            
            if self.col < grid.ROWS - 1:
                node = grid.grid[self.row + 1][self.col + 1] #neighbor bottom right
                if not node.is_wall():
                    self.neighbors.append((1.4, node)) #distance is approx sqrt(1 + 1) because diagonal

            if self.col > 0:
                node = grid.grid[self.row + 1][self.col - 1] #neighbor top right
                if not node.is_wall():
                    self.neighbors.append((1.4, node))

        if self.row > 0:
            node = grid.grid[self.row - 1][self.col] # neighbor to the left
            if not node.is_wall():
                self.neighbors.append((1, node))

            if self.col < grid.ROWS - 1:
                node = grid.grid[self.row - 1][self.col + 1] #neighbor bottom left
                if not node.is_wall():
                    self.neighbors.append((1.4, node))
            
            if self.col > 0:
                node = grid.grid[self.row - 1][self.col - 1] #neighbor top left
                if not node.is_wall():
                    self.neighbors.append((1.4, node))

        if self.col > 0:
            node = grid.grid[self.row][self.col - 1] # top neighbor
            if not node.is_wall():
                self.neighbors.append((1, node))

        if self.col < grid.ROWS - 1:
            node = grid.grid[self.row][self.col + 1] # bottom neighbor
            if not node.is_wall():
                self.neighbors.append((1, node))



def h_score(current, goal):
    return abs(goal.row - current.row) + abs(goal.col - current.col)

        
def algorithm(draw, start, goal, grid):
    count = 0
    open_set = PriorityQueue()
    open_set_hash = {start}
    came_from = {}
    g_scores = {node: float("inf") for row in grid.grid for node in row}
    f_scores = {node: float("inf") for row in grid.grid for node in row}
    g_scores[start] = 0
    f_scores[start] = h_score(start, goal)

    open_set.put((0, count, start))
    open_set_hash.add(start)

    while not open_set.empty():

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] # gets the node in the queue which has the smallest f score
        open_set_hash.remove(current)

        if current == goal:
            # recreating the path
            while current in came_from:
                current = came_from[current]
                current.make_path()
                draw()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_scores[current] + neighbor[0] # distance (1 or 1.4 depending on straight or diagonal)
            neighbor = neighbor[1]
            
            if temp_g_score < g_scores[neighbor]:
                came_from[neighbor] = current
                g_scores[neighbor] = temp_g_score
                f_scores[neighbor] = temp_g_score + h_score(neighbor, goal)
                if neighbor not in open_set_hash:
                    count += 1
                    open_set_hash.add(neighbor)
                    open_set.put((f_scores[neighbor], count, neighbor))
                    neighbor.open()

        if current != start: 
            current.close()

        draw()

    print("there is no path")
    return False # not path found


    
def main():
    window = pygame.display.set_mode( (Grid.WIDTH, Grid.WIDTH) )
    pygame.display.set_caption("PATHFINDING ALGORITHM VISUALISATION")

    run = True

    grid = Grid()
    start = False
    goal = False
    started = False

    while run:
        grid.draw(window)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if not started: #set up of maze
                if pygame.mouse.get_pressed()[0]: # left click
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_col = int(Grid.ROWS * mouse_pos[0] / Grid.WIDTH)
                    mouse_row = int(Grid.ROWS * mouse_pos[1] / Grid.WIDTH)
                    node = grid.grid[mouse_col][mouse_row]

                    if not start and not node.is_wall(): #there isnt a start yet and we have not clicked a wall
                        node.make_start()
                        start = node

                    elif not goal and not node.is_start() and not node.is_wall(): #there is not yet a goal and we have not clicked a wall
                        node.make_goal()
                        goal = node
                    elif not node.is_start() and not node.is_goal(): # if we have a start and goal
                        node.make_wall()
                    
                if pygame.mouse.get_pressed()[2]: # right click
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_col = int(Grid.ROWS * mouse_pos[0] / Grid.WIDTH)
                    mouse_row = int(Grid.ROWS * mouse_pos[1] / Grid.WIDTH)
                    node = grid.grid[mouse_col][mouse_row]

                    node.reset() #leftclick resets the node
                    if node == start:
                        start = None
                    elif node == goal:
                        goal = None

                if start and goal:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            grid.update_grid() # setting all the neighbors with the walls in mind
                            started = True
                            if not algorithm(lambda: grid.draw(window), start, goal, grid): #calling pathfinding algorithm
                                run = False
                                break
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # quitting and calling main again makes a new window, which is reset
                    main()
                    break
    
    pygame.quit()

if __name__ == "__main__":
    main()