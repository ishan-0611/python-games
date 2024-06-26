import pygame
from sys import exit
from random import randint, choice

# Game variables
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("RUN FOR LIFE")
clock = pygame.time.Clock()
FPS = 60
test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
game_active = False
start_time = 0
score = 0
bg_music = pygame.mixer.Sound('audio/music.wav')
bg_music.set_volume(0.1)

# Basic surfaces
sky_surf = pygame.image.load('graphics/Sky.png').convert()
ground_surf = pygame.image.load('graphics/ground.png').convert()

# Snail frames
snail_frame1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
snail_frame2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
snail_frames = [snail_frame1, snail_frame2]
snail_frame_index = 0
snail_surf = snail_frames[snail_frame_index]

# Fly frames
fly_frame1 = pygame.image.load('graphics/Fly/Fly1.png').convert_alpha()
fly_frame2 = pygame.image.load('graphics/Fly/Fly2.png').convert_alpha()
fly_frames = [fly_frame1, fly_frame2]
fly_frame_index = 0
fly_surf = fly_frames[fly_frame_index]

# Obstacles list
obstacle_rect_list = []

# Player
player_walk_1 = pygame.image.load('graphics/Player/player_walk_1.png').convert_alpha()
player_walk_2 = pygame.image.load('graphics/Player/player_walk_2.png').convert_alpha()
player_walk = [player_walk_1, player_walk_2]
player_index = 0
player_jump = pygame.image.load('graphics/Player/jump.png').convert_alpha()

player_surf = player_walk[player_index]
player_rect = player_surf.get_rect(midbottom=(80, 300))
player_gravity = 0

# Intro Screen
player_stand = pygame.image.load('graphics/Player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 1)
player_stand_rect = player_stand.get_rect(center=(400, 200))
intro_surf = test_font.render('Run For Life', 0, (0, 0, 0))
intro_text = intro_surf.get_rect(center=(400, 100))
intro_inst_surf = test_font.render('Press Space to Play !!', 0, (0, 0, 0))
intro_inst_text = intro_inst_surf.get_rect(center=(400, 300))

# Timers
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

snail_animation_timer = pygame.USEREVENT + 2
pygame.time.set_timer(snail_animation_timer, 500)

fly_animation_timer = pygame.USEREVENT + 3
pygame.time.set_timer(fly_animation_timer, 200)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_1 = pygame.image.load('graphics/Player/player_walk_1.png').convert_alpha()
        player_2 = pygame.image.load('graphics/Player/player_walk_2.png').convert_alpha()
        self.player_walk = [player_1, player_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/Player/jump.png').convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.gravity = 0
        self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
        self.jump_sound.set_volume(0.3)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()


class Obstacle(pygame.sprite.Sprite):
     def __init__(self, obs_type):
         super().__init__()
         if obs_type == 'fly':
             fly_1 = pygame.image.load('graphics/Fly/Fly1.png').convert_alpha()
             fly_2 = pygame.image.load('graphics/Fly/Fly2.png').convert_alpha()
             self.frames = [fly_1, fly_2]
             y_pos = 210
         else:
             snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
             snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
             self.frames = [snail_1, snail_2]
             y_pos = 300

         self.animation_index = 0
         self.image = self.frames[self.animation_index]
         self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))

     def animation_state(self):
         self.animation_index += 0.1
         if self.animation_index >= len(self.frames):
             self.animation_index = 0
         self.image = self.frames[int(self.animation_index)]
    
     def update(self):
         self.animation_state()
         self.rect.x -= 6
         self.destroy()

     def destroy(self):
         if self.rect.x < -100:
             self.kill()


# Groups
player = pygame.sprite.GroupSingle()
# noinspection PyTypeChecker
player.add(Player())
obstacle_group = pygame.sprite.Group()


