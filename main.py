#region Regions

#region Imports

    #region Pygame
import pygame
import pygame_gui
#import pyinstaller
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
import pytweening
    #endregion

    #region Python Default
import colorsys
import random
import math
import time
import json
import sys
from pathlib import Path
from enum import Enum
from game import Game, GameState as RoomState
    #endregion
#endregion

#region Funções
def Better_scale(imagem, largura_max, altura_max):
    proporcao = min(largura_max / imagem.get_width(), altura_max / imagem.get_height())
    nova_largura = int(imagem.get_width() * proporcao)
    nova_altura = int(imagem.get_height() * proporcao)
    return pygame.transform.scale(imagem, (nova_largura, nova_altura))

def saturar(surface, fator):
    result = surface.copy()
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            r, g, b, a = surface.get_at((x, y))
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            s = min(1, s * fator)
            r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
            result.set_at((x, y), (int(r2*255), int(g2*255), int(b2*255), a))
    return result
#endregion

#region Paths
if getattr(sys, "frozen", False):
    # Rodando como .exe empacotado (PyInstaller) — assets ficam extraidos em sys._MEIPASS
    BASE_DIR = Path(sys._MEIPASS)
else:
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

#init
pygame.init()

    #region Tab Config

    #Caption
pygame.display.set_caption("Hack and Slash")

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
    OPTIONS = 2
    EXIT = 3
    JOGANDO = 4
#endregion

#region Sprites/Sounds/GUI

#region Sprites

#raio
raio_sprite = pygame.image.load(SPRITES / "raio.png").convert_alpha()

#chave
chave_sprite = pygame.image.load(SPRITES / "chave.png").convert_alpha()
chave_sprite = pygame.transform.scale(chave_sprite, (105, 105))

#coletável de vida
vida_sprite = pygame.image.load(SPRITES / "vida.png").convert_alpha()
vida_sprite = pygame.transform.scale(vida_sprite, (80, 80))

#Cenários
predios = pygame.image.load(SPRITES / "predios.png")
predios = pygame.transform.scale_by(predios, 2.25)
predios.set_alpha(200)
sala1_surface = pygame.image.load(SPRITES / "sala 1.png")
sala1_surface = pygame.transform.scale_by(sala1_surface, 2.73)
carro_direita = pygame.image.load(SPRITES / "carro_facing_right.png")
carro_direita = pygame.transform.scale_by(carro_direita, 2.25)
carro_esquerda = pygame.image.load(SPRITES / "carro_facing_left.png")
carro_esquerda = pygame.transform.scale_by(carro_esquerda, 2.25)

sala_geral = pygame.image.load(SPRITES / "sala geral.png")
sala_geral = pygame.transform.scale_by(sala_geral, 2.73)

sala3 = pygame.image.load(SPRITES / "sala grande.png")
sala3 = pygame.transform.scale_by(sala3, 2.73)

#Serra (obstáculo Sala 3)
serra_sprite = pygame.image.load(SPRITES / "serra.png")
serra_sprite = pygame.transform.scale_by(serra_sprite, 3)


#Player

    #Idle
player_idle_sheet = pygame.image.load(SPRITES / "Spritesheets" / "idle.png")
player_idle_sprite = spritesheet.Spritesheet(player_idle_sheet)
player_idle_animation_list = []
player_idle_animation_list = player_idle_sprite.get_animation(0, 7, 64, 128, 2.73, (50, 50, 50))
player_idle_animation_list_saturada = [saturar(frame, 1.5) for frame in player_idle_animation_list]

    #Walking
player_walking_sheet = pygame.image.load(SPRITES / "Spritesheets" / "walking.png").convert_alpha()
player_walking_sprite = spritesheet.Spritesheet(player_walking_sheet)
player_walking_animation_list = []
player_walking_animation_list = player_walking_sprite.get_animation(0, 2, 64, 128, 2.73, (50, 50, 50))
player_walking_animation_list_saturada = [saturar(frame, 1.5) for frame in player_walking_animation_list]

#Shadow Opacity set

#Sprites Falas Tutorial
slash_neutro = pygame.image.load(SPRITES / "Dialogue" /  "slash.png")
slash_neutro = pygame.transform.scale_by(slash_neutro, 2)

slash_side_eye = pygame.image.load(SPRITES / "Dialogue" / "slash_olhando_pro_lado.png")
slash_side_eye = pygame.transform.scale_by(slash_side_eye, 2)

slash_bravo = pygame.image.load(SPRITES / "Dialogue" / "slash_bravo.png")
slash_bravo = pygame.transform.scale_by(slash_bravo, 2)

