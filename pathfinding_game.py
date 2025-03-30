import pygame
import numpy as np
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
GAME_SIZE = 800
BUTTON_HEIGHT = 80  # Increased button area height
WINDOW_SIZE = GAME_SIZE
TOTAL_WINDOW_HEIGHT = GAME_SIZE + BUTTON_HEIGHT
CELL_SIZE = 40
GRID_SIZE = GAME_SIZE // CELL_SIZE
PLAYER_SIZE = 30
WALL_THICKNESS = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
GRASS_GREEN = (34, 139, 34)  # Darker green for grass
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (180, 180, 180)

class PathfindingGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, TOTAL_WINDOW_HEIGHT))
        pygame.display.set_caption('Pokémon-Style Pathfinding')
        self.clock = pygame.time.Clock()
        
        # Create buttons
        button_width = 150  # Increased button width
        button_spacing = 20
        total_buttons_width = button_width * 2 + button_spacing
        start_x = (WINDOW_SIZE - total_buttons_width) // 2
        
        self.reset_button = pygame.Rect(start_x, 20, button_width, 40)  # Moved buttons down
        self.new_map_button = pygame.Rect(start_x + button_width + button_spacing, 20, button_width, 40)
        
        self.reset_game()

    def find_valid_position(self, min_distance_from_edge=2):
        while True:
            x = random.randint(min_distance_from_edge, GRID_SIZE - min_distance_from_edge - 1)
            y = random.randint(min_distance_from_edge, GRID_SIZE - min_distance_from_edge - 1)
            if self.grid[y, x] == 0:  # If it's a valid position (not a wall)
                return (x, y)

    def reset_game(self):
        # Create a grid with walls (1) and paths (0)
        self.grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        self.generate_landscape()
        
        # Find valid positions for start and end
        self.start_pos = self.find_valid_position()
        self.end_pos = self.find_valid_position()
        
        # Ensure start and end are not too close
        while abs(self.end_pos[0] - self.start_pos[0]) + abs(self.end_pos[1] - self.start_pos[1]) < GRID_SIZE // 3:
            self.end_pos = self.find_valid_position()
        
        # Player position (now in pixels instead of grid coordinates)
        self.player_pos = [self.start_pos[0] * CELL_SIZE + CELL_SIZE // 2,
                         self.start_pos[1] * CELL_SIZE + CELL_SIZE // 2]
        self.player_speed = 8  # Increased speed
        self.movement = [0, 0]
        
        # Game state
        self.game_over = False
        self.won = False

    def reset_player(self):
        # Only reset player position to start
        self.player_pos = [self.start_pos[0] * CELL_SIZE + CELL_SIZE // 2,
                         self.start_pos[1] * CELL_SIZE + CELL_SIZE // 2]
        self.movement = [0, 0]
        self.won = False

    def generate_landscape(self):
        # Create outer walls
        self.grid[0, :] = 1
        self.grid[-1, :] = 1
        self.grid[:, 0] = 1
        self.grid[:, -1] = 1
        
        # Create large open areas (like Pokémon routes)
        for _ in range(3):  # Number of main areas
            area_width = random.randint(8, 12)
            area_height = random.randint(8, 12)
            x = random.randint(2, GRID_SIZE - area_width - 2)
            y = random.randint(2, GRID_SIZE - area_height - 2)
            
            # Create main area
            self.grid[y:y+area_height, x:x+area_width] = 1
            
            # Create wide paths connecting areas
            path_width = 5  # Wider paths
            path_length = random.randint(6, 10)
            
            # Create multiple paths from each area
            for _ in range(2):
                # Horizontal path
                path_x = random.randint(2, GRID_SIZE - path_length - 2)
                path_y = random.randint(2, GRID_SIZE - path_width - 2)
                self.grid[path_y:path_y+path_width, path_x:path_x+path_length] = 1
                
                # Vertical path
                path_x = random.randint(2, GRID_SIZE - path_width - 2)
                path_y = random.randint(2, GRID_SIZE - path_length - 2)
                self.grid[path_y:path_y+path_length, path_x:path_x+path_width] = 1

    def handle_movement(self):
        # Update player position based on movement
        new_x = self.player_pos[0] + self.movement[0] * self.player_speed
        new_y = self.player_pos[1] + self.movement[1] * self.player_speed
        
        # Convert to grid coordinates for collision detection
        grid_x = int(new_x // CELL_SIZE)
        grid_y = int(new_y // CELL_SIZE)
        
        # Check if new position is valid (not a wall)
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE and self.grid[grid_y, grid_x] == 0:
            self.player_pos[0] = new_x
            self.player_pos[1] = new_y
            
            # Check if player reached the end
            if grid_x == self.end_pos[0] and grid_y == self.end_pos[1]:
                self.won = True

    def draw(self):
        # Draw button area background
        pygame.draw.rect(self.screen, WHITE, (0, 0, WINDOW_SIZE, BUTTON_HEIGHT))
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        font = pygame.font.Font(None, 32)  # Slightly smaller font
        
        # Reset button
        button_color = BUTTON_HOVER_COLOR if self.reset_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, self.reset_button)
        pygame.draw.rect(self.screen, BLACK, self.reset_button, 2)
        reset_text = font.render('Reset Player', True, BLACK)
        reset_text_rect = reset_text.get_rect(center=self.reset_button.center)
        self.screen.blit(reset_text, reset_text_rect)
        
        # New Map button
        button_color = BUTTON_HOVER_COLOR if self.new_map_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, self.new_map_button)
        pygame.draw.rect(self.screen, BLACK, self.new_map_button, 2)
        new_map_text = font.render('New Map', True, BLACK)
        new_map_text_rect = new_map_text.get_rect(center=self.new_map_button.center)
        self.screen.blit(new_map_text, new_map_text_rect)
        
        # Draw grass background
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y, x] == 0:  # If it's a path
                    pygame.draw.rect(self.screen, GRASS_GREEN,
                                   (x * CELL_SIZE, y * CELL_SIZE + BUTTON_HEIGHT, CELL_SIZE, CELL_SIZE))
        
        # Draw walls (now they're like tall grass or obstacles)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y, x] == 1:
                    pygame.draw.rect(self.screen, GRAY,
                                   (x * CELL_SIZE, y * CELL_SIZE + BUTTON_HEIGHT, CELL_SIZE, CELL_SIZE))
        
        # Draw end position (like a Pokémon Center or Gym)
        pygame.draw.rect(self.screen, BLUE,
                        (self.end_pos[0] * CELL_SIZE, self.end_pos[1] * CELL_SIZE + BUTTON_HEIGHT,
                         CELL_SIZE, CELL_SIZE))
        
        # Draw player (like a Pokémon trainer)
        pygame.draw.circle(self.screen, RED,
                         (int(self.player_pos[0]), int(self.player_pos[1] + BUTTON_HEIGHT)),
                         PLAYER_SIZE // 2)
        
        # Draw game status
        if self.won:
            # Create a semi-transparent overlay
            overlay = pygame.Surface((WINDOW_SIZE, GAME_SIZE))
            overlay.fill(WHITE)
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, BUTTON_HEIGHT))
            
            # Draw victory message in the center
            text = "You reached the destination!"
            color = GREEN
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, GAME_SIZE // 2 + BUTTON_HEIGHT))
            self.screen.blit(text_surface, text_rect)
        else:
            # Draw initial message at the top
            text = "Find the blue building! Use arrow keys to move"
            color = BLACK
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, 10))  # Moved text down
            self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.reset_button.collidepoint(event.pos):
                        self.reset_player()
                    elif self.new_map_button.collidepoint(event.pos):
                        self.reset_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Quit game
                        pygame.quit()
                        sys.exit()
            
            # Handle continuous key presses
            keys = pygame.key.get_pressed()
            self.movement = [0, 0]
            if keys[pygame.K_LEFT]:
                self.movement[0] = -1
            if keys[pygame.K_RIGHT]:
                self.movement[0] = 1
            if keys[pygame.K_UP]:
                self.movement[1] = -1
            if keys[pygame.K_DOWN]:
                self.movement[1] = 1
            
            self.handle_movement()
            self.draw()
            self.clock.tick(60)

if __name__ == '__main__':
    game = PathfindingGame()
    game.run() 