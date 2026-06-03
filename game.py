#region Regions

#region Imports

    #region Pygame
import pygame
import pygame_gui
    #endregion

    #region Mapa / Câmera
import pyscroll
import pytmx
    #endregion

    #region Física
import pymunk
    #endregion

    #region Animações
import pyganim
import spritesheet
    #endregion

    #region Python Default
import random
import math
import time
import json
import sys
from pathlib import Path
from enum import Enum
    #endregion
#endregion

#region Funções
def Better_scale(imagem, largura_max, altura_max):
    proporcao = min(largura_max / imagem.get_width(), altura_max / imagem.get_height())
    nova_largura = int(imagem.get_width() * proporcao)
    nova_altura = int(imagem.get_height() * proporcao)
    return pygame.transform.scale(imagem, (nova_largura, nova_altura))

def No_Chao(body):
    if body.velocity.y != 0:
        return False
    return True
#endregion

#region Paths
BASE_DIR = Path(__file__).parent
MAPS = BASE_DIR / "maps"
SPRITES = BASE_DIR / "sprites"
GUI = BASE_DIR / "gui"
MUSICS = BASE_DIR / "sounds" / "musics"
SFX = BASE_DIR / "sounds" / "sfx"
LOGO =  BASE_DIR / "logo"
FONTS = BASE_DIR / "fonts"
#endregion

#region Pygame Essentials
pygame.init()

    #region Tab Config

    #Caption
pygame.display.set_caption("Placeholder Name")

    #Icon
icon = pygame.image.load(LOGO / "logo.png")
icon = pygame.transform.scale(icon, (32, 32))
pygame.display.set_icon(icon)
    #endregion

    #region Screen Resolution
LARGURA, ALTURA = 1280, 720
screen = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE | pygame.SCALED)
    #endregion

clock = pygame.time.Clock()
run_game =  True
#endregion

#region Game States
class GameState(Enum):
    MENU = 0
    GAME = 1
    OPTIONS = 2
    EXIT = 3
#endregion

#region Sprites/Sounds/Maps/GUI

#region Sprites
#endregion

#region Sounds

#region Musics
menu_music = MUSICS / "menu.wav"
#endregion

#region SFX
#endregion

#endregion

#region Maps
    #region Test Map
test_map = pytmx.load_pygame(MAPS/"blue_map2.tmx")
test_map_data = pyscroll.data.TiledMapData(test_map)
test_map_layer = pyscroll.orthographic.BufferedRenderer(test_map_data, screen.get_size())
group = pyscroll.PyscrollGroup(map_layer=test_map_layer)
    #endregion
#endregion

#region GUI
menu_logo = pygame.image.load(GUI / "menu.png")
menu_logo = pygame.transform.scale_by(menu_logo, 1)
large_button_ui = pygame.image.load(GUI / "black_large_button.png")
#endregion

#region GUI's

    #region Menu GUI
font = pygame.font.Font(FONTS / "Minecraft.ttf")
manager = pygame_gui.UIManager((LARGURA, ALTURA))
large_button_width, large_button_height = 400, 50
square_button_width, square_button_height = 50, 50
play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA - large_button_width) // 2, 300), (large_button_width, large_button_height)), text="", manager=manager, object_id="#play_button")
options_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA - large_button_width) // 2, 375), (large_button_width, large_button_height)), text="", manager=manager, object_id="#options_button")
credits_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA - large_button_width) // 2, 450), (large_button_width, large_button_height)), text="", manager=manager, object_id="#exit_button")
exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA - large_button_width) // 2, 525), (large_button_width, large_button_height)), text="", manager=manager, object_id="#exit_button")
    #endregion

    #region Options GUI

geral_bar_y = 200
volume_bar_y = 275
sound_bar_y = 350
geral_bar = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((LARGURA - large_button_width) // 2, geral_bar_y, large_button_width, 25), start_value=1, value_range=(0.0, 1.0), manager=manager, object_id="#geral")
music_bar = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((LARGURA - large_button_width) // 2, volume_bar_y, large_button_width, 25), start_value=1, value_range=(0.0, 1.0), manager=manager, object_id="#volume")
sound_bar = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((LARGURA - large_button_width) // 2, sound_bar_y, large_button_width, 25), start_value=1, value_range=(0.0, 1.0), manager=manager, object_id="#sound")
back_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA - large_button_width) // 2, 525), (large_button_width, large_button_height)), text="", manager=manager, object_id="#back_button")
geral_bar.hide()
music_bar.hide()
sound_bar.hide()
back_button.hide()

Volume_Geral = 1
Volume_Musicas = 1
Volume_Sons = 1

    #endregion

    #region Exit GUI
medium_button_width, medium_button_height = 175, 50
yes_x = 425
no_x = 1280 - yes_x
yes_no_button_y = 375
yes_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((yes_x, yes_no_button_y), (medium_button_width, large_button_height)), text="", manager=manager, object_id="#yes_button")
no_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((no_x - medium_button_width, yes_no_button_y), (medium_button_width, large_button_height)), text="", manager=manager, object_id="#no_button")
yes_button.hide()
no_button.hide()
    #endregion

