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
from player import Player
from enemy import Enemy
from sala3 import Sala3
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

def trocar_chao(space, chao_antigo_body, chao_antigo_shape, chao_novo_body, chao_novo_shape):
    """Remove o chão antigo (se estiver no space) e adiciona o novo (se ainda não estiver)."""
    if chao_antigo_shape in space.shapes:
        space.remove(chao_antigo_shape, chao_antigo_body)
    if chao_novo_shape not in space.shapes:
        space.add(chao_novo_body, chao_novo_shape)

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
    FASE1 = 1
    OPTIONS = 2
    EXIT = 3
    SALAGERAL = 4
    SALA3 = 5
    SALA2 = 6
#endregion

#region Sprites/Sounds/Maps/GUI

#region Sprites

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
shadow_opacity = 100

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

fala_tutorial = 0

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
#endregion

#endregion

#region Maps

#endregion

#region GUI
menu_logo = pygame.image.load(GUI / "menu_logo_ui.png")
menu_logo = pygame.transform.scale_by(menu_logo, 1)
large_button_ui = pygame.image.load(GUI / "black_large_button_ui.png")
square_ui = pygame.image.load(GUI / "square_ui.png")

medium_button_ui = pygame.image.load(GUI / "black_medium_button_ui.png")

#Black Overlay do pause
black_overlay = pygame.Surface((LARGURA, ALTURA))
black_overlay.fill('Black')
black_overlay.set_alpha(175)

E_gui = pygame.image.load(GUI / "interact_ui.png")
range_da_porta = False
range_da_porta2 = False
todas_chaves = False
fala_porta = False

#Física da Logo mexendo
logo_yt = 0
logo_yvel = 0.005
logo_y = 75
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

#Opacidade das transições
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

    #region Pause GUI
