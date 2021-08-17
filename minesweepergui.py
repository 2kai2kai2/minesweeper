import tkinter
from tkinter import font, simpledialog
from tkinter.constants import LEFT, RIGHT
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageTk

import minesweepergame

bombimage = Image.open("resources/bomb.gif")
flagimage = Image.open("resources/flag.gif")
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


class newboarddialog(simpledialog.Dialog):
    def __init__(self, ggui):
        """
        Create a dialog to create a new board for a `gamegui`.
        """
        self.gui: gamegui = ggui
        super().__init__(self.gui.top, "New Game")

    def body(self, master: tkinter.Widget):
        # Width
        self.widthframe = tkinter.Frame(master)
        self.widthlabel = tkinter.Label(self.widthframe, text="Width")
        self.widthbox = tkinter.Spinbox(
            self.widthframe, from_=4, to=100, command=self.updatemaxbombs)
        self.widthlabel.pack(side=LEFT)
        self.widthbox.pack(side=RIGHT)
        self.widthframe.pack()
        # Height
        self.heightframe = tkinter.Frame(master)
        self.heightlabel = tkinter.Label(self.heightframe, text="Height")
        self.heightbox = tkinter.Spinbox(
            self.heightframe, from_=4, to=100, command=self.updatemaxbombs)
        self.heightlabel.pack(side=LEFT)
        self.heightbox.pack(side=RIGHT)
        self.heightframe.pack()
        # Bombs
        self.bombsframe = tkinter.Frame(master)
        self.bombslabel = tkinter.Label(self.bombsframe, text="Bombs")
        self.bombsbox = tkinter.Spinbox(self.bombsframe, from_=1, to=100)
        self.bombslabel.pack(side=LEFT)
        self.bombsbox.pack(side=RIGHT)
        self.bombsframe.pack()
        self.updatemaxbombs()
        return master

    def buttonbox(self):
        return super().buttonbox()

    def apply(self):
        self.gui.boardInit(int(self.widthbox.get()), int(
            self.heightbox.get()), int(self.bombsbox.get()))

    def updatemaxbombs(self):
        """
        Change the maximum number of bombs allowed to be half the tiles.
        """
        tiles: int = int(self.widthbox.get()) * int(self.heightbox.get())
        self.bombsbox.configure(to=tiles/2)