#region Colors
BG = (38, 38, 38)
BLACK = (0, 0, 0)
#endregion

#region game_state MENU and Menu Music
game_state = GameState.MENU

pygame.mixer.music.load(menu_music)
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1)
#endregion

#endregion
#endregion

#region Física
gravidade = 0.4
velocidade_y = -6
space = pymunk.Space()
space.gravity = (0, 900)
space.damping = 0.8
#endregion

#endregion

opacity = 255

#region Player
player_sprite = pygame.Surface((40, 60))
player_sprite.fill('Blue')

player_body = pymunk.Body(1, float('inf'))
player_body.position = (50, 0)
player_shape = pymunk.Poly.create_box(player_body, (40, 60))
player_shape.friction = 0.9
player_shape.elasticity = 0
space.add(player_body, player_shape)

#tp
tp_x = 0
tp_y = 0
has_tp = False
#endregion

    #region Colisão Chão
for obj in test_map.objects:
            if obj.type == "colisão":
                body = pymunk.Body(body_type=pymunk.Body.STATIC)
                body.position = (obj.x + obj.width / 2, obj.y + obj.height / 2)
                shape = pymunk.Poly.create_box(body, (obj.width, obj.height))
                shape.friction = 0.9
                shape.elasticity = 0
                space.add(body, shape)
    #endregion

