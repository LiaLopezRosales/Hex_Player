class HexBoard:
    def __init__(self, size: int):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.player_positions = {1: set(), 2: set()}
    
    def clone(self):
        new_board = HexBoard(self.size)
        new_board.board = [row.copy() for row in self.board]
        new_board.player_positions = {
            1: self.player_positions[1].copy(),
            2: self.player_positions[2].copy()
        }
        return new_board
    
    def place_piece(self, row: int, col: int, player_id: int) -> bool:
        if self.board[row][col] == 0:
            self.board[row][col] = player_id
            self.player_positions[player_id].add((row, col))
            return True
        return False
    
    def get_possible_moves(self) -> list:
        return [
            (r, c) 
            for r in range(self.size) 
            for c in range(self.size) 
            if self.board[r][c] == 0
        ]
    
    def check_connection(self, player_id: int) -> bool:
        visited = set()
        to_visit = []
        
        if player_id == 1:
            start_nodes = [(0, c) for c in range(self.size)]
            end_condition = lambda r, c: r == self.size - 1
        else:
            start_nodes = [(r, 0) for r in range(self.size)]
            end_condition = lambda r, c: c == self.size - 1
        
        for node in start_nodes:
            if node in self.player_positions[player_id]:
                to_visit.append(node)
                visited.add(node)
        
        while to_visit:
            r, c = to_visit.pop()
            if end_condition(r, c):
                return True
            
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if (nr, nc) in self.player_positions[player_id] and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        to_visit.append((nr, nc))
        
        return False