class gamegui:
    def __init__(self):
        # Window
        self.top = tkinter.Tk()
        self.top.title("Minesweeper")
        self.top.configure(bd=0, bg="black")
        # Canvas
        self.canvas = tkinter.Canvas(self.top, bd=0, bg="light grey")
        self.prevsize: Tuple[int, int] = (
            self.top.winfo_width(), self.top.winfo_height())
        self.canvas.pack()
        # Menu
        self.menu = tkinter.Menu(self.top)
        self.menu.add_command(label="New Game", command=self.boardDialog)
        self.menu.add_command(label="Restart", command=lambda: self.boardInit(
            self.width, self.height, self.bombs))
        self.top.configure(menu=self.menu)

        # Icons
        # These will be reused and resizing will only be calculated when the canvas resizes.
        bombscaled = bombimage
        self.bombphoto = ImageTk.PhotoImage(image=bombscaled)
        flagscaled = flagimage
        self.flagphoto = ImageTk.PhotoImage(image=flagscaled)
        # Font
        self.fontscaled = font.Font(
            family="Terminal", size=12, weight=font.BOLD)

        # Get size and initialize board
        self.boardDialog()

        # Events
        self.canvas.bind("<Button-1>", self.button1)  # Left-click
        self.canvas.bind("<Button-3>", self.button2)  # Right-click
        self.top.bind("<Configure>", self.resize)  # Resize

        # Run loop
        self.top.mainloop()

    def boardDialog(self):
        newboarddialog(self)

    def boardInit(self, width: int, height: int, bombs: int):
        """
        Does the initialization stuff that needs to happen for the board.

        This is separate so we can reset and reinitialize the board within the same window.
        """
        # New board
        self.width = width
        self.height = height
        self.bombs = bombs
        self.board = minesweepergame.game(width, height, bombs)

        # New board items
        self.canvas.delete(*self.canvas.find_all())
        self.canvassquares: List[List[Optional[int]]] = [[None for y in range(
            self.board.height)] for x in range(self.board.width)]  # Store the `_CanvasItemId`s
        self.canvasicons: List[List[Optional[int]]] = [[None for y in range(
            self.board.height)] for x in range(self.board.width)]  # Store the `_CanvasItemId`s

        # Render
        self.render()

    def drawIcon(self, symbol: str, x: int, y: int, tilewidth: int = None, tileheight: int = None):
        """
        Draw an icon for the given visible symbol in a given tile.
        This does NOT delete previous icons.

        `x` and `y` represent the tile number (not pixels) starting from (0, 0) at the top left.

        `tilewidth` and `tileheight` are optional parameters that may be given if the pixel size of tiles is already calculated. If `None` (default), they will automatically be calculated.
        """
        if tilewidth is None:
            tilewidth = self.canvas.winfo_reqwidth()/self.board.width
        if tileheight is None:
            tileheight = self.canvas.winfo_reqheight()/self.board.height

        if symbol == "?":  # Blank tiles are not drawn.
            return
        elif symbol == "F":  # Flagged tiles.
            self.canvasicons[x][y] = self.canvas.create_image(
                int(tilewidth*(x + 0.5)), int(tileheight*(y + 0.5)), image=self.flagphoto)
        elif symbol == "Q":
            self.canvasicons[x][y] = self.canvas.create_image(
                int(tilewidth*(x + 0.5)), int(tileheight*(y + 0.5)), image=self.bombphoto)
        else:  # Number tiles
            self.canvasicons[x][y] = self.canvas.create_text(tilewidth*(x + 0.5), tileheight*(
                y + 0.5), text=symbol, justify="center", fill=colors[symbol], font=self.fontscaled)

    def render(self):
        tilewidth = self.canvas.winfo_reqwidth()/self.board.width
        tileheight = self.canvas.winfo_reqheight()/self.board.height
        for x in range(self.board.width):
            # We go through and replace a line at a time, deleting the whole line at once.
            self.canvas.delete(
                *filter(lambda i: i is not None, self.canvassquares[x]))
            self.canvas.delete(
                *filter(lambda i: i is not None, self.canvasicons[x]))
            # We have to make icons None since flags that have been removed won't overwrite.
            self.canvasicons[x] = [None for y in range(self.board.height)]

            for y in range(self.board.height):
                self.canvassquares[x][y] = self.canvas.create_rectangle(
                    tilewidth*x, tileheight*y, tilewidth*(x+1), tileheight*(y+1), outline="black", width=1)
                self.drawIcon(self.board.getVisible(
                    x, y), x, y, tilewidth, tileheight)

    def button1(self, event: tkinter.Event):
        if self.board.isGameOver() or self.board.isVictory():
            return
        # Calculate board position relative to pixels
        tilewidth = self.canvas.winfo_reqwidth()/self.board.width
        tileheight = self.canvas.winfo_reqheight()/self.board.height
        x = int(event.x/tilewidth)
        y = int(event.y/tileheight)
        # We can't open the tile if it's flagged or already open.
        if self.board.visible[x][y] == 0:
            opened = self.board.open(x, y)
            if opened is None:
                # We stepped on a bomb
                self.drawIcon("Q", x, y, tilewidth, tileheight)
            else:
                # Tile is safe.
                for _x, _y in opened:
                    self.drawIcon(self.board.getVisible(_x, _y),
                                  _x, _y, tilewidth, tileheight)

    def button2(self, event: tkinter.Event):
        if self.board.isGameOver() or self.board.isVictory():
            return
        # Calculate board position relative to pixels
        tilewidth = self.canvas.winfo_reqwidth()/self.board.width
        tileheight = self.canvas.winfo_reqheight()/self.board.height
        x = int(event.x/tilewidth)
        y = int(event.y/tileheight)
        if self.board.flag(x, y):  # Try to change the flag
            # If something changed, draw or remove the flag.
            if self.board.visible[x][y] == -1:  # Draw a flag
                self.drawIcon("F", x, y, tilewidth, tileheight)
            else:
                self.canvas.delete(self.canvasicons[x][y])
                self.canvasicons[x][y] = None

    def canvasResize(self, width: int, height: int):
        """
        Resizes the canvas to be the largest that will fit in the window while maintaining the board's aspect ratio.
        - Resizes canvas element
        - Resizes icons
        - Re-renders the entire canvas
        """
        # Ensure board is initialized. If not, make canvas fill window.
        if not hasattr(self, "board"):
            self.canvas.configure(width=self.top.winfo_width(
            ) - 4, height=self.top.winfo_height() - 4)
            return

        boardaspectratio: float = self.board.height / self.board.width  # y/x
        canvasaspectratio: float = height / width  # y/x
        if boardaspectratio <= canvasaspectratio:
            canvaswidth = int(width)
            canvasheight = int(boardaspectratio * width)
        else:
            canvaswidth = int(height / boardaspectratio)
            canvasheight = int(height)
        # TODO: For some reason this doesn't work without the -4, or else it slowly expands by 4px recursively.
        self.canvas.configure(width=canvaswidth - 4, height=canvasheight - 4)
        # Resize icons
        iconsize = (int(canvaswidth/self.board.width),
                    int(canvasheight/self.board.height))
        bombscaled = bombimage.resize(iconsize)
        self.bombphoto = ImageTk.PhotoImage(bombscaled)
        flagscaled = flagimage.resize(iconsize)
        self.flagphoto = ImageTk.PhotoImage(flagscaled)
        # Resize font
        # If negative, font size is measured in pixels.
        self.fontscaled.configure(
            size=int(canvasheight/self.board.height * -3/4))
        # Draw
        self.render()

    def resize(self, event: tkinter.Event):
        newsize: Tuple[int, int] = (event.width, event.height)
        if event.widget == self.top and newsize != self.prevsize:
            self.canvasResize(event.width, event.height)
            self.prevsize = newsize


gamegui()
