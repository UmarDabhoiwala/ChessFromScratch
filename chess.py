import tkinter as tk
from PIL import Image, ImageTk

black_board = [
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
]

board = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
]

pieces_images = {
    'K': 'assets/white_king.png',
    'Q': 'assets/white_queen.png',
    'B': 'assets/white_bishop.png',
    'N': 'assets/white_knight.png',
    'R': 'assets/white_rook.png',
    'P': 'assets/white_pawn.png',
    'k': 'assets/black_king.png',
    'q': 'assets/black_queen.png',
    'b': 'assets/black_bishop.png',
    'n': 'assets/black_knight.png',
    'r': 'assets/black_rook.png',
    'p': 'assets/black_pawn.png',
}

root = tk.Tk()
root.title("Chess Game")

current_turn = 'W'

moves_taken = []

def switch_turn():
    global current_turn
    current_turn = 'W' if current_turn == 'B' else 'B'
    turn_label.config(text="Turn: " + ("White" if current_turn == 'W' else "Black"))


turn_label = tk.Label(root, text="Turn: White", font=("Helvetica", 14))
turn_label.grid(row=0, column=8, rowspan=2, sticky='nw')

def draw_board():
    for row in range(8):
        for col in range(8):
            color = "white" if (row + col) % 2 == 0 else "gray"
            square = tk.Frame(root, width=60, height=60, bg=color)
            square.grid(row=row, column=col)
            square.bind("<Button-1>", lambda event, r=row, c=col: on_square_click(r, c)) # Notice the change here
            piece = board[row][col]
            if piece != '.':
                image_path = pieces_images[piece]
                photo = tk.PhotoImage(file=image_path)
                label = tk.Label(square, image=photo, bg=color)
                label.photo = photo  # Keep a reference to prevent garbage collection
                label.pack()
                label.bind("<Button-1>", lambda event, row=row, col=col: on_square_click(row, col))  # Use named arguments
            else:
                square.bind("<Button-1>", lambda event, row=row, col=col: on_square_click(row, col)) # Use named arguments


selected_piece = None

def select_piece(row, col, piece):
    global selected_piece
    if selected_piece and selected_piece[0] == row and selected_piece[1] == col:
        selected_piece = None  # Deselect the piece if already selected
        clear_highlighted_squares()
    else:
        selected_piece = (row, col, piece)

def on_square_click(row, col):
    global highlighted_squares, selected_piece
    piece = board[row][col]
    
    # Early Return if we click other persons piece
    if piece != '.' and (current_turn == 'W' and piece.islower()) or (current_turn == 'B' and piece.isupper()):
        return
    
    if selected_piece:
        src_row, src_col, _ = selected_piece
        if (row, col) in highlighted_squares:
            make_move(row, col)
            clear_highlighted_squares()  # Clear the highlighted squares
            return
        else:
            clear_highlighted_squares()  # If the clicked square is not a valid move, clear highlights

    if piece != '.':
        highlight_valid_moves(row, col, piece)
        select_piece(row, col, piece)
        

def clear_highlighted_squares():
    global highlighted_squares
    for highlight in highlighted_squares:
        highlight_row, highlight_col = highlight[:2]
        color = "white" if (highlight_row + highlight_col) % 2 == 0 else "gray"
        square = root.grid_slaves(row=highlight_row, column=highlight_col)[0]
        square.config(bg=color)
        # Remove red overlay if present
        if len(highlight) == 3:
            highlight[2].destroy()
    highlighted_squares = []  # Reset the list of highlighted squares


# Keep track of the highlighted squares
highlighted_squares = []

def create_red_overlay_with_piece(piece_image):
    red_overlay = Image.new('RGBA', (60, 60), (255, 0, 0, 100))
    combined_image = Image.alpha_composite(piece_image.convert('RGBA'), red_overlay)
    return ImageTk.PhotoImage(combined_image)

def highlight_valid_moves(row, col, piece):
    global highlighted_squares
    # Clear previous highlights
    clear_highlighted_squares()
    
    valid_moves = get_moves(row, col, piece)
    
    # Highlight the valid moves
    for move_row, move_col in valid_moves:
        square = root.grid_slaves(row=move_row, column=move_col)[0]
        if is_enemy(piece, board[move_row][move_col]):
           
            # Get the image of the target piece
            target_piece = board[move_row][move_col]
            piece_image_path = pieces_images[target_piece]
            piece_image = Image.open(piece_image_path)

            # Create a combined red overlay and piece image
            red_overlay_image = create_red_overlay_with_piece(piece_image)

            red_overlay = tk.Label(square, image=red_overlay_image)
            red_overlay.image = red_overlay_image
            red_overlay.bind("<Button-1>", lambda event, r=move_row, c=move_col: capture_piece(r, c))
            red_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            highlighted_squares.append((move_row, move_col, red_overlay))
        else:
            color = "yellow"
            square.config(bg=color)
            highlighted_squares.append((move_row, move_col)) 


def is_enemy(piece1, piece2):
    return (piece1.isupper() and piece2.islower()) or (piece1.islower() and piece2.isupper())


def capture_piece(dest_row, dest_col):
    global selected_piece
    if selected_piece:
        make_move(dest_row, dest_col)
        clear_highlighted_squares()
        
