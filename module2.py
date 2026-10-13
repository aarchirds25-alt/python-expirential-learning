

Skip to content
Using S. B. Jain Institute of Technology, Management and Research Mail with screen readers
Enable desktop notifications for S. B. Jain Institute of Technology, Management and Research Mail.
   OK  No thanks

Conversations
 
Program Policies
Powered by Google
Last account activity: 7 minutes ago
Details
	
Pause mobile notifications while you're using this device
To pause Chat mobile notifications while you’re active on this device, allow your browser to detect if you’re active or away. Click Continue and then Allow when prompted by your browser.

#!/usr/bin/env python3
"""
TIC TAC TOE  -  Python Programming Lab (N-PCCCD304P)
=====================================================
A full-screen, real-game style Tic Tac Toe built with tkinter (ships with Python).

Game flow
    1. Title screen (full screen, animated)
    2. Select mode: 2 Players  /  Vs Computer  (+ difficulty)
    3. 3 - 2 - 1 countdown (horizontal)
    4. Play the game
    5. Winner / draw page  ->  Play Again, Main Menu, Quit

Functions from the presentation are kept by name:
    reset_game, validate_move, check_winner, check_draw, switch_player,
    display_board (drawn on the canvas), get_move, play_game (the game loop)

Controls
    Mouse click  : buttons / cells          1-9 : choose a cell (same numbering as the PPT)
    ENTER/SPACE  : start / play again       ESC : back (quit on title screen)
    F11          : toggle full screen / window
"""

import math
import random
import threading
import time
import tkinter as tk

try:                                # sound effects on Windows only (optional)
    import winsound
except ImportError:                 # macOS / Linux: silent
    winsound = None

# --------------------------------------------------------------------------
#  Look & feel
# --------------------------------------------------------------------------
BG, BG2 = "#080c1c", "#0d1330"
PANEL, PANEL_HI, EDGE = "#131c3d", "#1d2b5e", "#27336b"
TEXT, MUTED = "#f4f6ff", "#8592c2"
X_COL, O_COL = "#ff4d6d", "#3ad6ff"
GLOW_X, GLOW_O = "#5c1b2f", "#0f4357"
GHOST_X, GHOST_O = "#4a2340", "#183d5c"
GOLD, GREEN, PURPLE = "#ffd166", "#5ef2a0", "#9b7bff"
FONT = "Helvetica"

VW, VH = 1600, 900                  # virtual canvas, scaled to any screen size

# --------------------------------------------------------------------------
#  Game logic  (same functions as in the presentation)
# --------------------------------------------------------------------------
EMPTY = " "
WIN_LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8),      # 3 rows
             (0, 3, 6), (1, 4, 7), (2, 5, 8),      # 3 columns
             (0, 4, 8), (2, 4, 6)]                 # 2 diagonals


def reset_game():
    """Clear the board: a list of 9 empty slots."""
    return [EMPTY] * 9


def validate_move(board, move):
    """Range check + occupied check.  Returns (is_valid, message)."""
    if not isinstance(move, int) or not 1 <= move <= 9:
        return False, "Choose a cell from 1 to 9"
    if board[move - 1] != EMPTY:
        return False, "That cell is already taken!"
    return True, ""


def check_winner(board):
    """Return (winner, winning_line) or (None, None)."""
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    return None, None


def check_draw(board):
    """Board full and nobody has won."""
    return EMPTY not in board and check_winner(board)[0] is None


def switch_player(player):
    return "O" if player == "X" else "X"


# ----- computer opponent ----------------------------------------------------
def minimax(board, player, me, depth):
    winner, _ = check_winner(board)
    if winner == me:
        return 10 - depth
    if winner:
        return depth - 10
    if EMPTY not in board:
        return 0
    scores = []
    for i in range(9):
        if board[i] == EMPTY:
            board[i] = player
            scores.append(minimax(board, switch_player(player), me, depth + 1))
            board[i] = EMPTY
    return max(scores) if player == me else min(scores)


