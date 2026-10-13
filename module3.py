
import random

def display_board(board):
    print("\n")
    for i in range(3):
        print(" " + " | ".join(board[i * 3:(i + 1) * 3]))
        if i < 2:
            print("---+---+---")
    print()


def get_move(board, player):
    while True:
        try:
            position = int(input(f"Player {player}, enter position (1-9): "))

            if position < 1 or position > 9:
                print("Invalid position! Choose between 1 and 9.")
            elif board[position - 1] in ["X", "O"]:
                print("This position is already occupied! Try again.")
            else:
                return position - 1

        except ValueError:
            print("Please enter a number between 1 and 9.")


def computer_move(board):
    available = [
        i for i in range(9)
        if board[i] not in ["X", "O"]
    ]
    position = random.choice(available)
    print(f"Computer chooses position {position + 1}")
    return position


def check_winner(board, player):
    winning_positions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]

    for a, b, c in winning_positions:
        if board[a] == board[b] == board[c] == player:
            return True

    return False


def check_draw(board):
    return all(cell in ["X", "O"] for cell in board)


def play_game():
    while True:
        board = [str(i) for i in range(1, 10)]

        print("\n===== TIC TAC TOE =====")
        print("1. Player vs Player")
        print("2. Player vs Computer")

        while True:
            mode = input("Choose game mode (1 or 2): ")
            if mode in ["1", "2"]:
                break
            print("Invalid choice! Enter 1 or 2.")

        current_player = "X"

        while True:
            display_board(board)

            if mode == "2" and current_player == "O":
                position = computer_move(board)
            else:
                position = get_move(board, current_player)

            board[position] = current_player

            if check_winner(board, current_player):
                display_board(board)
                if mode == "2" and current_player == "O":
                    print("Computer wins!")
                else:
                    print(f"Player {current_player} wins!")
                break

            if check_draw(board):
                display_board(board)
                print("It's a draw!")
                break

            current_player = "O" if current_player == "X" else "X"

        again = input("\nDo you want to play again? (yes/no): ").lower()
        if again not in ["yes", "y"]:
            print("Thank you for playing Tic Tac Toe!")
            break


if __name__ == "__main__":
    play_game()
