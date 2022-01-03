import pygame
from wink_detection import *
from dino import *
import cv2
import time
import os

screen_size = (800, 600)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
RED = (255,0,0)

cap = cv2.VideoCapture(0)
modes = ['Keep both your eyes opened for 5 sec. Press enter to start',
         'Keep both your eyes closed for 5 sec. Press enter to start',
         'Keep your left eye closed for 5 sec. Press enter to start',
         'Keep your right eye closed for 5 sec. Press enter to start']


class Game(object):
    standard = [(492.03125, 469.5625), (269.8378378378378, 268.0), (210.94594594594594, 265.4054054054054), (302.6216216216216, 215.64864864864865)]
    highest_score = 0
    def __init__(self, screen):
        self.font = pygame.font.Font(None, 40)
        # phase
        self.calibrate = False
        self.have_not_start = True
        self.game_over = False
        self.finish_calibrate = False
        self.initial = False
        # setting
        self.menu = Menu(("Calibration", "Start", "Exit"), font_color=WHITE, select_color=RED)
        # dino run
        self.dino = Dino(screen, 44,47)
        self.gamespeed = 4
        self.ground = Ground(screen, -1*self.gamespeed)
        self.scoreboards = [Scoreboard(screen), Scoreboard(screen, SCREEN_WIDTH*0.78)]
        # cacti, pteras, clouds
        self.enemies = [pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()]
        self.last_obstacle = pygame.sprite.Group()
        self.counter = 0
        # calibrate
        self.left_val = []
        self.right_val = []
        self.calibrate_stop = True
        self.calibrate_count = 0
        self.calibrate_succeed = False
        self.t_start = 0
        self.interval = 1
        # detect
        self.window = []
        self.motion = ""
        self.last_motion = ""
        
    def run_logic(self ,screen):
        if self.calibrate and not self.calibrate_stop:
            if time.time() - self.t_start > self.interval:
                self.standard.append(ave(self.left_val, self.right_val))
                self.left_val = []
                self.right_val = []
                self.calibrate_stop = True
                self.calibrate_count = (self.calibrate_count + 1) % 4
                if self.calibrate_count == 0:
                    self.calibrate_succeed = check_valid(self.standard)
                    self.finish_calibrate = True
                    self.calibrate = False
                print(self.standard)
        
        if not self.have_not_start and not self.initial:
            if self.counter % 700 == 699:
                self.ground.speed -= 1
                self.gamespeed += 1
        
        if self.dino.isDead:
            self.game_over = True
            self.gamespeed = 0
            if self.dino.score > self.highest_score:
                self.highest_score = self.dino.score
        
        # wink activated logic
        if not self.have_not_start: 
            motions = {0: 'both eyes opened', 1: 'both eyes closed', 2: 'left eye closed', 3: 'right eye closed'}
            wink = detect_wink(cap, self.standard, self.window)
            if wink:
                self.last_motion = self.motion
                self.motion = wink
                if self.initial:
                    if self.motion == motions[0] and self.last_motion == motions[1]:
                        self.dino.isJumping = True
                        self.dino.isBlinking = False
                        self.dino.movement[1] = -1*self.dino.jumpSpeed
                elif not self.game_over:
                    if self.motion == motions[0] and self.last_motion == motions[2]:
                        if self.dino.rect.bottom == int(0.98*height):
                            self.dino.isJumping = True
                            self.dino.movement[1] = -1*self.dino.jumpSpeed
                    elif self.motion == motions[3]:
                        if not (self.dino.isJumping and self.dino.isDead):
                            self.dino.isDucking = True
                    elif self.motion == motions[0] and self.last_motion == motions[3]:
                        self.dino.isDucking = False 
                else:
                    if self.motion == motions[0] and self.last_motion == motions[1]:
                        self.__init__(screen)
                        Cactus.containers = self.enemies[0]
                        Ptera.containers = self.enemies[1]
                        Cloud.containers = self.enemies[2]
                        self.have_not_start = False
                        self.initial = True
                        
    
    def process_events(self, screen):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                cv2.destroyAllWindows()
                return True
            self.menu.event_handler(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.have_not_start and not self.calibrate and not self.finish_calibrate:
                        if self.menu.state == 0:
                            self.calibrate = True
                            self.standard = []
                        elif self.menu.state == 1:
                            self.__init__(screen)
                            Cactus.containers = self.enemies[0]
                            Ptera.containers = self.enemies[1]
                            Cloud.containers = self.enemies[2]
                            self.have_not_start = False
                            self.initial = True
                        elif self.menu.state == 2:
                            cap.release()
                            cv2.destroyAllWindows()
                            return True
                    elif self.calibrate and self.calibrate_stop:
                        self.calibrate_stop = False
                        self.t_start = time.time()
                    elif self.finish_calibrate:
                        self.finish_calibrate = False
                        self.calibrate = False
                elif event.key == pygame.K_ESCAPE:
                    self.have_not_start = True
                    self.calibrate = False
                # test dino run
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self.initial == True:
                        self.dino.isJumping = True
                        self.dino.isBlinking = False
                        self.dino.movement[1] = -1*self.dino.jumpSpeed
                    elif self.game_over == False:
                        if self.dino.rect.bottom == int(0.98*height):
                            self.dino.isJumping = True
                            self.dino.movement[1] = -1*self.dino.jumpSpeed
                    else:
                        self.__init__(screen)
                        Cactus.containers = self.enemies[0]
                        Ptera.containers = self.enemies[1]
                        Cloud.containers = self.enemies[2]
                        self.have_not_start = False
                        self.initial = True
                elif event.key == pygame.K_DOWN:
                    if not (self.dino.isJumping and self.dino.isDead):
                        self.dino.isDucking = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.dino.isDucking = False 
                    
        return False
    
    def display_frame(self, screen):
        screen.fill(BLACK)
        if self.have_not_start:
            if self.calibrate:
                if self.calibrate_stop:
                    self.display_message(screen, modes[self.calibrate_count])
                else:
                    EAR_val = calibrate_wink(cap)
                    if EAR_val:
                        (left, right) = EAR_val
                        self.left_val.append(left)
                        self.right_val.append(right)
                    frame, frame_rect = load_image('frame.PNG', sizex=800, sizey=600)
                    screen.blit(frame, frame_rect)
            elif self.finish_calibrate:
                if self.calibrate_succeed:
                    self.display_message(screen, "Calibration Succeeded! You can start the game")
                else:
                    self.display_message(screen, "Calibration Failed! Please re-calibrate")
            else:
                self.menu.display_frame(screen)
        elif self.initial:
            screen.fill(WHITE)
            self.display_message(screen,"Blink to Start!")
            # frame, frame_rect = load_image('frame.PNG', sizex=800, sizey=600)
            # screen.blit(frame, frame_rect)
            initialscreen(screen, self.dino)
            if not self.dino.isJumping and not self.dino.isBlinking:
                self.initial = False
            self.display_message(screen, self.motion, color=(255, 255, 0), pos=(100, 100))
        else:
            screen.fill(WHITE)
            detect_wink(cap, self.standard, self.window)
            gamingscreen(screen, self.game_over, self.dino, self.enemies, self.last_obstacle, self.ground, self.counter, self.gamespeed, self.scoreboards, self.highest_score)
            self.display_message(screen, self.motion, color=(255, 255, 0), pos=(100, 100))
        
        pygame.display.flip()
            
    def display_message(self,screen,message,color=(255,0,0), pos=(-1, -1)):
        label = self.font.render(message,True,color)
        # Get the width and height of the label
        width = label.get_width()
        height = label.get_height()
        # Determine the position of the label
        if pos == (-1, -1):
            posX = (SCREEN_WIDTH /2) - (width /2)
            posY = (SCREEN_HEIGHT /2) - (height /2)
        else:
            posX, posY = pos
        # Draw the label onto the screen
        screen.blit(label,(posX,posY))
            
                    
                    
class Menu(object):
    def __init__(self,items,font_color=(255, 255, 255),select_color=(255,0,0),ttf_font=None,font_size=60):
        self.font_color = font_color
        self.select_color = select_color
        self.items = items
        self.font = pygame.font.Font(ttf_font,font_size)
        self.state = 0
        
    def display_frame(self,screen):
        for index, item in enumerate(self.items):
            if self.state == index:
                label = self.font.render(item,True,self.select_color)
            else:
                label = self.font.render(item,True,self.font_color)
            
            width = label.get_width()
            height = label.get_height()
            
            posX = (SCREEN_WIDTH /2) - (width /2)
            # t_h: total height of text block
            t_h = len(self.items) * height
            posY = (SCREEN_HEIGHT /2) - (t_h /2) + (index * height)
            
            screen.blit(label,(posX,posY))
        
    def event_handler(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.state > 0:
                    self.state -= 1
            elif event.key == pygame.K_DOWN:
                if self.state < len(self.items) -1:
                    self.state += 1
