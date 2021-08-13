import tkinter
from typing import Dict, List, Optional, Tuple
import minesweepergame

board = minesweepergame.game(10, 10, 10)

top = tkinter.Tk()
top.title("Minesweeper")
top.configure(bd=0, bg="black")

canvas = tkinter.Canvas(top, bd=0, bg="light grey")

canvassquares: List[List[Optional[int]]] = [[None for y in range(
    board.height)] for x in range(board.width)]  # Store the `_CanvasItemId`s
canvasicons: List[List[Optional[int]]] = [[None for y in range(
    board.height)] for x in range(board.width)]  # Store the `_CanvasItemId`s


def drawIcon(symbol: str, x: int, y: int, tilewidth: int = None, tileheight: int = None):
    """
    Draw an icon for the given visible symbol in a given tile.
    This does NOT delete previous icons.

    `x` and `y` represent the tile number (not pixels) starting from (0, 0) at the top left.

    `tilewidth` and `tileheight` are optional parameters that may be given if the pixel size of tiles is already calculated. If `None` (default), they will automatically be calculated.
    """
    if tilewidth is None:
        tilewidth = canvas.winfo_reqwidth()/board.width
    if tileheight is None:
        tileheight = canvas.winfo_reqheight()/board.height

    if symbol == "?":  # Blank tiles are not drawn.
        return
    elif symbol == "F":  # Flagged tiles. TODO: Should eventually have an image.
        canvasicons[x][y] = canvas.create_text(
            tilewidth*(x + 0.5), tileheight*(y + 0.5), text="F", justify="center")
    elif symbol == "Q":
        pass
    else:  # Number tiles
        colors: Dict[str, str] = {
            "0": "grey",
            "1": "blue",
            "2": "green",
            "3": "red",
            "4": "navy",
            "5": "red4",
            "6": "cyan3",
            "7": "black",
            "8": "slate grey"
        }
        canvasicons[x][y] = canvas.create_text(
            tilewidth*(x + 0.5), tileheight*(y + 0.5), text=symbol, justify="center", fill=colors[symbol])


def render():
    boxwidth = canvas.winfo_reqwidth()/board.width
    boxheight = canvas.winfo_reqheight()/board.height
    for x in range(board.width):
        canvas.delete(*filter(lambda i: i is not None, canvassquares[x]))
        canvas.delete(*filter(lambda i: i is not None, canvasicons[x]))
        canvasicons[x] = [None for y in range(board.height)]
        for y in range(board.height):
            canvassquares[x][y] = canvas.create_rectangle(
                boxwidth*x, boxheight*y, boxwidth*(x+1), boxheight*(y+1), outline="black", width=1)
            drawIcon(board.getVisible(x, y), x, y, boxwidth, boxheight)


def button1(event: tkinter.Event):
    boxwidth = canvas.winfo_reqwidth()/board.width
    boxheight = canvas.winfo_reqheight()/board.height
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
                drawIcon(board.getVisible(_x, _y), _x, _y, boxwidth, boxheight)


def button2(event: tkinter.Event):
    boxwidth = canvas.winfo_reqwidth()/board.width
    boxheight = canvas.winfo_reqheight()/board.height
    x = int(event.x/boxwidth)
    y = int(event.y/boxheight)
    if board.flag(x, y):  # Try to change the flag
        # If something changed, draw or remove the flag.
        if board.visible[x][y] == -1:  # Draw a flag
            drawIcon("F", x, y, boxwidth, boxheight)
        else:
            canvas.delete(canvasicons[x][y])
            canvasicons[x][y] = None


canvas.bind("<Button-1>", button1)  # Left-click
canvas.bind("<Button-3>", button2)  # Right-click
canvas.pack()


def canvasResize(width: int, height: int):
    boardaspectratio: float = board.height / board.width  # y/x
    canvasaspectratio: float = height / width  # y/x
    if boardaspectratio <= canvasaspectratio:
        canvaswidth = width
        canvasheight = boardaspectratio * width
    else:
        canvaswidth = height / boardaspectratio
        canvasheight = height
    # TODO: For some reason this doesn't work without the -4, or else it slowly expands by 4px recursively.
    canvas.configure(width=int(canvaswidth) - 4, height=int(canvasheight) - 4)
    render()


prevsize: Tuple[int, int] = (top.winfo_width(), top.winfo_height())


def resize(event: tkinter.Event):
    global prevsize
    newsize: Tuple[int, int] = (event.width, event.height)
    if event.widget == top and newsize != prevsize:
        canvasResize(event.width, event.height)
        prevsize = newsize


top.bind("<Configure>", resize)

top.mainloop()
