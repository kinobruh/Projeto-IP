import pygame
import pytweening
from enemy import Enemy

class Sala2:
    LARGURA_TELA = 1280
    ALTURA_TELA  = 720

    def __init__(self, surfece, enemy_sprite):
        self.surface = surfece
        self.largura    = surfece.get_width()
        self.range_volta = False

        self.inimigo = Enemy(
            x=900, y=455,
            patrulha_min=700,
            patrulha_max=1200,
            sprite=enemy_sprite,
        )

    def calcular_camera(self, player_x):
        camera_x = player_x - self.LARGURA_TELA // 2
        return max(0, min(camera_x, self.largura - self.LARGURA_TELA))

    def update(self, time_delta, player, space, shoot_sfx, volume_sfx):
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

        self.inimigo.update(
            time_delta,
            player.body.position.x,
            player.body.position.y,
            sfx_tiro=shoot_sfx,
            volume_sfx=volume_sfx,
        )

        # clamp do player
        x = max(190, min(player.body.position.x, self.largura - 70))
        y = max(0,   min(player.body.position.y, self.ALTURA_TELA))
        player.body.position = (x, y)

    def draw(self, screen, player, camera_x, pos_x, pos_y, time_delta):
        screen.fill((0, 0, 0))
        screen.blit(self.surface, (-camera_x, 10))

        player.draw(screen, pos_x, pos_y)
        self.inimigo.draw(screen, camera_x)

    def checar_colisao_balas(self, player_hitbox, camera_x, damage_sfx, volume_sfx):
        acertou = False
        for bullet in self.inimigo.bullets:
            if bullet.vivo and player_hitbox.colliderect(bullet.get_rect(camera_x)):
                bullet.vivo = False
                damage_sfx.set_volume(volume_sfx)
                damage_sfx.play()
                acertou = True
        self.inimigo.bullets = [b for b in self.inimigo.bullets if b.vivo]
        return acertou

    def checar_saida(self, player_x, screen, E_gui):
        if player_x < 400:
            screen.blit(E_gui, (140, 275))
            self.range_volta = True
        else:
            self.range_volta = False