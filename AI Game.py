import tkinter as tk
from tkinter import ttk, font as tkFont
import math
import random

# --- Constants for Styling ---
BG_COLOR = "#2E3440"
FG_COLOR = "#ECEFF4"
BUTTON_COLOR = "#434C5E"
BUTTON_HOVER_COLOR = "#5E81AC"
BUTTON_TEXT_COLOR = "#ECEFF4"
X_COLOR = "#BF616A"
O_COLOR = "#A3BE8C"
WIN_HIGHLIGHT_COLOR = "#EBCB8B"
WIN_FLASH_COLOR = "#D08770"
DEFAULT_FONT = ('Arial', 24, 'bold')
STATUS_FONT = ('Arial', 16)
TITLE_FONT = ('Arial', 28, 'bold')
BUTTON_FONT = ('Arial', 14)

# --- Game Logic (TicTacToe class - Unchanged) ---
class TicTacToe:
    def __init__(self, size=3):
        self.size = size
        self.board = [["" for _ in range(size)] for _ in range(size)]
        self.current_player = "X"

    def make_move(self, row, col, player):
        if 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == "":
            self.board[row][col] = player
            return True
        return False

    def get_available_moves(self):
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == ""]

    def check_winner(self):
        n = self.size
        # Check rows
        for r in range(n):
            if self.board[r][0] != "" and all(self.board[r][c] == self.board[r][0] for c in range(n)):
                return self.board[r][0], "row", r
        # Check columns
        for c in range(n):
            if self.board[0][c] != "" and all(self.board[r][c] == self.board[0][c] for r in range(n)):
                return self.board[0][c], "col", c
        # Check diagonals
        if n > 0 and self.board[0][0] != "" and all(self.board[i][i] == self.board[0][0] for i in range(n)):
            return self.board[0][0], "diag", 0
        if n > 0 and self.board[0][n - 1] != "" and all(self.board[i][n - 1 - i] == self.board[0][n - 1] for i in range(n)):
            return self.board[0][n - 1], "diag", 1
        return None, None, None

    def is_board_full(self):
        return not any("" in row for row in self.board)

    def copy(self):
        new_game = TicTacToe(self.size)
        new_game.board = [row[:] for row in self.board]
        new_game.current_player = self.current_player
        return new_game

# --- AI Logic (MinimaxAI class - Unchanged) ---
class MinimaxAI:
    def __init__(self, game, difficulty="Medium"):
        self.game = game
        self.difficulty = difficulty

    def get_best_move(self):
        if self.difficulty == "Easy":
            available_moves = self.game.get_available_moves()
            return random.choice(available_moves) if available_moves else None
        elif self.difficulty == "Medium" and random.random() < 0.3:
            available_moves = self.game.get_available_moves()
            return random.choice(available_moves) if available_moves else None

        best_score = -math.inf
        best_move = None
        alpha = -math.inf
        beta = math.inf
        available_moves = self.game.get_available_moves()
        if not available_moves: return None

        # Opening book for standard 3x3
        if len(available_moves) == self.game.size * self.game.size and self.game.size == 3:
            center = (1, 1)
            if center in available_moves: return center
            corners = [(0,0), (0, 2), (2, 0), (2, 2)]
            return random.choice(corners)

        random.shuffle(available_moves)

        for move in available_moves:
            row, col = move
            game_copy = self.game.copy()
            game_copy.make_move(row, col, "O")
            score = self.minimax_alpha_beta(game_copy, 0, False, alpha, beta)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if best_score == 1 and self.difficulty != "Easy": return best_move # Optimization
            if beta <= alpha: break

        return best_move if best_move is not None else (available_moves[0] if available_moves else None)

    def minimax_alpha_beta(self, game, depth, is_maximizing_player, alpha, beta):
        winner, _, _ = game.check_winner()
        if winner == "O": return 1
        if winner == "X": return -1
        if game.is_board_full(): return 0

        max_depth = 0
        if self.difficulty == "Medium": max_depth = 4
        elif self.difficulty == "Hard": max_depth = 8 # Adjusted for performance

        if depth >= max_depth and self.difficulty != "Easy": return 0

        if is_maximizing_player:
            best_score = -math.inf
            for r, c in game.get_available_moves():
                game_copy = game.copy(); game_copy.make_move(r, c, "O")
                score = self.minimax_alpha_beta(game_copy, depth + 1, False, alpha, beta)
                best_score = max(score, best_score); alpha = max(alpha, best_score)
                if beta <= alpha: break
            return best_score
        else: # Minimizing player
            best_score = math.inf
            for r, c in game.get_available_moves():
                game_copy = game.copy(); game_copy.make_move(r, c, "X")
                score = self.minimax_alpha_beta(game_copy, depth + 1, True, alpha, beta)
                best_score = min(score, best_score); beta = min(beta, best_score)
                if beta <= alpha: break
            return best_score

