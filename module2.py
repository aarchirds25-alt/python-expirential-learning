class TicTacToe:
    def __init__(self):
        self.board = [str(i) for i in range(1, 10)]
        self.current_player = "X"

    def display_board(self):
        for i in range(0, 9, 3):
            print(" | ".join(self.board[i:i + 3]))
            if i < 6:
                print("--+---+--")

    def make_move(self, position):
        if position < 1 or position > 9:
            print("Invalid position!")
            return False

        if self.board[position - 1] in ["X", "O"]:
            print("Position already occupied!")
            return False

        self.board[position - 1] = self.current_player
        return True

    def check_winner(self):
        winning_positions = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6)
        ]

        for a, b, c in winning_positions:
            if self.board[a] == self.board[b] == self.board[c]:
                return True

        return False

    def check_draw(self):
        return all(cell in ["X", "O"] for cell in self.board)

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"

    def reset_game(self):
        self.board = [str(i) for i in range(1, 10)]
        self.current_player = "X"

    def play_game(self):
        while True:
            self.display_board()

            try:
                position = int(input(
                    f"Player {self.current_player}, enter position (1-9): "
                ))
            except ValueError:
                print("Please enter a valid number.")
                continue

            if not self.make_move(position):
                continue

            if self.check_winner():
                self.display_board()
                print(f"Player {self.current_player} wins!")
            elif self.check_draw():
                self.display_board()
                print("It's a draw!")
            else:
                self.switch_player()
                continue

            again = input("Play again? (yes/no): ").lower()
            if again not in ["yes", "y"]:
                break

            self.reset_game()


if __name__ == "__main__":
    game = TicTacToe()
    game.play_game()