while run_game == True:
    time_delta = clock.tick(60) / 1000.0
    #region Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            hover_sfx = pygame.mixer.Sound(SFX / "hover.mp3")
            hover_sfx.set_volume(1 * Volume_Sons * Volume_Geral)
            hover_sfx.play()
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            press_sfx = pygame.mixer.Sound(SFX / "menu_click.mp3")
            press_sfx.set_volume(0.3 * Volume_Sons * Volume_Geral)
            press_sfx.play()
            if game_state == GameState.MENU:
                if event.ui_element == play_button:
                    game_state = GameState.GAME
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(MUSICS / "menu.wav")
                    pygame.mixer.music.set_volume(0.6 * Volume_Musicas * Volume_Geral)
                    pygame.mixer.music.play(-1)
                elif event.ui_element == exit_button:
                    game_state = GameState.EXIT
                elif event.ui_element == options_button:
                    game_state = GameState.OPTIONS
            elif game_state == GameState.OPTIONS:
                if event.ui_element == back_button:
                    game_state = GameState.MENU
            elif game_state == GameState.EXIT:
                if event.ui_element == yes_button:
                    run_game = False
                elif event.ui_element == no_button:
                    game_state = GameState.MENU
        elif game_state == GameState.OPTIONS:
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == geral_bar:
                    Volume_Geral = geral_bar.get_current_value()
                    pygame.mixer.music.set_volume(0.6 * Volume_Musicas * Volume_Geral)
                elif event.ui_element == music_bar:
                    Volume_Musicas = music_bar.get_current_value()
                    pygame.mixer.music.set_volume(0.6 * Volume_Musicas * Volume_Geral)
                elif event.ui_element == sound_bar:
                    Volume_Sons = sound_bar.get_current_value()
        elif game_state == GameState.GAME:
            if event.type == pygame.KEYDOWN:
                if No_Chao(player_body):
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        player_body.velocity = (player_body.velocity.x, -300)
                if event.key == pygame.K_x:
                    if has_tp == False:
                        tp_x = player_body.position.x
                        tp_y = player_body.position.y
                        has_tp = True
                    else:
                        player_body.position = (tp_x, tp_y)
                        has_tp = False
        manager.process_events(event)
    #endregion

    manager.update(time_delta)

    if game_state == GameState.MENU:
        #region show/hide
        play_button.show()
        options_button.show()
        credits_button.show()
        exit_button.show()
        geral_bar.hide()
        music_bar.hide()
        sound_bar.hide()
        back_button.hide()
        yes_button.hide()
        no_button.hide()
        #endregion
        screen.fill(BG)
        screen.blit(menu_logo, ((LARGURA - menu_logo.get_width()) // 2 , 75))
        manager.draw_ui(screen)
        #region text
        screen.blit(large_button_ui, ((LARGURA - large_button_width) // 2, 300))
        screen.blit(large_button_ui, ((LARGURA - large_button_width) // 2, 375))
        screen.blit(large_button_ui, ((LARGURA - large_button_width) // 2, 450))
        screen.blit(large_button_ui, ((LARGURA - large_button_width) // 2, 525))
        play_text = font.render("Jogar", True, "White")
        options_text = font.render("Opcoes", True, "White")
        credits_text = font.render("Creditos", True, "White")
        exit_text = font.render("Sair", True, "White")
        screen.blit(play_text, (615, 317))
        screen.blit(options_text, (605, 392))
        screen.blit(credits_text, (603, 467))
        screen.blit(exit_text, (623, 542))
        #endregion
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.fill("Black")
        overlay.set_alpha(opacity)
        screen.blit(overlay, (0, 0))
        if opacity > 0:
            opacity -= 2
    elif game_state == GameState.OPTIONS:
        opacity = 0
        screen.fill(BG)
        manager.draw_ui(screen)
        #region show/hide
        play_button.hide()
        options_button.hide()
        credits_button.hide()
        exit_button.hide()
        geral_bar.show()
        music_bar.show()
        sound_bar.show()
        back_button.show()
        #endregion
        #region text
        screen.blit(large_button_ui, ((LARGURA - large_button_width) // 2, 525))
        back_text = font.render("Voltar", True, "White")
        geral_volume_text = font.render("Volume Geral:", True, "White")
        music_volume_text = font.render("Volume da Musica:", True, "White")
        sound_volume_text = font.render("Volume dos Sons:", True, "White")
        cem_text = font.render("100", True, "White")
        zero_text = font.render("0", True, "White")
        screen.blit(back_text, (615, 542))
        screen.blit(geral_volume_text, (578, geral_bar_y - 25))
        screen.blit(music_volume_text, (559, volume_bar_y - 25))
        screen.blit(sound_volume_text, (562, sound_bar_y - 25))
        screen.blit(cem_text, (850, geral_bar_y + 4))
        screen.blit(zero_text, (417, geral_bar_y + 4))
        screen.blit(cem_text, (850, volume_bar_y + 4))
        screen.blit(zero_text, (417, volume_bar_y + 4))
        screen.blit(cem_text, (850, sound_bar_y + 4))
        screen.blit(zero_text, (417, sound_bar_y + 4))
        #endregion
    elif game_state == GameState.EXIT:
        opacity = 0
        screen.fill(BG)
        manager.draw_ui(screen)
        #region show/hide
        play_button.hide()
        options_button.hide()
        credits_button.hide()
        exit_button.hide()
        back_button.hide()
        no_button.show()
        yes_button.show()
        #endregion
        #region text
        yes_text = font.render("Sim", True, "White")
        no_text = font.render("Nao", True, "White")
        exit_game_text = font.render("Sair do jogo?", True, "White")
        screen.blit(exit_game_text, ((LARGURA - exit_game_text.get_width()) // 2, 300))
        screen.blit(yes_text, ((yes_x + medium_button_width // 2) - yes_text.get_width() // 2 - 1, yes_no_button_y + 15))
        screen.blit(no_text, ((no_x - medium_button_width // 2) - no_text.get_width() // 2 + 3, yes_no_button_y + 15))
        #endregion

    elif game_state == GameState.GAME:
        space.step(1/60)
        keys = pygame.key.get_pressed()

        x = player_body.position.x
        y = player_body.position.y

        x = max(0, min(x, LARGURA))
        y = max(0, min(y, ALTURA))

        player_body.position = (x, y)

        screen.fill(BLACK)
        group.draw(screen)
        screen.blit(player_sprite, (player_body.position.x - player_sprite.get_width() / 2, player_body.position.y - player_sprite.get_height() / 2))
        if keys[pygame.K_d]:
            player_body.velocity = (200, player_body.velocity.y)
        if keys[pygame.K_a]:
            player_body.velocity = (-200, player_body.velocity.y)

    pygame.display.update()

pygame.quit()