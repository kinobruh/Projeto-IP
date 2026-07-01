from __future__ import annotations
import random
import pygame

from sala_base import SalaBase

_FALAS = [
    ("slash_neutro",   "slash", ["Tutorial_Fala0",   "Tutorial_Fala0_1"]),
    ("hack_falando",   "hack",  ["Tutorial_Fala1"]),
    ("slash_side_eye", "slash", ["Tutorial_Fala2"]),
    ("slash_neutro",   "slash", ["Tutorial_Fala3"]),
    ("slash_neutro",   "slash", ["Tutorial_Fala4"]),
    ("slash_bravo",    "slash", ["Tutorial_Fala5"]),
    ("slash_neutro",   "slash", ["Tutorial_Fala6",   "Tutorial_Fala6_1"]),
    ("slash_neutro",   "slash", ["Tutorial_Fala7",   "Tutorial_Fala7_1"]),
    ("slash_neutro",   "slash", ["Tutorial_Fala8",   "Tutorial_Fala8_1", "Tutorial_Fala8_2"]),
    ("slash_neutro",   "slash", ["Tutorial_Fala9",   "Tutorial_Fala9_1"]),
    ("slash_neutro",   "slash", ["Tutorial_Fala10"]),
    ("hack_neutra",    "hack",  ["Tutorial_Fala11"]),
    ("slash_neutro",   "slash", ["Tutorial_Fala12"]),
]

ENTER_FALAS = {0, 1, 2, 5, 11}

def _criar_textos_tutorial(font: pygame.font.Font):
    slash_name = font.render("Slash", False, (235, 52, 116))
    slash_name = pygame.transform.scale_by(slash_name, 1.5)
    hack_name = font.render("Hack", False, (235, 52, 116))
    hack_name = pygame.transform.scale_by(hack_name, 1.5)
    aperte_enter = font.render("Aperte ENTER para continuar", False, (100, 100, 100))
    aperte_enter = pygame.transform.scale_by(aperte_enter, 0.8)

    return {
        "slash_name":   slash_name,
        "hack_name":    hack_name,
        "aperte_enter": aperte_enter,

        "Tutorial_Fala0":   font.render("Voce nao podia ter invadido o predio de um jeito menos", False, "White"),
        "Tutorial_Fala0_1": font.render("escandaloso?!", False, "White"),
        "Tutorial_Fala1":   font.render("E de que outro jeito eu entraria?", False, "White"),
        "Tutorial_Fala2":   font.render("Argh, deixa isso pra la.", False, "White"),
        "Tutorial_Fala3":   font.render("Enfim, deixa eu te explicar como vai ser essa missao.", False, "White"),
        "Tutorial_Fala4":   font.render('Voce pode usar "WASD" para se mover e Espaco para pular.', False, "White"),
        "Tutorial_Fala5":   font.render('Clique com o Mouse para realizar um ataque usando Slash.', False, "White"),
        "Tutorial_Fala6":   font.render('Segure "Shift" para correr e pressione "C" para dar um', False, "White"),
        "Tutorial_Fala6_1": font.render('avanco rapido.', False, "White"),
        "Tutorial_Fala7":   font.render('Alem disso, Hack possui a habilidade de se', False, "White"),
        "Tutorial_Fala7_1": font.render('teletransportar.', False, "White"),
        "Tutorial_Fala8":   font.render('Para criar um ponto de teleporte, aperte "X". apertando', False, "White"),
        "Tutorial_Fala8_1": font.render('novamente Hack consome o ponto de teleporte atual e', False, "White"),
        "Tutorial_Fala8_2": font.render('se teletransporta ate ele.', False, "White"),
        "Tutorial_Fala9":   font.render('Seu objetivo e invadir o escritorio do CEO da Cyber Corp.', False, "White"),
        "Tutorial_Fala9_1": font.render('e mata-lo.', False, "White"),
        "Tutorial_Fala10":  font.render('Acho que isso e tudo, pronta?', False, "White"),
        "Tutorial_Fala11":  font.render("Pronta.", False, "White"),
        "Tutorial_Fala12":  font.render('Boa sorte.', False, "White"),
    }

POSICOES_INICIAIS_CARROS = [
    ("carro_direita",  600, 200,  1, True),
    ("carro_direita",  400, 250,  1, True),
    ("carro_esquerda", 800, 180, -1, True),
    ("carro_direita",  900, 220,  1, True),
    ("carro_esquerda", 300, 260, -1, False),
]
CLAMP_MAX_X = 1230

