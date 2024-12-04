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

# MVC Components:
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
    """Model: Represents a single cell on the Minesweeper board."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_treasure = False
        self.state = STATE_DEFAULT
        self.adjacent_mines = 0

class GameModel:        
    """
    Model: Represents the game logic and state.
    
    :param self: The GameModel.
    :param level: The game level (beginner, intermediate, or expert.)
    @Requires (file_name &&
        level is in ['beginner', 'intermediate', 'expert'])
    @Ensures (self.level = level &&
        self.SIZE_X = LEVELS[level]['size_x'] &&
        self.SIZE_Y = LEVELS[level]['size_y'] &&
        self.num_mines = LEVELS[level]['mines'] &&
        self.num_treasures = LEVELS[level]['treasures'] &&
        self.flag_count = 0 &&
        self.correct_flag_count = 0 &&
        self.clicked_count = 0 &&
        self.start_time = None &&
        self.cells = {} &&
        self.mines = self.num_mines &
        self.treasures = self.num_treasures &&
        self.game_over = False &&
        (file_name == None && self.setup_board()) || 
            file_name is not None && self.setup_board_from_file(file_name))
        )
    """
    def __init__(self, file_name, level):
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
        
        if file_name == None:
            self.setup_board()
        else:
            self.setup_board_from_file(file_name)

    """
    Sets up the game board with randomly placed mines and treasure(s).
    
    :param self: The GameModel.
    @Requires (true)
    @Ensures(
        len(self.cells) == self.SIZE_X * self.SIZE_Y &&
        sum(1 for cell in self.cells.values() if cell.is_mine) == self.num_mines &&
        sum(1 for cell in self.cells.values() if cell.is_treasure) == 
            self.num_treasures &&
        all(cell.adjacent_mines == self.count_adjacent_mines(cell.x, cell.y) 
            for cell in self.cells.values())
    )
    """
    def setup_board(self):
        # Initialize the board with cells
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
            
    """
    Sets up the game board with randomly placed mines and treasure(s).
    
    @param self: The GameModel instance.
    @param file_name: The name of the CSV file containing board setup data.
    
    @Requires (file_name is not None && self.level == 'beginner')
    @Requires Number of rows and columns in the csv file is 8.
    @Ensures(
        len(self.cells) == self.SIZE_X * self.SIZE_Y and
        self.SIZE_X == 8 and
        self.SIZE_Y == 8 and
        sum(1 for cell in self.cells.values() if cell.is_mine) == num_mines_file and
        sum(1 for cell in self.cells.values() if cell.is_treasure) <= self.num_treasures and
        all(
            cell.adjacent_mines == self.count_adjacent_mines(cell.x, cell.y)
            for cell in self.cells.values()
            ) and
        (self.setup_board() or not self.setup_board())
        )
    """
    def setup_board_from_file(self, file_name):
        if len(file_name) < 4:
            file_name = file_name + '.csv'
        elif (len(file_name) >= 4) & (file_name[len(file_name) - 4:] != '.csv'):
            file_name = file_name + '.csv'
        print(file_name)
        # Initialize the board with cells
        
        file_path = os.path.join("tests", file_name)
        num_mines_file = 0;
        num_treasures_file = 0;
        
        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)  # Use csv.reader instead of DictReader for raw cells
                for row_index, row in enumerate(reader):  # Iterate over rows
                    for col_index, cell_value in enumerate(row):  # Iterate over cells in the row
                        # The following print statement exits for debugging purposes
                        #print(f"Cell[{row_index}][{col_index}]: {cell_value}")
                        
                        #Generate cell
                        cell = Cell(row_index, col_index)
                        # Read values from CSV file by row and column
                        try:
                            value = int(cell_value.strip())  # Convert to integer if possible
                            if value == 1:
                                cell.is_mine = True
                                num_mines_file += 1
                            elif value == 2:
                                cell.is_treasure = True
                                num_treasures_file += 1
                            self.cells[(row_index, col_index)] = cell
                        except ValueError: # Non-integer value found
                            print("Invalid tile detected. Generating random board.")
                            self.setup_board()
                            return
                
                # Adjust mines and treasues
                self.mines = num_mines_file
                self.treasures = num_treasures_file
                
                # Calculate adjacent mines for each cell
                for cell in self.cells.values():
                    cell.adjacent_mines = self.count_adjacent_mines(cell.x, cell.y)
        except FileNotFoundError:
            message = "Cannot find file. Generating random board instead."
            print(message)
            messagebox.showinfo("File Not Found", message)
            self.setup_board()
        except:
            message = "Cannot open file. Generating random board instead."
            messagebox.showinfo("Problem With File", message)
            self.setup_board()

    def count_adjacent_mines(self, x, y):
        count = 0
        for neighbor in self.get_neighbors(x, y):
            if neighbor.is_mine:
                count += 1
        return count

    def get_neighbors(self, x, y):
        neighbors = []
        coords = [
            (x - 1, y - 1),  # top left
            (x - 1, y),      # top middle
            (x - 1, y + 1),  # top right
            (x, y - 1),      # left
            (x, y + 1),      # right
            (x + 1, y - 1),  # bottom left
            (x + 1, y),      # bottom middle
            (x + 1, y + 1),  # bottom right
        ]
        for nx, ny in coords:
            if 0 <= nx < self.SIZE_X and 0 <= ny < self.SIZE_Y:
                neighbors.append(self.cells[(nx, ny)])
        return neighbors

# ------------------ Controller ------------------

class GameController:        
    """
    Controller: Manages the game flow and interactions between model and view.
    This constructor incorporates a test map from a csv file.
    
    :param self: The GameController.
    :param file_name: The name of the test map csv file.
    :param view_type: The gui or text view type.
    @Requires(file_name &&
        (view_type='gui' || view_type='text'))
    @Ensures(((fileName && self.model = GameModel(level)) || 
        (fileName is not None && self.model = GameModel(file_name, 'beginner')) && 
        ((view_type='gui' && self.view = GUIView(self, self.model)) ||
        (view_type='text' && self.view = TextView(self, self.model))))
    """
    def __init__(self, file_name, view_type='gui'):
        # Level selection
        level = None;
        if file_name is None:
            level = simpledialog.askstring("Select Level", "Enter level (beginner, intermediate, expert):")
            if level is None:
                exit()
            level = level.lower()
        if level not in LEVELS:
            level = 'beginner'  # Default to beginner if invalid input


        self.model = GameModel(file_name, level)
        
        # Initialize view
        if view_type == 'gui':
            self.view = GUIView(self, self.model)
        else:
            self.view = TextView(self, self.model)

    def start_game(self):
        self.view.start()

    def handle_left_click(self, x, y):
        cell = self.model.cells[(x, y)]
        if self.model.start_time is None:
            self.model.start_time = datetime.now()
        if cell.state == STATE_CLICKED or self.model.game_over:
            return
        if cell.is_mine:
            cell.state = STATE_CLICKED
            self.model.game_over = True
            self.view.update_cell(cell)
            #time.sleep(0.1)
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
        if cell.state != STATE_DEFAULT or cell.is_treasure:
            return
        cell.state = STATE_CLICKED
        self.model.clicked_count += 1
        self.view.update_cell(cell)
        if cell.adjacent_mines == 0:
            for neighbor in self.model.get_neighbors(cell.x, cell.y):
                self.clear_cell(neighbor)

    def game_over(self, won, treasure_found=False):
        self.model.game_over = True
        self.view.show_game_over(won, treasure_found)

# ------------------ Views ------------------

class GUIView:
    """View: Handles the GUI using Tkinter."""
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
            "numbers": []
        }
        for i in range(1, 9):
            self.images["numbers"].append(PhotoImage(file="images/tile_" + str(i) + ".gif"))

        # set up labels/UI
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
        self.tk.mainloop()

    def on_left_click_wrapper(self, x, y):
        return lambda event: self.controller.handle_left_click(x, y)

    def on_right_click_wrapper(self, x, y):
        return lambda event: self.controller.handle_right_click(x, y)

    def update_cell(self, cell):
        button = self.buttons[(cell.x, cell.y)]
        if cell.state == STATE_CLICKED:
            if cell.is_mine:
                button.config(image=self.images["mine"])
            elif cell.is_treasure:
                button.config(image=self.images["treasure"])  # No specific image for treasure
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
        for cell in self.model.cells.values():
            button = self.buttons[(cell.x, cell.y)]
            if cell.is_mine and cell.state != STATE_FLAGGED:
                button.config(image=self.images["mine"])
            elif not cell.is_mine and cell.state == STATE_FLAGGED:
                button.config(image=self.images["wrong"])
        if treasure_found:


            msg = "You found the treasure! You Win! Play again?"
        else:
            msg = "You Win! Play again?" if won else "You Lose! Play again?"
        res = messagebox.askyesno("Game Over", msg)
        if res:
            self.tk.destroy()
            new_controller = GameController(view_type='gui')
            new_controller.start_game() 
            self.start()
        else:
            self.tk.quit()

    def update_timer(self):
        ts = "00:00:00"
        if self.model.start_time:
            delta = datetime.now() - self.model.start_time
            ts = str(delta).split('.')[0]
            if delta.total_seconds() < 36000:
                ts = "0" + ts
        self.labels["time"].config(text=ts)
        if not self.model.game_over:
            self.frame.after(100, self.update_timer)

# ----------- Text-based View (Newly Implemented) ------------

class TextView:
    """View: Handles the text-based interface."""
    def __init__(self, controller, model):
        self.controller = controller
        self.model = model

    def start(self):
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
        pass  # For text view, l the board is redrawn each time

    def show_game_over(self, won, treasure_found=False):
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
    
    file_name = None;
    if game_type == 'test':
        file_name = simpledialog.askstring("Enter file name", "Enter file name:")
    
    # Choosing the view type
    view_type = simpledialog.askstring("Select View", "Enter view type (gui, text):")
    if view_type is None or view_type.lower() not in ['gui', 'text']:
        view_type = 'gui'  # Default to GUI

    controller = GameController(file_name=file_name, view_type=view_type.lower())
        
    controller.start_game()

if __name__ == "__main__":
    main()