def get_moves(row, col, piece):
    if piece in 'Pp':  # Pawn
        return pawn_moves(row, col, piece)
    elif piece in 'Rr':  # Rook
        return rook_moves(row, col)
    elif piece in 'Nn':  # Knight
        return knight_moves(row, col)
    elif piece in 'Bb':  # Bishop
        return bishop_moves(row, col)
    if piece in 'Kk':  # King
        return king_moves(row, col)
    elif piece in 'Qq':  # Queen
        return queen_moves(row, col)

    return []  # Should never happen

def pawn_moves(row, col, piece):
    moves = []
    forward = -1 if piece.isupper() else 1
    start_row = 6 if piece.isupper() else 1
    next_row = row + forward

    # Allow two-square move if on starting row
    if row == start_row and board[next_row][col] == '.' and board[next_row + forward][col] == '.':
        moves.append((next_row + forward, col))

    # Regular forward move
    if 0 <= next_row < 8 and board[next_row][col] == '.':
        moves.append((next_row, col))

    # Capturing logic for pawns
    for capture_col in [col - 1, col + 1]:
        if 0 <= capture_col < 8 and is_enemy(piece, board[next_row][capture_col]):
            moves.append((next_row, capture_col))
    return moves

def add_line_moves(row, col, d_row, d_col, moves):
    for i in range(1, 8):
        next_row = row + i * d_row
        next_col = col + i * d_col
        if 0 <= next_row < 8 and 0 <= next_col < 8:
            square_piece = board[next_row][next_col]
            if square_piece == '.':
                moves.append((next_row, next_col))
            elif is_enemy(board[row][col], square_piece):
                moves.append((next_row, next_col))
                break
            else:
                break
            
def knight_moves(row, col):
    # Simplified knight movement logic
    moves = [(row + 2, col + 1), (row + 2, col - 1), (row - 2, col + 1), (row - 2, col - 1),
             (row + 1, col + 2), (row + 1, col - 2), (row - 1, col + 2), (row - 1, col - 2)]
    return [(r, c) for r, c in moves if 0 <= r < 8 and 0 <= c < 8]

def rook_moves(row, col):
    moves = []
    for d_row, d_col in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        add_line_moves(row, col, d_row, d_col, moves)
    return moves

def bishop_moves(row, col):
    moves = []
    for d_row, d_col in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        add_line_moves(row, col, d_row, d_col, moves)
    return moves

def king_moves(row, col, check_check=True):
    moves = []
    for d_row in range(-1, 2):
        for d_col in range(-1, 2):
            if d_row != 0 or d_col != 0:
                next_row = row + d_row
                next_col = col + d_col
                if 0 <= next_row < 8 and 0 <= next_col < 8:
                    moves.append((next_row, next_col))
    return moves

# def is_king_in_check(row, col, dest_row, dest_col):
#     temp_board = [row[:] for row in board] # Create a copy of the board
#     temp_board[dest_row][dest_col] = temp_board[row][col]
#     temp_board[row][col] = '.'
    
#     king_piece = 'k' if temp_board[dest_row][dest_col].isupper() else 'K'
#     king_row, king_col = find_king(king_piece)

#     # Check all possible enemy moves to see if any target the king
#     for r in range(8):
#         for c in range(8):
#             piece = temp_board[r][c]
#             if piece != '.' and is_enemy(temp_board[dest_row][dest_col], piece):
#                 moves = get_moves(r, c, piece)
#                 if piece in 'Kk':
#                     moves = king_moves(r, c, check_check=False) # Bypass check
#                 if (king_row, king_col) in moves:
#                     return True
#     return False

# def find_king(king_piece):
#     for row in range(8):
#         for col in range(8):
#             if board[row][col] == king_piece:
#                 return row, col
#     return None, None  # Should never happen

def queen_moves(row, col):
    moves = []
    for d_row in range(-1, 2):
        for d_col in range(-1, 2):
            if d_row != 0 or d_col != 0:
                add_line_moves(row, col, d_row, d_col, moves)
    return moves



# A list to keep track of captured pieces
captured_pieces = []

def make_move(dest_row, dest_col):
    global selected_piece, captured_pieces
    
    src_row, src_col, piece = selected_piece
    target_piece = board[dest_row][dest_col]
    
    # If the target square contains an enemy piece, capture it
    if is_enemy(piece, target_piece):
        captured_pieces.append(target_piece)
        # Remove the enemy piece from the destination square
        dest_square = root.grid_slaves(row=dest_row, column=dest_col)[0]
        for widget in dest_square.winfo_children():
            widget.destroy()

    # Update the board array
    board[dest_row][dest_col] = piece
    board[src_row][src_col] = '.'

    # Remove the piece from the source square
    source_square = root.grid_slaves(row=src_row, column=src_col)[0]
    for widget in source_square.winfo_children():
        widget.destroy()
        
    # Add the piece to the destination square
    dest_square = root.grid_slaves(row=dest_row, column=dest_col)[0]
    color = "white" if (dest_row + dest_col) % 2 == 0 else "gray"
    image_path = pieces_images[piece]
    photo = tk.PhotoImage(file=image_path)
    label = tk.Label(dest_square, image=photo, bg=color)
    label.photo = photo  # Keep a reference to prevent garbage collection
    label.pack()

    # Bind the new label to the click event handler
    label.bind("<Button-1>", lambda event, r=dest_row, c=dest_col: on_square_click(r, c))
    
    switch_turn()
    moves_taken.append(f"{selected_piece[2]} from ({src_row}, {src_col}) to ({dest_row}, {dest_col})")

    selected_piece = None

  

draw_board() 
root.mainloop()