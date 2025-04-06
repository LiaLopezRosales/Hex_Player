import tkinter as tk
from tkinter import messagebox
from HexBoard import HexBoard
from HexPlayer import MyPlayer  # Tu jugador implementado

class HexGUI:
    def __init__(self, size=5):
        self.size = size
        self.root = tk.Tk()
        self.root.title("HEX AI Tester - Visualización Corregida")
        
        # Configuración de tamaño y márgenes
        self.cell_size = 70  # Aumentamos el tamaño de cada celda
        self.margin = 30  # Margen alrededor del tablero
        
        # Configurar tablero y jugadores
        self.board = HexBoard(size)
        self.ai_player = MyPlayer(player_id=2)
        self.current_player = 1
        
        # Calcular dimensiones del canvas
        canvas_width = 2 * self.margin + (self.size * 1.5 * self.cell_size)
        canvas_height = 2 * self.margin + (self.size * 0.866 * self.cell_size)
        
        self.canvas = tk.Canvas(
            self.root,
            width=canvas_width,
            height=canvas_height,
            bg='#F0F0F0'
        )
        self.canvas.pack()
        
        # Controles
        self.controls = tk.Frame(self.root)
        self.controls.pack(pady=10)
        tk.Button(self.controls, text="Nuevo Juego", command=self.reset_game).pack(side=tk.LEFT)
        
        self.draw_board()
        self.canvas.bind("<Button-1>", self.handle_click)
        
    def draw_board(self):
        self.canvas.delete("all")
        hex_height = self.cell_size * 0.866  # Altura vertical de un hexágono
        
        for row in range(self.size):
            for col in range(self.size):
                # Cálculo preciso de coordenadas
                x = self.margin + col * self.cell_size * 1.5
                y = self.margin + row * hex_height
                
                # Offset alternado para filas impares
                if row % 2 == 1:
                    x += self.cell_size * 0.75
                
                self.draw_hexagon(x, y, row, col)
                
    def draw_hexagon(self, x, y, row, col):
        size = self.cell_size/2
        points = [
            x, y,
            x + size, y - size/2,
            x + size*2, y,
            x + size*2, y + size,
            x + size, y + size*1.5,
            x, y + size,
        ]
        
        color = "white"
        if (row, col) in self.board.player_positions[1]:
            color = "#FF9999"  # Jugador humano
        elif (row, col) in self.board.player_positions[2]:
            color = "#9999FF"  # IA
        
        hex_id = self.canvas.create_polygon(
            points, 
            fill=color, 
            outline="black",
            tags=(f"cell_{row}_{col}", "clickable")
        )
        
    def handle_click(self, event):
        if self.current_player != 1:
            return
            
        # Encontrar celda clickeada
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        if "clickable" in tags:
            cell_tag = [t for t in tags if t.startswith("cell_")][0]
            _, row, col = cell_tag.split("_")
            row, col = int(row), int(col)
            
            if self.board.place_piece(row, col, 1):
                self.current_player = 2
                self.update_display()
                self.check_winner()
                self.ai_move()
    
    def ai_move(self):
        ai_move = self.ai_player.play(self.board)
        if ai_move:
            self.board.place_piece(ai_move[0], ai_move[1], 2)
        self.current_player = 1
        self.update_display()
        self.check_winner()
    
    def update_display(self):
        self.draw_board()
        self.root.update()
    
    def check_winner(self):
        if self.board.check_connection(1):
            self.show_winner("¡Ganaste!")
        elif self.board.check_connection(2):
            self.show_winner("La IA ganó")
    
    def show_winner(self, message):
        messagebox.showinfo("Fin del juego", message)
        self.reset_game()
    
    def reset_game(self):
        self.board = HexBoard(self.size)
        self.current_player = 1
        self.update_display()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = HexGUI(size=15)
    gui.run()