continue_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA // 2) - (medium_button_width // 2), 260), (medium_button_width, large_button_height)), text="", manager=manager, object_id="#continue_button")
options2_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA // 2) - (medium_button_width // 2), 335), (medium_button_width, large_button_height)), text="", manager=manager, object_id="#continue_button")
menu_button     = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(((LARGURA // 2) - (medium_button_width // 2), 410), (medium_button_width, large_button_height)), text="", manager=manager, object_id="#menu_button")

life_bar_3_3 = pygame.image.load(SPRITES / "life_bar3.png")
life_bar_3_3 = pygame.transform.scale_by(life_bar_3_3, 2)

life_bar_2_3 = pygame.image.load(SPRITES / "life_bar2.png")
life_bar_2_3 = pygame.transform.scale_by(life_bar_2_3, 2)

life_bar_1_3 = pygame.image.load(SPRITES / "life_bar1.png")
life_bar_1_3 = pygame.transform.scale_by(life_bar_1_3, 2)

#Hides
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

#region game_state Inicial
game_state = GameState.MENU

#Música
pygame.mixer.music.load(menu_music)
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1)
#endregion

#endregion
#endregion

#region Física
space = pymunk.Space()
space.gravity = (0, 900)
space.damping = 0.9
pausado = False
entrou_na_sala_geral = False
entrou_na_sala1 = False
entrou_na_sala2 = False
entrou_na_sala3 = False
range_volta_sala2 = False
cutscene1 = True
checou_porta = False
range_da_porta_geral_1 = False
range_da_porta_geral_2 = False
range_da_porta_geral_3 = False
#endregion

#endregion

#region Player
animations = {
    "Idle": player_idle_animation_list_saturada,
    "Walking": player_walking_animation_list_saturada
}
player = Player(space, animations)

tutorial_acabou = False
was_in_game = False
sala_anterior_options = GameState.FASE1  # guarda em qual sala o player estava antes de pausar e abrir Options
era_2 = False
era_3 = True

carro_1x = 600
carro_1y = 200

carro_2x = 400
carro_2y = 250

carro_3x = 800
carro_3y = 180

carro_4x = 900
carro_4y = 220

carro_5x = 300
carro_5y = 260
#endregion

#region Inimigo Sala 2
shoot_sfx = pygame.mixer.Sound(SFX / "shoot.mp3")  # ajuste o nome do arquivo se for diferente
enemy_sprite = pygame.image.load(SPRITES / "enemy.png").convert_alpha()
enemy_sprite = pygame.transform.scale_by(enemy_sprite, 2)
inimigo_sala2 = Enemy(
    x=900,
    y=455,
    patrulha_min=700,
    patrulha_max=1200,
    sprite=enemy_sprite,
)
#endregion

#Chão Fase 1
chao_sala1_body = pymunk.Body(body_type=pymunk.Body.STATIC)
chao_sala1_body.position = (0, 595)
chao_sala1_shape = pymunk.Segment(chao_sala1_body, (0, 0), (1280, 0), 5)
chao_sala1_shape.friction = 1
chao_sala1_shape.elasticity = 0
space.add(chao_sala1_body, chao_sala1_shape)

#Chão Sala Geral
chao_sala_geral_body = pymunk.Body(body_type=pymunk.Body.STATIC)
chao_sala_geral_x = 0
chao_sala_geral_body.position = (chao_sala_geral_x, 595)
chao_sala_geral_shape = pymunk.Segment(chao_sala_geral_body, (0, 0), (2560, 0), 5)
chao_sala_geral_shape.friction = 1
chao_sala_geral_shape.elasticity = 0
chao_sala_geral_body.position = (chao_sala_geral_x, 620)

#Chão Sala 3
chao_sala3_body = pymunk.Body(body_type=pymunk.Body.STATIC)
chao_sala3_x = 0
chao_sala3_body.position = (chao_sala3_x, 620)
chao_sala3_shape = pymunk.Segment(chao_sala3_body, (0, 0), (sala3.get_width(), 0), 5)
chao_sala3_shape.friction = 1
chao_sala3_shape.elasticity = 0

#Chão Sala 2
chao_sala2_body = pymunk.Body(body_type=pymunk.Body.STATIC)
chao_sala2_x = 0
chao_sala2_body.position = (chao_sala2_x, 620)
chao_sala2_shape = pymunk.Segment(chao_sala2_body, (0, 0), (sala3.get_width(), 0), 5)
chao_sala2_shape.friction = 1
chao_sala2_shape.elasticity = 0

sala3_obj = Sala3(sala3, serra_sprite)

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

aperte_enter = font.render("Aperte ENTER para continuar", False, (100, 100, 100))
Slash_name = font.render("Slash", False, (235, 52, 116))
Hack_name = font.render("Hack", False, (235, 52, 116))
Tutorial_Fala0 = font.render("Voce nao podia ter invadido o predio de um jeito menos", False, "White")
Tutorial_Fala0_1 = font.render("escandaloso?!", False, "White")
Tutorial_Fala1 = font.render("E de que outro jeito eu entraria?", False, "White")
Tutorial_Fala2 = font.render("Argh, deixa isso pra la.", False, "White")
Tutorial_Fala3 = font.render("Enfim, deixa eu te explicar como vai ser essa missao.", False, "White")
Tutorial_Fala4 = font.render('Voce pode usar "WASD" para se mover e Espaco para pular.', False, "White")
Tutorial_Fala6 = font.render('Segure "Shift" para correr e pressione "C" para dar um', False, "White")
Tutorial_Fala6_1 = font.render('avanco rapido.', False, "White")
Tutorial_Fala5 = font.render('Clique com o Mouse para realizar um ataque usando Slash.', False, "White")
Tutorial_Fala7 = font.render('Alem disso, Hack possui a habilidade de se', False, "White")
Tutorial_Fala7_1 = font.render('teletransportar.', False, "White")
Tutorial_Fala8 = font.render('Para criar um ponto de teleporte, aperte "X". apertando', False, "White")
Tutorial_Fala8_1 = font.render('novamente Hack consome o ponto de teleporte atual e', False, "White")
Tutorial_Fala8_2 = font.render('se teletransporta ate ele.', False, "White")
Tutorial_Fala9 = font.render('Seu objetivo e invadir o escritorio do CEO da Cyber Corp.', False, "White")
Tutorial_Fala9_1 = font.render('e mata-lo.', False, "White")
Tutorial_Fala10 = font.render('Acho que isso e tudo, pronta?', False, "White")
Tutorial_Fala11 = font.render("Pronta.", False, "White")
Tutorial_Fala12 = font.render('Boa sorte.', False, "White")
aperte_enter = pygame.transform.scale_by(aperte_enter, 0.8)
Slash_name = pygame.transform.scale_by(Slash_name, 1.5)
Hack_name = pygame.transform.scale_by(Hack_name, 1.5)

timer_cutscene = 300
timer_cutscene_progress = 300
timer_porta = 300
Cutscene_Fala1 = font.render('Aquela deve ser a porta do escritorio do chefe.', False, "White")
Cutscene_Fala2 = font.render('Vamos checar.', False, "White")

Porta_Fala1 = font.render('Tem 3 leitores aqui.', False, "White")
Porta_Fala2 = font.render('Parece que voce vai precisar de 3 chaves de acesso', False, "White")
Porta_Fala2_1 = font.render('pra conseguir abrir a porta.', False, "White")
Porta_Fala3 = font.render('Vamos checar as outras salas.', False, "White")
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
                    game_state = GameState.FASE1
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
                    pausado = False
            elif game_state == GameState.EXIT:
                if event.ui_element == yes_button:
                    run_game = False
                elif event.ui_element == no_button:
                    game_state = GameState.MENU
            elif game_state == GameState.FASE1 or game_state == GameState.SALAGERAL or game_state == GameState.SALA3 or game_state == GameState.SALA2:
                if event.ui_element == continue_button:
                    pausado = False
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
                    pausado = False
                    continue_button.hide()
                    options2_button.hide()
                    menu_button.hide()
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(MUSICS / "menu.mp3")
                    Volume_Transicao = 0
                    player.has_tp = False
                    player.body.position = (250, 430)
                    transicao_opacity = 255
                    player.virado = True
                    fala_tutorial = 0
                    tutorial_acabou = False
                    pygame.mixer.music.set_volume(0.25 * Volume_Transicao * Volume_Geral * Volume_Musicas)
                    pygame.mixer.music.play(-1)

        elif game_state == GameState.OPTIONS:
            if event.type == pygame.KEYDOWN and was_in_game:
                if event.key == pygame.K_ESCAPE:
                    game_state = sala_anterior_options
                    pausado = False
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

        elif game_state == GameState.FASE1 or game_state == GameState.SALAGERAL or game_state == GameState.SALA3 or game_state == GameState.SALA2:
            #region Keydowns
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        player.pular()
                if event.key == pygame.K_x:
                    player.usar_teleporte()
                if event.key == pygame.K_k:
                    player.life -= 1
                if event.key == pygame.K_c and not player.dashing:
                    dash_choose = random.choice([dash_sfx1, dash_sfx2])
                    dash_choose.set_volume(0.1 * Volume_Sons * Volume_Geral)
                    dash_choose.play()
                    player.iniciar_dash()
                if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN and not tutorial_acabou:
                    fala_tutorial += 1
                    click_sfx.set_volume(0.15 * Volume_Sons * Volume_Geral)
                    click_sfx.play()
                if event.key == pygame.K_ESCAPE and not pausado:
                    pausado = True
                elif event.key == pygame.K_ESCAPE and pausado:
                    pausado = False
                if event.key == pygame.K_e and range_da_porta and game_state == GameState.FASE1:
                    game_state = GameState.SALAGERAL
                    entrou_na_sala_geral = True
                    player.virado = True
                if event.key == pygame.K_e and range_da_porta2 and game_state == GameState.SALAGERAL and not todas_chaves:
                    fala_porta = True
                    checou_porta = True
                elif event.key == pygame.K_e and range_da_porta_geral_3 and game_state == GameState.SALAGERAL and not todas_chaves and checou_porta:
                    game_state = GameState.SALA3
                    entrou_na_sala3 = True
                    range_da_porta_geral_3 = False
                    sala3_obj.range_volta = False
                    player.virado = True
                elif event.key == pygame.K_e and range_da_porta_geral_2 and game_state == GameState.SALAGERAL and not todas_chaves and checou_porta:
                    game_state = GameState.SALA2
                    entrou_na_sala2 = True
                    range_da_porta_geral_2 = False
                    range_volta_sala2 = False
                    player.virado = True
                if event.key == pygame.K_e and sala3_obj.range_volta and game_state == GameState.SALA3:
                    game_state = GameState.SALAGERAL
                    player.body.position = (1900, 455)
                    trocar_chao(space, chao_sala3_body, chao_sala3_shape, chao_sala_geral_body, chao_sala_geral_shape)
                    open_door_sfx.set_volume(0.25 * Volume_Sons * Volume_Geral)
                    open_door_sfx.play()
                    transicao_opacity = 255
                    sala3_obj.range_volta = False
                    range_da_porta_geral_3 = False
                    virado = True
                if event.key == pygame.K_e and range_volta_sala2 and game_state == GameState.SALA2:
                    game_state = GameState.SALAGERAL
                    player.body.position = (1300, 455)
                    trocar_chao(space, chao_sala2_body, chao_sala2_shape, chao_sala_geral_body, chao_sala_geral_shape)
                    open_door_sfx.set_volume(0.25 * Volume_Sons * Volume_Geral)
                    open_door_sfx.play()
                    transicao_opacity = 255
                    range_volta_sala2 = False
                    range_da_porta_geral_2 = False
                    virado = True

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

    elif game_state == GameState.FASE1:
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

        saturado = True

        #region Estados
        if player.body.velocity.x == 0 and player.body.velocity.y == 0:
            player.estado = "Idle"
        elif player.body.velocity.y == 0 and player.body.velocity.x != 0:
            player.estado = "Walking"


        if player.dashing:
            dash_progress = pytweening.easeOutQuart(player.dash_t)
            new_pos_x = player.dash_inicial + (player.dash_final - player.dash_inicial) * dash_progress
            player.body.position = (new_pos_x, player.body.position.y)
            player.body.velocity = (0, player.body.velocity.y)

        space.step(1/60)
        keys = pygame.key.get_pressed()

        x = player.body.position.x
        y = player.body.position.y
        x = max(190, min(x, 1230))
        y = max(0, min(y, ALTURA))
        player.body.position = (x, y)

        screen.fill(BLACK)

        pos_x = player.body.position.x - 110
        pos_y = player.body.position.y - 235

        #Blit da sala
        screen.blit(sala1_surface, (0, 10))

        #region Carros
        screen.blit(carro_direita, (carro_1x, carro_1y))
        screen.blit(carro_direita, (carro_2x, carro_2y))
        screen.blit(carro_esquerda, (carro_3x, carro_3y))
        screen.blit(carro_direita, (carro_4x, carro_4y))
        screen.blit(carro_esquerda, (carro_5x, carro_5y))
        carro_1x += 1
        if carro_1x > 1085:
            carro_1x = 260
        carro_2x += 1
        if carro_2x > 1085:
            carro_2x = 260
            carro_2y = random.randint(180, 295)
        carro_3x -= 1
        if carro_3x < 260:
            carro_3x = 1085
            carro_3y = random.randint(180, 295)
        carro_4x += 1
        if carro_4x > 1085:
            carro_4x = 260
            carro_4y = random.randint(180, 295)
        carro_5x -= 1
        if carro_5x < 260:
            carro_5x = 1085

        if player.dashing:
            player.dash_t += time_delta / player.dash_duration
            player.image = pygame.transform.scale(player.image, (170, 349))
            player.traces.append([pos_x, pos_y, 180])

            for trace in player.traces:
                trace_surf = pygame.transform.scale(player.image, (200, 349))
                trace_surf.fill(('maroon1'), special_flags=pygame.BLEND_ADD)
                trace_surf.set_alpha(trace[2])
                if not player.virado:
                    screen.blit(trace_surf, (trace[0], trace[1]))
                else:
                    trace_surf = pygame.transform.flip(trace_surf, player.virado, False)
                    screen.blit(trace_surf, (trace[0] - 25, trace[1]))
                trace[2] -= 30

            player.traces = [t for t in player.traces if t[2] > 0]
            if player.dash_t >= 1:
                player.dash_t = 1
                player.dashing = False
                player.image = pygame.transform.scale(player.image, (170, 349))

        if player.virado:
            player.image = pygame.transform.flip(player.image, player.virado, False)

        if tutorial_acabou and player.body.position.x > 1000:
            screen.blit(E_gui, (1190, 275))
            range_da_porta = True
        else:
            range_da_porta = False

        #region Blit do Player Sala 1
        screen.blit(player.image, (pos_x, pos_y))

        #region Efeitos de filtro
        purple_overlay = player.image.copy()
        purple_overlay.fill(('Purple'), special_flags=pygame.BLEND_MULT)
        purple_overlay.set_alpha(40)
        screen.blit(purple_overlay, (pos_x, pos_y))

        blue_overlay = player.image.copy()
        blue_overlay.fill(('Blue'), special_flags=pygame.BLENDMODE_BLEND)
        blue_overlay.set_alpha(30)
        screen.blit(blue_overlay, (pos_x, pos_y))

        shadow_overlay = player.image.copy()
        shadow_overlay.fill((52, 9, 127), special_flags=pygame.BLENDMODE_MOD)
        shadow_overlay.set_alpha(shadow_opacity)
        if 450 <= pos_x <= 510 or 20 <= pos_x <= 100 or 795 <= pos_x <= 865 or 1105 <= pos_x <= 1200:
            screen.blit(shadow_overlay, (pos_x, pos_y))
            if shadow_opacity != 100:
                shadow_opacity += 25
        else:
            shadow_opacity = 0
        #endregion

        player.atualizar_animacao()

        #region Andar A e Andar D
        if keys[pygame.K_d]:
            player.body.velocity = (520, player.body.velocity.y)
            player.virado = True
        if keys[pygame.K_a]:
            player.body.velocity = (-375, player.body.velocity.y)
            player.virado = False
        else:
            player.body.velocity = (player.body.velocity.x * 0.7, player.body.velocity.y)

        #region Tutorial
        if not tutorial_acabou:
            screen.blit(slash_neutro, ((LARGURA // 2) - (slash_neutro.get_width() // 2), 520))
            screen.blit(aperte_enter, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 540, 640))

            #region Falas Tutorial
            if fala_tutorial == 0:
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala0, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
                screen.blit(Tutorial_Fala0_1, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 582))
            elif fala_tutorial == 1:
                screen.blit(hack_falando, ((LARGURA // 2) - (slash_neutro.get_width() // 2), 520))
                screen.blit(Hack_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala1, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
                screen.blit(aperte_enter, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 540, 640))
            elif fala_tutorial == 2:
                screen.blit(slash_side_eye, ((LARGURA // 2) - (slash_neutro.get_width() // 2), 520))
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala2, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
                screen.blit(aperte_enter, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 540, 640))
            elif fala_tutorial == 3:
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala3, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
            elif fala_tutorial == 4:
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala4, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
            elif fala_tutorial == 5:
                screen.blit(slash_bravo, ((LARGURA // 2) - (slash_neutro.get_width() // 2), 520))
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala5, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
                screen.blit(aperte_enter, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 540, 640))
            elif fala_tutorial == 6:
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala6, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
                screen.blit(Tutorial_Fala6_1, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 582))
            elif fala_tutorial == 7:
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala7, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
                screen.blit(Tutorial_Fala7_1, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 582))
            elif fala_tutorial == 8:
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala8, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
                screen.blit(Tutorial_Fala8_1, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 582))
                screen.blit(Tutorial_Fala8_2, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 604))
            elif fala_tutorial == 9:
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala9, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
                screen.blit(Tutorial_Fala9_1, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 582))
            elif fala_tutorial == 10:
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala10, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
            elif fala_tutorial == 11:
                screen.blit(hack_neutra, ((LARGURA // 2) - (slash_neutro.get_width() // 2), 520))
                screen.blit(Hack_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala11, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
                screen.blit(aperte_enter, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 540, 640))
            elif fala_tutorial == 12:
                screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
                screen.blit(Tutorial_Fala12, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
            elif fala_tutorial <= 13:
                tutorial_acabou = True
            #endregion

        #region Sistema de Vida
        if player.life == 3:
            screen.blit(life_bar_3_3, (20, 20))
            era_3 = True
        elif player.life == 2:
            if era_3:
                damage_sfx.set_volume(0.8 * Volume_Sons * Volume_Geral)
                damage_sfx.play()
                era_3 = False
            era_2 = True
            screen.blit(life_bar_2_3, (20, 20))
        elif player.life == 1:
            if era_2:
                damage_sfx.set_volume(0.8 * Volume_Sons * Volume_Geral)
                damage_sfx.play()
                era_2 = False
            screen.blit(life_bar_1_3, (20, 20))

        #region Pause
        if pausado:
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

        transicao_overlay.set_alpha(transicao_opacity)
        screen.blit(transicao_overlay, (0, 0))
        if transicao_opacity > 0:
            transicao_opacity -= 5

    elif game_state == GameState.SALAGERAL:
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

        if entrou_na_sala_geral:
            pygame.mixer.music.load(missao_music)
            pygame.mixer.music.set_volume(0.125 * Volume_Musicas * Volume_Geral)
            pygame.mixer.music.play(-1)
            entrou_na_sala_geral = False
            open_door_sfx.set_volume(0.25 * Volume_Sons * Volume_Geral)
            open_door_sfx.play()
            player.body.position = (250, 455)
            trocar_chao(space, chao_sala1_body, chao_sala1_shape, chao_sala_geral_body, chao_sala_geral_shape)
            transicao_opacity = 255
            cutscenex = 0
            
        pygame.mixer.music.set_volume(0.125 * Volume_Musicas * Volume_Geral)

        while cutscene1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            screen.fill('BLACK')
            screen.blit(sala_geral, (cutscenex, 10))
            cutscene1_progress = 1 - (timer_cutscene_progress / 300)
            cutscenex = 0 + (-1280 - 0) * pytweening.easeOutQuart(cutscene1_progress)
            screen.blit(slash_neutro, ((LARGURA // 2) - (slash_neutro.get_width() // 2), 520))
            screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
            if timer_cutscene > 150:
                screen.blit(Cutscene_Fala1, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
            else:
                if timer_cutscene == 150:
                    click_sfx.set_volume(0.15 * Volume_Sons * Volume_Geral)
                    click_sfx.play()
                screen.blit(Cutscene_Fala2, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
            timer_cutscene -= 1
            transicao_overlay.set_alpha(transicao_opacity)
            screen.blit(transicao_overlay, (0, 0))
            transicao_opacity -= 4
            if timer_cutscene_progress > 0:
                timer_cutscene_progress -= 2
            if timer_cutscene <= 0:
                cutscene1 = False
            pygame.display.update()
            clock.tick(60)

        if player.body.velocity.x == 0 and player.body.velocity.y == 0:
            player.estado = "Idle"
        elif player.body.velocity.y == 0 and player.body.velocity.x != 0:
            player.estado = "Walking"


        if player.dashing:
            dash_progress = pytweening.easeOutQuart(player.dash_t)
            new_pos_x = player.dash_inicial + (player.dash_final - player.dash_inicial) * dash_progress
            player.body.position = (new_pos_x, player.body.position.y)
            player.body.velocity = (0, player.body.velocity.y)

        space.step(1/60)
        keys = pygame.key.get_pressed()

        x = player.body.position.x
        y = player.body.position.y
        x = max(220, min(x, 1230 * 2 - 70))
        y = max(0, min(y, ALTURA))
        
        player.body.position = (x, y)

        screen.fill(BG)

        #camera centralizada no player
        camera_x = player.body.position.x - LARGURA // 2
        camera_x = max(0, min(camera_x, sala_geral.get_width() - LARGURA))
        pos_x = player.body.position.x - camera_x - 110
        pos_y = player.body.position.y - 235

        screen.blit(sala_geral, (-camera_x, 10))

        if player.dashing:
            player.dash_t += time_delta / player.dash_duration
            player.image = pygame.transform.scale(player.image, (170, 349))
            player.traces.append([pos_x, pos_y, 180])

            for trace in player.traces:
                trace_surf = pygame.transform.scale(player.image, (200, 349))
                trace_surf.fill(('maroon1'), special_flags=pygame.BLEND_ADD)
                trace_surf.set_alpha(trace[2])
                if not player.virado:
                    screen.blit(trace_surf, (trace[0], trace[1]))
                else:
                    trace_surf = pygame.transform.flip(trace_surf, player.virado, False)
                    screen.blit(trace_surf, (trace[0] - 25, trace[1]))
                trace[2] -= 30

            player.traces = [t for t in player.traces if t[2] > 0]
            if player.dash_t >= 1:
                player.dash_t = 1
                player.dashing = False
                player.image = pygame.transform.scale(player.image, (170, 349))

        if player.virado:
            player.image = pygame.transform.flip(player.image, player.virado, False)

        screen.blit(player.image, (pos_x, pos_y))

        if player.body.position.x > 2100:
            screen.blit(E_gui, (1075, 275))
            range_da_porta2 = True
        else:
            range_da_porta2 = False

        if 1700 < player.body.position.x < 2100:
            range_da_porta_geral_3 = True
        else:
            range_da_porta_geral_3 = False

        if 1100 <= player.body.position.x <= 1500:
            screen.blit(E_gui, (pos_x + 40, 275))
            range_da_porta_geral_2 = True
        else:
            range_da_porta_geral_2 = False

        print(player.body.position.x)
        
        while fala_porta:
            timer_porta -= 1
            screen.blit(slash_neutro, ((LARGURA // 2) - (slash_neutro.get_width() // 2), 520))
            screen.blit(Slash_name, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 530))
            if timer_porta > 200:
                screen.blit(Porta_Fala1, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
            elif 200 > timer_porta > 100:
                if timer_porta == 199:
                    click_sfx.set_volume(0.15 * Volume_Sons * Volume_Geral)
                    click_sfx.play()
                screen.blit(Porta_Fala2, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
                screen.blit(Porta_Fala2_1, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 582))
            elif 100 > timer_porta > 0:
                if timer_porta == 99:
                    click_sfx.set_volume(0.15 * Volume_Sons * Volume_Geral)
                    click_sfx.play()
                screen.blit(Porta_Fala3, ((LARGURA // 2) - (slash_neutro.get_width() // 2) + 150, 560))
            if timer_porta <= 0:
                fala_porta = False
                timer_porta = 300
            pygame.display.update()
            clock.tick(60)

        player.atualizar_animacao()

        #region Andar A e Andar D
        if keys[pygame.K_d]:
            player.body.velocity = (520, player.body.velocity.y)
            player.virado = True
        if keys[pygame.K_a]:
            player.body.velocity = (-375, player.body.velocity.y)
            player.virado = False
        else:
            player.body.velocity = (player.body.velocity.x * 0.7, player.body.velocity.y)

        if pausado:
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

    elif game_state == GameState.SALA3:
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

        if entrou_na_sala3:
            entrou_na_sala3 = False
            open_door_sfx.set_volume(0.25 * Volume_Sons * Volume_Geral)
            open_door_sfx.play()
            player.body.position = (250, 455)
            trocar_chao(space, chao_sala_geral_body, chao_sala_geral_shape, chao_sala3_body, chao_sala3_shape)
            transicao_opacity = 255

        sala3_obj.update(time_delta, player, space)
        keys = pygame.key.get_pressed()

        camera_x = sala3_obj.calcular_camera(player.body.position.x)
        pos_x = player.body.position.x - camera_x - 110
        pos_y = player.body.position.y - 235

        sala3_obj.draw(screen, player, camera_x, pos_x, pos_y, time_delta)

        player_hitbox = pygame.Rect(pos_x + 50, pos_y + 60, 70, 200)
        if sala3_obj.checar_colisao(player_hitbox, camera_x):
            damage_sfx.set_volume(0.8 * Volume_Sons * Volume_Geral)
            damage_sfx.play()
            player.body.position = (250, 455)
            player.body.velocity = (0, 0)
            player.has_tp = False

        sala3_obj.checar_saida(player.body.position.x, screen, E_gui)

        player.atualizar_animacao()

        #region Andar A e Andar D
        if keys[pygame.K_d]:
            player.body.velocity = (520, player.body.velocity.y)
            player.virado = True
        if keys[pygame.K_a]:
            player.body.velocity = (-375, player.body.velocity.y)
            player.virado = False
        else:
            player.body.velocity = (player.body.velocity.x * 0.7, player.body.velocity.y)

        if pausado:
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

        transicao_overlay.set_alpha(transicao_opacity)
        screen.blit(transicao_overlay, (0, 0))
        if transicao_opacity > 0:
            transicao_opacity -= 5

    elif game_state == GameState.SALA2:
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

        if entrou_na_sala2:
            entrou_na_sala2 = False
            open_door_sfx.set_volume(0.25 * Volume_Sons * Volume_Geral)
            open_door_sfx.play()
            player.body.position = (250, 455)
            trocar_chao(space, chao_sala_geral_body, chao_sala_geral_shape, chao_sala2_body, chao_sala2_shape)
            transicao_opacity = 255

        if player.body.velocity.x == 0 and player.body.velocity.y == 0:
            player.estado = "Idle"
        elif player.body.velocity.y == 0 and player.body.velocity.x != 0:
            player.estado = "Walking"


        if player.dashing:
            dash_progress = pytweening.easeOutQuart(player.dash_t)
            new_pos_x = player.dash_inicial + (player.dash_final - player.dash_inicial) * dash_progress
            player.body.position = (new_pos_x, player.body.position.y)
            player.body.velocity = (0, player.body.velocity.y)

        space.step(1/60)
        keys = pygame.key.get_pressed()

        # Atualiza o inimigo da sala 2 (patrulha / mira / dispara)
        inimigo_sala2.update(
            time_delta,
            player.body.position.x,
            player.body.position.y,
            sfx_tiro=shoot_sfx,
            volume_sfx=0.4 * Volume_Sons * Volume_Geral,
        )

        x = player.body.position.x
        y = player.body.position.y
        x = max(190, min(x, sala3.get_width() - 70))
        y = max(0, min(y, ALTURA))
        player.body.position = (x, y)

        screen.fill(BG)

        # Câmera centralizada no player
        camera_x = player.body.position.x - LARGURA // 2
        camera_x = max(0, min(camera_x, sala3.get_width() - LARGURA))
        pos_x = player.body.position.x - camera_x - 110
        pos_y = player.body.position.y - 235

        screen.blit(sala3, (-camera_x, 10))

        if player.dashing:
            player.dash_t += time_delta / player.dash_duration
            player.image = pygame.transform.scale(player.image, (170, 349))
            player.traces.append([pos_x, pos_y, 180])

            for trace in player.traces:
                trace_surf = pygame.transform.scale(player.image, (200, 349))
                trace_surf.fill(('maroon1'), special_flags=pygame.BLEND_ADD)
                trace_surf.set_alpha(trace[2])
                if not player.virado:
                    screen.blit(trace_surf, (trace[0], trace[1]))
                else:
                    trace_surf = pygame.transform.flip(trace_surf, player.virado, False)
                    screen.blit(trace_surf, (trace[0] - 25, trace[1]))
                trace[2] -= 30

            player.traces = [t for t in player.traces if t[2] > 0]
            if player.dash_t >= 1:
                player.dash_t = 1
                player.dashing = False
                player.image = pygame.transform.scale(player.image, (170, 349))

        if player.virado:
            player.image = pygame.transform.flip(player.image, player.virado, False)

        screen.blit(player.image, (pos_x, pos_y))

        inimigo_sala2.draw(screen, camera_x)

        #region colisao bala inimigo player
        player_hitbox = pygame.Rect(pos_x + 50, pos_y + 60, 70, 200)
        for bullet in inimigo_sala2.bullets:
            if bullet.vivo and player_hitbox.colliderect(bullet.get_rect(camera_x)):
                bullet.vivo = False
                damage_sfx.set_volume(0.8 * Volume_Sons * Volume_Geral)
                damage_sfx.play()
                player.life -= 1
        inimigo_sala2.bullets = [b for b in inimigo_sala2.bullets if b.vivo]
        #endregion

        if player.body.position.x < 400:
            screen.blit(E_gui, (140, 275))
            range_volta_sala2 = True
        else:
            range_volta_sala2 = False

        #region Animation Cooldowns
        player.atualizar_animacao()

        #region Andar A e Andar D
        if keys[pygame.K_d]:
            player.body.velocity = (520, player.body.velocity.y)
            player.virado = True
        if keys[pygame.K_a]:
            player.body.velocity = (-375, player.body.velocity.y)
            player.virado = False
        else:
            player.body.velocity = (player.body.velocity.x * 0.7, player.body.velocity.y)

        if pausado:
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

        transicao_overlay.set_alpha(transicao_opacity)
        screen.blit(transicao_overlay, (0, 0))
        if transicao_opacity > 0:
            transicao_opacity -= 5

    pygame.display.update()

pygame.quit()