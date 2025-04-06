import math
import heapq
import numpy as np
from HexBoard import HexBoard
from Player import Player
    
class MyPlayer(Player):
    def __init__(self, player_id: int):
        super().__init__(player_id)
        self.size = None
        self.weight_p1 = None  #Determinar peso inicial para columnas
        self.weight_p2 = None  #Determinar peso inicial para filas
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
        ordered_moves = self.order_moves(possible_moves, descending=True)
        
        for move in ordered_moves:
            new_board = board.clone()
            new_board.place_piece(move[0], move[1], self.player_id)
            value = self.minimax(new_board, depth-1, alpha, beta, False)
            
            if value > best_value:
                best_value = value
                best_move = move
            
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break
        
        return best_move

    def minimax(self, board: HexBoard, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        if depth == 0 or board.check_connection(self.player_id) or board.check_connection(self.opponent_id):
            return self.simple_evaluate(board)
        
        possible_moves = board.get_possible_moves()
        
        if maximizing:
            value = -math.inf
            for move in self.order_moves(possible_moves, descending=True):
                new_board = board.clone()
                new_board.place_piece(move[0], move[1], self.player_id)
                value = max(value, self.minimax(new_board, depth-1, alpha, beta, False))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = math.inf
            for move in self.order_moves(possible_moves, descending=False):
                new_board = board.clone()
                new_board.place_piece(move[0], move[1], self.opponent_id)
                value = min(value, self.minimax(new_board, depth-1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def calculate_weights(self):
        size = self.size
        #Dar mayor peso a extremos
        self.weight_p1 = np.maximum(size - np.arange(size), np.arange(size) + 1)
        self.weight_p2 = np.maximum(size - np.arange(size), np.arange(size) + 1)

    def get_move_weight(self, move: tuple) -> float:
        row, col = move
        return self.weight_p1[col] if self.player_id == 1 else self.weight_p2[row]

    def order_moves(self, moves: list, descending: bool) -> list:
        if not moves:
            return []
        
        weights = np.array([self.get_move_weight(move) for move in moves])
        sorted_indices = np.argsort(-weights if descending else weights).tolist() 
        return [moves[i] for i in sorted_indices]

    def simple_evaluate(self, board: HexBoard) -> float:
        if board.check_connection(self.player_id):
            return math.inf
        if board.check_connection(self.opponent_id):
            return -math.inf
        
        player_score = np.sum(self.weight_p1 * (board.board == self.player_id))
        opponent_score = np.sum(self.weight_p1 * (board.board == self.opponent_id))
        return player_score - opponent_score

    def calculate_depth(self, num_moves: int) -> int:
        return 3 if num_moves > 30 else 4 #Ajustar profundidad según situación