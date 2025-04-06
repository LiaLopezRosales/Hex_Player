import heapq
from HexBoard import HexBoard
from Player import Player
from typing import Tuple, List

class AStarHexPlayer(Player):
    def __init__(self, player_id: int):
        super().__init__(player_id)
        self.opponent_id = 2 if player_id == 1 else 1
        self.size = None
    
    def play(self, board: HexBoard) -> Tuple[int, int]:
        self.size = board.size
        possible_moves = board.get_possible_moves()
        
        # 1. Jugada ganadora inmediata
        for move in possible_moves:
            if self._is_winning_move(board, move, self.player_id):
                return move
        
        # 2. Bloquear jugada ganadora del oponente
        blocking_move = self._find_blocking_move(board, possible_moves)
        if blocking_move:
            return blocking_move
        
        # 3. Seleccionar mejores candidatos con nueva estrategia
        candidate_moves = self._prioritize_offensive_moves(board, possible_moves)
        
        best_score = float('-inf')
        best_move = candidate_moves[0]
        
        for move in candidate_moves:
            score = self._calculate_move_potential(board, move)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _is_winning_move(self, board: HexBoard, move: Tuple[int, int], player_id: int) -> bool:
        temp_board = board.clone()
        temp_board.place_piece(move[0], move[1], player_id)
        return temp_board.check_connection(player_id)
    
    def _find_blocking_move(self, board: HexBoard, possible_moves: list) -> Tuple[int, int]:
        for move in possible_moves:
            if self._is_winning_move(board, move, self.opponent_id):
                return move
        return None
    
    def _prioritize_offensive_moves(self, board: HexBoard, moves: list) -> list:
        offensive_moves = []
        for (r, c) in moves:
            score = 0
            # Priorizar conexiones hacia ambos lados
            score += self._connection_potential(board, r, c, self.player_id)
            # Bonus por control de puentes críticos
            score += 2.0 if self._is_bridge_position(r, c) else 0
            # Penalizar movimientos aislados
            score -= 0.5 * self._isolated_position_penalty(board, r, c)
            offensive_moves.append((-score, (r, c)))
        
        offensive_moves.sort()
        return [m[1] for m in offensive_moves[:15]]
    
    def _calculate_move_potential(self, board: HexBoard, move: Tuple[int, int]) -> float:
        r, c = move
        sim_board = board.clone()
        sim_board.place_piece(r, c, self.player_id)
        
        # Potencial ofensivo (nuestra conexión)
        own_potential = 1.0 / (self._pathfinding_cost(sim_board, self.player_id) + 1)
        
        # Potencial defensivo (bloqueo oponente)
        opponent_potential = self._pathfinding_cost(sim_board, self.opponent_id)
        
        # Valor estratégico posicional
        position_value = self._positional_value(r, c)
        
        return (own_potential * 2.0) + opponent_potential + position_value
    
    def _pathfinding_cost(self, board: HexBoard, player_id: int) -> float:
        """Nuevo algoritmo de pathfinding con optimización para conexiones múltiples"""
        frontier = []
        visited = {}
        start_nodes, end_condition = self._get_boundary_info(player_id)
        
        for (r, c) in start_nodes:
            cost = 0 if board.board[r][c] == player_id else 1
            heapq.heappush(frontier, (cost, r, c))
            visited[(r, c)] = cost
        
        min_cost = float('inf')
        while frontier:
            cost, r, c = heapq.heappop(frontier)
            
            if end_condition(r, c):
                min_cost = min(min_cost, cost)
                continue
                
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1), (-1,1), (1,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    new_cost = cost + (0 if board.board[nr][nc] == player_id else 1)
                    if (nr, nc) not in visited or new_cost < visited.get((nr, nc), float('inf')):
                        visited[(nr, nc)] = new_cost
                        heapq.heappush(frontier, (new_cost, nr, nc))
        
        return min_cost if min_cost != float('inf') else 1000
    
    def _connection_potential(self, board: HexBoard, r: int, c: int, player_id: int) -> float:
        """Calcula cuánto mejora este movimiento nuestra mejor conexión"""
        original_cost = self._pathfinding_cost(board, player_id)
        new_board = board.clone()
        new_board.place_piece(r, c, player_id)
        new_cost = self._pathfinding_cost(new_board, player_id)
        return (original_cost - new_cost) * 1.5
    
    def _is_bridge_position(self, r: int, c: int) -> bool:
        """Determina si la posición es un puente estratégico entre dos grupos"""
        return (r + c) % (self.size - 1) == 0 or abs(r - c) <= 1
    
    def _positional_value(self, r: int, c: int) -> float:
        """Valor estratégico basado en posición en el tablero"""
        center = (self.size - 1) / 2
        distance_to_center = abs(r - center) + abs(c - center)
        edge_value = 1.0 if (r == 0 or c == 0 or r == self.size-1 or c == self.size-1) else 0
        return (1.0 / (distance_to_center + 1)) + edge_value
    
    def _isolated_position_penalty(self, board: HexBoard, r: int, c: int) -> int:
        """Penaliza posiciones sin conexiones cercanas"""
        neighbors = 0
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1), (-1,1), (1,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                if board.board[nr][nc] == self.player_id:
                    neighbors += 1
        return 3 - neighbors  # Máxima penalización si no hay vecinos

    def _get_boundary_info(self, player_id: int):
        if player_id == 1:
            return [(0, c) for c in range(self.size)], lambda r, _: r == self.size-1
        else:
            return [(r, 0) for r in range(self.size)], lambda _, c: c == self.size-1