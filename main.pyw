import chess
import debug
import os
import pygame
import stockfish
import subprocess
import CTkMessagebox as ctkmbox
import customtkinter as ctk
from itertools import product
from PIL import Image, ImageTk
from typing import Dict, Literal, Optional

# Hides annoying Hello from pygame
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


class IllegalMoveError(Exception):
    """Custom exception for illegal moves."""
    pass


class InvalidMoveError(Exception):
    """Custom exception for invalid moves."""
    pass


class InvalidPositionError(Exception):
    """Custom exception for invalid positions."""
    pass


class ChessEngine(stockfish.Stockfish):
    def __init__(self, path: str, depth: int = 20, skill_level: int = 20) -> None:
        super().__init__(path=path)
        self.set_depth(depth)
        self.set_skill_level(skill_level)
        # Prevent Stockfish from opening a console window on Windows
        if os.name == "nt":
            self._Stockfish__process = subprocess.Popen(
                [path],
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )


class ChessBoard:
    def __init__(
        self,
        root: ctk.CTk | ctk.CTkFrame,
        asset_location: str,
        engine_location: str,
        tile_size: int = 60,
        start_flipped: bool = False,
        white_hex: str = "#ffcf9f",
        black_hex: str = "#d28c45",
        show: bool = True,
        draw_immediate: bool = False,
        sound: bool = True,
    ):
        self.root = root
        self.canvas = ctk.CTkCanvas(
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

        self._highlighted_square = None

        self.piece_names = {
            "K": "WK",
            "Q": "WQ",
            "R": "WR",
            "N": "WN",
            "B": "WB",
            "P": "WP",
            "k": "BK",
            "q": "BQ",
            "r": "BR",
            "n": "BN",
            "b": "BB",
            "p": "BP",
        }

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

        self.sound = sound

    def highlight_square(self, square: str) -> None:
        """Highlights a square with a yellow overlay if it belongs to the current player.

        Args:
            square (str): The square to highlight (e.g., "e4").
        """
        if square not in self.coords:
            raise ValueError(f"Invalid square: {square}")

        piece = self.board.piece_at(chess.parse_square(square.lower()))
        if piece is None:
            return  # No piece on the square, nothing to highlight

        # Check if the piece belongs to the current player
        if (self.isWhiteTurn() and piece.color) or (self.isBlackTurn() and not piece.color):
            col = self.cols.index(square[0].upper())
            row = self.rows.index(square[1])

            x1, y1 = col * self.tile_size, row * self.tile_size
            x2, y2 = x1 + self.tile_size, y1 + self.tile_size

            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill="yellow", outline="", stipple="gray50", tags="highlight")
            # Send the highlight rectangle to the back
            self.canvas.tag_lower("highlight", "piece")

    def on_square_click(self, event) -> None:
        """Handles square click events to highlight the square.

        Args:
            event: The click event.
        """
        col = event.x // self.tile_size
        row = event.y // self.tile_size

        if col < 0 or col > 7 or row < 0 or row > 7:  # If click is outside of board
            return

        self.canvas.delete("highlight")

        square = f"{self.cols[col]}{self.rows[row]}"
        piece = self.board.piece_at(chess.parse_square(square.lower()))
        piece_color = piece.color if piece else None
        debug.debug(f"""{square}: {self.piece_names[str(piece)] if piece else "Empty"}{f" [{'W' if self.isWhiteTurn() else 'B'}]" if piece else ""}: {
            "Yes" if (self.board.turn == piece_color) else "No"}""")
        if (self.isWhiteTurn() == piece_color):
            self.canvas.delete("highlight")
            if square.lower != self._highlighted_square:
                self.highlight_square(square)
                self._highlighted_square = square.lower()

    def enable_highlighting(self) -> None:
        """Enables square highlighting on click."""
        self.canvas.bind("<Button-1>", self.on_square_click)

    def disable_highlighting(self) -> None:
        """Disables square highlighting."""
        self.canvas.unbind("<Button-1>")
        self.canvas.delete("highlight")

    def get_possible_moves(self, square: str) -> list[str]:
        """Returns a list of possible moves for the piece on the given square.

        Args:
            square (str): The square to check for possible moves (e.g., "e4").

        Returns:
            list[str]: A list of possible moves in UCI format.
        """
        if square not in self.coords:
            raise ValueError(f"Invalid square: {square}")

        piece_square = chess.parse_square(square.lower())
        piece = self.board.piece_at(piece_square)

        if piece is None or (self.isWhiteTurn() != piece.color):
            return []

        legal_moves = [
            move.uci() for move in self.board.legal_moves if move.from_square == piece_square]
        return legal_moves

    def move_piece(self, from_square: str, to_square: str, promotion: Optional[str] = None) -> None:
        """Moves a piece from one square to another, with optional promotion.

        Args:
            from_square (str): The square to move the piece from (e.g., "e7").
            to_square (str): The square to move the piece to (e.g., "e8").
            promotion (str, optional): Piece to promote to ('q', 'r', 'b', 'n'). Defaults to None.

        Raises:
            IllegalMoveError: If the given move is illegal.
            InvalidMoveError: If the given move is invalid.
        """
        if from_square not in self.coords or to_square not in self.coords:
            raise ValueError(f"Invalid square: {from_square} or {to_square}")

        move_str = f"{from_square.lower()}{to_square.lower()}"
        # Handle promotion
        if promotion:
            if promotion.lower() not in ["q", "r", "b", "n"]:
                raise InvalidMoveError(f"Invalid promotion piece: {promotion}")
            move_str += promotion.lower()

        try:
            move = chess.Move.from_uci(move_str)
        except ValueError:
            raise InvalidMoveError(f"Invalid move: {move_str}")

        if move in self.board.legal_moves:
            if self.sound:
                testBoard = self.board.copy()
                testBoard.push(move)
                fn = []
                if testBoard.is_game_over():
                    fn.append("game_end")
                elif testBoard.is_check():
                    fn.append("check")
                elif self.board.is_capture(move):
                    fn.append("capture")
                elif self.board.is_castling(move):
                    fn.append("castle")
                elif move.promotion:
                    fn.append("promote")
                else:
                    fn.append("move")

                fp = os.path.join(self.assets_path, "sounds", fn[0] + ".ogg")
                playSound(fp)
                del testBoard

            self.board.push(move)
            self.engine.make_moves_from_current_position([move.uci()])
            self.update()
        else:
            raise IllegalMoveError(f"Illegal move: {move.uci()}")

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
        """Flips the chessboard vertically and horizontally."""
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
                    x1, y1, x2, y2, fill=color, outline="", tags="square")
                # Prevent garbage collection
                self.board_rects[f"{col},{row}"] = rect

                text_color = self._white if color == self._black else self._black

                if row == 7:
                    self.canvas.create_text(x1 + self.tile_size - 1, y1 + self.tile_size - 1,
                                            text=self.cols[col], anchor="se", font=("Arial", 8, "bold"), fill=text_color, tags="text")
                if col == 0:
                    self.canvas.create_text(
                        x1 + 3, y1 + 3, text=self.rows[row], anchor="nw", font=("Arial", 8, "bold"), fill=text_color, tags="text")

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
            move (str): The move in UCI format, e.g., "b1c3" (represents Nc3 in SAN).

        Raises:
            IllegalMoveError: If the move is illegal.
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
        return (
            self.board.is_insufficient_material() or
            self.board.is_seventyfive_moves() or
            self.board.is_fivefold_repetition() or
            self.board.is_stalemate() or
            (self.board.is_game_over() and self.board.result() == "1/2-1/2")
        )

    def is_over(self) -> bool:
        """Checks if the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.board.is_game_over()

    def result(self) -> Literal['1-0', '1/2-1/2', '0-1', '*']:
        """Returns the result of the game.

        Returns:
            Literal['1-0', '1/2-1/2', '0-1', '*']: The result of the game, either "1-0", "0-1", or "1/2-1/2".
        """
        return self.board.result()  # type: ignore

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

    def setPGN(self, pgn: str) -> None:
        """Sets the board to the given PGN position

        Args:
            pgn (str): str in PGN format. Must conatin multiple lines

        Raises:
            IllegalMoveError: Gets raised if one or multiple of the in pgn included moves are illegal
            InvalidMoveError: Gets raised if one or multiple of the in pgn included moves are invalid
        """
        lines = pgn.splitlines()
        moves_start = None
        if "" in lines:
            moves_start = lines.index("") + 1
        else:
            for idx, line in enumerate(lines):
                if line.startswith("1."):
                    moves_start = idx
                    break
        if moves_start is None:
            raise InvalidMoveError(
                "Could not determine where moves start in PGN.")
        move_lines = lines[moves_start:]
        moves_text = " ".join(move_lines)
        moves = moves_text.split(" ")
        del moves[-1]   # Removes game ending
        del moves[::3]  # Removes move numbers
        test_board = chess.Board()
        for move in moves:
            try:
                test_board.push_san(move)
            except chess.IllegalMoveError:
                raise IllegalMoveError(
                    f"{move} is not a legal move at board state\n{str(test_board)}")
            except chess.InvalidMoveError:
                raise InvalidMoveError(
                    f"{move} is not a valid move in SAN notation")
        self.board.reset()
        for move in moves:
            self.board.push_san(move)
        self.engine.set_fen_position(self.board.fen())
        self.update()


def playSound(fp: os.PathLike | str, block: bool = True) -> None:
    if not os.path.exists(fp):
        raise FileNotFoundError(
            f"File '{os.path.basename(fp)}' does not exist at '{fp}'")
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()
    if block:
        pygame.event.wait()


def close(app: ctk.CTk) -> None:
    """Quits the application after prompting the user."""
    msg = ctkmbox.CTkMessagebox(master=app,
                                title="Really Quit?",
                                message="Do you really want to quit Chess.py? Any unsaved progress will be lost.",
                                icon="question",
                                option_1="Cancel",
                                option_2="Quit",
                                sound=True,
                                topmost=True,
                                option_focus=1)
    if msg.get() == "Quit":
        os.remove("RUN.tmp")
        app.destroy()
        debug.finish()
        exit(0)


def main():
    """Main function to run the chessboard application."""
    debug.log("Running Chess.py")
    debug.log("Checking for running instance...")
    if os.path.exists("RUN.tmp"):
        debug.error("Chess.py is already running")
        ctkmbox.CTkMessagebox(title="Chess.py Error",
                              message="Chess.py is already running. Please close the other instance before running a new one.",
                              icon="cancel",
                              option_1="OK")
        exit(1)
    else:
        open("RUN.tmp", "w").close()

    app = ctk.CTk()  # Initialize the main application window
    try:
        __assets__ = os.path.join(os.path.dirname(__file__), "assets")
        __engine__ = os.path.join(os.path.dirname(
            __file__), "engine", "stockfish-windows-x86-64-avx2.exe")
        # Set the appearance mode to system default
        ctk.set_appearance_mode("system")
        # Set the default color theme to green
        ctk.set_default_color_theme("green")
        app.title("Chess.py")  # Set the title of the application window
        # Set the icon of the application window
        app.iconbitmap(os.path.join(__assets__, "icon.ico"))
        # Set the initial size of the application window
        app.geometry("500x700")
        # Allow the application window to be resizable
        app.resizable(True, True)
        # Set the protocol for closing the application window
        app.protocol("WM_DELETE_WINDOW", lambda: close(app))
        app.protocol("WM_SAVE_YOURSELF", lambda: close(app))

        tabview = ctk.CTkTabview(app, anchor="nw")  # Create a tabview widget
        # Pack the tabview widget to fill the application window
        tabview.pack(expand=True, fill="both")
        tabview.add("Analyze")
    #    tabview.add("Play")
        tabview.add("Settings")

        quit_button = ctk.CTkButton(tabview.tab("Settings"),
                                    text="Quit", command=lambda: close(app), fg_color="red", hover_color="darkred")
        quit_button.pack(pady=10, padx=10)

        analyze_board = ChessBoard(tabview.tab("Analyze"), asset_location=__assets__,
                                   engine_location=__engine__, tile_size=60, start_flipped=False, show=True, draw_immediate=True)
        analyze_board.enable_highlighting()

        pgnInput = ctk.CTkEntry(tabview.tab(
            "Analyze"), placeholder_text="Paste PGN here...", placeholder_text_color="lightgray")
        pgnSubmit = ctk.CTkButton(tabview.tab("Analyze"), text="Load")
        pgnInput.pack(side="left", pady=10)
        pgnSubmit.pack(side="right", pady=10)

        flip_button = ctk.CTkButton(tabview.tab(
            "Analyze"), text="Flip Board", command=lambda: analyze_board.flip(draw_immediate=True))
        flip_button.pack(padx=5, pady=10)

        app.mainloop()
    except KeyboardInterrupt:
        debug.log("chess.py closed due to KeyboardInterrupt (CTRL+C)")
        close(app)
    except Exception as e:
        debug.exception(f"chess.py closed tue to unexpected error: {e}")
        ctkmbox.CTkMessagebox(title="Chess.py Error",
                              message=f"Chess.py closed due to an unexpected error: {e}", icon="Error")
        close(app)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        debug.exception(str(e))
else:
    raise ImportError(
        "This file is designed to be run standalone")
