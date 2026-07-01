from __future__ import annotations
import pygame

from sala_base import SalaBase
from enemy import Enemy


class Sala1(SalaBase):

    CLAMP_MIN_X = 190

    def __init__(self, superficie: pygame.Surface):
        super().__init__(superficie)
        self.CLAMP_MAX_X = self.largura - 70

    def update(self, time_delta: float, player, space, volume_sfx: float = 1.0):
        player.update(space, time_delta)

        self.clamp_player(player)

    def draw(self, screen: pygame.Surface, player, camera_x: int, pos_x: int, pos_y: int, time_delta: float = 0):
        screen.fill((0, 0, 0))
        screen.blit(self.superficie, (-camera_x, 10))
        player.draw(screen, pos_x, pos_y)

    def checar_saida(self, player_x: float, screen: pygame.Surface, E_gui: pygame.Surface):
        super().checar_saida(player_x, screen, E_gui)
