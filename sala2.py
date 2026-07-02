from __future__ import annotations
import pygame

from sala_base import SalaBase
from enemy import Enemy


class Sala2(SalaBase):
    #sala do olho

    CLAMP_MIN_X = 190

    def __init__(self, superficie: pygame.Surface, enemy_sprite: pygame.Surface, bullet_sprite: pygame.Surface | None = None) -> None:
        super().__init__(superficie)
        self.CLAMP_MAX_X = self.largura - 70

        self.inimigo = Enemy(
            x=900, y=455,
            patrulha_min=700,
            patrulha_max=1200,
            sprite=enemy_sprite,
            bullet_sprite=bullet_sprite,
        )

        self.vida_pos = (1500, 340)
        self.pegou_vida = False

    def update(self, time_delta: float, player, space, shoot_sfx=None, volume_sfx: float = 1.0):
        player.update(space, time_delta)

        self.inimigo.update(
            time_delta,
            player.body.position.x,
            player.body.position.y,
            sfx_tiro=shoot_sfx,
            volume_sfx=volume_sfx,
        )

        self.checar_ataque_player(player, self.inimigo)
        
        self.clamp_player(player)

    def draw(self, screen: pygame.Surface, player,
             camera_x: int, pos_x: int, pos_y: int,
             time_delta: float = 0) -> None:
        screen.fill((0, 0, 0))
        screen.blit(self.superficie, (-camera_x, 10))
        player.draw(screen, pos_x, pos_y)
        self.inimigo.draw(screen, camera_x)

    def checar_colisao_balas(self, player_hitbox: pygame.Rect, camera_x: float, damage_sfx=None, volume_sfx: float = 1.0):
        acertou = False
        for bullet in self.inimigo.bullets:
            if bullet.vivo and player_hitbox.colliderect(bullet.get_rect(camera_x)):
                bullet.vivo = False
                if damage_sfx:
                    damage_sfx.set_volume(volume_sfx)
                    damage_sfx.play()
                acertou = True
        self.inimigo.bullets = [b for b in self.inimigo.bullets if b.vivo]
        return acertou

    def checar_saida(self, player_x: float, screen: pygame.Surface, E_gui: pygame.Surface):
        super().checar_saida(player_x, screen, E_gui)

    def desenhar_vida(self, screen, sprite_vida, camera_x):
        if not self.pegou_vida:
            x = self.vida_pos[0] - camera_x
            y = self.vida_pos[1]
            screen.blit(sprite_vida, (x, y))

    def checar_coleta_vida(self, player):

        if self.pegou_vida:
            return False

        player_rect = pygame.Rect(
            player.body.position.x - 45,
            player.body.position.y - 120,
            90,
            200
        )

        vida_rect = pygame.Rect(
            self.vida_pos[0],
            self.vida_pos[1],
            80,
            80
        )

        if player_rect.colliderect(vida_rect):
            self.pegou_vida = True
            return True

        return False

    def reset(self):
        super().reset()
        self.pegou_vida = False
