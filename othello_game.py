#!/usr/bin/env python3
"""
🎮 OTHELLO (Reversi) 8x8 - Game đánh cờ lật
Luật chơi: Lật các quân cờ đối phương bằng cách bao vây
"""

import os
import random
import time

class OthelloBoard:
    def __init__(self):
        """Khởi tạo bàn cờ 8x8"""
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.current_player = 1  # 1 = Black (●), -1 = White (○)
        
        # Setup vị trí ban đầu
        self.board[3][3] = -1  # White
        self.board[3][4] = 1   # Black
        self.board[4][3] = 1   # Black
        self.board[4][4] = -1  # White
        
        self.directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    
    def print_board(self):
        """In bàn cờ ra màn hình"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("🎮 OTHELLO (Cờ Lật) 8x8")
        print("=" * 40)
        print("   A B C D E F G H")
        
        for i in range(8):
            row = f"{i+1}  "
            for j in range(8):
                if self.board[i][j] == 1:
                    row += "● "  # Black
                elif self.board[i][j] == -1:
                    row += "○ "  # White
                else:
                    row += ". "  # Empty
            print(row)
        
        # Hiển thị điểm số
        black_count = sum(row.count(1) for row in self.board)
        white_count = sum(row.count(-1) for row in self.board)
        
        print(f"\n● Black: {black_count}  ○ White: {white_count}")
        print(f"Lượt: {'● Black' if self.current_player == 1 else '○ White'}")
        print("=" * 40)
    
    def is_valid_position(self, row, col):
        """Kiểm tra vị trí có hợp lệ không"""
        return 0 <= row < 8 and 0 <= col < 8
    
    def can_flip(self, row, col, direction):
        """Kiểm tra có thể lật quân cờ theo hướng này không"""
        dr, dc = direction
        r, c = row + dr, col + dc
        found_opponent = False
        
        while self.is_valid_position(r, c):
            if self.board[r][c] == 0:  # Ô trống
                return False
            elif self.board[r][c] == -self.current_player:  # Quân đối phương
                found_opponent = True
                r, c = r + dr, c + dc
            elif self.board[r][c] == self.current_player:  # Quân của mình
                return found_opponent
            else:
                return False
        
        return False
    
    def is_valid_move(self, row, col):
        """Kiểm tra nước đi có hợp lệ không"""
        if not self.is_valid_position(row, col) or self.board[row][col] != 0:
            return False
        
        # Kiểm tra có thể lật quân nào không
        for direction in self.directions:
            if self.can_flip(row, col, direction):
                return True
        
        return False
    
    def get_valid_moves(self):
        """Lấy tất cả nước đi hợp lệ"""
        valid_moves = []
        for i in range(8):
            for j in range(8):
                if self.is_valid_move(i, j):
                    valid_moves.append((i, j))
        return valid_moves
    
    def flip_pieces(self, row, col, direction):
        """Lật các quân cờ theo hướng"""
        dr, dc = direction
        r, c = row + dr, col + dc
        pieces_to_flip = []
        
        while self.is_valid_position(r, c):
            if self.board[r][c] == 0:
                break
            elif self.board[r][c] == -self.current_player:
                pieces_to_flip.append((r, c))
                r, c = r + dr, c + dc
            elif self.board[r][c] == self.current_player:
                # Lật tất cả quân cờ trong danh sách
                for flip_r, flip_c in pieces_to_flip:
                    self.board[flip_r][flip_c] = self.current_player
                return True
            else:
                break
        
        return False
    
    def make_move(self, row, col):
        """Thực hiện nước đi"""
        if not self.is_valid_move(row, col):
            return False
        
        # Đặt quân cờ
        self.board[row][col] = self.current_player
        
        # Lật các quân cờ theo tất cả hướng
        for direction in self.directions:
            if self.can_flip(row, col, direction):
                self.flip_pieces(row, col, direction)
        
        # Đổi lượt
        self.current_player = -self.current_player
        return True
    
    def is_game_over(self):
        """Kiểm tra game đã kết thúc chưa"""
        # Kiểm tra cả hai người chơi có nước đi không
        player1_moves = len(self.get_valid_moves())
        
        self.current_player = -self.current_player
        player2_moves = len(self.get_valid_moves())
        self.current_player = -self.current_player
        
        return player1_moves == 0 and player2_moves == 0
    
    def get_winner(self):
        """Xác định người thắng"""
        black_count = sum(row.count(1) for row in self.board)
        white_count = sum(row.count(-1) for row in self.board)
        
        if black_count > white_count:
            return 1  # Black wins
        elif white_count > black_count:
            return -1  # White wins
        else:
            return 0  # Tie

class SimpleAI:
    def __init__(self, difficulty="medium"):
        """AI đơn giản với các mức độ khó"""
        self.difficulty = difficulty
    
    def evaluate_move(self, board, row, col):
        """Đánh giá chất lượng nước đi"""
        score = 0
        
        # Ưu tiên góc (rất quan trọng)
        corners = [(0,0), (0,7), (7,0), (7,7)]
        if (row, col) in corners:
            score += 100
        
        # Tránh vị trí cạnh góc (nguy hiểm)
        corner_adjacent = [(0,1), (1,0), (1,1), (0,6), (1,6), (1,7), 
                          (6,0), (6,1), (7,1), (6,6), (6,7), (7,6)]
        if (row, col) in corner_adjacent:
            score -= 50
        
        # Ưu tiên cạnh
        if row == 0 or row == 7 or col == 0 or col == 7:
            score += 20
        
        # Đếm số quân lật được
        temp_board = [row[:] for row in board.board]
        temp_current = board.current_player
        
        board.make_move(row, col)
        flipped_count = sum(row.count(board.current_player) for row in board.board) - \
                       sum(row.count(board.current_player) for row in temp_board)
        score += flipped_count * 2
        
        # Restore board
        board.board = temp_board
        board.current_player = temp_current
        
        return score
    
    def choose_move(self, board):
        """AI chọn nước đi"""
        valid_moves = board.get_valid_moves()
        
        if not valid_moves:
            return None
        
        if self.difficulty == "easy":
            # Random move
            return random.choice(valid_moves)
        
        elif self.difficulty == "medium":
            # Chọn nước đi tốt nhất dựa trên evaluation
            best_move = None
            best_score = float('-inf')
            
            for row, col in valid_moves:
                score = self.evaluate_move(board, row, col)
                if score > best_score:
                    best_score = score
                    best_move = (row, col)
            
            return best_move
        
        elif self.difficulty == "hard":
            # Minimax đơn giản (depth 2)
            return self.minimax_move(board, valid_moves)
    
    def minimax_move(self, board, valid_moves):
        """Minimax algorithm đơn giản"""
        best_move = None
        best_score = float('-inf')
        
        for row, col in valid_moves:
            # Simulate move
            temp_board = [row[:] for row in board.board]
            temp_current = board.current_player
            
            board.make_move(row, col)
            
            # Evaluate opponent's best response
            opponent_moves = board.get_valid_moves()
            if opponent_moves:
                worst_score = float('inf')
                for opp_row, opp_col in opponent_moves:
                    temp_board2 = [row[:] for row in board.board]
                    temp_current2 = board.current_player
                    
                    board.make_move(opp_row, opp_col)
                    score = self.evaluate_position(board)
                    
                    if score < worst_score:
                        worst_score = score
                    
                    # Restore
                    board.board = temp_board2
                    board.current_player = temp_current2
                
                final_score = worst_score
            else:
                final_score = self.evaluate_position(board)
            
            if final_score > best_score:
                best_score = final_score
                best_move = (row, col)
            
            # Restore board
            board.board = temp_board
            board.current_player = temp_current
        
        return best_move
    
    def evaluate_position(self, board):
        """Đánh giá tổng thể vị trí"""
        ai_color = -1  # AI là White
        player_color = 1  # Player là Black
        
        ai_count = sum(row.count(ai_color) for row in board.board)
        player_count = sum(row.count(player_color) for row in board.board)
        
        return ai_count - player_count

def pos_to_str(row, col):
    """Convert position to string (e.g., (2,3) -> 'D3')"""
    return f"{chr(ord('A') + col)}{row + 1}"

def str_to_pos(move_str):
    """Convert string to position (e.g., 'D3' -> (2,3))"""
    if len(move_str) != 2:
        return None
    
    try:
        col = ord(move_str[0].upper()) - ord('A')
        row = int(move_str[1]) - 1
        
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
    except:
        pass
    
    return None

def show_rules():
    """Hiển thị luật chơi"""
    print("📋 LUẬT CHƠI OTHELLO (Cờ Lật)")
    print("=" * 50)
    print("🎯 Mục tiêu: Có nhiều quân cờ nhất khi hết ô trống")
    print()
    print("📜 Luật:")
    print("1. Mỗi lượt đặt 1 quân cờ vào ô trống")
    print("2. Phải bao vây ít nhất 1 quân đối phương")
    print("3. Tất cả quân bị bao vây sẽ bị lật màu")
    print("4. Nếu không có nước đi hợp lệ thì bỏ lượt")
    print("5. Game kết thúc khi không còn ô trống hoặc cả 2 bên bỏ lượt")
    print()
    print("💡 Chiến thuật:")
    print("• Ưu tiên chiếm góc (rất khó bị lật)")
    print("• Tránh cho đối phương chiếm góc")
    print("• Kiểm soát cạnh bàn cờ")
    print("• Đừng chỉ tập trung vào số lượng quân")
    print()
    input("Nhấn Enter để tiếp tục...")

def main():
    """Main game function"""
    print("🎮 OTHELLO (Cờ Lật) 8x8")
    print("=" * 40)
    print("1. 👤 Chơi với AI")
    print("2. 👥 Chơi 2 người")
    print("3. 📋 Xem luật chơi")
    print("4. 🚪 Thoát")
    print("=" * 40)
    
    choice = input("Chọn chế độ (1-4): ").strip()
    
    if choice == "1":
        play_vs_ai()
    elif choice == "2":
        play_two_players()
    elif choice == "3":
        show_rules()
        main()
    elif choice == "4":
        print("👋 Tạm biệt!")
        return
    else:
        print("❌ Lựa chọn không hợp lệ!")
        time.sleep(1)
        main()

def play_vs_ai():
    """Chơi với AI"""
    print("\n🤖 Chọn độ khó AI:")
    print("1. 😊 Dễ (Random)")
    print("2. 🤔 Trung bình (Smart)")
    print("3. 😈 Khó (Minimax)")
    
    difficulty_choice = input("Chọn độ khó (1-3): ").strip()
    
    if difficulty_choice == "1":
        difficulty = "easy"
    elif difficulty_choice == "2":
        difficulty = "medium"
    elif difficulty_choice == "3":
        difficulty = "hard"
    else:
        difficulty = "medium"
    
    board = OthelloBoard()
    ai = SimpleAI(difficulty)
    
    print(f"\n🎮 Bắt đầu game! Bạn là ● (Black), AI là ○ (White)")
    print("💡 Nhập nước đi theo format: D3, E4, etc.")
    print("💡 Nhập 'help' để xem nước đi hợp lệ, 'quit' để thoát")
    
    while True:
        board.print_board()
        
        if board.is_game_over():
            winner = board.get_winner()
            if winner == 1:
                print("🎉 Bạn thắng!")
            elif winner == -1:
                print("🤖 AI thắng!")
            else:
                print("🤝 Hòa!")
            break
        
        valid_moves = board.get_valid_moves()
        
        # Lượt người chơi
        if board.current_player == 1:
            if not valid_moves:
                print("⏭️  Bạn không có nước đi hợp lệ, bỏ lượt")
                board.current_player = -board.current_player
                input("Nhấn Enter để tiếp tục...")
                continue
            
            while True:
                move_input = input("Nhập nước đi: ").strip().lower()
                
                if move_input == 'quit':
                    print("👋 Tạm biệt!")
                    return
                elif move_input == 'help':
                    print(f"Nước đi hợp lệ: {[pos_to_str(r, c) for r, c in valid_moves]}")
                    continue
                
                pos = str_to_pos(move_input)
                if pos and pos in valid_moves:
                    board.make_move(pos[0], pos[1])
                    print(f"✅ Bạn đã chơi {move_input.upper()}")
                    break
                else:
                    print("❌ Nước đi không hợp lệ! Nhập 'help' để xem nước đi hợp lệ")
        
        # Lượt AI
        else:
            if not valid_moves:
                print("⏭️  AI không có nước đi hợp lệ, bỏ lượt")
                board.current_player = -board.current_player
                input("Nhấn Enter để tiếp tục...")
                continue
            
            print("🤖 AI đang suy nghĩ...")
            time.sleep(1)
            
            ai_move = ai.choose_move(board)
            if ai_move:
                board.make_move(ai_move[0], ai_move[1])
                print(f"🤖 AI chọn: {pos_to_str(ai_move[0], ai_move[1])}")
            
            input("Nhấn Enter để tiếp tục...")
    
    input("Nhấn Enter để quay lại menu...")
    main()

def play_two_players():
    """Chơi 2 người"""
    board = OthelloBoard()
    
    print("\n👥 Chế độ 2 người chơi")
    print("Player 1: ● (Black)")
    print("Player 2: ○ (White)")
    print("💡 Nhập nước đi theo format: D3, E4, etc.")
    
    while True:
        board.print_board()
        
        if board.is_game_over():
            winner = board.get_winner()
            if winner == 1:
                print("🎉 Player 1 (Black) thắng!")
            elif winner == -1:
                print("🎉 Player 2 (White) thắng!")
            else:
                print("🤝 Hòa!")
            break
        
        valid_moves = board.get_valid_moves()
        
        if not valid_moves:
            player_name = "Player 1 (Black)" if board.current_player == 1 else "Player 2 (White)"
            print(f"⏭️  {player_name} không có nước đi hợp lệ, bỏ lượt")
            board.current_player = -board.current_player
            input("Nhấn Enter để tiếp tục...")
            continue
        
        player_name = "Player 1 (●)" if board.current_player == 1 else "Player 2 (○)"
        print(f"Lượt {player_name}")
        print(f"Nước đi hợp lệ: {[pos_to_str(r, c) for r, c in valid_moves]}")
        
        while True:
            move_input = input("Nhập nước đi: ").strip().lower()
            
            if move_input == 'quit':
                print("👋 Tạm biệt!")
                return
            
            pos = str_to_pos(move_input)
            if pos and pos in valid_moves:
                board.make_move(pos[0], pos[1])
                print(f"✅ {player_name} đã chơi {move_input.upper()}")
                break
            else:
                print("❌ Nước đi không hợp lệ!")
    
    input("Nhấn Enter để quay lại menu...")
    main()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        input("Nhấn Enter để thoát...")