def quick_move(board, me):
    """Win if possible, otherwise block, otherwise None."""
    for who in (me, switch_player(me)):
        for i in range(9):
            if board[i] == EMPTY:
                board[i] = who
                won = check_winner(board)[0] == who
                board[i] = EMPTY
                if won:
                    return i
    return None


def computer_move(board, me, level):
    empty = [i for i in range(9) if board[i] == EMPTY]
    if level == "easy":
        return random.choice(empty)
    if level == "medium":
        move = quick_move(board, me)
        return move if move is not None else random.choice(empty)
    if len(empty) == 9:                                   # hard: opening move
        return random.choice([0, 2, 4, 6, 8])
    best, choices = -99, []
    for i in empty:
        board[i] = me
        score = minimax(board, switch_player(me), me, 1)
        board[i] = EMPTY
        if score > best:
            best, choices = score, [i]
        elif score == best:
            choices.append(i)
    return random.choice(choices)


# --------------------------------------------------------------------------
#  Tiny sound helper
# --------------------------------------------------------------------------
def play_tones(*notes):
    """notes = (frequency, milliseconds) pairs; plays in the background."""
    if not winsound:
        return

    def run():
        try:
            for f, ms in notes:
                winsound.Beep(f, ms)
        except Exception:
            pass
    threading.Thread(target=run, daemon=True).start()


