import pygame
import os
import random
import sys

# settings
SCREEN_SIZE = (1280, 720)
TILE_SIZE = 300
GRID_ROWS = 3
GRID_COLS = 4
FPS = 60

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()


GRID_WIDTH = GRID_COLS * TILE_SIZE
GRID_HEIGHT = GRID_ROWS * TILE_SIZE
OFFSET_X = (SCREEN_SIZE[0] - GRID_WIDTH) // 2
OFFSET_Y = (SCREEN_SIZE[1] - GRID_HEIGHT) // 2

# images load
class Block(pygame.sprite.Sprite):
    def __init__(self, img, pos, correct_index):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect(topleft=pos)
        self.correct_index = correct_index
        self.dragging = False

    def update(self, mouse_pos):
        if self.dragging:
            self.rect.center = mouse_pos

# tiles load
def load_tiles(path):
    images = []
    files = sorted(f for f in os.listdir(path) if f.endswith('.png'))
    if not files:
        raise FileNotFoundError("No PNG images found in the folder.")

    for f in files:
        img = pygame.image.load(os.path.join(path, f)).convert_alpha()
        images.append(pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)))
    return images

# grid generation
def make_grid(images):
    blocks = pygame.sprite.Group()

    coords = [(x * TILE_SIZE + OFFSET_X, y * TILE_SIZE + OFFSET_Y)
              for y in range(GRID_ROWS)
              for x in range(GRID_COLS)]

    indices = list(range(len(images)))
    random.shuffle(indices)

    for idx, pos in zip(indices, coords):
        block = Block(images[idx], pos, idx)
        blocks.add(block)
    return blocks

# check if row ordering is correct
def is_correct(blocks):
    rows = {}
    for block in blocks:
        # --- Adjust calculation to use OFFSET_Y ---
        y = (block.rect.y - OFFSET_Y) // TILE_SIZE
        if y not in rows:
            rows[y] = []
        rows[y].append(block)

    for row_blocks in rows.values():
        row_blocks.sort(key=lambda b: b.rect.x)
        correct_indices = [block.correct_index for block in row_blocks]
        if correct_indices != sorted(correct_indices):
            return False
    return True

# button rendering
def draw_button(surface, rect, text, font, color=(180, 180, 180)):
    pygame.draw.rect(surface, color, rect)
    label = font.render(text, True, (0, 0, 0))
    surface.blit(label, (rect.x + (rect.width - label.get_width()) // 2, rect.y + (rect.height - label.get_height()) // 2))

# draw grid lines
def draw_grid(surface):
    # --- Use calculated OFFSET_X and OFFSET_Y for grid lines ---
    for x in range(GRID_COLS + 1):
        pygame.draw.line(surface, (200, 200, 200), (OFFSET_X + x * TILE_SIZE, OFFSET_Y), (OFFSET_X + x * TILE_SIZE, OFFSET_Y + GRID_ROWS * TILE_SIZE), 2)
    for y in range(GRID_ROWS + 1):
        pygame.draw.line(surface, (200, 200, 200), (OFFSET_X, OFFSET_Y + y * TILE_SIZE), (OFFSET_X + GRID_COLS * TILE_SIZE, OFFSET_Y + y * TILE_SIZE), 2)
    # -----------------------------------------------------------

# game loop
def main():
    try:
        images = load_tiles('images')
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit()

    blocks = make_grid(images)
    selected = None
    solved_time = None
    check_result = None
    result_time = 0
    show_grid = False 

    font = pygame.font.SysFont(None, 36)
    result_font = pygame.font.SysFont(None, 48)

    check_button = pygame.Rect(SCREEN_SIZE[0] // 2 - 140, SCREEN_SIZE[1] - 60, 120, 40)
    grid_button = pygame.Rect(SCREEN_SIZE[0] // 2 + 20, SCREEN_SIZE[1] - 60, 120, 40)

    running = True
    while running:
        dt = clock.tick(FPS)
        mouse = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if check_button.collidepoint(e.pos):
                    check_result = "Correct!" if is_correct(blocks) else "Incorrect"
                    result_time = pygame.time.get_ticks()
                elif grid_button.collidepoint(e.pos):
                    show_grid = not show_grid
                else:
                    for block in reversed(blocks.sprites()):
                        if block.rect.collidepoint(e.pos):
                            block.dragging = True
                            selected = block
                            break
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                if selected:
                    selected.dragging = False
                    # --- Adjust snapping calculation to use OFFSET_X and OFFSET_Y ---
                    selected.rect.topleft = (
                        round((selected.rect.x - OFFSET_X) / TILE_SIZE) * TILE_SIZE + OFFSET_X,
                        round((selected.rect.y - OFFSET_Y) / TILE_SIZE) * TILE_SIZE + OFFSET_Y
                    )
                    selected = None
                    if is_correct(blocks):
                        solved_time = pygame.time.get_ticks()

        if selected:
            selected.update(mouse)

        if solved_time and pygame.time.get_ticks() - solved_time > 2000:
            blocks = make_grid(images)
            solved_time = None

        screen.fill((50, 50, 50))
        blocks.draw(screen)

        if show_grid:
            draw_grid(screen)

        draw_button(screen, check_button, "Check", font)
        draw_button(screen, grid_button, "Grid", font)

        if check_result and pygame.time.get_ticks() - result_time < 2000:
            color = (0, 200, 0) if check_result == "Correct!" else (200, 0, 0)
            result_text = result_font.render(check_result, True, color)
            screen.blit(result_text, (SCREEN_SIZE[0] // 2 - result_text.get_width() // 2, 20))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()