hack_falando = pygame.image.load(SPRITES / "Dialogue" / "hack.png")
hack_falando = pygame.transform.scale_by(hack_falando, 2)

hack_neutra = pygame.image.load(SPRITES / "Dialogue" / "hack_neutra.png")
hack_neutra = pygame.transform.scale_by(hack_neutra, 2)


#endregion

#region Sounds

#region Musics
menu_music = MUSICS / "menu.mp3"
missao_music = MUSICS / "missao.mp3"
#endregion

#region SFX
hover_sfx = pygame.mixer.Sound(SFX / "hover.mp3")
press_sfx = pygame.mixer.Sound(SFX / "menu_click.mp3")
click_sfx = pygame.mixer.Sound(SFX / "click.mp3")
damage_sfx = pygame.mixer.Sound(SFX / "damage.mp3")
open_door_sfx = pygame.mixer.Sound(SFX / "open_door.mp3")
dash_sfx1 = pygame.mixer.Sound(SFX / "dash3.mp3")
dash_sfx2 = pygame.mixer.Sound(SFX / "dash.mp3")
heal_sfx = pygame.mixer.Sound(SFX / "hpup.mp3")
#endregion

#endregion

#region GUI
#Menu GUI
menu_logo = pygame.image.load(GUI / "menu_logo_ui.png")
menu_logo = pygame.transform.scale_by(menu_logo, 1)

#Buttons GUI
large_button_ui = pygame.image.load(GUI / "black_large_button_ui.png")
medium_button_ui = pygame.image.load(GUI / "black_medium_button_ui.png")

E_gui = pygame.image.load(GUI / "interact_ui.png")
square_ui = pygame.image.load(GUI / "square_ui.png")

#Black Overlay do pause
black_overlay = pygame.Surface((LARGURA, ALTURA))
black_overlay.fill('Black')
black_overlay.set_alpha(175)

#Física da Logo mexendo
logo_yt = 0
logo_yvel = 0.005
logo_y = 75
#endregion
#endregion

#region GUI's

    #region Menu GUI
font = pygame.font.Font(FONTS / "PIXY.ttf")
manager = pygame_gui.UIManager((LARGURA, ALTURA))
large_button_width, large_button_height =   400, 50
square_button_width, square_button_height = 50, 50
play_button =       pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA - large_button_width) // 2, 300), (large_button_width, large_button_height)), text="", manager=manager, object_id="#play_button")
options_button =    pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA - large_button_width) // 2, 375), (large_button_width, large_button_height)), text="", manager=manager, object_id="#options_button")
credits_button =    pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA - large_button_width) // 2, 450), (large_button_width, large_button_height)), text="", manager=manager, object_id="#exit_button")
exit_button =       pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA - large_button_width) // 2, 525), (large_button_width, large_button_height)), text="", manager=manager, object_id="#exit_button")

transicao_opacity = 255

    #endregion

    #region Options GUI

