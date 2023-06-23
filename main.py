import sys 
import pygame
from pygame.locals import *
from pygame import mixer
from os import path

pygame.mixer.pre_init(44100,-16,2,512)
mixer.init()
pygame.init()

clock=pygame.time.Clock()
fps=60

#create game screen/ platformer 
screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Moving Mouse')

#define font
font_score=pygame.font.SysFont('Bauhaus 93', 30)

#define game variables
tile_size = 20
game_over=0
main_menu= True
level=1
max_levels=5
score=0

#define colours
white=(255,255,255)

#load images
skybg_img=pygame.image.load('data/background/skybackground.jpeg')
replay_img=pygame.image.load('data/replay.png')
intro_img=pygame.image.load('data/introscreen.png')
start_img=pygame.image.load('data/start.png')
exit_img=pygame.image.load('data/exit.png')
charA_img=pygame.image.load('data/mouseA.png')
charB_img=pygame.image.load('data/mouseBside.png')


#load sounds
pygame.mixer.music.load('data/background.wav')
pygame.mixer.music.play(-1,0,5000)
pygame.mixer.music.set_volume(0.5)
cheese_fx=pygame.mixer.Sound('data/cheese.wav')
cheese_fx.set_volume(0.3)
jump_fx=pygame.mixer.Sound('data/jump.mp3')
jump_fx.set_volume(0.5)
gameover_fx=pygame.mixer.Sound('data/gameover.wav')
gameover_fx.set_volume(0.5)
levelpass_fx=pygame.mixer.Sound('data/levelpass.wav')
levelpass_fx.set_volume(0.8)
click_fx=pygame.mixer.Sound('data/click.wav')

#text
def draw_text(text, font, text_col, x, y):
    img=font.render(text, True, text_col)
    screen.blit(img,(x,y))
    

#function to reset level
def reset_level(level):
    playera.replay(25, 500)
    playerb.replay(20,500)
    trap_group.empty()
    cheese_group.empty()
    gate_group.empty()
    
    #load in level data and create world
    if path.exists(f'level{level}_data.txt'):
        with open(f'level{level}_data.txt') as file:
            world_data = [[int(digit) for digit in line.split(',')] for line in file]
    world = World(world_data)
    
    return world


#create buttons
class Button():
    def __init__ (self,x,y,image):
        self.image=image
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.clicked=False

    def draw(self):
        action=False
        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked condition
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]==1 and self.clicked==False:
                action=True
                self.clicked=True
                click_fx.play()
                
        if pygame.mouse.get_pressed()[0]==0:
            self.clicked=False
                
            
        
        #draw button
        screen.blit(self.image,self.rect)

        return action


#class Player 
class Player():
    def __init__(self,x,y):
        self.replay(x,y)
        

    def update(self,game_over):
        dx=0
        dy=0

        if game_over==0:

            #get key presses
            key= pygame.key.get_pressed()
            if key[self.key_up] and self.jumped==False:
                jump_fx.play()
                self.vel_y=-15
                self.jumped=True
            if key[self.key_up]==False:
                self.jumped=False
            if key[self.key_left]:
                dx-=2
            if key[self.key_right]:
                dx+=2

            #add gravity
            self.vel_y+=1
            if self.vel_y>10:
                 self.vel_y=10
            dy+=self.vel_y

            #check for collision
            for tile in world.tile_list:
                #check for collision in x direction
                if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width, self.height):
                     dx=0
                #check for collision in y direction
                if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width, self.height):
                    #check if below the ground i.e. jumping
                    if self.vel_y<0:
                        dy=tile[1].bottom-self.rect.top
                        self.vel_y=0
                    #check if above the ground i.e. falling
                    elif self.vel_y>=0:
                        dy=tile[1].top-self.rect.bottom

            #check for collision with traps
                if pygame.sprite.spritecollide(self,trap_group, False): 
                    game_over=-1
                    gameover_fx.play()
                    
            #check for collision with gate
                if pygame.sprite.spritecollide(playera,gate_group, False) and pygame.sprite.spritecollide(playerb,gate_group, False):
                    game_over=1
                    levelpass_fx.play()

            
            #update player coordinates
            self.rect.x+=dx
            self.rect.y+=dy
            
   
        #draw player on screen
        screen.blit(self.image, self.rect)
        return game_over

    def replay(self,x,y):
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.vel_y=0
        self.jumped=False

