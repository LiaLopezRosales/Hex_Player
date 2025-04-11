import math
import numpy as np
import time
from board import HexBoard

class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id  # Tu identificador (1 o 2)

    def play(self, board: HexBoard) -> tuple:
        raise NotImplementedError("¡Implementa este método!")
    
class HexPlayer(Player):
    def __init__(self, player_id: int):
        super().__init__(player_id)
        self.size = None
        self.edge_weights = None
        self.bridge_bonus = None
        self.opponent_penalty = None
        self.is_horizontal_player = (player_id == 1) 
        self.opponent_id = 2 if player_id == 1 else 1 
        self.center_weights = None
        self.max_moves = None 
        

    def play(self, board: HexBoard, time_limit: float) -> tuple:
        possible_moves = board.get_possible_moves()
        time_limit=time_limit-0.15 #Ajustar tiempo por si acaso
        
        if not possible_moves: #Por si acaso(nunca debería entrar)
            return None
        
        if self.size is None:
            self.size = board.size
            self.calculate_weights() #Calcular pesos iniciales de cada posición
            
        # Verificar victoria inmediata
        for move in possible_moves:
            temp_board = board.clone()
            temp_board.place_piece(move[0], move[1], self.player_id)
            if temp_board.check_connection(self.player_id):
                return move 

        # Verificar si oponente puede ganar en siguiente turno
        opponent_moves = []
        for move in possible_moves:
            temp_board = board.clone()
            temp_board.place_piece(move[0], move[1], self.opponent_id)
            if temp_board.check_connection(self.opponent_id):
                opponent_moves.append(move)
        
        # Determinar los movimientos a considerar
        if opponent_moves:
            #Si el oponente puede ganar en el próximo movimiento priorizar bloqueo
            possible_moves_block = opponent_moves
        else:
            possible_moves_block = possible_moves
        
        # Ordenar movimientos a explorar
        ordered_moves = self.order_moves(possible_moves_block, board)
        
        # Profundidad iterativa con manejo de tiempo
        start_time = time.time()
        abs_time_limit = start_time + time_limit
        best_move = ordered_moves[0]
        best_value = -math.inf
        depth = 1
        
        try:
            while True:
                # Verificar tiempo antes de cada profundidad
                if time.time() >= abs_time_limit:
                    raise TimeoutError()
                
                current_move, current_value = self.alpha_beta_search(
                    board, possible_moves_block, depth, abs_time_limit
                )
                
                if current_value > best_value:
                    best_move = current_move
                    best_value = current_value
                
                depth += 1
        except TimeoutError:
            pass
        
        return best_move

    def alpha_beta_search(self, board: HexBoard, possible_moves: list, depth: int, abs_time_limit: float) -> tuple:
        best_move = possible_moves[0]
        best_value = -math.inf
        alpha = -math.inf
        beta = math.inf
        
        ordered_moves = self.order_moves(possible_moves, board)
        
        for move in ordered_moves:
            if time.time() >= abs_time_limit:
                raise TimeoutError()
            
            new_board = board.clone()
            new_board.place_piece(move[0], move[1], self.player_id)
            value = self.minimax(
                new_board, depth-1, alpha, beta, False, self.opponent_id, abs_time_limit
            )
            
            if value > best_value:
                best_value = value
                best_move = move
                alpha = max(alpha, value)
            
            if beta <= alpha:
                break
        
        return best_move, best_value
    
    def minimax(self, board: HexBoard, depth: int, alpha: float, beta: float, maximizing: bool, current_player: int, abs_time_limit: float) -> float:
        if time.time() >= abs_time_limit:
            raise TimeoutError()
        
        if depth == 0 or board.check_connection(self.player_id) or board.check_connection(self.opponent_id):
            return self.simple_evaluate(board)
        
        possible_moves = board.get_possible_moves()
        
        if maximizing:
            value = -math.inf
            ordered_moves = self.order_moves(possible_moves, board)
            for move in ordered_moves:
                if time.time() >= abs_time_limit:
                    raise TimeoutError()
                
                new_board = board.clone()
                new_board.place_piece(move[0], move[1], self.player_id)
                child_value = self.minimax(
                    new_board, depth-1, alpha, beta, False, self.opponent_id, abs_time_limit
                )
                value = max(value, child_value)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = math.inf
            ordered_moves = self.order_moves(possible_moves, board)
            for move in ordered_moves:
                if time.time() >= abs_time_limit:
                    raise TimeoutError()
                
                new_board = board.clone()
                new_board.place_piece(move[0], move[1], self.opponent_id)
                child_value = self.minimax(
                    new_board, depth-1, alpha, beta, True, self.player_id, abs_time_limit
                )
                value = min(value, child_value)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def calculate_weights(self):
        size = self.size
        self.max_moves = size * size
        x, y = np.mgrid[:size, :size]
        #Bonificación por posiciones centrales
        center = (size-1)/2
        self.center_weights = 1 / (1 + np.sqrt((x - center)**2 + (y - center)**2))
        self.center_weights /= np.max(self.center_weights)  #Ajustar peso
        
        #Bonificación por extremos relevantes
        if self.is_horizontal_player:  
            self.edge_weights = np.minimum(y + 1, size - y) 
            self.target_edges = {(0, col) for col in range(size)} | {(size-1, col) for col in range(size)}
        else: 
            self.edge_weights = np.minimum(x + 1, size - x)  
            self.target_edges = {(row, 0) for row in range(size)} | {(row, size-1) for row in range(size)}

        # Bonificación por puentes 
        self.bridge_bonus = np.zeros((size, size))
        for i in range(size-1):
            for j in range(size-1):
                self.bridge_bonus[i,j] = 2 if (i + j) % 2 == 0 else 1

        # Penalización por cercanía al oponente
        self.opponent_penalty = np.fromfunction(
            lambda i, j: 1.5 - 0.5*np.abs(i - j)/size, 
            (size, size)
        )

    def get_game_phase(self, board: HexBoard) -> float:
        #Estimar fase actual del juego(Escala de 0 a 1)
        moves_made = self.max_moves - len(board.get_possible_moves())
        return min(moves_made / self.max_moves, 1.0)

    def order_moves(self, moves: list, board: HexBoard) -> list:
        scores = []
        target_edge_bonus = 2.0  
        
        for move in moves:
            row, col = move
            score = self.edge_weights[row, col]
            score += self.center_weights[row, col]
            
            # Bonus extra si está en el borde inicial o final
            if self.player_id == 1:  
                if col == 0 or col == self.size-1:
                    score += target_edge_bonus
            else: 
                if row == 0 or row == self.size-1:
                    score += target_edge_bonus
                    
            if (row, col) in self.target_edges:
                score += target_edge_bonus
                    
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
        #Si es un estado final determina si se gana o pierde y premia acorde
        my_conn = board.check_connection(self.player_id)
        opp_conn = board.check_connection(self.opponent_id)
        
        if my_conn and self.is_horizontal_player == (self.player_id == 1):
            return math.inf
        if opp_conn and self.is_horizontal_player == (self.opponent_id == 1):
            return -math.inf

        player_mask = (board.board == self.player_id)
        opponent_mask = (board.board == self.opponent_id)
        
        game_phase = self.get_game_phase(board)
        
        #Pesos varian acorde a etapa de juego
        # Valor central
        player_center = np.sum(self.center_weights * (np.array(board.board) == self.player_id)) * (1.0 - game_phase)
        opponent_center = np.sum(self.center_weights * (np.array(board.board) == self.opponent_id)) * (1.0 - game_phase)

        # Valor posicional
        positional = np.sum(self.edge_weights * player_mask) - np.sum(self.edge_weights * opponent_mask)
        
        # Conexiones potenciales
        player_connections = np.sum(self.bridge_bonus * player_mask)
        opponent_connections = np.sum(self.bridge_bonus * opponent_mask)
        
        # Control de área
        player_area = np.sum(self.opponent_penalty * player_mask)
        opponent_area = np.sum(self.opponent_penalty * opponent_mask)
        
        return positional * 0.6 + (player_connections - opponent_connections) * 0.3 + (player_area - opponent_area) * 0.1 + (player_center - opponent_center)*0.3
    
    # def calculate_depth(self, num_moves: int) -> int:
    #     if num_moves > 100:
    #         return 2
    #     elif num_moves > 50:
    #         return 2
    #     elif num_moves > 20:
    #         return 3
    #     else:
    #         return 4