# --- Widget Enhancements ---
class AnimatedButton(ttk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_bg = BUTTON_COLOR
        self.hover_bg = BUTTON_HOVER_COLOR

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.config(style="Hover.TButton")

    def on_leave(self, e):
        self.config(style="TButton")

# --- Main GUI Class ---
class TicTacToeGUI:
    def __init__(self, master):
        self.master = master
        master.title("Tic-Tac-Toe")
        master.configure(bg=BG_COLOR)
        master.geometry("700x800")
        master.minsize(600, 700)
        
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        self.game_mode = None
        self.board_size = None
        self.ai_difficulty = None
        self.game = None
        self.ai = None
        self.buttons = []
        self.current_player = "X"
        self.game_over = False
        self.who_starts_next = "X" 
        self.who_starts_round = "X"
        self.move_history = []
        
        self.configure_styles()

        self.main_frame = None
        self.create_menu()

    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure(".", background=BG_COLOR, foreground=FG_COLOR, borderwidth=0, focusthickness=0)
        self.style.layout('TButton', [('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})])

        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("TLabel", padding=10, font=STATUS_FONT, anchor="center", background=BG_COLOR)
        self.style.configure("Title.TLabel", font=TITLE_FONT, padding=(10, 20), foreground=FG_COLOR)
        self.style.configure("Status.TLabel", font=STATUS_FONT, padding=(10, 10))

        self.style.configure("TButton", background=BUTTON_COLOR, foreground=BUTTON_TEXT_COLOR, relief="flat", padding=10, font=BUTTON_FONT)
        self.style.map("TButton", background=[('active', BUTTON_HOVER_COLOR)])
        self.style.configure("Hover.TButton", background=BUTTON_HOVER_COLOR)

        self.style.configure("Game.TButton", font=DEFAULT_FONT, padding=5, width=3, background=BUTTON_COLOR)
        self.style.map("Game.TButton", background=[('active', BUTTON_COLOR), ('disabled', BUTTON_COLOR)])
        
        for player, color in [("X", X_COLOR), ("O", O_COLOR)]:
            style_name = f"{player}.Game.TButton"
            win_style_name = f"{player}.Win.Game.TButton"
            flash_style_name = f"{player}.Flash.Game.TButton"
            
            self.style.configure(style_name, foreground=color)
            self.style.map(style_name, foreground=[('disabled', color)])
            
            self.style.configure(win_style_name, background=WIN_HIGHLIGHT_COLOR, foreground=color)
            self.style.map(win_style_name, background=[('disabled', WIN_HIGHLIGHT_COLOR)], foreground=[('disabled', color)])
            
            self.style.configure(flash_style_name, background=WIN_FLASH_COLOR, foreground=color)
            self.style.map(flash_style_name, background=[('disabled', WIN_FLASH_COLOR)], foreground=[('disabled', color)])

    def clear_screen(self):
        if self.main_frame:
            self.main_frame.destroy()
        self.main_frame = ttk.Frame(self.master, style="TFrame")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

    def create_menu(self):
        self.clear_screen()
        self.game_over = False
        self.who_starts_next = "X"
        
        menu_container = ttk.Frame(self.main_frame, style="TFrame")
        menu_container.pack(expand=True)

        ttk.Label(menu_container, text="Tic-Tac-Toe", style="Title.TLabel").pack(pady=(20, 30))
        ttk.Label(menu_container, text="Select Game Mode:", style="TLabel").pack(pady=10)
        
        AnimatedButton(menu_container, text="Play Against AI", command=self.select_difficulty, width=25).pack(pady=8)
        AnimatedButton(menu_container, text="Two Player", command=self.select_multiplayer_size, width=25).pack(pady=8)
    
    def select_difficulty(self):
        self.game_mode = "AI"
        self.clear_screen()
        
        diff_container = ttk.Frame(self.main_frame, style="TFrame")
        diff_container.pack(expand=True)

        ttk.Label(diff_container, text="Select AI Difficulty", style="Title.TLabel").pack(pady=(20, 30))
        AnimatedButton(diff_container, text="Easy", command=lambda: self.start_ai_game("Easy"), width=20).pack(pady=8)
        AnimatedButton(diff_container, text="Medium", command=lambda: self.start_ai_game("Medium"), width=20).pack(pady=8)
        AnimatedButton(diff_container, text="Hard", command=lambda: self.start_ai_game("Hard"), width=20).pack(pady=8)
        AnimatedButton(diff_container, text="Back", command=self.create_menu, width=20).pack(pady=20)

    def select_multiplayer_size(self):
        self.game_mode = "Multiplayer"
        self.clear_screen()
        
        size_container = ttk.Frame(self.main_frame, style="TFrame")
        size_container.pack(expand=True)

        ttk.Label(size_container, text="Select Board Size", style="Title.TLabel").pack(pady=(20, 30))
        AnimatedButton(size_container, text="3x3", command=lambda: self.start_multiplayer_game(3), width=20).pack(pady=8)
        AnimatedButton(size_container, text="4x4", command=lambda: self.start_multiplayer_game(4), width=20).pack(pady=8)
        AnimatedButton(size_container, text="5x5", command=lambda: self.start_multiplayer_game(5), width=20).pack(pady=8)
        AnimatedButton(size_container, text="Back", command=self.create_menu, width=20).pack(pady=20)

    def start_multiplayer_game(self, size):
        self.board_size = size
        self.ai_difficulty = None
        self.game_mode = "Multiplayer"
        self.who_starts_next = "X"
        self.start_game()

    def start_ai_game(self, difficulty):
        self.game_mode = "AI"
        self.board_size = 3
        self.ai_difficulty = difficulty
        self.start_game()

    def start_game(self, keep_starter=False):
        self.clear_screen()
        self.move_history.clear()
        
        if self.game_mode == "AI":
            if not keep_starter:
                self.who_starts_round = self.who_starts_next
                self.who_starts_next = "O" if self.who_starts_round == "X" else "X"
        else:
            self.who_starts_round = "X"
            
        self.current_player = self.who_starts_round
        self.game = TicTacToe(size=self.board_size)
        self.game.current_player = self.current_player
        if self.game_mode == "AI":
            self.ai = MinimaxAI(self.game, self.ai_difficulty)
        self.game_over = False

        self.create_board_gui()
        self.update_status_label()

        if self.game_mode == "AI" and self.current_player == "O":
            self.master.after(500, self.ai_move)

    def reset_game(self):
        self.start_game(keep_starter=True)

    def create_board_gui(self):
        self.status_label = ttk.Label(self.main_frame, style="Status.TLabel")
        self.status_label.pack(side=tk.TOP, pady=(20, 10), fill=tk.X)

        board_frame = ttk.Frame(self.main_frame, style="TFrame")
        board_frame.pack(expand=True, padx=20, pady=10)

        self.buttons = []
        btn_size = max(60, 450 // self.board_size)
        for i in range(self.board_size):
            board_frame.grid_rowconfigure(i, weight=1, minsize=btn_size)
            board_frame.grid_columnconfigure(i, weight=1, minsize=btn_size)
            row_buttons = []
            for j in range(self.board_size):
                button = ttk.Button(
                    board_frame, text="", style="Game.TButton",
                    command=lambda r=i, c=j: self.player_move(r, c))
                button.grid(row=i, column=j, sticky="nsew", padx=3, pady=3)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

        # In-game controls
        self.ingame_control_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.ingame_control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 20), padx=20)
        self.ingame_control_frame.columnconfigure((0, 1, 2), weight=1)

        self.reset_button = AnimatedButton(self.ingame_control_frame, text="Reset", command=self.reset_game)
        self.reset_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.undo_button = AnimatedButton(self.ingame_control_frame, text="Undo", command=self.undo_move, state=tk.DISABLED)
        self.undo_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.back_button = AnimatedButton(self.ingame_control_frame, text="Back to Menu", command=self.create_menu)
        self.back_button.grid(row=0, column=2, padx=5, sticky="ew")

        # End-game controls (initially hidden)
        self.endgame_control_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.endgame_control_frame.columnconfigure((0, 1), weight=1)

        self.play_again_button = AnimatedButton(self.endgame_control_frame, text="Play Again", command=lambda: self.start_game(keep_starter=False))
        self.back_to_menu_button_end = AnimatedButton(self.endgame_control_frame, text="Back to Menu", command=self.create_menu)

    def update_status_label(self):
        if self.game_over or not self.status_label.winfo_exists(): return
        
        if self.game_mode == "AI":
            text = "Your Turn (X)" if self.current_player == "X" else "AI's Turn (O)..."
            color = X_COLOR if self.current_player == "X" else O_COLOR
        else:
            text = f"Player {self.current_player}'s Turn"
            color = X_COLOR if self.current_player == "X" else O_COLOR
        
        self.status_label.config(text=text, foreground=color)

    def player_move(self, row, col):
        if self.game_over or (self.game_mode == "AI" and self.current_player == "O"):
            return

        player = self.current_player
        if self.game.make_move(row, col, player):
            self.move_history.append((row, col, player))
            self.update_button(row, col, player)
            
            if not self.check_game_end(player):
                self.current_player = "O" if player == "X" else "X"
                self.game.current_player = self.current_player
                self.update_status_label()
                if self.game_mode == "AI" and self.current_player == "O":
                    self.undo_button.config(state=tk.DISABLED)
                    self.master.after(random.randint(400, 700), self.ai_move)
                else: # Multiplayer, enable undo after a move
                    self.undo_button.config(state=tk.NORMAL)

    def ai_move(self):
        if self.game_over or self.current_player != "O": return

        move = self.ai.get_best_move()
        if move:
            row, col = move
            if self.game.make_move(row, col, "O"):
                self.move_history.append((row, col, "O"))
                self.update_button(row, col, "O")
                if not self.check_game_end("O"):
                    self.current_player = "X"
                    self.game.current_player = self.current_player
                    self.update_status_label()
                    self.undo_button.config(state=tk.NORMAL)

    def undo_move(self):
        if self.game_over or not self.move_history:
            return

        if self.game_mode == "AI":
            if len(self.move_history) < 2: return # Can't undo if not a full turn has passed
            # Undo AI move
            r_ai, c_ai, _ = self.move_history.pop()
            self._reset_cell(r_ai, c_ai)
            # Undo Player move
            r_p, c_p, _ = self.move_history.pop()
            self._reset_cell(r_p, c_p)
            self.current_player = "X"
        else: # Multiplayer
            r, c, player = self.move_history.pop()
            self._reset_cell(r, c)
            self.current_player = player

        self.game.current_player = self.current_player
        self.update_status_label()
        if not self.move_history:
            self.undo_button.config(state=tk.DISABLED)

    def _reset_cell(self, r, c):
        self.game.board[r][c] = ""
        button = self.buttons[r][c]
        if button.winfo_exists():
            button.config(text="", state=tk.NORMAL, style="Game.TButton")
    
    def check_game_end(self, last_player):
        winner, line_type, line_index = self.game.check_winner()
        
        if winner:
            self.game_over = True
            self.highlight_winner(winner, line_type, line_index)
            status_text = "You Win!" if winner == "X" and self.game_mode == "AI" else f"AI Wins!" if self.game_mode == "AI" else f"Player {winner} Wins!"
            status_color = X_COLOR if winner == "X" else O_COLOR
            self.status_label.config(text=status_text, foreground=status_color)
            self.show_end_game_buttons()
            return True
        elif self.game.is_board_full():
            self.game_over = True
            self.status_label.config(text="It's a Draw!", foreground=FG_COLOR)
            self.show_end_game_buttons()
            return True
        return False

    def highlight_winner(self, winner, line_type, line_index, flashes=5):
        win_buttons = []
        if line_type == "row":
            win_buttons = [self.buttons[line_index][j] for j in range(self.board_size)]
        elif line_type == "col":
            win_buttons = [self.buttons[i][line_index] for i in range(self.board_size)]
        elif line_type == "diag":
            if line_index == 0:
                win_buttons = [self.buttons[i][i] for i in range(self.board_size)]
            else:
                win_buttons = [self.buttons[i][self.board_size - 1 - i] for i in range(self.board_size)]
        
        self.disable_all_buttons()
        
        def flash(count):
            is_flash_style = count % 2 == 1
            style_to_apply = f"{winner}.{'Flash' if is_flash_style else 'Win'}.Game.TButton"
            for btn in win_buttons:
                if btn.winfo_exists():
                    btn.config(style=style_to_apply)
            if count > 0:
                self.master.after(150, lambda: flash(count - 1))
        
        flash(flashes * 2)

    def show_end_game_buttons(self):
        self.ingame_control_frame.pack_forget()
        self.endgame_control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 20), padx=20)
        self.play_again_button.grid(row=0, column=0, padx=10, sticky="ew")
        self.back_to_menu_button_end.grid(row=0, column=1, padx=10, sticky="ew")
        self.disable_all_buttons()

    def update_button(self, row, col, player):
        button = self.buttons[row][col]
        if button.winfo_exists():
            button.config(text=player, style=f"{player}.Game.TButton", state=tk.DISABLED)

    def disable_all_buttons(self):
        for row in self.buttons:
            for button in row:
                if button.winfo_exists():
                    button.config(state=tk.DISABLED)

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    gui = TicTacToeGUI(root)
    root.mainloop()