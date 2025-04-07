import math
import heapq
import numpy as np
from HexBoard import HexBoard
from Player import Player
    
class MyPlayer(Player):
    def __init__(self, player_id: int):
        super().__init__(player_id)
        self.size = None
        self.edge_weights = None
        self.bridge_bonus = None
        self.opponent_penalty = None
        self.opponent_id = 2 if player_id == 1 else 1 #Determinar papel de jugador

    def play(self, board: HexBoard) -> tuple:
        possible_moves = board.get_possible_moves()
        if not possible_moves:
            return None
        
        if self.size is None:
            self.size = board.size
            self.calculate_weights() #Calcular pesos iniciales
        
        return self.alpha_beta_search(board, possible_moves)

    def alpha_beta_search(self, board: HexBoard, possible_moves: list) -> tuple:
        best_move = None
        best_value = -math.inf
        alpha = -math.inf
        beta = math.inf
        depth = self.calculate_depth(len(possible_moves))  #Alterar profundidad de búsqueda según situación actual
        
        # Ordenamiento optimizado con numpy
        ordered_moves = self.order_moves(possible_moves, board)
        
        for move in ordered_moves:
            new_board = board.clone()
            new_board.place_piece(move[0], move[1], self.player_id)
            value = self.minimax(new_board, depth-1, alpha, beta, False, self.opponent_id)
            
            if value > best_value:
                best_value = value
                best_move = move
                alpha = max(alpha, value)
            
            if beta <= alpha:
                break
        
        return best_move

    def minimax(self, board: HexBoard, depth: int, alpha: float, beta: float, maximizing: bool, current_player: int) -> float:
        if depth == 0 or board.check_connection(self.player_id) or board.check_connection(self.opponent_id):
            return self.simple_evaluate(board)
        
        possible_moves = board.get_possible_moves()
        
        if maximizing:
            value = -math.inf
            for move in self.order_moves(possible_moves, board):
                new_board = board.clone()
                new_board.place_piece(move[0], move[1], self.player_id)
                value = max(value, self.minimax(new_board, depth-1, alpha, beta, False, 
                    self.opponent_id))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = math.inf
            for move in self.order_moves(possible_moves, board):
                new_board = board.clone()
                new_board.place_piece(move[0], move[1], self.opponent_id)
                value = min(value, self.minimax(new_board, depth-1, alpha, beta, True, self.player_id))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def calculate_weights(self):
        size = self.size
        x, y = np.mgrid[:size, :size]
        
        # Distancia estratégica a los bordes objetivo
        if self.player_id == 1:
            self.edge_weights = np.minimum(y + 1, size - y)  # Columnas horizontales
        else:
            self.edge_weights = np.minimum(x + 1, size - x)  # Filas verticales

        # Bonificación por puentes potenciales
        self.bridge_bonus = np.zeros((size, size))
        for i in range(size-1):
            for j in range(size-1):
                self.bridge_bonus[i,j] = 2 if (i + j) % 2 == 0 else 1

        # Penalización por cercanía al oponente
        self.opponent_penalty = np.fromfunction(
            lambda i, j: 1.5 - 0.5*np.abs(i - j)/size, 
            (size, size)
        )

    # def get_move_weight(self, move: tuple) -> float:
    #     row, col = move
    #     return self.weight_p1[col] if self.player_id == 1 else self.weight_p2[row]

    def order_moves(self, moves: list, board: HexBoard) -> list:
        scores = []
        for move in moves:
            row, col = move
            score = self.edge_weights[row, col] 
            score += self.bridge_bonus[row, col] * 0.8
            
            opponent_count = 0
            for i in range(max(0, row-1), min(row+2, self.size)):
                for j in range(max(0, col-1), min(col+2, self.size)):
                    if board.board[i][j] == self.opponent_id: 
                        opponent_count += 1
            
            score -= opponent_count * 0.6 * self.opponent_penalty[row, col]
            scores.append(score)
        
        return [moves[i] for i in np.argsort(-np.array(scores))]

    def simple_evaluate(self, board: HexBoard) -> float:
        if board.check_connection(self.player_id):
            return math.inf
        if board.check_connection(self.opponent_id):
            return -math.inf

        player_mask = (board.board == self.player_id)
        opponent_mask = (board.board == self.opponent_id)

        # Valor posicional
        positional = np.sum(self.edge_weights * player_mask) - np.sum(self.edge_weights * opponent_mask)
        
        # Conexiones potenciales
        player_connections = np.sum(self.bridge_bonus * player_mask)
        opponent_connections = np.sum(self.bridge_bonus * opponent_mask)
        
        # Control de área
        player_area = np.sum(self.opponent_penalty * player_mask)
        opponent_area = np.sum(self.opponent_penalty * opponent_mask)
        
        return positional * 0.6 + (player_connections - opponent_connections) * 0.3 + (player_area - opponent_area) * 0.1
    
    def calculate_depth(self, num_moves: int) -> int:
        if num_moves > 100:
            return 2
        elif num_moves > 50:
            return 3
        elif num_moves > 20:
            return 4
        else:
            return 5