# Python Version 3.x
# File: minesweeper.py

from tkinter import *
from tkinter import messagebox
from collections import deque
import random
import platform
import time
import csv
import os
from datetime import datetime
from tkinter import simpledialog

# MVC Components:l 
# - Model: GameModel, Cell
# - View: GUIView, TextView
# - Controller: GameController

LEVELS = {
    'beginner': {'size_x': 8, 'size_y': 8, 'mines': 10, 'treasures': 1},
    'intermediate': {'size_x': 16, 'size_y': 16, 'mines': 40, 'treasures': 2},
    'expert': {'size_x': 16, 'size_y': 30, 'mines': 99, 'treasures': 3}
}

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

# ------------------ Model ------------------

class Cell:
    """
    Model: Represents a single cell on the Minesweeper board.

    Args:
        x (int): The x-coordinate (row index) of the cell.
        y (int): The y-coordinate (column index) of the cell.

    Preconditions:
        - x >= 0
        - y >= 0

    Postconditions:
        - self.x == x
        - self.y == y
        - self.is_mine == False
        - self.is_treasure == False
        - self.state == STATE_DEFAULT
        - self.adjacent_mines == 0
    """
    def __init__(self, x, y):
        assert x >= 0 and y >= 0, "Cell coordinates must be non-negative integers."
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_treasure = False
        self.state = STATE_DEFAULT
        self.adjacent_mines = 0