class Fase1(SalaBase):
    CLAMP_MIN_X = 190
    CLAMP_MAX_X = 1230
    X_PORTA = 1000

    def __init__(self, superficie: pygame.Surface, sprites: dict, font: pygame.font.Font):
        super().__init__(superficie)
        self.sprites = sprites
        self.textos  = _criar_textos_tutorial(font)
        self.range_da_porta  = False
        self.tutorial_acabou = False
        self.fala_tutorial   = 0
        self._carros = self._criar_carros()
        self._vida_anterior = 3
        self.tocou_dano = False

    @staticmethod
    def _criar_carros():
        carros = []
        x_min, x_max = 260, 1085
        for sprite_key, x, y, dx, rand_y in POSICOES_INICIAIS_CARROS:
            carros.append({
                "sprite": sprite_key,
                "x": x, "y": y,
                "dx": dx,
                "x_min": x_min, "x_max": x_max,
                "rand_y": rand_y,
                "_x0": x, "_y0": y,      # guarda posicao inicial pro reset
            })
        return carros

    def avancar_tutorial(self):
        self.fala_tutorial += 1

    def reset(self):
        super().reset()
        self.tutorial_acabou = False
        self.fala_tutorial   = 0
        self._vida_anterior  = 3
        self.tocou_dano      = False
        for c in self._carros:
            c["x"] = c["_x0"]
            c["y"] = c["_y0"]

    def update(self, time_delta: float, player, space): 
        player.update(space, time_delta)
        self._mover_carros()
        self._verificar_porta(player)
        self._verificar_vida(player)
        if self.fala_tutorial >= len(_FALAS):
            self.tutorial_acabou = True

    def draw(self, screen: pygame.Surface, player, camera_x: int = 0, pos_x: int = 0, pos_y: int = 0):
        pos_x = int(player.body.position.x - 110)
        pos_y = int(player.body.position.y - 235)
        screen.fill((0, 0, 0))
        screen.blit(self.superficie, (0, 10))
        for c in self._carros:
            screen.blit(self.sprites[c["sprite"]], (c["x"], c["y"]))
        player.draw(screen, pos_x, pos_y, efeitos_fase1=True)
        if self.range_da_porta:
            screen.blit(self.sprites["E_gui"], (1190, 275))
        if not self.tutorial_acabou:
            self._desenhar_tutorial(screen)
        self._desenhar_vida(screen, player)

    def _mover_carros(self):
        for c in self._carros:
            c["x"] += c["dx"]
            if c["dx"] > 0 and c["x"] > c["x_max"]:
                c["x"] = c["x_min"]
                if c["rand_y"]:
                    c["y"] = random.randint(180, 295)
            elif c["dx"] < 0 and c["x"] < c["x_min"]:
                c["x"] = c["x_max"]
                if c["rand_y"]:
                    c["y"] = random.randint(180, 295)

    def _verificar_porta(self, player):
        if self.tutorial_acabou and player.body.position.x > self.X_PORTA:
            self.range_da_porta = True

    def _verificar_vida(self, player):
        self.tocou_dano = False
        if player.life < self._vida_anterior:
            self.tocou_dano = True
        self._vida_anterior = player.life

    def _desenhar_tutorial(self, screen: pygame.Surface):
        i = self.fala_tutorial
        if i >= len(_FALAS):
            return
        sprite_key, personagem, linhas = _FALAS[i]
        sp = self.sprites
        t  = self.textos
        base_x = (self.LARGURA_TELA // 2) - (sp["slash_neutro"].get_width() // 2)
        nome_y  = 530
        texto_y = 560
        screen.blit(sp[sprite_key], (base_x, 520))
        screen.blit(t[f"{personagem}_name"], (base_x + 150, nome_y))
        for j, chave in enumerate(linhas):
            screen.blit(t[chave], (base_x + 150, texto_y + j * 22))
        if i in ENTER_FALAS:
            screen.blit(t["aperte_enter"], (base_x + 540, 640))

    def _desenhar_vida(self, screen: pygame.Surface, player):
        sp = self.sprites
        vida = player.life
        if vida >= 3:
            screen.blit(sp["life_bar_3"], (20, 20))
        elif vida == 2:
            screen.blit(sp["life_bar_2"], (20, 20))
        elif vida == 1:
            screen.blit(sp["life_bar_1"], (20, 20))