def display_score():
    current_time = pygame.time.get_ticks() - start_time
    score_surf = test_font.render(str(round(current_time / 1000)), 0, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 50))
    screen.blit(score_surf, score_rect)
    return current_time


def obstacle_movement(obstacle_list):
     if obstacle_list:
         for obstacle_rect in obstacle_list:
             obstacle_rect.x -= 5

             if obstacle_rect.bottom == 300:
                screen.blit(snail_surf, obstacle_rect)
             else:
                 screen.blit(fly_surf, obstacle_rect)

         obstacle_list = [obstacle for obstacle in obstacle_list if obstacle.x > -100]

         return obstacle_list
     else:
         return []


def collision(player_, obstacles):
    if obstacles:
        for obstacle_rect in obstacles:
            if player_.colliderect(obstacle_rect):
                return False
    return True


def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    else:
        return True


def player_animation():
    global player_surf, player_index
    # Display jump surface when player is not on the floor
    if player_rect.bottom < 300:
        player_surf = player_jump
    # Player walking animation if player is on the floor
    else:
        player_index += 0.1
        if player_index >= len(player_walk):
            player_index = 0
        player_surf = player_walk[int(player_index)]


while True:
    # bg_music.play()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if player_rect.collidepoint(event.pos) and player_rect.bottom >= 300:
                    player_gravity = -20

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_rect.bottom >= 300:
                    player_gravity = -20

        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_active = True
                    start_time = pygame.time.get_ticks()

        if game_active:
            if event.type == obstacle_timer:
                # noinspection PyTypeChecker
                obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail'])))
                # if randint(0, 2):
                #     obstacle_rect_list.append(snail_surf.get_rect(bottomright=(randint(900, 1100), 300)))
                # else:
                #     obstacle_rect_list.append(fly_surf.get_rect(bottomright=(randint(900, 1100), 210)))

            if event.type == snail_animation_timer:
                if snail_frame_index == 0:
                    snail_frame_index = 1
                else:
                    snail_frame_index = 0
                snail_surf = snail_frames[snail_frame_index]

            if event.type == fly_animation_timer:
                if fly_frame_index == 0:
                    fly_frame_index = 1
                else:
                    fly_frame_index = 0
                fly_surf = fly_frames[fly_frame_index]

    if game_active:
        screen.blit(sky_surf, (0, 0))
        screen.blit(ground_surf, (0, 300))
        # pygame.draw.rect(screen, '#c0e8ec', score_rect)
        # pygame.draw.rect(screen, '#c0e8ec', score_rect, 10)
        # screen.blit(score_surf, score_rect)

        score = display_score()

        # snail_rect.x -= 5
        # if snail_rect.right <= 0:
        #     snail_rect.left = 800
        # screen.blit(snail_surf, snail_rect)

        # Player
        # player_gravity += 1
        # player_rect.y += player_gravity
        # if player_rect.bottom >= 300:
        #     player_rect.bottom = 300
        # player_animation()
        # screen.blit(player_surf, player_rect)

        player.draw(screen)
        player.update()
        obstacle_group.draw(screen)
        obstacle_group.update()

        # Obstacle movement
        # obstacle_rect_list = obstacle_movement(obstacle_rect_list)

        # Collision
        game_active = collision_sprite()
        # game_active = collision(player_rect, obstacle_rect_list)

    else:
        # Intro/Outro screen
        screen.fill((94, 159, 162))
        screen.blit(player_stand, player_stand_rect)
        obstacle_rect_list.clear()
        player_rect.midbottom = (80, 300)
        player_gravity = 0

        score_msg = test_font.render(f"Your score : {round(score/1000)}", 0, (0, 0, 0))
        score_msg_rect = score_msg.get_rect(center=(400, 300))
        screen.blit(intro_surf, intro_text)

        if score == 0:
            screen.blit(intro_inst_surf, intro_inst_text)
        else:
            screen.blit(score_msg, score_msg_rect)

    pygame.display.update()
    clock.tick(FPS)
