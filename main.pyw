from email import message
import os
import chess
import stockfish
from customtkinter import *
from debug import *
from itertools import product
from PIL import Image, ImageTk
from tkinter import messagebox
from typing import Dict


class IllegalMoveError(Exception):
    """Custom exception for illegal moves."""
    pass


class InvalidPositionError(Exception):
    """Custom exception for invalid positions."""
    pass


class ChessBoard:
    def __init__(
        self,
        root: CTk,
        asset_location: os.PathLike,
        engine_location: os.PathLike,
        tile_size: int = 60,
        start_flipped: bool = False,
        white_hex: str = "#ffcf9f",
        black_hex: str = "#d28c45",
        show: bool = True,
        draw_immediate: bool = False,
    ):
        self.root = root
        self.canvas = CTkCanvas(
            self.root, width=8*tile_size, height=8*tile_size)

        if os.path.exists(asset_location):
            self.assets_path = asset_location
        else:
            raise FileNotFoundError(
                f"Asset location '{asset_location}' does not exist.")

        try:
            self.engine = ChessEngine(
                path=engine_location, depth=20, skill_level=20)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"No stockfish executable at '{engine_location}'")

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

        self.piece_imgs = self.__fetch_img_assets()

        self.board_rects = {}

        self._flipped = False
        if start_flipped:
            self.flip(draw_immediate=False)

        if show:
            self.shown = True
            self.canvas.pack()
            if draw_immediate:
                self.draw()
        else:
            self.shown = False

    def __fetch_img_assets(self) -> Dict[str, ImageTk.PhotoImage]:
        """Fetches the image assets for the chess pieces.

        Raises:
            FileNotFoundError: If one or multiple image files do not exist.

        Returns:
            Dict[str, ImageTk.PhotoImage]: A dictionary mapping piece names to their corresponding image objects.
        """
        piece_img_paths = {}
        for color in self.colors:
            for piece in self.pieces:
                piece_img_paths[f"{color}{piece}"] = os.path.join(
                    self.assets_path, "pieces", f"{color}{piece}.png")

        pieces = {}
        for piece in piece_img_paths.values():
            if not os.path.exists(piece):
                raise FileNotFoundError(
                    f"Piece image '{piece}' does not exist.")
            else:
                piece_name = piece.split(".")[0].split("\\")[-1].upper()
                img_raw = Image.open(piece)
                img_rsz = img_raw.resize((self.tile_size, self.tile_size))
                img_ctk = ImageTk.PhotoImage(img_rsz)
                pieces[piece_name] = img_ctk

        return pieces

    def flip(self, draw_immediate: bool = False) -> None:
        """Flips the chessboard vertically."""
        self._flipped = not self._flipped
        self.rows.reverse()
        self.cols.reverse()
        self.board.apply_transform(chess.flip_vertical)
        self.board.apply_transform(chess.flip_horizontal)
        if draw_immediate:
            self.draw()

    def draw(self):
        """Draws the chessboard and pieces on the canvas."""
        self.canvas.delete("all")
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
                    self.canvas.create_text(x1 + self.tile_size - 1, y1 + self.tile_size - 1,
                                            text=self.cols[col], anchor="se", font=("Arial", 8, "bold"), fill=text_color)
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

                self.canvas.create_image(
                    piece_x, piece_y, image=self.piece_imgs[cell], tags="piece")

    def update(self) -> None:
        """Updates the chessboard with the current state of the pieces."""
        self.canvas.delete("piece")
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

                self.canvas.create_image(
                    piece_x, piece_y, image=self.piece_imgs[cell], tags="piece")

    def move(self, move: str) -> None:
        """Moves a piece on the chessboard.

        Args:
            move (str): The move in UCI format, e.g., "e2e4" (represents e4 in SAN).
        """
        try:
            chess_move = chess.Move.from_uci(move)
            if chess_move in self.board.legal_moves:
                self.board.push(chess_move)
                self.engine.make_moves_from_current_position([move])
                self.update()
            else:
                raise IllegalMoveError(f"Illegal move: {move}")
        except Exception as e:
            print(f"Error: {e}")

    def show(self) -> None:
        """Shows the chessboard."""
        if not self.shown:
            self.canvas.pack()
            self.shown = True
            self.draw()

    def hide(self) -> None:
        """Hides the chessboard."""
        if self.shown:
            self.canvas.pack_forget()
            self.shown = False

    def is_check(self) -> bool:
        """Checks if the game is in check.

        Returns:
            bool: True if the game is in check, False otherwise.
        """
        return self.board.is_check()

    def is_checkmate(self) -> bool:
        """Checks if the game is in checkmate.

        Returns:
            bool: True if the game is in checkmate, False otherwise.
        """
        return self.board.is_checkmate()

    def is_stalemate(self) -> bool:
        """Checks if the game is in stalemate.

        Returns:
            bool: True if the game is in stalemate, False otherwise.
        """
        return self.board.is_stalemate()

    def is_draw(self) -> bool:
        """Checks if the game is a draw.

        Returns:
            bool: True if the game is a draw, False otherwise.
        """
        return self.board.is_draw()

    def is_over(self) -> bool:
        """Checks if the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.board.is_game_over()

    def get_board(self) -> chess.Board:
        """Returns the current board.

        Returns:
            chess.Board: The current chess board.
        """
        return self.board

    def get_board_str(self) -> str:
        """Returns the current board as a string.

        Returns:
            str: The current board as a string.
        """
        return str(self.board)

    def getFEN(self) -> str:
        """Returns the current FEN of the board.

        Returns:
            str: The current FEN of the board.
        """
        return self.board.fen()

    def getTurn(self) -> str:
        """Returns the current turn of the board.
        Returns:
            str: Either "W" or "B" depending on the current turn.
        """
        return "W" if self.board.turn else "B"

    def setFEN(self, fen: str) -> None:
        """Sets the board to a specific FEN position.

        Args:
            fen (str): The FEN string representing the position.

        Raises:
            InvalidPositionError: If the FEN string is invalid.
        """
        try:
            self.board.set_fen(fen)
            self.update()
        except ValueError:
            raise InvalidPositionError(f"Invalid FEN: {fen}")

    def isWhiteTurn(self) -> bool:
        """Checks if it's White's turn.

        Returns:
            bool: True if White's turn, False otherwise.
        """
        return self.board.turn

    def isBlackTurn(self) -> bool:
        """Checks if it's Black's turn.

        Returns:
            bool: True if Black's turn, False otherwise
        """
        return not self.board.turn


class ChessEngine:
    def __init__(self, path: os.PathLike, depth: int = 20, skill_level: int = 20):
        if not os.path.exists(path):
            raise FileNotFoundError()
        if depth < 0:
            raise ValueError(
                f"ChessEngine.depth must be integer greater than 0, not {depth}")
        elif depth > 20:
            raise RuntimeWarning(
                f"Performance may be seriously impacted due to ChessEngine.depth being greater than 20 ({depth})")
        if skill_level > 20 or skill_level < 0:
            raise ValueError(
                f"ChessEngine.skill_level must be integer between 0 and 20, not {skill_level}")

        self.engine = stockfish.Stockfish(path, depth)
        self.engine.set_skill_level(skill_level)

    def set_skill_level(self, skill_level: int = 20):
        if skill_level > 20 or skill_level < 0:
            raise ValueError(
                f"ChessEngine.set_skill_level() arg 1 skill_level must be integer between 0 and 20, not {skill_level}")
        self.engine.set_skill_level(skill_level)


def close(app: CTk) -> None:
    """Quits the application."""
    os.remove("RUN.tmp")
    app.destroy()
    log("Chess.py was closed")
    exit(0)


def main():
    """Main function to run the chessboard application."""
    log("Running Chess.py")
    log("Checking for running instance...")
    if os.path.exists("RUN.tmp"):
        error("Chess.py is already running")
        messagebox.showerror(title="Chess.py Error",
                             message="Chess.py is already running. Please close the other instance before running a new one. If currently no intance is open, delte the .run file manually",
                             icon=messagebox.ERROR,
                             type=messagebox.OK)
        exit(1)
    else:
        open("RUN.tmp", "w").close()
    __assets__ = os.path.join(os.path.dirname(__file__), "assets")
    __engine__ = os.path.join(os.path.dirname(
        __file__), "engine", "stockfish-windows-x86-64-avx2.exe")
    app = CTk()  # Initialize the main application window
    set_appearance_mode("system")  # Set the appearance mode to system default
    set_default_color_theme("green")  # Set the default color theme to green
    app.title("Chess.py")  # Set the title of the application window
    app.iconbitmap("assets/icon.ico")  # Set the icon of the application window
    app.geometry("500x600")  # Set the initial size of the application window
    app.resizable(True, True)  # Allow the application window to be resizable
    # Set the protocol for closing the application window
    app.protocol("WM_DELETE_WINDOW", lambda: close(app))

    tabview = CTkTabview(app, anchor="nw")  # Create a tabview widget
    # Pack the tabview widget to fill the application window
    tabview.pack(expand=True, fill="both")
    tabview.add("Analyze")
    tabview.add("Play")
    tabview.add("Settings")

    quit_button = CTkButton(tabview.tab("Settings"),
                            text="Quit", command=lambda: close(app))
    quit_button.pack(pady=10, padx=10)

    analyze_board = ChessBoard(tabview.tab("Analyze"), asset_location=__assets__,
                               engine_location=__engine__, tile_size=60, start_flipped=False, show=False)

    app.mainloop()


if __name__ == "__main__":
    main()