# --------------------------------------------------------------------------
#  The game
# --------------------------------------------------------------------------
class TicTacToe:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tic Tac Toe")
        self.root.configure(bg=BG)
        self.root.minsize(800, 450)
        self.fullscreen = True
        self.root.attributes("-fullscreen", True)

        self.cv = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.cv.pack(fill="both", expand=True)
        self.W, self.H = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.fit()

        self.cv.bind("<Configure>", self.on_resize)
        self.cv.bind("<Motion>", self.on_motion)
        self.cv.bind("<Button-1>", self.on_click)
        self.root.bind("<Key>", self.on_key)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.vm = (-1000, -1000)          # mouse in virtual coordinates
        self.buttons = []
        self.hovering = False
        self.mode, self.level = "pvp", "hard"
        self.scores = {"X": 0, "O": 0, "D": 0}
        self.starter = "X"
        self.confetti = []
        self.prev = time.time()
        self.dt = 0.03
        self.beeped = -1

        self.bg_symbols = [{"x": random.random(), "y": random.random(),
                            "v": random.uniform(0.008, 0.028), "s": random.uniform(34, 100),
                            "ch": random.choice("XO"), "ph": random.uniform(0, 6.28)}
                           for _ in range(24)]

        self.new_round()
        self.goto("title")
        self.tick()

    # ---------------- window helpers ----------------
    def fit(self):
        self.u = min(self.W / VW, self.H / VH)
        self.ox = (self.W - VW * self.u) / 2
        self.oy = (self.H - VH * self.u) / 2

    def on_resize(self, e):
        self.W, self.H = e.width, e.height
        self.fit()

    def toggle_fullscreen(self, _=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        if not self.fullscreen:
            self.root.geometry("1280x720+60+40")

    def quit(self):
        self.root.destroy()

    def px(self, x):
        return self.ox + x * self.u

    def py(self, y):
        return self.oy + y * self.u

    def inside(self, x1, y1, x2, y2):
        return x1 <= self.vm[0] <= x2 and y1 <= self.vm[1] <= y2

    # ---------------- drawing primitives ----------------
    def text(self, x, y, s, size, color=TEXT, anchor="center"):
        px = -max(6, int(size * self.u))
        return self.cv.create_text(self.px(x), self.py(y), text=s, fill=color, anchor=anchor,
                                   font=(FONT, px, "bold"), justify="center")

    def glow_text(self, x, y, s, size, color, glow, anchor="center"):
        d = max(2, size * 0.03)
        for dx, dy in ((-d, 0), (d, 0), (0, -d), (0, d), (-d, -d), (d, d), (-d, d), (d, -d), (2 * d, 2 * d)):
            self.text(x + dx, y + dy, s, size, glow, anchor)
        self.text(x, y, s, size, color, anchor)

    def line(self, x1, y1, x2, y2, width=4, color=TEXT):
        return self.cv.create_line(self.px(x1), self.py(y1), self.px(x2), self.py(y2),
                                   width=max(1, width * self.u), fill=color, capstyle=tk.ROUND)

    def oval(self, x1, y1, x2, y2, fill="", outline="", width=1):
        return self.cv.create_oval(self.px(x1), self.py(y1), self.px(x2), self.py(y2),
                                   fill=fill, outline=outline, width=max(1, width * self.u) if outline else 0)

    def arc(self, x1, y1, x2, y2, start, extent, width, color):
        return self.cv.create_arc(self.px(x1), self.py(y1), self.px(x2), self.py(y2), start=start,
                                  extent=extent, style="arc", outline=color, width=max(1, width * self.u))

    def rect(self, x1, y1, x2, y2, fill):
        return self.cv.create_rectangle(self.px(x1), self.py(y1), self.px(x2), self.py(y2), fill=fill, outline="")

    def poly(self, pts, fill, outline="", width=1):
        flat = []
        for x, y in pts:
            flat += [self.px(x), self.py(y)]
        return self.cv.create_polygon(flat, fill=fill, outline=outline, width=width)

    def rrect(self, x1, y1, x2, y2, r, fill="", outline="", width=1):
        x1, y1, x2, y2, r = self.px(x1), self.py(y1), self.px(x2), self.py(y2), r * self.u
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2,
               x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.cv.create_polygon(pts, smooth=True, fill=fill, outline=outline,
                                      width=max(1, width * self.u) if outline else 0)

    # ---------------- X and O marks ----------------
    def mark(self, kind, cx, cy, r, prog=1.0, width=20, ghost=False):
        if prog <= 0:
            return
        prog = min(1.0, prog)
        if ghost:
            passes = [(width, GHOST_X if kind == "X" else GHOST_O)]
        else:
            passes = [(width + 14, GLOW_X if kind == "X" else GLOW_O),
                      (width, X_COL if kind == "X" else O_COL)]
        for w, col in passes:
            if kind == "X":
                p1, p2 = min(1, prog * 2), max(0, prog * 2 - 1)
                self.line(cx - r, cy - r, cx - r + 2 * r * p1, cy - r + 2 * r * p1, w, col)
                if p2 > 0:
                    self.line(cx + r, cy - r, cx + r - 2 * r * p2, cy - r + 2 * r * p2, w, col)
            elif prog >= 1:
                self.oval(cx - r, cy - r, cx + r, cy + r, outline=col, width=w)
            else:
                self.arc(cx - r, cy - r, cx + r, cy + r, 90, 359.9 * prog, w, col)

    # ---------------- reusable widgets ----------------
    def button(self, cx, cy, w, h, label, cb, color=PURPLE, size=30):
        x1, y1, x2, y2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        hover = self.inside(x1, y1, x2, y2)
        g = 6 if hover else 0
        if hover:
            self.hovering = True
        self.rrect(x1 - g, y1 - g, x2 + g, y2 + g, 26, fill=color if hover else PANEL, outline=color, width=3)
        self.text(cx, cy, label, size, BG if hover else TEXT)
        self.buttons.append((x1, y1, x2, y2, cb))

    def card(self, cx, cy, w, h, color, title, desc, icon, cb):
        x1, y1, x2, y2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        hover = self.inside(x1, y1, x2, y2)
        lift = -12 if hover else 0
        if hover:
            self.hovering = True
            self.rrect(x1 - 10, y1 - 10 + lift, x2 + 10, y2 + 10 + lift, 40, fill=BG2, outline=color, width=2)
        self.rrect(x1, y1 + lift, x2, y2 + lift, 34, fill=PANEL_HI if hover else PANEL,
                   outline=color if hover else EDGE, width=4 if hover else 2)
        icon(cx, cy + lift - h * 0.14)
        self.text(cx, cy + lift + h * 0.22, title, 46, color)
        self.text(cx, cy + lift + h * 0.36, desc, 22, MUTED)
        self.buttons.append((x1, y1, x2, y2, cb))

    def header(self, title, sub):
        self.glow_text(800, 100, title, 66, TEXT, "#20295a")
        self.text(800, 168, sub, 26, MUTED)

    def back_button(self):
        self.button(150, 838, 220, 62, "<  BACK", self.back, MUTED, 26)

    # ---------------- background ----------------
    def draw_background(self, now):
        W, H = self.W, self.H
        for cx, cy, rad in ((0.15 + 0.03 * math.sin(now * 0.2), 0.2, 0.45),
                            (0.85, 0.85 + 0.03 * math.cos(now * 0.25), 0.5)):
            r = rad * min(W, H)
            self.cv.create_oval(cx * W - r, cy * H - r, cx * W + r, cy * H + r, fill=BG2, outline="")
        for s in self.bg_symbols:
            x = s["x"] * W + math.sin(now * 0.5 + s["ph"]) * 25
            y = ((s["y"] + s["v"] * now) % 1.15 - 0.07) * H
            col = "#22112e" if s["ch"] == "X" else "#0d2138"
            self.cv.create_text(x, y, text=s["ch"], fill=col, font=(FONT, -int(s["s"] * self.u * 1.4), "bold"))

    # ---------------- screen management ----------------
    def goto(self, name):
        self.screen = name
        self.screen_t = time.time()
        self.beeped = -1
        if name == "result":
            self.spawn_confetti()
            if self.winner and not (self.mode == "cpu" and self.winner == "O"):
                play_tones((660, 120), (784, 120), (988, 120), (1319, 300))
            elif not self.winner:
                play_tones((523, 150), (440, 250))
            else:
                play_tones((392, 200), (330, 200), (262, 400))

    def back(self):
        if self.screen == "title":
            self.quit()
        else:
            self.goto({"mode": "title", "level": "mode"}.get(self.screen, "mode"))

    def names(self):
        return ("PLAYER 1", "PLAYER 2") if self.mode == "pvp" else ("YOU", "COMPUTER")

    # ---------------- game flow ----------------
    def new_round(self):
        self.board = reset_game()
        self.turn = self.starter
        self.over, self.winner, self.win_line = False, None, None
        self.anim, self.msg, self.msg_until = {}, "", 0
        self.cpu_at, self.end_t = 0, 0

    def start_match(self, mode, level="hard"):
        self.mode, self.level = mode, level
        self.scores = {"X": 0, "O": 0, "D": 0}
        self.starter = "X"
        self.new_round()
        self.goto("countdown")

    def play_again(self):
        self.starter = switch_player(self.starter)
        self.new_round()
        self.goto("countdown")

    def human_turn(self):
        return self.mode == "pvp" or self.turn == "X"

    def flash(self, msg):
        self.msg, self.msg_until = msg, time.time() + 1.6
        play_tones((200, 120))

    def get_move(self, move):
        """Player picks cell 1-9 (click or keyboard) - validated first."""
        if self.over or not self.human_turn():
            return
        ok, message = validate_move(self.board, move)
        if not ok:
            self.flash(message)
            return
        self.place(move - 1)

    def place(self, i):
        now = time.time()
        self.board[i] = self.turn
        self.anim[i] = now
        play_tones((660 if self.turn == "X" else 520, 70))
        winner, line = check_winner(self.board)
        if winner:
            self.over, self.winner, self.win_line, self.end_t = True, winner, line, now
            self.scores[winner] += 1
        elif check_draw(self.board):
            self.over, self.end_t = True, now
            self.scores["D"] += 1
        else:
            self.turn = switch_player(self.turn)                 # switch_player()
            if self.mode == "cpu" and self.turn == "O":
                self.cpu_at = now + random.uniform(0.6, 1.1)

    # ---------------- input ----------------
    def on_motion(self, e):
        self.vm = ((e.x - self.ox) / self.u, (e.y - self.oy) / self.u)

    def on_click(self, e):
        self.on_motion(e)
        for x1, y1, x2, y2, cb in reversed(self.buttons):
            if self.inside(x1, y1, x2, y2):
                cb()
                return

    def on_key(self, e):
        k = e.keysym
        if k == "Escape":
            self.back()
        elif k in ("Return", "space"):
            if self.screen == "title":
                self.goto("mode")
            elif self.screen == "result":
                self.play_again()
        elif self.screen == "game" and e.char and e.char in "123456789":
            self.get_move(int(e.char))

    # ---------------- main loop ----------------
    def tick(self):
        now = time.time()
        self.dt, self.prev = min(0.1, now - self.prev), now
        self.cv.delete("all")
        self.buttons, self.hovering = [], False
        self.draw_background(now)
        getattr(self, "draw_" + self.screen)(now)
        self.cv.config(cursor="hand2" if self.hovering else "")
        self.root.after(30, self.tick)

    # ======================================================================
    #  SCREENS
    # ======================================================================
    def draw_title(self, now):
        # animated demo board
        s, cx, cy = 230, 800, 225
        cell = s / 3
        for k in (1, 2):
            self.line(cx - s / 2 + k * cell, cy - s / 2 + 8, cx - s / 2 + k * cell, cy + s / 2 - 8, 10, "#2c3a7c")
            self.line(cx - s / 2 + 8, cy - s / 2 + k * cell, cx + s / 2 - 8, cy - s / 2 + k * cell, 10, "#2c3a7c")
        t = now % 6.0
        for idx, kind, t0 in ((0, "X", 0.4), (1, "O", 1.0), (4, "X", 1.6), (2, "O", 2.2), (8, "X", 2.8)):
            r_, c_ = divmod(idx, 3)
            self.mark(kind, cx - s / 2 + c_ * cell + cell / 2, cy - s / 2 + r_ * cell + cell / 2,
                      cell * 0.27, (t - t0) / 0.35, 11)
        if t > 3.4:
            p = min(1, (t - 3.4) / 0.5)
            a, b = (cx - cell, cy - cell), (cx + cell, cy + cell)
            self.line(a[0], a[1], a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p, 9, GOLD)

        # title
        for i, (word, x, col, glow) in enumerate((("TIC", 472, X_COL, GLOW_X),
                                                    ("TAC", 770, TEXT, "#252f63"),
                                                    ("TOE", 1098, O_COL, GLOW_O))):
            self.glow_text(x, 470 + math.sin(now * 2 + i * 0.9) * 8, word, 130, col, glow)
        self.text(800, 565, "T H E   C L A S S I C   3 x 3   B A T T L E", 28, MUTED)

        self.button(800, 665, 430 + math.sin(now * 3) * 10, 92, "START GAME",
                    lambda: self.goto("mode"), GREEN, 40)
        if int(now * 1.6) % 2 == 0:
            self.text(800, 742, "or press ENTER", 22, MUTED)

        self.text(800, 812, "Python Programming Lab (N-PCCCD304P)   |   Guided by Prof. Ashwini Yerlekar", 21, MUTED)
        self.text(800, 846, "Aarchi Prabhakar Ramtekkar   |   CD25063", 21, MUTED)
        self.text(1570, 30, "F11  Full screen / Window      ESC  Quit", 18, MUTED, "e")

    def draw_mode(self, now):
        self.header("SELECT GAME MODE", "Choose how you want to play")

        def icon_pvp(cx, cy):
            b = math.sin(now * 3) * 5
            self.mark("X", cx - 100, cy + b, 42, 1, 16)
            self.mark("O", cx + 100, cy - b, 42, 1, 16)
            self.text(cx, cy, "VS", 30, MUTED)

        def icon_cpu(cx, cy):
            self.mark("X", cx - 105, cy, 42, 1, 16)
            rx = cx + 105                                  # little robot
            self.line(rx, cy - 62, rx, cy - 44, 5, MUTED)
            self.oval(rx - 8, cy - 74, rx + 8, cy - 58, fill=GOLD)
            self.rrect(rx - 52, cy - 44, rx + 52, cy + 46, 18, fill=O_COL)
            blink = 0.25 if int(now * 2.2) % 7 == 0 else 1
            for ex in (-20, 20):
                self.oval(rx + ex - 10, cy - 16, rx + ex + 10, cy - 16 + 20 * blink, fill=BG)
            self.line(rx - 20, cy + 22, rx + 20, cy + 22, 6, BG)

        self.card(470, 490, 520, 440, PURPLE, "2 PLAYERS", "Two friends, one board.\nTake turns as X and O.",
                  icon_pvp, lambda: self.start_match("pvp"))
        self.card(1130, 490, 520, 440, O_COL, "VS COMPUTER", "Test your skills against\nthe computer player.",
                  icon_cpu, lambda: self.goto("level"))
        self.back_button()

    def draw_level(self, now):
        self.header("CHOOSE DIFFICULTY", "How smart should the computer be?")

        def stars(n, col):
            def icon(cx, cy):
                for k in range(3):
                    x = cx + (k - 1) * 70
                    on = k < n
                    self.oval(x - 24, cy - 24, x + 24, cy + 24, fill=col if on else "", outline=col if on else EDGE, width=5)
            return icon

        for x, lv, col, desc in ((300, "easy", GREEN, "Plays random moves.\nGreat for warming up."),
                                 (800, "medium", GOLD, "Takes wins and blocks\nyour winning move."),
                                 (1300, "hard", X_COL, "Unbeatable AI.\nBest you can do is draw!")):
            n = ("easy", "medium", "hard").index(lv) + 1
            self.card(x, 490, 420, 400, col, lv.upper(), desc, stars(n, col),
                      lambda lv=lv: self.start_match("cpu", lv))
        self.back_button()

    def draw_countdown(self, now):
        e = now - self.screen_t
        n1, n2 = self.names()
        self.text(400, 110, f"{n1}  (X)", 40, X_COL)
        self.text(800, 110, "VS", 34, MUTED)
        self.text(1200, 110, f"{n2}  (O)", 40, O_COL)
        first = n1 if self.starter == "X" else n2
        self.text(800, 175, "YOU go first" if first == "YOU" else f"{first} goes first", 28, MUTED)

        if e < 3:
            step = int(e)
            frac = e - step
            cols = (X_COL, GOLD, GREEN)
            if step != self.beeped:
                self.beeped = step
                play_tones((440, 110))
            for i, n in enumerate("321"):
                cx, cy = 450 + 350 * i, 470
                if i < 2:                                   # connector between circles
                    self.line(cx + 165, cy, cx + 185, cy, 6, cols[i] if i < step else "#1c2650")
                if i == step:
                    k = 1 + 0.25 * max(0, 1 - frac * 3)
                    r = 140 * k
                    ring = 140 + 70 * frac
                    self.oval(cx - ring, cy - ring, cx + ring, cy + ring, outline=cols[i], width=max(1, 6 * (1 - frac)))
                    self.oval(cx - r, cy - r, cx + r, cy + r, fill=cols[i])
                    self.text(cx, cy + 6, n, 210 * k, BG)
                elif i < step:
                    self.oval(cx - 140, cy - 140, cx + 140, cy + 140, outline="#2c3970", width=6)
                    self.text(cx, cy + 6, n, 190, "#34427f")
                else:
                    self.oval(cx - 140, cy - 140, cx + 140, cy + 140, outline="#1c2650", width=6)
                    self.text(cx, cy + 6, n, 190, "#232d5c")
            self.text(800, 720, "GET READY!", 40, MUTED if int(e * 4) % 2 else TEXT)
        else:
            if self.beeped != 99:
                self.beeped = 99
                play_tones((880, 300))
            k = min(1, (e - 3) / 0.25)
            self.glow_text(800, 470, "GO!", 300 * (0.6 + 0.4 * k), GREEN, "#14573a")
            if e > 3.7:
                self.goto("game")
                if self.mode == "cpu" and self.turn == "O":
                    self.cpu_at = time.time() + 0.7

    def score_card(self, cx, cy, w, h, mark, label, score, active, now):
        x1, y1, x2, y2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
        col = X_COL if mark == "X" else O_COL
        pulse = 4 + 2 * math.sin(now * 6) if active else 2
        self.rrect(x1, y1, x2, y2, 26, fill=PANEL_HI if active else PANEL, outline=col if active else EDGE, width=pulse)
        self.mark(mark, x1 + 62, cy, 22, 1, 9)
        self.text(x1 + 112, cy - 20, label, 22, MUTED, "w")
        self.text(x1 + 112, cy + 20, str(score), 46, TEXT, "w")

    def draw_game(self, now):
        n1, n2 = self.names()
        self.score_card(330, 90, 340, 110, "X", n1, self.scores["X"], not self.over and self.turn == "X", now)
        self.score_card(1270, 90, 340, 110, "O", n2, self.scores["O"], not self.over and self.turn == "O", now)
        self.rrect(680, 35, 920, 145, 26, fill=PANEL, outline=EDGE, width=2)
        self.text(800, 70, "DRAWS", 22, MUTED)
        self.text(800, 110, str(self.scores["D"]), 46)

        # computer's turn
        if not self.over and self.mode == "cpu" and self.turn == "O" and now >= self.cpu_at:
            self.place(computer_move(self.board, "O", self.level))

        # status line
        col = X_COL if self.turn == "X" else O_COL
        if self.over:
            status, col = ("IT'S A DRAW!", GOLD) if not self.winner else (f"{self.winner} WINS!", GOLD)
        elif self.mode == "cpu" and self.turn == "O":
            status = "COMPUTER IS THINKING" + "." * (int(now * 3) % 4)
        else:
            who = n1 if self.turn == "X" else n2
            status = "YOUR TURN" if who == "YOU" else f"{who}'S TURN"
        self.text(800, 195, status, 36, col)
        if self.msg and now < self.msg_until:
            self.text(800, 238, self.msg, 24, X_COL)

        # board  (display_board)
        size, gap = 560, 12
        cell = (size - 2 * gap) / 3
        bx, by = 800 - size / 2, 275
        for i in range(9):
            r_, c_ = divmod(i, 3)
            x1, y1 = bx + c_ * (cell + gap), by + r_ * (cell + gap)
            x2, y2 = x1 + cell, y1 + cell
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            can = not self.over and self.human_turn() and self.board[i] == EMPTY
            hover = can and self.inside(x1, y1, x2, y2)
            if hover:
                self.hovering = True
            in_win = self.win_line and i in self.win_line
            self.rrect(x1, y1, x2, y2, 24, fill=PANEL_HI if hover else PANEL,
                       outline=GOLD if in_win else (EDGE if hover else "#1a2450"), width=5 if in_win else 2)
            if self.board[i] == EMPTY:
                self.text(x1 + 22, y1 + 20, str(i + 1), 20, "#2c397a", "nw")
                if hover:
                    self.mark(self.turn, cx, cy, cell * 0.27, 1, 20, ghost=True)
            else:
                self.mark(self.board[i], cx, cy, cell * 0.27, (now - self.anim.get(i, 0)) / 0.25, 20)
            self.buttons.append((x1, y1, x2, y2, lambda i=i: self.get_move(i + 1)))

        # winning line
        if self.win_line:
            def centre(i):
                r_, c_ = divmod(i, 3)
                return bx + c_ * (cell + gap) + cell / 2, by + r_ * (cell + gap) + cell / 2
            (ax, ay), (cx2, cy2) = centre(self.win_line[0]), centre(self.win_line[2])
            p = max(0, min(1, (now - self.end_t - 0.3) / 0.45))
            ex, ey = ax + (cx2 - ax) * p, ay + (cy2 - ay) * p
            self.line(ax, ay, ex, ey, 34, "#6b5320")
            self.line(ax, ay, ex, ey, 16, GOLD)

        self.text(1570, 870, "Click a cell or press 1-9      ESC  Menu", 18, MUTED, "e")

        if self.over and now - self.end_t > (1.9 if self.winner else 1.1):
            self.goto("result")

    # ---------------- winning page ----------------
    def spawn_confetti(self):
        self.confetti = []
        if self.winner and not (self.mode == "cpu" and self.winner == "O"):
            colors = [X_COL, O_COL, GOLD, GREEN, PURPLE, TEXT]
            for _ in range(140):
                self.confetti.append([random.random(), random.uniform(-self.H, 0), random.uniform(120, 300),
                                      random.uniform(8, 16), random.choice(colors), random.uniform(0, 6.28)])

    def trophy(self, cx, cy, now):
        gold, dark = GOLD, "#c99a2e"
        self.arc(cx - 140, cy - 100, cx - 55, cy - 5, 90, 180, 16, gold)
        self.arc(cx + 55, cy - 100, cx + 140, cy - 5, -90, 180, 16, gold)
        self.poly([(cx - 90, cy - 115), (cx + 90, cy - 115), (cx + 80, cy - 20), (cx + 40, cy + 40),
                   (cx - 40, cy + 40), (cx - 80, cy - 20)], gold, dark, 4)
        self.rect(cx - 16, cy + 40, cx + 16, cy + 98, "#e0ae3a")
        self.rrect(cx - 72, cy + 96, cx + 72, cy + 128, 10, fill=dark)
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rad = 30 if k % 2 == 0 else 13
            pts.append((cx + rad * math.cos(ang), cy - 48 + rad * math.sin(ang)))
        self.poly(pts, "#fff3c4")
        for k in range(4):                                  # sparkles
            a = now * 1.5 + k * math.pi / 2
            sx, sy = cx + 170 * math.cos(a), cy - 10 + 90 * math.sin(a)
            sz = 8 + 6 * math.sin(now * 5 + k)
            self.line(sx - sz, sy, sx + sz, sy, 4, TEXT)
            self.line(sx, sy - sz, sx, sy + sz, 4, TEXT)

    def draw_result(self, now):
        e = now - self.screen_t
        for c in self.confetti:                             # confetti rain
            c[1] += c[2] * self.dt
            if c[1] > self.H + 20:
                c[1] = -20
            x = c[0] * self.W + math.sin(now * 2 + c[5]) * 30
            self.cv.create_rectangle(x, c[1], x + c[3], c[1] + c[3] * 0.6, fill=c[4], outline="")

        n1, n2 = self.names()
        pop = min(1, e / 0.5)
        pop = 1 - (1 - pop) ** 3
        if self.winner:
            cpu_won = self.mode == "cpu" and self.winner == "O"
            name = n1 if self.winner == "X" else n2
            title = "YOU WIN!" if name == "YOU" else f"{name} WINS!"
            col = X_COL if self.winner == "X" else O_COL
            sub = "Better luck next time!" if cpu_won else "Three in a row - well played!"
            if cpu_won:
                self.mark(self.winner, 800, 250 + math.sin(now * 3) * 6, 70, 1, 28)
            else:
                self.trophy(800, 245 + math.sin(now * 3) * 8, now)
            self.glow_text(800, 470, title, 100 * (0.5 + 0.5 * pop), col, GLOW_X if self.winner == "X" else GLOW_O)
        else:
            sub = "Evenly matched - nobody wins this one."
            self.mark("X", 690, 250, 62, 1, 26)
            self.mark("O", 910, 250, 62, 1, 26)
            self.text(800, 250, "=", 70, MUTED)
            self.glow_text(800, 470, "IT'S A DRAW!", 100 * (0.5 + 0.5 * pop), GOLD, "#5a4519")
        self.text(800, 550, sub, 30, MUTED)
        self.text(800, 615, f"{n1}  {self.scores['X']}      DRAWS  {self.scores['D']}      {n2}  {self.scores['O']}",
                  30, TEXT)
        self.button(450, 735, 340, 88, "PLAY AGAIN", self.play_again, GREEN, 32)
        self.button(800, 735, 340, 88, "MAIN MENU", lambda: self.goto("mode"), PURPLE, 32)
        self.button(1150, 735, 340, 88, "QUIT", self.quit, X_COL, 32)
        self.text(800, 850, "Press ENTER to play again", 20, MUTED)

    # ---------------- run ----------------
    def play_game(self):
        self.root.mainloop()


if __name__ == "__main__":
    TicTacToe().play_game()
python.py
Displaying python.py.