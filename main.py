import pygame
import random
from entities import Unit
from constants import *

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike Game")

def generate_level():
    width = SCREEN_WIDTH // TILE_SIZE
    height = SCREEN_HEIGHT // TILE_SIZE
    level = [[1 for _ in range(width)] for _ in range(height)]  # Initialize all as walls
    
    # Generate random number of rooms
    num_rooms = random.randint(5, 10)
    rooms = []

    # Force outer edges to always be walls
    for y in range(height):
        level[y][0] = 1
        level[y][width-1] = 1
    for x in range(width):
        level[0][x] = 1
        level[height-1][x] = 1
    
    # Create multiple rooms
    for _ in range(num_rooms):
        attempts = 0
        while attempts < 100:  # Limit attempts to prevent infinite loop
            room_x = random.randint(1, width-7)  # Leave space for outer walls
            room_y = random.randint(1, height-7)  # Leave space for outer walls
            room_w = random.randint(5, 10)
            room_h = random.randint(4, 8)
            
            # Check if room overlaps with existing rooms
            new_room = pygame.Rect(room_x, room_y, room_w, room_h)
            if not any(new_room.inflate(2,2).colliderect(pygame.Rect(r[0], r[1], r[2], r[3])) for r in rooms):
                rooms.append((room_x, room_y, room_w, room_h))
                break
            attempts += 1
    
    # Create the rooms
    for room in rooms:
        room_x, room_y, room_w, room_h = room
        # Fill room with floor
        for y in range(room_y, room_y + room_h):
            for x in range(room_x, room_x + room_w):
                if 0 < y < height-1 and 0 < x < width-1:  # Ensure we're not touching outer walls
                    level[y][x] = 0
    
    # Connect rooms with corridors
    for i in range(len(rooms)-1):
        room1_x = rooms[i][0] + rooms[i][2]//2
        room1_y = rooms[i][1] + rooms[i][3]//2
        room2_x = rooms[i+1][0] + rooms[i+1][2]//2
        room2_y = rooms[i+1][1] + rooms[i+1][3]//2
        
        # Create horizontal corridor
        for x in range(min(room1_x, room2_x), max(room1_x, room2_x) + 1):
            if 0 < room1_y < height-1 and 0 < x < width-1:  # Ensure we're not touching outer walls
                level[room1_y][x] = 0
                # Create doorway
                if x == room1_x or x == room2_x:
                    if 0 < room1_y-1 < height-1:
                        level[room1_y-1][x] = 0
                    if 0 < room1_y+1 < height-1:
                        level[room1_y+1][x] = 0
        
        # Create vertical corridor
        for y in range(min(room1_y, room2_y), max(room1_y, room2_y) + 1):
            if 0 < y < height-1 and 0 < room2_x < width-1:  # Ensure we're not touching outer walls
                level[y][room2_x] = 0
                # Create doorway
                if y == room1_y or y == room2_y:
                    if 0 < room2_x-1 < width-1:
                        level[y][room2_x-1] = 0
                    if 0 < room2_x+1 < width-1:
                        level[y][room2_x+1] = 0
    
    # Find a random room for player starting position
    start_room = random.choice(rooms)
    player_x = start_room[0] + start_room[2]//2
    player_y = start_room[1] + start_room[3]//2

    # Generate coins in rooms
    coins = []
    for room in rooms:
        room_x, room_y, room_w, room_h = room
        # Number of coins in the room
        num_coins = random.randint(1, 3)
        for _ in range(num_coins):
            coin_x = random.randint(room_x + 1, room_x + room_w - 2)
            coin_y = random.randint(room_y + 1, room_y + room_h - 2)
            coins.append(pygame.Rect(coin_x * TILE_SIZE + TILE_SIZE // 4, coin_y * TILE_SIZE + TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE // 2))
            
    return level, player_x, player_y, width, height, coins
def main():
    clock = pygame.time.Clock()
    current_level = 1
    running = True
    
    # Initialize level
    level, player_x, player_y, level_width, level_height, coins = generate_level()
    player = Unit(player_x, player_y)
    score = 0
    
    # Create wall list
    walls = []
    for y in range(level_height):
        for x in range(level_width):
            if level[y][x] == 1:
                walls.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
        
        # Get the current state of all keyboard buttons
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-0.25, 0, walls)
        if keys[pygame.K_RIGHT]:
            player.move(0.25, 0, walls)
        if keys[pygame.K_UP]:
            player.move(0, -0.25, walls)
        if keys[pygame.K_DOWN]:
            player.move(0, 0.25, walls)
        
        # Draw
        screen.fill(BLACK)
        
        # Draw walls
        for wall in walls:
            pygame.draw.rect(screen, GRAY, wall)
        
        # Draw player
        pygame.draw.rect(screen, GREEN, player.rect)

        # Check for coin collision
        for coin in coins[:]:
            if player.rect.colliderect(coin):
                coins.remove(coin)
                score += 10
        
        # Check if all coins are collected
        if len(coins) == 0:
            # Generate new level
            current_level += 1
            level, player_x, player_y, level_width, level_height, coins = generate_level()
            player = Unit(player_x, player_y)
            
            # Update walls for new level
            walls = []
            for y in range(level_height):
                for x in range(level_width):
                    if level[y][x] == 1:
                        walls.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        
        # Draw coins
        for coin in coins:
            pygame.draw.rect(screen, YELLOW, coin)
        
        # Draw score and level
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {current_level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()