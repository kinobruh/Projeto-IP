import random
import pygame
import pytweening

from serra import SerraVertical, SerraHorizontal


class Sala3:
    LARGURA_TELA       = 1280
    ALTURA_TELA        = 720
    ESPACAMENTO_SERRA  = 350
    INICIO     = 600
    SOBRA = 500

    def __init__(self, superficie, sprite_serra):
        self.superficie   = superficie
        self.largura      = superficie.get_width()
        self.sprite_serra = sprite_serra
        self.rotacao      = 0
        self.range_volta  = False

        # serras verticais
        start       = [0.0, 0.3, 0.6, 0.15, 0.45, 0.75]
        velocidades_serras = [0.45, 0.55, 0.4, 0.5, 0.6, 0.35]
        limite   = self.largura - self.SOBRA
        x_atual  = self.INICIO
        fase_i = 0
        self.serras = []
        while x_atual < limite:
            self.serras.append(SerraVertical(
                x      = x_atual,
                y_topo = random.randint(80, 150),
                y_base = random.randint(450, 540),
                vel    = velocidades_serras[fase_i % len(velocidades_serras)],
                fase   = start[fase_i % len(start)],
            ))
            x_atual  += self.ESPACAMENTO_SERRA
            fase_i += 1

        self.serra_horizontal = SerraHorizontal(x_min=1100, x_max=1900, y=540, vel=280)

    def calcular_camera(self, player_x):
        camera_x = player_x - self.LARGURA_TELA // 2
        return max(0, min(camera_x, self.largura - self.LARGURA_TELA))

    def update(self, time_delta, player, space):
        # estado do player
        velx, vely = player.body.velocity
        if velx == 0 and vely == 0:
            player.estado = "Idle"
        elif vely == 0 and velx != 0:
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

        # serras
        self.rotacao = (self.rotacao + 4) % 360
        for serra in self.serras:
            serra.update(time_delta)
        self.serra_horizontal.update(time_delta)

        # clamp do player
        x = max(190, min(player.body.position.x, self.largura - 70))
        y = max(0,   min(player.body.position.y, self.ALTURA_TELA))
        player.body.position = (x, y)

    def draw(self, screen, player, camera_x, pos_x, pos_y, time_delta):
        screen.fill((0, 0, 0))
        screen.blit(self.superficie, (-camera_x, 10))

        sprite_rot = pygame.transform.rotate(self.sprite_serra, self.rotacao)
        for serra in self.serras:
            serra.draw(screen, sprite_rot, camera_x)
        self.serra_horizontal.draw(screen, sprite_rot, camera_x)

        player.draw(screen, pos_x, pos_y)

    def checar_colisao(self, player_hitbox, camera_x):
        for serra in self.serras:
            if player_hitbox.colliderect(serra.get_hitbox(camera_x)):
                return True
        return player_hitbox.colliderect(self.serra_horizontal.get_hitbox(camera_x))

    def checar_saida(self, player_x, screen, E_gui):
        if player_x < 400:
            screen.blit(E_gui, (140, 275))
            self.range_volta = True
        else:
            self.range_volta = False