class GameModel:
    """
    Model: Represents the game logic and state.

    Args:
        file_name (str or None): The name of the CSV file containing board setup data, or None.
        level (str): The game level ('beginner', 'intermediate', 'expert').

    Preconditions:
        - level in ['beginner', 'intermediate', 'expert']
        - If file_name is not None, it must be a valid path to a CSV file.

    Postconditions:
        - self.level == level
        - self.SIZE_X == LEVELS[level]['size_x']
        - self.SIZE_Y == LEVELS[level]['size_y']
        - self.num_mines == LEVELS[level]['mines']
        - self.num_treasures == LEVELS[level]['treasures']
        - self.flag_count == 0
        - self.correct_flag_count == 0
        - self.clicked_count == 0
        - self.start_time is None
        - self.cells is a dictionary mapping (x, y) to Cell instances
        - self.mines == number of mines on the board
        - self.treasures == number of treasures on the board
        - self.game_over == False
        - If file_name is None, self.setup_board() is called
        - If file_name is not None, self.setup_board_from_file(file_name) is called
    """
    def __init__(self, file_name, level):
        assert level in LEVELS, "Invalid game level."
        self.level = level
        self.SIZE_X = LEVELS[level]['size_x']
        self.SIZE_Y = LEVELS[level]['size_y']
        self.num_mines = LEVELS[level]['mines']
        self.num_treasures = LEVELS[level]['treasures']
        self.flag_count = 0
        self.correct_flag_count = 0
        self.clicked_count = 0
        self.start_time = None
        self.cells = {}
        self.mines = self.num_mines
        self.treasures = self.num_treasures
        self.game_over = False
        self.invalid_board = False

        if file_name is None:
            self.setup_board()
        else:
            self.setup_board_from_file(file_name)

    def setup_board(self):
        """
        Sets up the game board with randomly placed mines and treasures.

        Postconditions:
            - self.cells contains SIZE_X * SIZE_Y Cell instances.
            - Exactly self.num_mines cells have is_mine == True.
            - Exactly self.num_treasures cells have is_treasure == True.
            - All other cells have is_mine == False and is_treasure == False.
            - For each cell, cell.adjacent_mines == number of adjacent mines.
        """
        positions = [(x, y) for x in range(self.SIZE_X) for y in range(self.SIZE_Y)]
        random.shuffle(positions)
        mine_positions = positions[:self.num_mines]
        treasure_positions = positions[self.num_mines:self.num_mines + self.num_treasures]

        for x in range(self.SIZE_X):
            for y in range(self.SIZE_Y):
                cell = Cell(x, y)
                if (x, y) in mine_positions:
                    cell.is_mine = True
                elif (x, y) in treasure_positions:
                    cell.is_treasure = True
                self.cells[(x, y)] = cell

        # Calculate adjacent mines for each cell
        for cell in self.cells.values():
            cell.adjacent_mines = self.count_adjacent_mines(cell.x, cell.y)

    def setup_board_from_file(self, file_name):
        """
        Sets up the game board from a CSV file.

        Args:
            file_name (str): The name of the CSV file containing board setup data.

        Preconditions:
            - self.level must be "beginner".
            - file_name is not None and is a valid name of a CSV file.
            - The CSV file has 8 rows and 8 columns.
            - Each cell in the CSV file contains 0, 1, or 2.
            - The board meets the specified criteria for a test board.

        Postconditions:
            - self.cells contains SIZE_X * SIZE_Y Cell instances.
            - Cells are set up according to the data in the CSV file.
            - self.mines == number of mines on the board.
            - self.treasures == number of treasures on the board.
            - For each cell, cell.adjacent_mines == number of adjacent mines.
            - If the board is invalid, self.invalid_board == True and self.setup_board() is called.
        """
        # Ensure file_name ends with '.csv'
        if not file_name.lower().endswith('.csv'):
            file_name += '.csv'

        # Create file path from file name
        file_path = os.path.join("tests", file_name)
        print(file_path)

        num_mines_file = 0
        num_treasures_file = 0

        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

                # Validate row and column counts
                if len(rows) != 8:
                    message = "Invalid file: There must be exactly 8 rows."
                    messagebox.showinfo("Invalid File", message)
                    self.invalid_board = True
                    return

                for row_index, row in enumerate(rows):
                    if len(row) != 8:
                        message = f"Invalid file: Row {row_index + 1} must have exactly 8 columns."
                        messagebox.showinfo("Invalid File", message)
                        self.invalid_board = True
                        return

                    for col_index, cell_value in enumerate(row):
                        cell = Cell(row_index, col_index)
                        try:
                            value = int(cell_value.strip())
                            if value == 1:
                                cell.is_mine = True
                                num_mines_file += 1
                            elif value == 2:
                                cell.is_treasure = True
                                num_treasures_file += 1
                            elif value != 0:
                                message = f"Invalid value {value} at ({row_index}, {col_index})."
                                messagebox.showinfo("Invalid File", message)
                                self.invalid_board = True
                                return
                            self.cells[(row_index, col_index)] = cell
                        except ValueError:
                            message = "Invalid tile detected."
                            messagebox.showinfo("Invalid File", message)
                            self.invalid_board = True
                            return

                # Adjust mines and treasures
                self.mines = num_mines_file
                self.treasures = num_treasures_file

                # Calculate adjacent mines for each cell
                for cell in self.cells.values():
                    cell.adjacent_mines = self.count_adjacent_mines(cell.x, cell.y)

                

        except FileNotFoundError:
            message = "Cannot find file."
            messagebox.showinfo("File Not Found", message)
            self.invalid_board = True
        except Exception as e:
            message = f"Cannot open file. Error: {str(e)}. Generating random board instead."
            messagebox.showinfo("Problem With File", message)
            self.invalid_board = True

        if self.invalid_board:
            self.cells.clear()
            self.setup_board()

    def count_adjacent_mines(self, x, y):
        """
        Counts the number of adjacent mines for the cell at (x, y).

        Args:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.

        Returns:
            int: The number of adjacent mines.
        """
        count = 0
        for neighbor in self.get_neighbors(x, y):
            if neighbor.is_mine:
                count += 1
        return count

    def get_neighbors(self, x, y):
        """
        Retrieves the neighboring cells of the cell at (x, y).

        Args:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.

        Returns:
            list[Cell]: A list of neighboring Cell instances.
        """
        neighbors = []
        coords = [
            (x - 1, y),      # top
            (x + 1, y),      # bottom
            (x, y - 1),      # left
            (x, y + 1),      # right
            (x - 1, y - 1),  # top-left
            (x - 1, y + 1),  # top-right
            (x + 1, y - 1),  # bottom-left
            (x + 1, y + 1),  # bottom-right
        ]
        for nx, ny in coords:
            if 0 <= nx < self.SIZE_X and 0 <= ny < self.SIZE_Y:
                neighbors.append(self.cells[(nx, ny)])
        return neighbors

