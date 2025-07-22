#!/usr/bin/env python3
"""
🎮 OTHELLO GPT GAME - Sử dụng GPT AI từ othello_world project
"""

import os
import torch
import numpy as np
import time
from data import get_othello
from data.othello import OthelloBoardState
from mingpt.model import GPT, GPTConfig
from mingpt.dataset import CharDataset
from mingpt.utils import sample


class OthelloGPTAI:
    def __init__(self, checkpoint_path=None):
        """
        Khởi tạo Othello GPT AI sử dụng model từ othello_world

        Args:
            checkpoint_path: Đường dẫn đến checkpoint GPT model
        """
        print("🤖 Đang khởi tạo Othello GPT AI...")

        # Load data để tạo dataset và vocab
        print("📊 Loading championship data...")
        othello = get_othello(data_root="data/othello_championship")
        self.train_dataset = CharDataset(othello)

        print(f"✅ Dataset: {len(self.train_dataset)} sequences")
        print(f"✅ Vocab size: {self.train_dataset.vocab_size}")
        print(f"✅ Block size: {self.train_dataset.block_size}")

        # Tạo model config
        mconf = GPTConfig(
            self.train_dataset.vocab_size,
            self.train_dataset.block_size,
            n_layer=8,
            n_head=8,
            n_embd=512
        )

        self.model = GPT(mconf)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load checkpoint
        if checkpoint_path and os.path.exists(checkpoint_path):
            print(f"📂 Loading GPT checkpoint: {checkpoint_path}")
            self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
            print("✅ GPT model loaded successfully")
        else:
            # Thử tìm checkpoint có sẵn
            available_checkpoints = [
                "./ckpts/gpt_championship.ckpt",
                "./ckpts/gpt_synthetic.ckpt",
                "./ckpts/gpt_quick.ckpt"
            ]

            loaded = False
            for ckpt in available_checkpoints:
                if os.path.exists(ckpt):
                    print(f"📂 Found checkpoint: {ckpt}")
                    self.model.load_state_dict(torch.load(ckpt, map_location=self.device))
                    print("✅ GPT model loaded successfully")
                    loaded = True
                    break

            if not loaded:
                print("⚠️  No checkpoint found, using random weights")
                print("💡 Model sẽ chơi random, để có AI tốt hơn cần train model")

        self.model.to(self.device)
        self.model.eval()

        param_count = sum(p.numel() for p in self.model.parameters())
        print(f"🧠 GPT Model: {param_count:,} parameters")
        print(f"💻 Device: {self.device}")
        print("✅ Othello GPT AI ready!")

    def predict_next_move(self, game_sequence, temperature=0.8, top_k=10):
        """
        Sử dụng GPT model để predict next move

        Args:
            game_sequence: List các moves đã chơi (integers)
            temperature: Temperature cho sampling
            top_k: Top-k sampling

        Returns:
            predicted_move: Move được predict (integer)
        """
        if len(game_sequence) == 0:
            # First move thường ở giữa
            return 26  # D4

        # Convert sequence to tokens
        tokens = []
        for move in game_sequence:
            if move in self.train_dataset.stoi:
                tokens.append(self.train_dataset.stoi[move])
            else:
                # Fallback cho moves không có trong vocab
                tokens.append(0)

        # Truncate nếu quá dài
        max_len = self.train_dataset.block_size - 1
        if len(tokens) > max_len:
            tokens = tokens[-max_len:]

        # Convert to tensor
        x = torch.tensor(tokens, dtype=torch.long).unsqueeze(0).to(self.device)

        # Generate prediction
        with torch.no_grad():
            # Sample next token
            y = sample(self.model, x, 1, temperature=temperature, sample=True, top_k=top_k)[0]
            predicted_token = y[-1].item()

            # Convert token back to move
            predicted_move = self.train_dataset.itos.get(predicted_token, -1)

            return predicted_move

    def choose_best_move(self, board_state, game_sequence):
        """
        Chọn nước đi tốt nhất từ GPT predictions

        Args:
            board_state: OthelloBoardState object
            game_sequence: List các moves đã chơi

        Returns:
            best_move: Nước đi được chọn (integer position)
        """
        valid_moves = board_state.get_valid_moves()

        if not valid_moves:
            return None

        if len(valid_moves) == 1:
            return valid_moves[0]

        # Thử predict với nhiều temperature khác nhau
        move_scores = {}

        for temp in [0.5, 0.8, 1.0]:
            for _ in range(5):  # Sample 5 lần cho mỗi temperature
                predicted_move = self.predict_next_move(game_sequence, temperature=temp)

                if predicted_move in valid_moves:
                    if predicted_move not in move_scores:
                        move_scores[predicted_move] = 0
                    move_scores[predicted_move] += 1

        # Chọn move có score cao nhất
        if move_scores:
            best_move = max(move_scores.items(), key=lambda x: x[1])[0]
            return best_move

        # Fallback: chọn random từ valid moves
        return np.random.choice(valid_moves)


