import math
import time
import random
from board import HexBoard
from player_base import Player
from collections import deque

class AIPlayer(Player):
    def __init__(self, player_id: int, time_limit: float = 2.0):
        super().__init__(player_id)
        self.opponent_id = 3 - player_id
        self.time_limit = time_limit
        self.best_move = None
        self.current_depth = 0
        self.size = None
        self.move_history = []
        
        # Parámetros de optimización
        self.opening_moves = {}  # Diccionario de aperturas para tamaños comunes
        self._init_opening_book()
        
        # Estadísticas para seguimiento
        self.nodes_evaluated = 0
        self.prunes = 0

    def _init_opening_book(self):
        """Aperturas conocidas para HEX"""
        # Aperturas para tablero 7x7
        self.opening_moves[7] = {
            1: [(3, 3)],  # Centro para jugador 1
            2: [(3, 3), (2, 2), (4, 4)]  # Opciones para jugador 2
        }
        # Aperturas para tablero 11x11
        self.opening_moves[11] = {
            1: [(5, 5)],
            2: [(5, 5), (4, 4), (6, 6)]
        }

    def play(self, board: HexBoard) -> tuple:
        self.size = board.size
        start_time = time.time()
        possible_moves = board.get_possible_moves()
        
        # Verificar si el juego ya terminó
        if board.check_connection(self.player_id) or board.check_connection(self.opponent_id):
            raise ValueError("El juego ya terminó")
        
        if not possible_moves:
            raise ValueError("No hay movimientos posibles")
        
        # Movimiento por defecto (aleatorio)
        self.best_move = random.choice(possible_moves)
        self.nodes_evaluated = 0
        self.prunes = 0
        
        # Usar apertura conocida si está disponible
        if len(possible_moves) == self.size * self.size and self.size in self.opening_moves:
            if self.player_id in self.opening_moves[self.size]:
                return random.choice(self.opening_moves[self.size][self.player_id])
        
        # Búsqueda con Iterative Deepening
        max_depth = min(20, self.size * 2)  # Límite de profundidad razonable
        for depth in range(1, max_depth + 1):
            if time.time() - start_time > self.time_limit * 0.85:  # 15% de margen
                break
                
            try:
                self.current_depth = depth
                alpha = -math.inf
                beta = math.inf
                
                # Ordenar movimientos por heurística antes de evaluar
                ordered_moves = self._order_moves(board, possible_moves, self.player_id)
                
                best_value = -math.inf
                for move in ordered_moves:
                    new_board = board.clone()
                    new_board.place_piece(*move, self.player_id)
                    
                    value = self._minimax(
                        new_board, 
                        depth - 1, 
                        alpha, 
                        beta, 
                        False, 
                        start_time
                    )
                    
                    if value > best_value or (value == best_value and self.best_move not in possible_moves):
                        best_value = value
                        self.best_move = move
                    
                    alpha = max(alpha, best_value)
                    if alpha >= beta:
                        self.prunes += 1
                        break
                        
            except TimeoutError:
                break
        
        # Guardar el movimiento en el historial
        self.move_history.append(self.best_move)
        return self.best_move

    def _minimax(self, board, depth, alpha, beta, maximizing, start_time):
        """Minimax optimizado con alpha-beta pruning"""
        if time.time() - start_time > self.time_limit:
            raise TimeoutError()
            
        self.nodes_evaluated += 1
        
        # Condiciones de terminación
        if depth == 0 or board.check_connection(self.player_id) or board.check_connection(self.opponent_id):
            return self._evaluate(board)
        
        possible_moves = board.get_possible_moves()
        if not possible_moves:
            return 0
        
        # Ordenar movimientos por heurística
        current_player = self.player_id if maximizing else self.opponent_id
        ordered_moves = self._order_moves(board, possible_moves, current_player)
        
        if maximizing:
            value = -math.inf
            for move in ordered_moves:
                new_board = board.clone()
                new_board.place_piece(*move, self.player_id)
                
                value = max(
                    value, 
                    self._minimax(new_board, depth - 1, alpha, beta, False, start_time)
                )
                
                alpha = max(alpha, value)
                if alpha >= beta:
                    self.prunes += 1
                    break
            return value
        else:
            value = math.inf
            for move in ordered_moves:
                new_board = board.clone()
                new_board.place_piece(*move, self.opponent_id)
                
                value = min(
                    value,
                    self._minimax(new_board, depth - 1, alpha, beta, True, start_time)
                )
                beta = min(beta, value)
                if alpha >= beta:
                    self.prunes += 1
                    break
            return value

    def _order_moves(self, board, moves, player_id):
        """Ordena movimientos por potencial heurístico"""
        if not moves:
            return moves
            
        # Priorizar movimientos que:
        # 1. Conectan nuestros lados
        # 2. Bloquean al oponente
        # 3. Están cerca del centro
        move_scores = []
        for move in moves:
            score = 0
            
            # Conexión a nuestros lados
            if player_id == 1:  # Horizontal
                score += (self.size - move[1])  # Más cerca del lado derecho
                score += move[1]  # Más cerca del lado izquierdo
            else:  # Vertical
                score += (self.size - move[0])  # Más cerca del lado inferior
                score += move[0]  # Más cerca del lado superior
            
            # Bloquear al oponente
            opponent_id = 3 - player_id
            opponent_dist = self._calculate_min_distance(board, opponent_id, exclude=move)
            score += opponent_dist * 0.5  # Penalizar movimientos que ayudan al oponente
            
            # Control del centro
            center = self.size // 2
            distance_to_center = math.sqrt((move[0] - center)**2 + (move[1] - center)**2)
            score += (self.size - distance_to_center) * 0.3
            
            move_scores.append((score, move))
        
        # Ordenar por puntuación descendente
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for (score, move) in move_scores]

    def _evaluate(self, board):
        """Función de evaluación mejorada para HEX"""
        # 1. Victoria/derrota inmediata
        if board.check_connection(self.player_id):
            return math.inf
        if board.check_connection(self.opponent_id):
            return -math.inf
        
        # 2. Distancias potenciales
        player_dist = self._calculate_min_distance(board, self.player_id)
        opponent_dist = self._calculate_min_distance(board, self.opponent_id)
        
        # 3. Conexiones y puentes
        player_bridges = self._count_bridges(board, self.player_id)
        opponent_bridges = self._count_bridges(board, self.opponent_id)
        
        # 4. Control estratégico
        player_control = self._calculate_control(board, self.player_id)
        opponent_control = self._calculate_control(board, self.opponent_id)
        
        # Ponderación de factores
        distance_diff = opponent_dist - player_dist
        bridge_diff = player_bridges - opponent_bridges
        control_diff = player_control - opponent_control
        
        return (distance_diff * 0.6 + bridge_diff * 0.3 + control_diff * 0.1)

    def _calculate_min_distance(self, board, player_id, exclude=None):
        """Calcula la distancia mínima potencial para conectar los lados"""
        size = board.size
        distances = []
        
        if player_id == 1:  # Conectar izquierda-derecha
            starts = [(i, 0) for i in range(size)]
            targets = [(i, size-1) for i in range(size)]
        else:  # Conectar arriba-abajo
            starts = [(0, j) for j in range(size)]
            targets = [(size-1, j) for j in range(size)]
        
        for start in starts:
            if board.board[start[0]][start[1]] == player_id:
                distance = self._bfs_shortest_path(board, start, targets, player_id, exclude)
                if distance is not None:
                    distances.append(distance)
        
        return min(distances) if distances else size * 2

    def _bfs_shortest_path(self, board, start, targets, player_id, exclude=None):
        """BFS optimizado para encontrar el camino más corto potencial"""
        size = board.size
        visited = [[False] * size for _ in range(size)]
        queue = deque([(start[0], start[1], 0)])
        visited[start[0]][start[1]] = True
        
        while queue:
            row, col, dist = queue.popleft()
            
            if (row, col) in targets:
                return dist
            
            for r, c in self.get_adjacent_hexes(row, col):
                if 0 <= r < size and 0 <= c < size and not visited[r][c]:
                    if (r, c) == exclude:
                        continue
                    if board.board[r][c] == player_id or board.board[r][c] == 0:
                        visited[r][c] = True
                        queue.append((r, c, dist + 1))
        
        return None
    
    def get_adjacent_hexes(self, row: int, col: int) -> list:
        """Devuelve las casillas adyacentes según even-r"""
        if row % 2 == 0:  # Fila par
            directions = [
                (0, -1), (0, 1),    # Izquierda, derecha
                (-1, 0), (1, 0),    # Arriba, abajo
                (-1, 1), (1, 1)     # Arriba-derecha, abajo-derecha
            ]
        else:  # Fila impar
            directions = [
                (0, -1), (0, 1),    # Izquierda, derecha
                (-1, 0), (1, 0),    # Arriba, abajo
                (-1, -1), (1, -1)   # Arriba-izquierda, abajo-izquierda
            ]
        
        return [(row + dr, col + dc) for dr, dc in directions 
                if 0 <= row + dr < self.size and 0 <= col + dc < self.size]

    def _count_bridges(self, board, player_id):
        """Cuenta puentes potenciales (dos conexiones separadas por una celda vacía)"""
        bridges = 0
        size = board.size
        
        for i in range(size):
            for j in range(size):
                if board.board[i][j] == 0:  # Celda vacía
                    # Verificar si conecta dos piezas del jugador
                    neighbors = self.get_adjacent_hexes(i, j)
                    player_neighbors = 0
                    
                    for r, c in neighbors:
                        if 0 <= r < size and 0 <= c < size and board.board[r][c] == player_id:
                            player_neighbors += 1
                            if player_neighbors >= 2:
                                bridges += 1
                                break
        return bridges

    def _calculate_control(self, board, player_id):
        """Calcula el control estratégico del tablero"""
        control = 0
        size = board.size
        center = size // 2
        
        for i in range(size):
            for j in range(size):
                if board.board[i][j] == player_id:
                    # Valor más alto para piezas cerca del centro
                    distance_to_center = math.sqrt((i - center)**2 + (j - center)**2)
                    control += (size - distance_to_center)
                    
                    # Bonus por conexiones adyacentes
                    neighbors = self.get_adjacent_hexes(i, j)
                    for r, c in neighbors:
                        if 0 <= r < size and 0 <= c < size and board.board[r][c] == player_id:
                            control += 0.5
        return control


