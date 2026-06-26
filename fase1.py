import random
import pygame
import pytweening

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

ENTER = {0, 1, 2, 5, 11}

class Fase1:
    LARGURA_TELA = 1280
    ALTURA_TELA  = 720
    CLAMP_MAX_X  = 1230

    def __init__(self, superficie, sprites, textos):
        self.superficie = superficie
        self.sprites    = sprites
        self.textos     = textos

        self.range_da_porta = False
        self.tutorial_acabou = False
        self.fala_tutorial   = 0

        # carros
        self._carros = [
            {"sprite": "carro_direita",   "x": 600, "y": 200, "dx":  1, "x_min": 260, "x_max": 1085, "rand_y": True},
            {"sprite": "carro_direita",   "x": 400, "y": 250, "dx":  1, "x_min": 260, "x_max": 1085, "rand_y": True},
            {"sprite": "carro_esquerda",  "x": 800, "y": 180, "dx": -1, "x_min": 260, "x_max": 1085, "rand_y": True},
            {"sprite": "carro_direita",   "x": 900, "y": 220, "dx":  1, "x_min": 260, "x_max": 1085, "rand_y": True},
            {"sprite": "carro_esquerda",  "x": 300, "y": 260, "dx": -1, "x_min": 260, "x_max": 1085, "rand_y": False},
        ]

        self._vida_anterior = 3

    def avancar_tutorial(self):
        self.fala_tutorial += 1

    def reset(self):
        self.tutorial_acabou = False
        self.fala_tutorial   = 0
        self._vida_anterior  = 3
        for i, c in enumerate(self._carros):
            c["x"] = [600, 400, 800, 900, 300][i]
            c["y"] = [200, 250, 180, 220, 260][i]

    def update(self, player, space, time_delta):
        # estado do player
        vx, vy = player.body.velocity
        if vx == 0 and vy == 0:
            player.estado = "Idle"
        elif vy == 0 and vx != 0:
            player.estado = "Walking"

        # dash
        if player.dashing:
            dash_progress = pytweening.easeOutQuart(player.dash_t)
            new_x = player.dash_inicial + (player.dash_final - player.dash_inicial) * dash_progress
            player.body.position = (new_x, player.body.position.y)
            player.body.velocity = (0, player.body.velocity.y)
            player.dash_t += time_delta / player.dash_duration
            if player.dash_t >= 1:
                player.dash_t = 1
                player.dashing = False

        space.step(1 / 60)

        # clamp
        x = max(190, min(player.body.position.x, self.CLAMP_MAX_X))
        y = max(0,   min(player.body.position.y, self.ALTURA_TELA))
        player.body.position = (x, y)

        # carros
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

        # porta
        self.range_da_porta = self.tutorial_acabou and player.body.position.x > 1000

        # tutorial
        if self.fala_tutorial >= len(_FALAS):
            self.tutorial_acabou = True


    def draw(self, screen, player, damage_sfx, volume_sfx):
        pos_x = player.body.position.x - 110
        pos_y = player.body.position.y - 235

        screen.fill((0, 0, 0))
        screen.blit(self.superficie, (0, 10))

        for c in self._carros:
            screen.blit(self.sprites[c["sprite"]], (c["x"], c["y"]))

        player.draw(screen, pos_x, pos_y, efeitos_fase1=True)

        if self.range_da_porta:
            screen.blit(self.sprites["E_gui"], (1190, 275))

        if not self.tutorial_acabou:
            self._desenhar_tutorial(screen)

        # vida
        if player.life == 3:
            screen.blit(self.sprites["life_bar_3"], (20, 20))
            self._vida_anterior = 3

        elif player.life == 2:
            if self._vida_anterior == 3:
                damage_sfx.set_volume(volume_sfx)
                damage_sfx.play()

            self._vida_anterior = 2
            screen.blit(self.sprites["life_bar_2"], (20, 20))

        elif player.life == 1:
            if self._vida_anterior == 2:
                damage_sfx.set_volume(volume_sfx)
                damage_sfx.play()

            self._vida_anterior = 1
            screen.blit(self.sprites["life_bar_1"], (20, 20))

        return pos_x, pos_y

    def _desenhar_tutorial(self, screen):
        text  = self.textos
        spritetext = self.sprites
        i = self.fala_tutorial
        if i >= len(_FALAS):
            return

        sprite_key, personagem, linhas = _FALAS[i]
        base_x = (self.LARGURA_TELA // 2) - (spritetext["slash_neutro"].get_width() // 2)
        nome_y  = 530
        texto_y = 560

        screen.blit(spritetext[sprite_key], (base_x, 520))
        screen.blit(text[f"{personagem}_name"], (base_x + 150, nome_y))
        for i, chave in enumerate(linhas):
            screen.blit(text[chave], (base_x + 150, texto_y + i * 22))

        if i in ENTER:
            screen.blit(text["aperte_enter"], (base_x + 540, 640))

    def _desenhar_vida(self, screen, player, damage_sfx, volume_sfx):
        sp = self.sprites
        if player.life == 3:
            screen.blit(sp["life_bar_3"], (20, 20))
            self._vida_anterior = 3
        elif player.life == 2:
            if self._vida_anterior == 3:
                damage_sfx.set_volume(volume_sfx)
                damage_sfx.play()
            self._vida_anterior = 2
            screen.blit(sp["life_bar_2"], (20, 20))
        elif player.life == 1:
            if self._vida_anterior == 2:
                damage_sfx.set_volume(volume_sfx)
                damage_sfx.play()
            self._vida_anterior = 1
            screen.blit(sp["life_bar_1"], (20, 20))