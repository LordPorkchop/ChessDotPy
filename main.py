import os
import chess
from customtkinter import *
from itertools import product
from PIL import Image, ImageTk

class ChessBoard:
    def __init__(
        self,
        root: CTk,
        asset_location: os.PathLike,
        tile_size: int = 60,
        start_flipped: bool = False,
        white_hex: str = "#ffcf9f",
        black_hex: str = "#d28c45",
        show: bool = True
    ):
        self.root = root
        self.canvas = CTkCanvas(self.root, width=8*tile_size, height=8*tile_size)

        if os.path.exists(asset_location):
            self.assets_path = asset_location
        else:
            raise FileNotFoundError(f"Asset location '{asset_location}' does not exist.")

        self.tile_size = tile_size

        self._white = white_hex
        self._black = black_hex
        self._colors = [self._white, self._black]

        self.board = chess.Board()
        self.rows = ["8", "7", "6", "5", "4", "3", "2", "1"]
        self.cols = ["A", "B", "C", "D", "E", "F", "G", "H"]
        self.coords = ["".join(x) for x in product(self.cols, self.rows)]
        self.pieces = ["K", "Q", "R", "N", "B", "P"]
        self.colors = ["W", "B"]

        self.piece_img_paths = self.__fetch_img_assets()
        self.piece_imgs = {}

        self.board_rects = {}

        if start_flipped:
            self.flip()
            self._flipped = True
        else:
            self._flipped = False

        if show:
            self.shown = True
            self.canvas.pack()
        else:
            self.shown = False
    
    def __fetch_img_assets(self):
        piece_img_paths = {}
        for color in self.colors:
            for piece in self.pieces:
                piece_img_paths[f"{color}{piece}"] = os.path.join(
                    self.assets_path, f"pieces/{color}{piece}.png")
        return piece_img_paths
    
    def flip(self):
        self._flipped = not self._flipped
        self.rows.reverse()
        self.cols.reverse()
        self.board.apply_transform(chess.flip_vertical)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.piece_imgs.clear()
        for row in range(8):
            for col in range(8):
                color = self._colors[(row + col) % 2]
                x1, y1 = col * self.tile_size, row * self.tile_size
                x2, y2 = x1 + self.tile_size, y1 + self.tile_size
                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline="")
                # Prevent garbage collection
                self.board_rects[f"{col},{row}"] = rect

                text_color = self._white if color == self._black else self._black
                if row == 7:
                    self.canvas.create_text(x1 + self.tile_size - 1, y1 + self.tile_size - 1, text=chr(
                        97 + col).upper(), anchor="se", font=("Arial", 8, "bold"), fill=text_color)
                if col == 0:
                    self.canvas.create_text(
                        x1 + 3, y1 + 3, text=self.rows[row], anchor="nw", font=("Arial", 8, "bold"), fill=text_color)

        board_lines = str(self.board).splitlines()
        for row, line in enumerate(board_lines):
            line = line.replace(" ", "")
            for col, cell in enumerate(line):
                if (not cell) or cell == " " or cell == ".":
                    continue
                if cell.isupper():
                    cell = "W" + cell
                else:
                    cell = "B" + cell.upper()

                piece_x = (0.5 * self.tile_size) + col * self.tile_size
                piece_y = (0.5 * self.tile_size) + row * self.tile_size

                img_raw = Image.open(self.piece_img_paths[cell])
                img_rsz = img_raw.resize((self.tile_size, self.tile_size))
                img_ctk = ImageTk.PhotoImage(img_rsz)
                # Prevent garbage collection
                self.piece_imgs[f"{row},{col}"] = img_ctk

                self.canvas.create_image(
                    piece_x, piece_y, image=img_ctk, tags="piece")

if __name__ == "__main__":
    root = CTk()
    board = ChessBoard(root, asset_location="assets", tile_size=60, start_flipped=False, show=True)
    board.draw()
    root.mainloop()