# ------------------ Controller ------------------

class GameController:
    """
    Controller: Manages the game flow and interactions between model and view.

    Args:
        file_name (str or None): The name of the test map CSV file, or None.
        view_type (str): The view type ('gui' or 'text').

    Preconditions:
        - view_type in ['gui', 'text']

    Postconditions:
        - self.model is an instance of GameModel
        - self.view is an instance of GUIView or TextView, depending on view_type
    """
    def __init__(self, file_name, view_type='gui'):
        if file_name is None:
            level = simpledialog.askstring("Select Level", "Enter level (beginner, intermediate, expert):")
            if level is None:
                exit()
            level = level.lower()
            if level not in LEVELS:
                level = 'beginner'  # Default to beginner if invalid input
        else:
            # In testing mode, set level to 'beginner'
            level = 'beginner'

        self.model = GameModel(file_name, level)

        # If the board is invalid, prompt the user again
        if self.model.invalid_board:
            messagebox.showinfo("Invalid Board", "The test board was invalid. Restarting the game.")
            # Restart the game
            main()
            return

        # Initialize view
        if view_type == 'gui':
            self.view = GUIView(self, self.model)
        else:
            self.view = TextView(self, self.model)

    def start_game(self):
        """
        Starts the game by invoking the view's start method.
        """
        self.view.start()

    def handle_left_click(self, x, y):
        """
        Handles a left-click action on the cell at (x, y).

        Args:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
        """
        cell = self.model.cells[(x, y)]
        if self.model.start_time is None:
            self.model.start_time = datetime.now()
        if cell.state == STATE_CLICKED or self.model.game_over:
            return
        if cell.is_mine:
            cell.state = STATE_CLICKED
            self.model.game_over = True
            self.view.update_cell(cell)
            self.game_over(won=False)
        elif cell.is_treasure:
            cell.state = STATE_CLICKED
            self.model.game_over = True
            self.view.update_cell(cell)
            self.game_over(won=True, treasure_found=True)
        else:
            self.clear_cell(cell)
            if self.model.clicked_count == (self.model.SIZE_X * self.model.SIZE_Y) - self.model.mines - self.model.treasures:
                self.game_over(won=True)

    def handle_right_click(self, x, y):
        """
        Handles a right-click action (flag/unflag) on the cell at (x, y).

        Args:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
        """
        cell = self.model.cells[(x, y)]
        if self.model.start_time is None:
            self.model.start_time = datetime.now()
        if cell.state == STATE_DEFAULT:
            cell.state = STATE_FLAGGED
            self.model.flag_count += 1
            if cell.is_mine:
                self.model.correct_flag_count += 1
            self.view.update_cell(cell)
        elif cell.state == STATE_FLAGGED:
            cell.state = STATE_DEFAULT
            self.model.flag_count -= 1
            if cell.is_mine:
                self.model.correct_flag_count -= 1
            self.view.update_cell(cell)

    def clear_cell(self, cell):
        """
        Clears the cell and recursively clears neighboring cells if necessary.

        Args:
            cell (Cell): The cell to clear.
        """
        if cell.state != STATE_DEFAULT or cell.is_treasure:
            return
        cell.state = STATE_CLICKED
        self.model.clicked_count += 1
        self.view.update_cell(cell)
        if cell.adjacent_mines == 0:
            for neighbor in self.model.get_neighbors(cell.x, cell.y):
                self.clear_cell(neighbor)

    def game_over(self, won, treasure_found=False):
        """
        Handles the game over condition.

        Args:
            won (bool): True if the player won, False otherwise.
            treasure_found (bool): True if the treasure was found, False otherwise.
        """
        self.model.game_over = True
        self.view.show_game_over(won, treasure_found)

# ------------------ Views ------------------

