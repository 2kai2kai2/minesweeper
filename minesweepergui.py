import tkinter
from tkinter import font
from typing import Dict, List, Optional, Tuple
import minesweepergame
from PIL import Image, ImageTk

board = minesweepergame.game(10, 10, 10)

top = tkinter.Tk()
top.title("Minesweeper")
top.configure(bd=0, bg="black")

canvas = tkinter.Canvas(top, bd=0, bg="light grey")

canvassquares: List[List[Optional[int]]] = [[None for y in range(
    board.height)] for x in range(board.width)]  # Store the `_CanvasItemId`s
canvasicons: List[List[Optional[int]]] = [[None for y in range(
    board.height)] for x in range(board.width)]  # Store the `_CanvasItemId`s

# Icons
# These will be reused and resizing will only be calculated when the canvas resizes.
bombimage = Image.open("resources/bomb.gif")
bombscaled = bombimage
bombphoto = ImageTk.PhotoImage(image=bombscaled)
flagimage = Image.open("resources/flag.gif")
flagscaled = flagimage
flagphoto = ImageTk.PhotoImage(image=flagscaled)
# Font
numfont = font.Font(family="Terminal", size=12, weight=font.BOLD)


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
    elif symbol == "F":  # Flagged tiles.
        canvasicons[x][y] = canvas.create_image(
            int(tilewidth*(x + 0.5)), int(tileheight*(y + 0.5)), image=flagphoto)
    elif symbol == "Q":
        canvasicons[x][y] = canvas.create_image(
            int(tilewidth*(x + 0.5)), int(tileheight*(y + 0.5)), image=bombphoto)
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
            tilewidth*(x + 0.5), tileheight*(y + 0.5), text=symbol, justify="center", fill=colors[symbol], font=numfont)


def render():
    boxwidth = canvas.winfo_reqwidth()/board.width
    boxheight = canvas.winfo_reqheight()/board.height
    for x in range(board.width):
        # We go through and replace a line at a time, deleting the whole line at once.
        canvas.delete(*filter(lambda i: i is not None, canvassquares[x]))
        canvas.delete(*filter(lambda i: i is not None, canvasicons[x]))
        # We have to make icons None since flags that have been removed won't overwrite.
        canvasicons[x] = [None for y in range(board.height)]

        for y in range(board.height):
            canvassquares[x][y] = canvas.create_rectangle(
                boxwidth*x, boxheight*y, boxwidth*(x+1), boxheight*(y+1), outline="black", width=1)
            drawIcon(board.getVisible(x, y), x, y, boxwidth, boxheight)


def button1(event: tkinter.Event):
    if board.isGameOver() or board.isVictory():
        return
    # Calculate board position relative to pixels
    boxwidth = canvas.winfo_reqwidth()/board.width
    boxheight = canvas.winfo_reqheight()/board.height
    x = int(event.x/boxwidth)
    y = int(event.y/boxheight)
    # We can't open the tile if it's flagged or already open.
    if board.visible[x][y] == 0:
        opened = board.open(x, y)
        if opened is None:
            # We stepped on a bomb
            drawIcon("Q", x, y, boxwidth, boxheight)
        else:
            # Tile is safe.
            for _x, _y in opened:
                drawIcon(board.getVisible(_x, _y), _x, _y, boxwidth, boxheight)


def button2(event: tkinter.Event):
    if board.isGameOver() or board.isVictory():
        return
    # Calculate board position relative to pixels
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
    """
    Resizes the canvas to be the largest that will fit in the window while maintaining the board's aspect ratio.
    - Resizes canvas element
    - Resizes icons
    - Re-renders the entire canvas
    """
    boardaspectratio: float = board.height / board.width  # y/x
    canvasaspectratio: float = height / width  # y/x
    if boardaspectratio <= canvasaspectratio:
        canvaswidth = int(width)
        canvasheight = int(boardaspectratio * width)
    else:
        canvaswidth = int(height / boardaspectratio)
        canvasheight = int(height)
    # TODO: For some reason this doesn't work without the -4, or else it slowly expands by 4px recursively.
    canvas.configure(width=canvaswidth - 4, height=canvasheight - 4)
    # Resize icons
    iconsize = (int(canvaswidth/board.width), int(canvasheight/board.height))
    global bombscaled
    global bombphoto
    bombscaled = bombimage.resize(iconsize)
    bombphoto = ImageTk.PhotoImage(bombscaled)
    global flagscaled
    global flagphoto
    flagscaled = flagimage.resize(iconsize)
    flagphoto = ImageTk.PhotoImage(flagscaled)
    # Resize font
    # If negative, font size is measured in pixels.
    numfont.configure(size=int(canvasheight/board.height * -3/4))
    # Draw
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
