from typing import List
import random

class game:
    def __init__(self, width: int, height: int, bombs: int):
        self.width = max(4, width) # At least width of 4
        self.height = max(4, height) # At least height of 4
        self.numbombs = min(int(self.width * self.height / 2), max(1, bombs)) # At most, half the squares. At least, 1
        self.truemap: List[List[int]] = [[0 for y in range(height)] for x in range(width)]
        self.visible: List[List[int]] = [[0 for y in range(height)] for x in range(width)]
        self.first = True
    def open(self, x, y) -> bool:
        if x < 0 or self.width <= x or y < 0 or self.height <= y: # Ensure we are within the grid.
            raise IndexError(f"Tile ({x}, {y}) is invalid for a grid of size ({self.width}, {self.height}).")
        if self.first:
            # On the first one, we generate the map so this tile must be clear.
            bombstoplant = self.numbombs
            while bombstoplant > 0:
                rx = random.randint(0, self.width - 1)
                ry = random.randint(0, self.height - 1)
                if abs(rx - x) <= 1 and abs(ry - y) <= 1:
                    continue # Don't plant a bomb on this first tile or the neighboring ones
                elif self.truemap[rx][ry] == -1:
                    continue # There's already a bomb on this tile
                else:
                    # Set the tile to be the bomb
                    self.truemap[rx][ry] = -1
                    # Increment the neighboring tiles' neighbor count
                    for dx in (rx - 1, rx, rx + 1):
                        if 0 <= dx and dx < self.width: # Ensure we're not over the edge for x
                            for dy in (ry - 1, ry, ry + 1):
                                if 0 <= dy and dy < self.height: # Ensure we're not over the edge for y
                                    if self.truemap[dx][dy] >= 0: # Ensure this isn't a bomb tile
                                        self.truemap[dx][dy] += 1
                    bombstoplant -= 1
            self.first = False
        # Now we do the normal stuff of checking the tile
        tile = self.truemap[x][y]
        self.visible[x][y] = 1
        if tile == -1:
            # You just stepped on a bomb.
            return True
        elif tile == 0:
            # We can recursively open all neighbors since they must be safe.
            for dx in (x - 1, x, x + 1):
                if 0 <= dx and dx < self.width: # Ensure we're not over the edge for x
                    for dy in (y - 1, y, y + 1):
                        if 0 <= dy and dy < self.height: # Ensure we're not over the edge for y
                            if self.visible[dx][dy] != 1: # Ensure the tile is not already opened (otherwise infinite recursion)
                                self.open(dx, dy)
            return False
        else:
            # Just a tile.
            return False
    def flag(self, x, y) -> bool:
        """
        Places or removes a flag on the given tile. 
        
        Returns `True` if it changed the tile, or `False` if already open/game has not started.
        """
        if x < 0 or self.width <= x or y < 0 or self.height <= y: # Ensure we are within the grid.
            raise IndexError(f"Tile ({x}, {y}) is invalid for a grid of size ({self.width}, {self.height}).")
        elif self.first: # Your first move cannot be placing a flag. At least one tile must be opened first.
            return False
        elif self.visible[x][y] == 1: # You cannot place a flag on an opened tile.
            return False
        elif self.visible[x][y] == 0: # Place flag
            self.visible[x][y] = -1
        elif self.visible[y][y] == -1: # Remove flag
            self.visible[x][y] = 0
        else: # This really shouldn't happen.
            raise RuntimeError(f"Tile ({x}, {y}) has an invalid visibility state of {self.visible[x][y]}.")
    def __str__(self) -> str:
        string = f"Mine Sweeper Game ({self.width}x{self.height}; {self.numbombs} bombs)"
        for y in range(self.height):
            string += "\n"
            for x in range(self.width):
                if self.visible[x][y] == -1:
                    string += "F"
                elif self.visible[x][y] == 0:
                    string += "?"
                elif self.visible[x][y] == 1:
                    if self.truemap[x][y] == -1:
                        string += "Q"
                    else:
                        string += str(self.truemap[x][y])
                string += " "
        return string
    def showFull(self) -> str:
        string = f"Mine Sweeper Game ({self.width}x{self.height}; {self.numbombs} bombs)"
        for y in range(self.height):
            string += "\n"
            for x in range(self.width):
                if self.truemap[x][y] == -1:
                    string += "Q"
                else:
                    string += str(self.truemap[x][y])
                string += " "
        return string


g = game(10, 10, 20)
print(g.open(1, 1))
print(g)
print(g.showFull())