#Barras de Volume
geral_bar_y =   200
volume_bar_y =  275
sound_bar_y =   350
geral_bar =     pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((LARGURA - large_button_width) // 2, geral_bar_y, large_button_width, 25), start_value=1, value_range=(0.0, 1.0), manager=manager, object_id="#geral")
music_bar =     pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((LARGURA - large_button_width) // 2, volume_bar_y, large_button_width, 25), start_value=1, value_range=(0.0, 1.0), manager=manager, object_id="#volume")
sound_bar =     pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((LARGURA - large_button_width) // 2, sound_bar_y, large_button_width, 25), start_value=1, value_range=(0.0, 1.0), manager=manager, object_id="#sound")
back_button =   pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA - large_button_width) // 2, 525), (large_button_width, large_button_height)), text="", manager=manager, object_id="#back_button")

#Hides
geral_bar.hide()
music_bar.hide()
sound_bar.hide()
back_button.hide()

#Sets Volume Default
Volume_Geral =      1
Volume_Musicas =    1
Volume_Sons =       1
Volume_Transicao =  0

    #endregion

    #region Exit GUI
medium_button_width, medium_button_height = 175, 50
yes_x = 425
no_x = 1280 - yes_x
yes_no_button_y = 375
yes_button =    pygame_gui.elements.UIButton(relative_rect=pygame.Rect((yes_x, yes_no_button_y), (medium_button_width, large_button_height)), text="", manager=manager, object_id="#yes_button")
no_button =     pygame_gui.elements.UIButton(relative_rect=pygame.Rect((no_x - medium_button_width, yes_no_button_y), (medium_button_width, large_button_height)), text="", manager=manager, object_id="#no_button")
    #endregion

    #region Pause GUI
continue_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA // 2) - (medium_button_width // 2), 260), (medium_button_width, large_button_height)), text="", manager=manager, object_id="#continue_button")
options2_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA // 2) - (medium_button_width // 2), 335), (medium_button_width, large_button_height)), text="", manager=manager, object_id="#continue_button")
menu_button     = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA // 2) - (medium_button_width // 2), 410), (medium_button_width, large_button_height)), text="", manager=manager, object_id="#menu_button")
    #endregion

life_bar_3_3 = pygame.image.load(SPRITES / "life_bar3.png")
life_bar_3_3 = pygame.transform.scale_by(life_bar_3_3, 2)

life_bar_2_3 = pygame.image.load(SPRITES / "life_bar2.png")
life_bar_2_3 = pygame.transform.scale_by(life_bar_2_3, 2)

life_bar_1_3 = pygame.image.load(SPRITES / "life_bar1.png")
life_bar_1_3 = pygame.transform.scale_by(life_bar_1_3, 2)

    #hides
yes_button.hide()
no_button.hide()
continue_button.hide()
options2_button.hide()
menu_button.hide()
    #endregion

#region Colors
BG = (0, 0, 0)
BLACK = (0, 0, 0)
#endregion

#sets iniciais
game_state = GameState.MENU

pygame.mixer.music.load(menu_music)
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1)

#region Player
animations = {
    "Idle": player_idle_animation_list_saturada,
    "Walking": player_walking_animation_list_saturada
}

was_in_game = False
chaves_inv = 0
todas_chaves = False
sala_anterior_options = GameState.JOGANDO

#endregion

#region enemy
shoot_sfx = pygame.mixer.Sound(SFX / "shoot.mp3")
enemy_sprite = pygame.image.load(SPRITES / "enemy.png").convert_alpha()
enemy_sprite = pygame.transform.scale_by(enemy_sprite, 2)
bullet_sprite = pygame.image.load(SPRITES / "bullet.png").convert_alpha()
#endregion

#region Textos
back_text = font.render("Voltar", True, "White")
geral_volume_text = font.render("Volume Geral:", True, "White")
music_volume_text = font.render("Volume da Musica:", True, "White")
sound_volume_text = font.render("Volume dos Sons:", True, "White")
cem_text = font.render("100", True, "White")
zero_text = font.render("0", True, "White")
play_text = font.render("Jogar", True, "White")
options_text = font.render("Opcoes", True, "White")
credits_text = font.render("Creditos", True, "White")
exit_text = font.render("Sair", True, "White")
continue_text = font.render('Continuar', False, "White")
options2_text = font.render('Opcoes', False, "White")
menu_text = font.render('Menu', False, "White")
yes_text = font.render("Sim", True, "White")
no_text = font.render("Nao", True, "White")
exit_game_text = font.render("Sair do jogo?", True, "White")

fase1_sprites = {
    "slash_neutro":   slash_neutro,
    "slash_side_eye": slash_side_eye,
    "slash_bravo":    slash_bravo,
    "hack_falando":   hack_falando,
    "hack_neutra":    hack_neutra,
    "carro_direita":  carro_direita,
    "carro_esquerda": carro_esquerda,
    "E_gui":          E_gui,
    "life_bar_3":     life_bar_3_3,
    "life_bar_2":     life_bar_2_3,
    "life_bar_1":     life_bar_1_3,
}

sala_geral_sprites = {
    "slash_neutro": slash_neutro,
    "E_gui":        E_gui,
    "chave":        chave_sprite, 
    "vida":         vida_sprite,
}

game_sons = {
    "open_door": open_door_sfx,
    "shoot":     shoot_sfx,
    "damage":    damage_sfx,
    "click":     click_sfx,
    "dash1":     dash_sfx1,
    "dash2":     dash_sfx2,
    "heal":      heal_sfx
}

fonte_contador = pygame.font.Font(FONTS / "PIXY.ttf", 40)
life_bar_sprites = {
    "life_bar_3": life_bar_3_3,
    "life_bar_2": life_bar_2_3,
    "life_bar_1": life_bar_1_3,
}
game_over_sprite = pygame.image.load(SPRITES / "game over.png").convert_alpha()

game = Game(
    animations,
    sala1_surface, sala_geral, sala3,
    serra_sprite, enemy_sprite, bullet_sprite,
    fase1_sprites,
    sala_geral_sprites,
    font,
    E_gui,
    game_sons,
    fonte_contador,
    life_bar_sprites,
    game_over_sprite,
    raio_sprite,
)
#endregion

#region Loop Start
while run_game:
    time_delta = clock.tick(60) / 1000.0
    #region Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            hover_sfx.set_volume(1.5 * Volume_Sons * Volume_Geral)
            hover_sfx.play()
        
        #region Botões
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            press_sfx.set_volume(0.35 * Volume_Sons * Volume_Geral)
            press_sfx.play()
            if game_state == GameState.MENU:
                if event.ui_element == play_button:
                    game_state = GameState.JOGANDO
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(MUSICS / "sala 1.mp3")
                    pygame.mixer.music.set_volume(0.1 * Volume_Musicas * Volume_Geral)
                    pygame.mixer.music.play(-1)
                    transicao_opacity = 255
                elif event.ui_element == exit_button:
                    game_state = GameState.EXIT
                elif event.ui_element == options_button:
                    game_state = GameState.OPTIONS
            elif game_state == GameState.OPTIONS:
                if event.ui_element == back_button and not was_in_game:
                    game_state = GameState.MENU
                elif event.ui_element == back_button and was_in_game:
                    game_state = sala_anterior_options
                    game.pausado = False
            elif game_state == GameState.EXIT:
                if event.ui_element == yes_button:
                    run_game = False
                elif event.ui_element == no_button:
                    game_state = GameState.MENU
            elif game_state == GameState.JOGANDO:
                if event.ui_element == continue_button:
                    game.pausado = False
                elif event.ui_element == options2_button:
                    sala_anterior_options = game_state
                    game_state = GameState.OPTIONS
                    was_in_game = True
                    continue_button.hide()
                    options2_button.hide()
                    menu_button.hide()
                elif event.ui_element == menu_button:
                    game_state = GameState.MENU
                    was_in_game = False
                    continue_button.hide()
                    options2_button.hide()
                    menu_button.hide()
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(MUSICS / "menu.mp3")
                    Volume_Transicao = 0
                    transicao_opacity = 255
                    game.reset()
                    pygame.mixer.music.set_volume(0.25 * Volume_Transicao * Volume_Geral * Volume_Musicas)
                    pygame.mixer.music.play(-1)

        elif game_state == GameState.OPTIONS:
            if event.type == pygame.KEYDOWN and was_in_game:
                if event.key == pygame.K_ESCAPE:
                    game_state = sala_anterior_options
                    game.pausado = False
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == geral_bar:
                    Volume_Geral = geral_bar.get_current_value()
                    if not was_in_game:
                        pygame.mixer.music.set_volume(0.25 * Volume_Musicas * Volume_Geral)
                    else:
                        pygame.mixer.music.set_volume(0.1 * Volume_Musicas * Volume_Geral)
                elif event.ui_element == music_bar:
                    Volume_Musicas = music_bar.get_current_value()
                    if not was_in_game:
                        pygame.mixer.music.set_volume(0.25 * Volume_Musicas * Volume_Geral)
                    else:
                        pygame.mixer.music.set_volume(0.1 * Volume_Musicas * Volume_Geral)
                elif event.ui_element == sound_bar:
                    Volume_Sons = sound_bar.get_current_value()

        elif game_state == GameState.JOGANDO:
            if event.type == pygame.KEYDOWN:
                game.handle_keydown(event, Volume_Sons, Volume_Geral)

        manager.process_events(event)
    #endregion

    manager.update(time_delta)

    #region GameState Menu
    if game_state == GameState.MENU:
        pygame.mixer.music.set_volume(Volume_Transicao * 0.25 * Volume_Geral * Volume_Musicas)
        if Volume_Transicao < 1:
            Volume_Transicao += 0.01
        screen.fill(BG)
        screen.blit(predios, (0, 0))
        logo_yt += logo_yvel
        if logo_yt > 1:
            logo_yt = 0
        logo_ytt = logo_yt * 2 if logo_yt < 0.5 else 2 - logo_yt * 2
        logo_y = 60 + (80 - 60) * pytweening.easeInOutQuad(logo_ytt)
        screen.blit(menu_logo, ((LARGURA - menu_logo.get_width()) // 2, logo_y))
        manager.draw_ui(screen)
    
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

        #region text
        screen.blit(large_button_ui, ((LARGURA - large_button_width) // 2, 300))
        screen.blit(large_button_ui, ((LARGURA - large_button_width) // 2, 375))
        screen.blit(large_button_ui, ((LARGURA - large_button_width) // 2, 450))
        screen.blit(large_button_ui, ((LARGURA - large_button_width) // 2, 525))
        screen.blit(play_text, ((LARGURA // 2) - (play_text.get_width() // 2), 313))
        screen.blit(options_text, ((LARGURA // 2) - (options_text.get_width() // 2), 388))
        screen.blit(credits_text, ((LARGURA // 2) - (credits_text.get_width() // 2), 463))
        screen.blit(exit_text, ((LARGURA // 2) - (exit_text.get_width() // 2), 538))
        #endregion

        #region Transição
        transicao_overlay = pygame.Surface((LARGURA, ALTURA))
        transicao_overlay.fill("Black")
        transicao_overlay.set_alpha(transicao_opacity)
        screen.blit(transicao_overlay, (0, 0))
        if transicao_opacity > 0:
            transicao_opacity -= 2
        #endregion

    #region GameState Options
    elif game_state == GameState.OPTIONS:

        transicao_opacity = 0
        screen.fill(BG)
        screen.blit(predios, (0, 0))
        screen.blit(square_ui, ((LARGURA // 2) - (square_ui.get_width() // 2), 145))
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
        screen.blit(back_text, ((LARGURA // 2) - (back_text.get_width() // 2), 538))
        screen.blit(geral_volume_text, ((LARGURA // 2) - (geral_volume_text.get_width() // 2), geral_bar_y - 25))
        screen.blit(music_volume_text, ((LARGURA // 2) - (music_volume_text.get_width() // 2), volume_bar_y - 25))
        screen.blit(sound_volume_text, ((LARGURA // 2) - (sound_volume_text.get_width() // 2), sound_bar_y - 25))
        screen.blit(cem_text, (850, geral_bar_y))
        screen.blit(zero_text, (417, geral_bar_y))
        screen.blit(cem_text, (850, volume_bar_y))
        screen.blit(zero_text, (417, volume_bar_y))
        screen.blit(cem_text, (850, sound_bar_y))
        screen.blit(zero_text, (417, sound_bar_y))
        #endregion

    #region Gamestate Exit
    elif game_state == GameState.EXIT:

        transicao_opacity = 0
        screen.fill(BG)
        screen.blit(predios, (0, 0))
        screen.blit(square_ui, ((LARGURA // 2) - (square_ui.get_width() // 2), 225))
        manager.draw_ui(screen)
        screen.blit(medium_button_ui, (yes_x, yes_no_button_y))
        screen.blit(medium_button_ui, (no_x - medium_button_width, yes_no_button_y))

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
        screen.blit(exit_game_text, ((LARGURA - exit_game_text.get_width()) // 2, 300))
        screen.blit(yes_text, ((yes_x + medium_button_width // 2) - yes_text.get_width() // 2 - 1, yes_no_button_y + 13))
        screen.blit(no_text, ((no_x - medium_button_width // 2) - no_text.get_width() // 2 + 3, yes_no_button_y + 13))
        #endregion

    elif game_state == GameState.JOGANDO:
        
        #region show/hide
        play_button.hide()
        options_button.hide()
        credits_button.hide()
        exit_button.hide()
        geral_bar.hide()
        music_bar.hide()
        sound_bar.hide()
        back_button.hide()
        #endregion

        game.update(time_delta, Volume_Sons, Volume_Geral)

        if game.fechar:
            run_game = False
            continue

        if game.consumir_trocou_para_sala_geral():
            pygame.mixer.music.load(missao_music)
            pygame.mixer.music.set_volume(0.125 * Volume_Musicas * Volume_Geral)
            pygame.mixer.music.play(-1)

        if game.state == RoomState.SALAGERAL:
            pygame.mixer.music.set_volume(0.125 * Volume_Musicas * Volume_Geral)

        game.draw(screen, 0.15 * Volume_Sons * Volume_Geral)

        if game.pausado:
            screen.blit(black_overlay, (0, 0))
            screen.blit(square_ui, ((LARGURA // 2) - (square_ui.get_width() // 2), ((ALTURA // 2) - (square_ui.get_height() // 2))))
            continue_button.show()
            options2_button.show()
            menu_button.show()
            manager.draw_ui(screen)
            screen.blit(medium_button_ui, ((LARGURA // 2) - (medium_button_width // 2), 260))
            screen.blit(medium_button_ui, ((LARGURA // 2) - (medium_button_width // 2), 335))
            screen.blit(medium_button_ui, ((LARGURA // 2) - (medium_button_width // 2), 410))
            screen.blit(continue_text, ((LARGURA // 2) - (continue_text.get_width() // 2), 260 + 12))
            screen.blit(options2_text, ((LARGURA // 2) - (options2_text.get_width() // 2), 335 + 12))
            screen.blit(menu_text, ((LARGURA // 2) - (menu_text.get_width() // 2), 410 + 12))

        transicao_overlay.set_alpha(game.transicao_opacity)
        screen.blit(transicao_overlay, (0, 0))

    pygame.display.update()

pygame.quit()