def print_board(board_state):
    """In bàn cờ Othello"""
    os.system('cls' if os.name == 'nt' else 'clear')

    print("🎮 OTHELLO GPT GAME")
    print("🤖 Powered by GPT AI from othello_world")
    print("=" * 50)
    print("   A B C D E F G H")

    for i in range(8):
        row = f"{i + 1}  "
        for j in range(8):
            if board_state.state[i][j] == 1:
                row += "● "  # Black
            elif board_state.state[i][j] == -1:
                row += "○ "  # White
            else:
                row += ". "  # Empty
        print(row)

    # Hiển thị điểm số
    black_count = np.sum(board_state.state == 1)
    white_count = np.sum(board_state.state == -1)

    print(f"\n● Black: {black_count}  ○ White: {white_count}")
    print(f"Next player: {'● Black' if board_state.next_hand_color == 1 else '○ White'}")
    print("=" * 50)


def pos_to_str(pos):
    """Convert position to string (e.g., 26 -> 'D4')"""
    if pos < 0 or pos >= 64:
        return "Invalid"
    row = pos // 8
    col = pos % 8
    return f"{chr(ord('A') + col)}{row + 1}"


def str_to_pos(move_str):
    """Convert string to position (e.g., 'D4' -> 26)"""
    if len(move_str) != 2:
        return -1
    try:
        col = ord(move_str[0].upper()) - ord('A')
        row = int(move_str[1]) - 1
        if 0 <= row < 8 and 0 <= col < 8:
            return row * 8 + col
    except:
        pass
    return -1


def play_game():
    """Main game function"""
    print("🎮 OTHELLO GPT GAME")
    print("=" * 50)
    print("🤖 Sử dụng GPT AI từ othello_world project")
    print("🧠 Model được train trên championship data")
    print("=" * 50)
    print("Bạn là ● (Black), GPT AI là ○ (White)")
    print("Nhập nước đi theo format: D4, E3, etc.")
    print("Nhập 'quit' để thoát, 'help' để xem nước đi hợp lệ")
    print("=" * 50)

    # Khởi tạo GPT AI
    try:
        ai = OthelloGPTAI()
    except Exception as e:
        print(f"❌ Lỗi khởi tạo GPT AI: {e}")
        print("💡 Đảm bảo đã setup environment và có data")
        return

    # Khởi tạo game
    board = OthelloBoardState()
    game_sequence = []

    print("\n🚀 Game bắt đầu!")
    input("Nhấn Enter để tiếp tục...")

    while True:
        print_board(board)

        # Kiểm tra game over
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            # Thử đổi lượt
            board.next_hand_color *= -1
            valid_moves_other = board.get_valid_moves()
            board.next_hand_color *= -1

            if not valid_moves_other:
                # Game over
                black_count = np.sum(board.state == 1)
                white_count = np.sum(board.state == -1)

                print("\n🏁 GAME OVER!")
                if black_count > white_count:
                    print("🎉 ● Black (Bạn) thắng!")
                elif white_count > black_count:
                    print("🤖 ○ White (GPT AI) thắng!")
                else:
                    print("🤝 Hòa!")

                print(f"Final score: ● {black_count} - {white_count} ○")
                break

        # Lượt người chơi (Black)
        if board.next_hand_color == 1:
            if not valid_moves:
                print("⏭️  Bạn không có nước đi hợp lệ, bỏ lượt")
                board.next_hand_color *= -1
                input("Nhấn Enter để tiếp tục...")
                continue

            print(f"Nước đi hợp lệ: {[pos_to_str(pos) for pos in valid_moves]}")

            while True:
                move_input = input("Nhập nước đi của bạn: ").strip()

                if move_input.lower() == 'quit':
                    print("👋 Tạm biệt!")
                    return
                elif move_input.lower() == 'help':
                    print(f"Nước đi hợp lệ: {[pos_to_str(pos) for pos in valid_moves]}")
                    continue

                move_pos = str_to_pos(move_input)
                if move_pos in valid_moves:
                    board.umpire(move_pos)
                    game_sequence.append(move_pos)
                    print(f"✅ Bạn đã chơi {move_input.upper()}")
                    break
                else:
                    print("❌ Nước đi không hợp lệ!")

        # Lượt GPT AI (White)
        else:
            if not valid_moves:
                print("⏭️  GPT AI không có nước đi hợp lệ, bỏ lượt")
                board.next_hand_color *= -1
                input("Nhấn Enter để tiếp tục...")
                continue

            print("🤖 GPT AI đang suy nghĩ...")
            time.sleep(1.5)  # Tạo cảm giác AI đang "suy nghĩ"

            try:
                ai_move = ai.choose_best_move(board, game_sequence)
                if ai_move is not None and ai_move in valid_moves:
                    board.umpire(ai_move)
                    game_sequence.append(ai_move)
                    print(f"🤖 GPT AI chọn: {pos_to_str(ai_move)}")
                else:
                    # Fallback nếu GPT prediction không hợp lệ
                    fallback_move = np.random.choice(valid_moves)
                    board.umpire(fallback_move)
                    game_sequence.append(fallback_move)
                    print(f"🤖 GPT AI chọn: {pos_to_str(fallback_move)} (fallback)")
            except Exception as e:
                print(f"⚠️  GPT AI error: {e}")
                # Fallback to random
                fallback_move = np.random.choice(valid_moves)
                board.umpire(fallback_move)
                game_sequence.append(fallback_move)
                print(f"🤖 AI chọn: {pos_to_str(fallback_move)} (random fallback)")

            input("Nhấn Enter để tiếp tục...")

    input("Nhấn Enter để thoát...")


if __name__ == '__main__':
    try:
        play_game()
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        input("Nhấn Enter để thoát...")
