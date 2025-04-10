class HexBoard:
    def __init__(self, size: int):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        
        # Códigos de color ANSI
        self.RED = '\033[91m'
        self.BLUE = '\033[94m'
        self.GRAY = '\033[90m'
        self.RESET = '\033[0m'

    def clone(self) -> 'HexBoard':
        """Devuelve una copia exacta del tablero"""
        new_board = HexBoard(self.size)
        new_board.board = [row.copy() for row in self.board]
        return new_board

    def place_piece(self, row: int, col: int, player_id: int) -> bool:
        """Coloca una ficha si la posición es válida"""
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise ValueError("Posición fuera del tablero")
        if self.board[row][col] == 0:
            self.board[row][col] = player_id
            return True
        return False

    def get_possible_moves(self) -> list:
        """Devuelve todas las casillas vacías"""
        return [(i, j) for i in range(self.size) 
                       for j in range(self.size) 
                       if self.board[i][j] == 0]

    def check_connection(self, player_id: int) -> bool:
        """Verifica si el jugador conectó sus lados (BFS)"""
        visited = [[False for _ in range(self.size)] for _ in range(self.size)]
        queue = []
        
        # Inicializar BFS según el jugador
        if player_id == 1:  # Conectar izquierda (col=0) a derecha (col=size-1)
            for i in range(self.size):
                if self.board[i][0] == player_id:
                    queue.append((i, 0))
                    visited[i][0] = True
        else:  # Conectar arriba (fila=0) a abajo (fila=size-1)
            for j in range(self.size):
                if self.board[0][j] == player_id:
                    queue.append((0, j))
                    visited[0][j] = True
        
        # Búsqueda de conexión con adyacencias even-r
        while queue:
            row, col = queue.pop(0)
            
            # Condición de victoria
            if (player_id == 1 and col == self.size - 1) or (player_id == 2 and row == self.size - 1):
                return True
            
            # Explorar vecinos
            for r, c in self.get_adjacent_hexes(row, col):
                if 0 <= r < self.size and 0 <= c < self.size:
                    if not visited[r][c] and self.board[r][c] == player_id:
                        visited[r][c] = True
                        queue.append((r, c))
        
        return False

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

    def print_board(self):
        """Imprime el tablero con colores y formato even-r"""
        max_row_width = len(str(self.size - 1))
        
        # Encabezado de columnas
        header = " " * (max_row_width + 1)
        for j in range(self.size):
            header += f"{self.GRAY}{j:>3}{self.RESET}"
        print(header)
        
        # Filas con indentación alternada
        for i in range(self.size):
            indent = "  " * ((i + 1) % 2)  # Filas impares indentadas
            row_str = f"{self.GRAY}{i:>{max_row_width}}{self.RESET} {indent}"
            
            for j in range(self.size):
                cell = self.board[i][j]
                if cell == 1:
                    row_str += f"{self.RED} R {self.RESET}"
                elif cell == 2:
                    row_str += f"{self.BLUE} B {self.RESET}"
                else:
                    row_str += f"{self.GRAY} • {self.RESET}"
            print(row_str)