class GUIView:
    """
    View: Handles the GUI using Tkinter.

    Args:
        controller (GameController): The game controller.
        model (GameModel): The game model.

    Preconditions:
        - controller is not None
        - model is not None

    Postconditions:
        - The GUI is initialized and ready to start.
    """
    def __init__(self, controller, model):
        self.controller = controller
        self.model = model
        self.tk = Tk()
        self.tk.title("Minesweeper")
        self.frame = Frame(self.tk)
        self.frame.pack()
        self.images = {
            "plain": PhotoImage(file="images/tile_plain.gif"),
            "clicked": PhotoImage(file="images/tile_clicked.gif"),
            "mine": PhotoImage(file="images/tile_mine.gif"),
            "flag": PhotoImage(file="images/tile_flag.gif"),
            "wrong": PhotoImage(file="images/tile_wrong.gif"),
            "treasure": PhotoImage(file="images/treasure.gif"),
            "numbers": []
        }
        for i in range(1, 9):
            self.images["numbers"].append(PhotoImage(file="images/tile_" + str(i) + ".gif"))

        # Set up labels/UI
        self.labels = {
            "time": Label(self.frame, text="00:00:00"),
            "mines": Label(self.frame, text="Mines: " + str(self.model.mines)),
            "flags": Label(self.frame, text="Flags: 0")
        }
        self.labels["time"].grid(row=0, column=0, columnspan=self.model.SIZE_Y)
        self.labels["mines"].grid(row=self.model.SIZE_X + 1, column=0, columnspan=int(self.model.SIZE_Y / 2))
        self.labels["flags"].grid(row=self.model.SIZE_X + 1, column=int(self.model.SIZE_Y / 2) - 1, columnspan=int(self.model.SIZE_Y / 2))

        self.buttons = {}
        for x in range(self.model.SIZE_X):
            for y in range(self.model.SIZE_Y):
                cell = self.model.cells[(x, y)]
                button = Button(self.frame, image=self.images["plain"])
                button.bind(BTN_CLICK, self.on_left_click_wrapper(x, y))
                button.bind(BTN_FLAG, self.on_right_click_wrapper(x, y))
                button.grid(row=x + 1, column=y)
                self.buttons[(x, y)] = button

        self.update_timer()

    def start(self):
        """
        Starts the GUI event loop.
        """
        self.tk.mainloop()

    def on_left_click_wrapper(self, x, y):
        return lambda event: self.controller.handle_left_click(x, y)

    def on_right_click_wrapper(self, x, y):
        return lambda event: self.controller.handle_right_click(x, y)

    def update_cell(self, cell):
        """
        Updates the visual representation of a cell.

        Args:
            cell (Cell): The cell to update.
        """
        button = self.buttons[(cell.x, cell.y)]
        if cell.state == STATE_CLICKED:
            if cell.is_mine:
                button.config(image=self.images["mine"])
            elif cell.is_treasure:
                button.config(image=self.images["treasure"])
            elif cell.adjacent_mines == 0:
                button.config(image=self.images["clicked"])
            else:
                button.config(image=self.images["numbers"][cell.adjacent_mines - 1])
        elif cell.state == STATE_FLAGGED:
            button.config(image=self.images["flag"])
        else:
            button.config(image=self.images["plain"])
        self.labels["flags"].config(text="Flags: " + str(self.model.flag_count))

    def show_game_over(self, won, treasure_found=False):
        """
        Displays the game over message and handles game restart.

        Args:
            won (bool): True if the player won, False otherwise.
            treasure_found (bool): True if the treasure was found, False otherwise.
        """
        for cell in self.model.cells.values():
            button = self.buttons[(cell.x, cell.y)]
            if cell.is_mine and cell.state != STATE_FLAGGED:
                button.config(image=self.images["mine"])
            elif not cell.is_mine and cell.state == STATE_FLAGGED:
                button.config(image=self.images["wrong"])
            elif cell.is_treasure and cell.state != STATE_CLICKED:
                button.config(image=self.images["treasure"])
        self.tk.update()
        
        if treasure_found:
            msg = "You found the treasure! You Win! Play again?"
        else:
            msg = "You Win! Play again?" if won else "You Lose! Play again?"
        res = messagebox.askyesno("Game Over", msg)
        if res:
            self.tk.destroy()
            main()
        else:
            self.tk.quit()

    def update_timer(self):
        """
        Updates the game timer displayed in the GUI.
        """
        ts = "00:00:00"
        if self.model.start_time:
            delta = datetime.now() - self.model.start_time
            ts = str(delta).split('.')[0]
            if delta.total_seconds() < 36000:
                ts = "0" + ts
        self.labels["time"].config(text=ts)
        if not self.model.game_over:
            self.frame.after(100, self.update_timer)

