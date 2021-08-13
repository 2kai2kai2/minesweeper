import tkinter
from typing import List, Optional
import minesweepergame

board = minesweepergame.game(10, 10, 10)

top = tkinter.Tk()
top.title("Minesweeper")

canvas = tkinter.Canvas(top, bd=0, bg="grey")


canvasids: List[List[Optional[int]]] = [[None for y in range(
    board.height)] for x in range(board.width)]  # Store the `_CanvasItemId`s

boxwidth = canvas.winfo_reqwidth()/board.width
boxheight = canvas.winfo_reqheight()/board.height
for x in range(board.width):
    for y in range(board.height):
        canvas.create_rectangle(
            boxwidth*x, boxheight*y, boxwidth*(x+1), boxheight*(y+1), outline="black", width=2)


def button1(event: tkinter.Event):
    x = int(event.x/boxwidth)
    y = int(event.y/boxheight)
    # We can't open the tile if it's flagged or already open.
    if board.visible[x][y] == 0:
        opened = board.open(x, y)
        if opened is None:
            # We stepped on a bomb
            pass
        else:
            # Tile is safe.
            for _x, _y in opened:
                canvasids[_x][_y] = canvas.create_text(
                    boxwidth*(_x + 0.5), boxheight*(_y + 0.5), text=board.getVisible(_x, _y), justify="center")
        print(board)


def button2(event: tkinter.Event):
    x = int(event.x/boxwidth)
    y = int(event.y/boxheight)
    if board.flag(x, y):  # Try to change the flag
        # If something changed, draw or remove the flag.
        if board.visible[x][y] == -1:  # Draw a flag
            canvasids[x][y] = canvas.create_text(
                boxwidth*(x + 0.5), boxheight*(y + 0.5), text="F", justify="center")
        else:
            canvas.delete(canvasids[x][y])
            canvasids[x][y] = None


canvas.bind("<Button-1>", button1)  # Left-click
canvas.bind("<Button-3>", button2)  # Right-click
canvas.pack()

top.mainloop()
