#herda as caracteristicas da classe sala base
#sala1 não tá feita
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

_ENTER_FALAS = {0, 1, 2, 5, 11}

_POSICOES_INICIAIS_CARROS = [
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

   
    _X_PORTA = 1000

    def __init__(self, superficie: pygame.Surface,
                 sprites: dict, textos: dict) -> None:
        super().__init__(superficie)
        self.sprites = sprites
        self.textos  = textos

        self.range_da_porta  = False
        self.tutorial_acabou = False
        self.fala_tutorial   = 0

        self._carros = self._criar_carros()
        self._vida_anterior = 3
        self.tocou_dano = False

    
    #usa o 2@staticmethod para criar um método que não depende da instância da classe
    @staticmethod
    def _criar_carros() -> list[dict]:
        carros = []
        x_min, x_max = 260, 1085
        for sprite_key, x, y, dx, rand_y in _POSICOES_INICIAIS_CARROS:
            carros.append({
                "sprite": sprite_key,
                "x": x, "y": y,
                "dx": dx,
                "x_min": x_min, "x_max": x_max,
                "rand_y": rand_y,
                "_x0": x, "_y0": y,      # guarda posição inicial p/ reset
            })
        return carros


    def avancar_tutorial(self) -> None:
        self.fala_tutorial += 1

    def reset(self) -> None:
        super().reset()
        self.tutorial_acabou = False
        self.fala_tutorial   = 0
        self._vida_anterior  = 3
        self.tocou_dano      = False
        for c in self._carros:
            c["x"] = c["_x0"]
            c["y"] = c["_y0"]


    def update(self, time_delta: float, player, space) -> None:
        
        player.update(space, time_delta)
        self._mover_carros()
        self._verificar_porta(player)
        self._verificar_vida(player)

        if self.fala_tutorial >= len(_FALAS):
            self.tutorial_acabou = True

    def draw(self, screen: pygame.Surface, player,
             camera_x: int = 0, pos_x: int = 0, pos_y: int = 0) -> None:
    
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


    def _mover_carros(self) -> None:
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

    def _verificar_porta(self, player) -> None:
        self.range_da_porta = (self.tutorial_acabou
                               and player.body.position.x > self._X_PORTA)

    def _verificar_vida(self, player) -> None:
       
        self.tocou_dano = False
        if player.life < self._vida_anterior:
            self.tocou_dano = True
        self._vida_anterior = player.life


    def _desenhar_tutorial(self, screen: pygame.Surface) -> None:
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

        if i in _ENTER_FALAS:
            screen.blit(t["aperte_enter"], (base_x + 540, 640))

    def _desenhar_vida(self, screen: pygame.Surface, player) -> None:
        sp = self.sprites
        vida = player.life
        if vida >= 3:
            screen.blit(sp["life_bar_3"], (20, 20))
        elif vida == 2:
            screen.blit(sp["life_bar_2"], (20, 20))
        elif vida == 1:
            screen.blit(sp["life_bar_1"], (20, 20))
