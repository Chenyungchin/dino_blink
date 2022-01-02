import pygame
import random
from game import Game

screen_size = (800, 600)
FPS = 60

def main():
    pygame.init()

    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    pygame.display.set_caption("Dino Blink")
    game = Game(screen)
    done = False
    while not done:
        done = game.process_events(screen)
        game.run_logic()
        game.display_frame(screen)
        clock.tick(FPS)
        
    pygame.quit()
    
if __name__ == '__main__':
    main()
    