# ----------- Text-based View ------------

class TextView:
    """
    View: Handles the text-based interface.

    Args:
        controller (GameController): The game controller.
        model (GameModel): The game model.

    Preconditions:
        - controller is not None
        - model is not None
    """
    def __init__(self, controller, model):
        self.controller = controller
        self.model = model

    def start(self):
        """
        Starts the text-based game loop.
        """
        print("Welcome to Minesweeper!")
        while not self.model.game_over:
            self.display_board()
            action = input("Enter action (l for left-click, r for right-click) followed by coordinates x y: ")
            parts = action.strip().split()
            if len(parts) != 3:
                print("Invalid input. Please enter action and coordinates, e.g., 'l 1 2'")
                continue
            act, x_str, y_str = parts
            try:
                x = int(x_str)
                y = int(y_str)
                if not (0 <= x < self.model.SIZE_X and 0 <= y < self.model.SIZE_Y):
                    print("Coordinates out of bounds.")
                    continue
                if act.lower() == 'l':
                    self.controller.handle_left_click(x, y)
                elif act.lower() == 'r':
                    self.controller.handle_right_click(x, y)
                else:
                    print("Invalid action. Use 'l' for left-click or 'r' for right-click.")
            except ValueError:
                print("Invalid coordinates. Please enter integers.")
        self.display_board()
        if self.model.game_over:
            if self.controller.model.clicked_count == (self.model.SIZE_X * self.model.SIZE_Y) - self.model.mines - self.model.treasures:
                print("Congratulations! You've won!")
            else:
                print("Game Over!")

    def display_board(self):
        """
        Displays the current state of the game board.
        """
        print("Current Board:")
        for x in range(self.model.SIZE_X):
            row = ''
            for y in range(self.model.SIZE_Y):
                cell = self.model.cells[(x, y)]
                if cell.state == STATE_DEFAULT:
                    row += '. '
                elif cell.state == STATE_FLAGGED:
                    row += 'F '
                elif cell.state == STATE_CLICKED:
                    if cell.is_mine:
                        row += 'M '
                    elif cell.is_treasure:
                        row += 'T '
                    elif cell.adjacent_mines > 0:
                        row += f'{cell.adjacent_mines} '
                    else:
                        row += '  '
            print(row)
        print(f"Flags: {self.model.flag_count}, Mines: {self.model.mines}")

    def update_cell(self, cell):
        """
        Updates the visual representation of a cell (not needed in text view).
        """
        pass  # For text view, the board is redrawn each time

    def show_game_over(self, won, treasure_found=False):
        """
        Displays the game over message.

        Args:
            won (bool): True if the player won, False otherwise.
            treasure_found (bool): True if the treasure was found, False otherwise.
        """
        if treasure_found:
            print("You found the treasure! You Win!")
        elif won:
            print("You Win!")
        else:
            print("You Lose!")

# ------------------ Main Execution ------------------

def main():
    # Choosing the game type (test or normal)
    game_type = simpledialog.askstring("Select Game", "Enter game type (test, play):")
    if game_type is None or game_type.lower() not in ['test', 'play']:
        game_type = 'play'  # Default to normal gameplay

    file_name = None
    if game_type == 'test':
        file_name = simpledialog.askstring("Enter file name", "Enter test board file name (without extension):")
        if file_name is None:
            messagebox.showinfo("No File", "No file provided. Switching to normal mode.")
            game_type = 'play'
            file_name = None

    # Choosing the view type
    view_type = simpledialog.askstring("Select View", "Enter view type (gui, text):")
    if view_type is None or view_type.lower() not in ['gui', 'text']:
        view_type = 'gui'  # Default to GUI

    controller = GameController(file_name=file_name, view_type=view_type.lower())
    if not controller.model.invalid_board:
        controller.start_game()

if __name__ == "__main__":
    main()