#playerA 
class PlayerA(Player):
    def __init__(self,x,y):
        img=pygame.image.load('data/mouseA.PNG')
        self.image= pygame.transform.scale(img,(60,60))
        self.key_up = pygame.K_UP
        self.key_left = pygame.K_LEFT
        self.key_right= pygame.K_RIGHT
        

        super(PlayerA, self).__init__(x, y)
   

#playerB    
class PlayerB(Player):
    def __init__(self,x,y):
        img=pygame.image.load('data/mouseB.PNG')
        self.image= pygame.transform.scale(img,(60,60))
        self.key_up = pygame.K_w
        self.key_left = pygame.K_a
        self.key_right= pygame.K_d
        
    
        super(PlayerB, self).__init__(x,y)

    

#level background- class world 
class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        border_img=pygame.image.load('data/background/grey_border.jpeg')
        platform_img=pygame.image.load('data/background/darkgrey_platform.jpeg')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(border_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                    
                if tile == 2:
                    img = pygame.transform.scale(platform_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile==3:
                    trap=Trap(col_count*tile_size, row_count*tile_size)
                    trap_group.add(trap)

                if tile==4:
                    cheese=Cheese(col_count*tile_size, row_count*tile_size)
                    cheese_group.add(cheese)

                if tile==5:
                    gate=Gate(col_count*tile_size, row_count*tile_size)
                    gate_group.add(gate)
                    
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            

#class Trap  
class Trap(pygame.sprite.Sprite):
    def __init__ (self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img=pygame.image.load('data/mousetrap.PNG')
        self.image=pygame.transform.scale(img,(60,60))
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        

#class Cheese
class Cheese(pygame.sprite.Sprite):
    def __init__ (self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img=pygame.image.load('data/cheese.PNG')
        self.image=pygame.transform.scale(img,(tile_size,tile_size))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

#class Gate
class Gate(pygame.sprite.Sprite):
    def __init__ (self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img=pygame.image.load('data/gate.PNG')
        self.image=pygame.transform.scale(img,(tile_size,tile_size*2))
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y


playera= PlayerA(25, 500)
playerb=PlayerB(20,500)
trap_group=pygame.sprite.Group()
cheese_group=pygame.sprite.Group()
gate_group=pygame.sprite.Group()

#dummy cheese for showing the score
score_cheese=Cheese(tile_size, tile_size)
cheese_group.add(score_cheese)

#load in level data and create world
if path.exists(f'level{level}_data.txt'):
    with open(f'level{level}_data.txt') as file:
        world_data = [[int(digit) for digit in line.split(',')] for line in file]

world = World(world_data)

#create buttons
replay_button= Button(screen_width//2 -150 , screen_height//2 , replay_img)
start_button=Button(screen_width//2 -300 , screen_height//2 , start_img)
exit_button=Button(screen_width//2 +80 , screen_height//2 , exit_img)



run = True
while run:
    clock.tick(fps)
    screen.blit(skybg_img, (0,0))
  

    if main_menu== True:
        screen.blit(intro_img, (120, 80))
        if start_button.draw():
            main_menu= False
        if exit_button.draw():
            run= False
        
    else: 
        world.draw()

        if game_over==0:
            trap_group.update()
            #update score
            #check if a cheese has been collected
            if pygame.sprite.spritecollide(playera,cheese_group,True) or pygame.sprite.spritecollide(playerb,cheese_group,True) :
                score+=1
                cheese_fx.play()
            draw_text('x '+ str(score), font_score, white,45, 20)
    
        
        trap_group.draw(screen)
        cheese_group.draw(screen)
        gate_group.draw(screen)
        #dummy cheese for showing the score
        score_cheese=Cheese(tile_size, tile_size)
        cheese_group.add(score_cheese)

    
        game_over=playera.update(game_over)
        game_over=playerb.update(game_over)

        #if player has died
        if game_over==-1:
            if replay_button.draw():
                world_data=[]
                world=reset_level(level)
                game_over=0
                score=0

        #if player has completed the level
        if game_over==1:
            #reset game and go to next level
            level+=1
            if level<= max_levels:
                #reset level
                world_data=[]
                world=reset_level(level)
                game_over=0
                score=0
            else:
                if replay_button.draw():
                    level=1
                    #reset level
                    world_data=[]
                    world=reset_level(level)
                    game_over=0
                    score=0
        

    #quit game-game  red button
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()



