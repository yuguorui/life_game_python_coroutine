from collections import namedtuple
import curses
import time
import copy

Query = namedtuple('Query', ('y', 'x'))
Transition = namedtuple('Transition', ('y', 'x', 'state'))

ALIVE = '*'
EMPTY = '-'

def count_neighbors(y, x):
    dx = [0, 0, 1, -1, 1, -1, 1, -1]
    dy = [1, -1, 0, 0, 1, -1, -1, 1]

    count = 0
    for i in range(8):
        t = yield Query(y + dy[i], x + dx[i])
        if t == ALIVE:
            count += 1
    return count

def game_logic(state, neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY    # too few
        elif neighbors > 3:
            return EMPTY    # too many
    else:
        if neighbors == 3:
            breakpoint
            return ALIVE
    return state

def step_cell(y, x):
    state = yield Query(y, x)
    neighbors = yield from count_neighbors(y, x)
    next_state = game_logic(state, neighbors)
    if next_state != state:
        yield Transition(y, x, next_state)


TICK = object()
def simulate(height, width):
    while True:
        for y in range(height):
            for x in range(width):
                yield from step_cell(y, x)
        yield TICK


class Grid(object):
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []

        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)
    
    def __str__(self):
        return '\n'.join([''.join(x) for x in self.rows])
    
    def query(self, y, x):
        return self.rows[y % self.height][x % self.width]
    
    def assign(self, y, x, state):
        self.rows[y % self.height][x % self.width] = state

    @classmethod
    def from_instance(cls, class_instance):
        obj = copy.deepcopy(class_instance)
        return obj


def live_a_generaton(grid, sim):
    progeny = Grid.from_instance(grid)
    item = next(sim)
    while item is not TICK:
        if isinstance(item, Query):
            state = grid.query(item.y, item.x)
            item = sim.send(state)
        else:   # must be a Transition
            assert isinstance(item, Transition)
            progeny.assign(item.y, item.x, item.state)
            item = next(sim)
    return progeny


def main(stdscr):
    grid = Grid(10, 20)
    grid.assign(0, 3, ALIVE)
    grid.assign(1, 4, ALIVE)
    grid.assign(2, 2, ALIVE)
    grid.assign(2, 3, ALIVE)
    grid.assign(2, 4, ALIVE)

    sim = simulate(grid.height, grid.width)
    stdscr.clear()

    while(True):
        rows = str(grid).split('\n')
        for i, row in enumerate(rows):
            stdscr.addstr(i, 0, row)
        grid = live_a_generaton(grid, sim)
        stdscr.refresh()
        time.sleep(0.5)
        

if __name__ == "__main__":
    curses.wrapper(main)
