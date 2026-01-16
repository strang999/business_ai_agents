import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 400
HEIGHT = 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird Clone')

# Set up fonts
FONT = pygame.font.SysFont('Arial', 32)

# Define game variables
GRAVITY = 0.5
GAME_SPEED = 3

# Colors
WHITE = (255, 255, 255)

# Load images
try:
    BIRD_IMAGE = pygame.image.load('bird.png').convert_alpha()
    # Scale down the bird image
    BIRD_IMAGE = pygame.transform.scale(BIRD_IMAGE, (50, 35))
    BG_IMAGE = pygame.image.load('bg.png').convert()
    PIPE_IMAGE = pygame.image.load('pipe.png').convert_alpha()
except pygame.error as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    sys.exit()

# Player class representing the character
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Use the scaled bird image for the player
        self.image = BIRD_IMAGE
        self.rect = self.image.get_rect()
        self.rect.center = (50, HEIGHT // 2)  # Start position
        self.velocity = 0  # Initial velocity

    def update(self):
        # Apply gravity to the player's velocity
        self.velocity += GRAVITY
        # Update the player's position
        self.rect.y += int(self.velocity)

        # Prevent the player from moving off-screen
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity = 0
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity = 0

    def flap(self):
        # Move the player upward when the spacebar is pressed
        self.velocity = -10

# Pipe class for obstacles
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, orientation):
        super().__init__()
        # Flip the pipe image for the top pipe
        if orientation == 'top':
            self.image = pygame.transform.flip(PIPE_IMAGE, False, True)
            self.rect = self.image.get_rect(midbottom=(x, y - 100))
        else:
            self.image = PIPE_IMAGE
            self.rect = self.image.get_rect(midtop=(x, y + 100))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        # Move the pipe leftward
        self.rect.x -= GAME_SPEED
        # Remove the pipe when it's off-screen
        if self.rect.right < 0:
            self.kill()

# Function to create a new pair of pipes
def create_pipes():
    # Randomly determine the gap's vertical position
    gap_center = random.randint(150, HEIGHT - 150)
    top_pipe = Pipe(WIDTH, gap_center, 'top')
    bottom_pipe = Pipe(WIDTH, gap_center, 'bottom')
    return top_pipe, bottom_pipe

# Main game function
def main_game():
    global GAME_SPEED
    clock = pygame.time.Clock()
    score = 0
    running = True
    game_over = False

    # Sprite groups for efficient rendering and updates
    all_sprites = pygame.sprite.Group()
    pipe_group = pygame.sprite.Group()

    # Create the player object and add it to the sprite group
    player = Player()
    all_sprites.add(player)

    # Custom event for adding new pipes
    ADDPIPE = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDPIPE, 1500)  # New pipe every 1.5 seconds

    while running:
        clock.tick(60)  # Limit the frame rate to 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    player.flap()  # Make the player jump
                if event.key == pygame.K_r and game_over:
                    main_game()  # Restart the game

            elif event.type == ADDPIPE and not game_over:
                # Add new pipes to the game
                top_pipe, bottom_pipe = create_pipes()
                all_sprites.add(top_pipe, bottom_pipe)
                pipe_group.add(top_pipe, bottom_pipe)

        if not game_over:
            all_sprites.update()

            # Check for collisions with pipes
            if pygame.sprite.spritecollide(player, pipe_group, False, pygame.sprite.collide_mask):
                game_over = True
            # Check for collisions with the screen boundaries
            if player.rect.top <= 0 or player.rect.bottom >= HEIGHT:
                game_over = True

            # Update the score and remove off-screen pipes
            for pipe in pipe_group:
                if pipe.rect.right < player.rect.left and not hasattr(pipe, 'scored'):
                    score += 0.5  # Each pipe counts as 0.5 points
                    pipe.scored = True  # Ensure each pipe is only counted once

            # Gradually increase the game speed to raise difficulty
            if int(score) % 5 == 0 and score != 0:
                GAME_SPEED += 0.001  # Slightly increase the speed

        # Draw the background
        SCREEN.blit(BG_IMAGE, (0, 0))

        # Draw all sprites (player and pipes)
        all_sprites.draw(SCREEN)

        # Display the current score
        score_surface = FONT.render(f'Score: {int(score)}', True, WHITE)
        SCREEN.blit(score_surface, (10, 10))

        if game_over:
            # Display 'Game Over' message
            game_over_surface = FONT.render('Game Over!', True, WHITE)
            SCREEN.blit(game_over_surface, (WIDTH // 2 - game_over_surface.get_width() // 2, HEIGHT // 2 - 50))
            restart_surface = FONT.render('Press R to Restart', True, WHITE)
            SCREEN.blit(restart_surface, (WIDTH // 2 - restart_surface.get_width() // 2, HEIGHT // 2))

        # Update the display
        pygame.display.flip()

# Run the game
if __name__ == '__main__':
    main_game()
