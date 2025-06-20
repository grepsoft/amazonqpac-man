import pygame
import sys
import random

pygame.init()

# Constants
WIDTH, HEIGHT = 600, 650
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Game setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()

# Simple maze (1 = wall, 0 = path, 2 = dot, 3 = prize box)
maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,3,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,2,1,1,1,1,1,1,2,1,2,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,0,1,1,0,1,1,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,0,0,0,0,0,0,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,1,0,0,0,1,0,0,1,2,1,1,1,1],
    [0,0,0,0,2,0,0,1,0,0,0,1,0,0,0,2,0,0,0,0],
    [1,1,1,1,2,1,0,1,1,1,1,1,0,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,0,0,0,0,0,0,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,1,1,0,1,1,0,1,1,1,2,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,2,2,1,2,2,2,2,2,3,3,2,2,2,2,2,1,2,2,1],
    [1,1,2,1,2,1,2,1,1,1,1,1,1,2,1,2,1,2,1,1],
    [1,2,2,2,2,1,2,2,2,1,1,2,2,2,1,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,2,1],
    [1,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# Game state
def reset_game():
    global player_x, player_y, score, enemies, game_over, enemy_timer
    player_x, player_y = 9, 15
    score = 0
    game_over = False
    enemy_timer = 0
    enemies = [[1, 1, 1, 0], [18, 1, -1, 0], [9, 9, 0, 1], [10, 9, 0, -1]]

reset_game()
show_quit_dialog = False

def draw_maze():
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            x, y = col * 30, row * 30
            if maze[row][col] == 1:  # Wall
                pygame.draw.rect(screen, BLUE, (x, y, 30, 30))
            elif maze[row][col] == 2:  # Dot
                pygame.draw.circle(screen, WHITE, (x + 15, y + 15), 3)
            elif maze[row][col] == 3:  # Prize box
                pygame.draw.rect(screen, GREEN, (x + 10, y + 10, 10, 10))

def draw_player():
    x, y = player_x * 30 + 15, player_y * 30 + 15
    pygame.draw.circle(screen, YELLOW, (x, y), 12)

def move_player(dx, dy):
    global player_x, player_y, score
    new_x, new_y = player_x + dx, player_y + dy
    
    if (0 <= new_y < len(maze) and 0 <= new_x < len(maze[0]) and 
        maze[new_y][new_x] != 1):
        player_x, player_y = new_x, new_y
        
        if maze[player_y][player_x] == 2:
            maze[player_y][player_x] = 0
            score += 10
        elif maze[player_y][player_x] == 3:
            maze[player_y][player_x] = 0
            score += 50

def draw_enemies():
    for enemy in enemies:
        x, y = enemy[0] * 30 + 15, enemy[1] * 30 + 15
        pygame.draw.circle(screen, RED, (x, y), 12)

def move_enemies():
    global enemy_timer
    enemy_timer += 1
    
    if enemy_timer % 15 != 0:  # Move every 15 frames (slightly faster)
        return
    
    for enemy in enemies:
        # Get possible directions
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        valid_moves = []
        
        for dx, dy in directions:
            new_x, new_y = enemy[0] + dx, enemy[1] + dy
            if (0 <= new_y < len(maze) and 0 <= new_x < len(maze[0]) and 
                maze[new_y][new_x] != 1):
                valid_moves.append((dx, dy))
        
        if valid_moves:
            # Calculate direction towards player
            player_dx = player_x - enemy[0]
            player_dy = player_y - enemy[1]
            
            # Find best move towards player
            best_move = None
            best_distance = float('inf')
            
            for dx, dy in valid_moves:
                new_x, new_y = enemy[0] + dx, enemy[1] + dy
                distance = abs(player_x - new_x) + abs(player_y - new_y)
                if distance < best_distance:
                    best_distance = distance
                    best_move = (dx, dy)
            
            # 80% chance to chase player, 20% random movement
            if best_move and random.random() < 0.8:
                dx, dy = best_move
            else:
                dx, dy = random.choice(valid_moves)
            
            enemy[0] += dx
            enemy[1] += dy
            enemy[2], enemy[3] = dx, dy

def check_collision():
    for enemy in enemies:
        if player_x == enemy[0] and player_y == enemy[1]:
            return True
    return False

def draw_quit_dialog():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    font = pygame.font.Font(None, 48)
    text = font.render("Quit Game? Y/N", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    font = pygame.font.Font(None, 48)
    text1 = font.render("Game Over!", True, WHITE)
    text2 = font.render("Press R to Restart", True, WHITE)
    
    text1_rect = text1.get_rect(center=(WIDTH//2, HEIGHT//2 - 30))
    text2_rect = text2.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))
    
    screen.blit(text1, text1_rect)
    screen.blit(text2, text2_rect)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if show_quit_dialog:
                if event.key == pygame.K_y:
                    running = False
                elif event.key == pygame.K_n:
                    show_quit_dialog = False
            elif game_over:
                if event.key == pygame.K_r:
                    reset_game()
            else:
                if event.key == pygame.K_ESCAPE:
                    show_quit_dialog = True
                elif event.key == pygame.K_UP:
                    move_player(0, -1)
                elif event.key == pygame.K_DOWN:
                    move_player(0, 1)
                elif event.key == pygame.K_LEFT:
                    move_player(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    move_player(1, 0)
    
    if not game_over and not show_quit_dialog:
        move_enemies()
        if check_collision():
            game_over = True
    
    screen.fill(BLACK)
    draw_maze()
    draw_player()
    draw_enemies()
    
    # Score display
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, HEIGHT - 40))
    
    if show_quit_dialog:
        draw_quit_dialog()
    elif game_over:
        draw_game_over()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()