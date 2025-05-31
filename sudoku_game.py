import pygame
import random
import sys
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 540, 600
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE
BUFFER = 5  # Buffer space inside cells
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 100
BUTTON_MARGIN = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
HIGHLIGHT = (240, 240, 150)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

# Fonts
number_font = pygame.font.SysFont('Arial', 35)
button_font = pygame.font.SysFont('Arial', 20)
message_font = pygame.font.SysFont('Arial', 30)

class SudokuGenerator:
    def __init__(self, difficulty=0.5):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.difficulty = difficulty  # 0.3 easy, 0.5 medium, 0.7 hard
        
    def is_valid(self, grid, row, col, num):
        # Check row
        for x in range(GRID_SIZE):
            if grid[row][x] == num:
                return False
        
        # Check column
        for x in range(GRID_SIZE):
            if grid[x][col] == num:
                return False
        
        # Check 3x3 box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if grid[i + start_row][j + start_col] == num:
                    return False
        
        return True
    
    def solve(self, grid):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if grid[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(grid, row, col, num):
                            grid[row][col] = num
                            
                            if self.solve(grid):
                                return True
                            
                            grid[row][col] = 0
                    return False
        return True
    
    def generate(self):
        # Start with an empty grid
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Fill diagonal 3x3 boxes first (these can be filled independently)
        for i in range(0, GRID_SIZE, 3):
            self.fill_box(i, i)
        
        # Solve the rest of the grid
        self.solve(self.grid)
        
        # Create a copy of the solved grid
        solution = [row[:] for row in self.grid]
        
        # Remove numbers based on difficulty
        cells_to_remove = int(GRID_SIZE * GRID_SIZE * self.difficulty)
        
        while cells_to_remove > 0:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            
            if self.grid[row][col] != 0:
                self.grid[row][col] = 0
                cells_to_remove -= 1
        
        return self.grid, solution
    
    def fill_box(self, row, col):
        nums = list(range(1, 10))
        random.shuffle(nums)
        
        for i in range(3):
            for j in range(3):
                self.grid[row + i][col + j] = nums.pop()

class SudokuGame:
    def __init__(self):
        self.generator = SudokuGenerator()
        self.difficulty = 0.3  # Start with easy
        self.reset_game()
        
    def reset_game(self):
        self.original_grid, self.solution = self.generator.generate()
        self.current_grid = [row[:] for row in self.original_grid]
        self.selected_cell = None
        self.game_over = False
        
    def next_level(self):
        self.difficulty = min(0.8, self.difficulty + 0.2)  # Increase difficulty
        self.generator.difficulty = self.difficulty
        self.reset_game()
        
    def select_cell(self, row, col):
        if self.original_grid[row][col] == 0:  # Only select cells that were empty originally
            self.selected_cell = (row, col)
        else:
            self.selected_cell = None
            
    def input_number(self, num):
        if self.selected_cell and not self.game_over:
            row, col = self.selected_cell
            if self.original_grid[row][col] == 0:  # Only modify cells that were empty originally
                self.current_grid[row][col] = num
                
    def delete_number(self):
        if self.selected_cell and not self.game_over:
            row, col = self.selected_cell
            if self.original_grid[row][col] == 0:  # Only modify cells that were empty originally
                self.current_grid[row][col] = 0
                
    def is_valid_move(self, row, col, num):
        if num == 0:  # Empty cell is always valid
            return True
            
        # Check row
        for x in range(GRID_SIZE):
            if x != col and self.current_grid[row][x] == num:
                return False
        
        # Check column
        for x in range(GRID_SIZE):
            if x != row and self.current_grid[x][col] == num:
                return False
        
        # Check 3x3 box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if (i + start_row != row or j + start_col != col) and self.current_grid[i + start_row][j + start_col] == num:
                    return False
        
        return True
    
    def is_solved(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.current_grid[row][col] == 0:
                    return False
                if not self.is_valid_move(row, col, self.current_grid[row][col]):
                    return False
        return True
    
    def draw(self, screen):
        # Draw grid background
        screen.fill(WHITE)
        
        # Draw cells
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x, y = col * CELL_SIZE, row * CELL_SIZE
                
                # Highlight selected cell
                if self.selected_cell == (row, col):
                    pygame.draw.rect(screen, HIGHLIGHT, (x, y, CELL_SIZE, CELL_SIZE))
                else:
                    pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))
                
                # Draw cell value
                if self.current_grid[row][col] != 0:
                    num = self.current_grid[row][col]
                    text_color = BLACK
                    
                    # If it's a user-entered value, check validity
                    if self.original_grid[row][col] == 0:
                        if self.is_valid_move(row, col, num):
                            text_color = GREEN
                        else:
                            text_color = RED
                    
                    text = number_font.render(str(num), True, text_color)
                    text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                    screen.blit(text, text_rect)
        
        # Draw grid lines
        for i in range(GRID_SIZE + 1):
            line_width = 3 if i % 3 == 0 else 1
            # Horizontal lines
            pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), line_width)
            # Vertical lines
            pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), line_width)
        
        # Draw buttons
        reset_button = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH - BUTTON_MARGIN, WIDTH + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(screen, LIGHT_GRAY, reset_button)
        reset_text = button_font.render("Reset", True, BLACK)
        reset_text_rect = reset_text.get_rect(center=reset_button.center)
        screen.blit(reset_text, reset_text_rect)
        
        next_button = pygame.Rect(WIDTH // 2 + BUTTON_MARGIN, WIDTH + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(screen, LIGHT_GRAY, next_button)
        next_text = button_font.render("Next Level", True, BLACK)
        next_text_rect = next_text.get_rect(center=next_button.center)
        screen.blit(next_text, next_text_rect)
        
        # Draw game over message
        if self.game_over:
            message = message_font.render("Puzzle Solved!", True, BLUE)
            message_rect = message.get_rect(center=(WIDTH // 2, WIDTH + BUTTON_HEIGHT + 2 * BUTTON_MARGIN))
            screen.blit(message, message_rect)
            
    def check_buttons(self, pos):
        reset_button = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH - BUTTON_MARGIN, WIDTH + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT)
        next_button = pygame.Rect(WIDTH // 2 + BUTTON_MARGIN, WIDTH + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT)
        
        if reset_button.collidepoint(pos):
            self.reset_game()
            return True
        elif next_button.collidepoint(pos) and self.game_over:
            self.next_level()
            return True
        return False

def main():
    game = SudokuGame()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Check if clicked on a button
                if game.check_buttons(pos):
                    continue
                
                # Check if clicked on the grid
                if pos[1] < WIDTH:
                    col = pos[0] // CELL_SIZE
                    row = pos[1] // CELL_SIZE
                    game.select_cell(row, col)
                    
            if event.type == pygame.KEYDOWN:
                if game.selected_cell:
                    if event.key == pygame.K_BACKSPACE:
                        game.delete_number()
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, 
                                      pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        num = int(pygame.key.name(event.key))
                        game.input_number(num)
                    elif event.key in [pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP5, 
                                      pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9]:
                        num = int(pygame.key.name(event.key)[1])
                        game.input_number(num)
        
        # Check if the puzzle is solved
        if not game.game_over and game.is_solved():
            game.game_over = True
        
        # Draw everything
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
