from __future__ import annotations
import random
import pygame

from sala_base import SalaBase
from serra import SerraVertical, SerraHorizontal


class Sala3(SalaBase):
    #sala das serras

    CLAMP_MIN_X = 190

    _ESPACAMENTO_SERRA = 350
    _INICIO_SERRAS     = 600
    _SOBRA             = 500

    def __init__(self, superficie: pygame.Surface,
                 sprite_serra: pygame.Surface) -> None:
        super().__init__(superficie)
        self.CLAMP_MAX_X = self.largura - 70
        self.sprite_serra = sprite_serra
        self.rotacao      = 0

        self.serras = self._criar_serras_verticais()
        self.serra_horizontal = SerraHorizontal(
            x_min=1100, x_max=1900, y=540, vel=280)

   

    def _criar_serras_verticais(self) -> list[SerraVertical]:
        velocidades = [0.45, 0.55, 0.40, 0.50, 0.60, 0.35]
        fases       = [0.00, 0.30, 0.60, 0.15, 0.45, 0.75]
        limite  = self.largura - self._SOBRA
        x_atual = self._INICIO_SERRAS
        serras  = []
        i = 0
        while x_atual < limite:
            serras.append(SerraVertical(
                x      = x_atual,
                y_topo = random.randint(80, 150),
                y_base = random.randint(450, 540),
                vel    = velocidades[i % len(velocidades)],
                fase   = fases[i % len(fases)],
            ))
            x_atual += self._ESPACAMENTO_SERRA
            i += 1
        return serras

    #mesma coisa, usa sala base
    def update(self, time_delta: float, player, space) -> None:
        # dash + física + estado do player em um só lugar
        player.update(space, time_delta)

        self.rotacao = (self.rotacao + 4) % 360
        for serra in self.serras:
            serra.update(time_delta)
        self.serra_horizontal.update(time_delta)

        self.clamp_player(player)

    def draw(self, screen: pygame.Surface, player,
             camera_x: int, pos_x: int, pos_y: int,
             time_delta: float = 0) -> None:
        screen.fill((0, 0, 0))
        screen.blit(self.superficie, (-camera_x, 10))

        sprite_rot = pygame.transform.rotate(self.sprite_serra, self.rotacao)
        for serra in self.serras:
            serra.draw(screen, sprite_rot, camera_x)
        self.serra_horizontal.draw(screen, sprite_rot, camera_x)

        player.draw(screen, pos_x, pos_y)

    #fisica das serras, colisão com o player

    def checar_colisao(self, player_hitbox: pygame.Rect,
                        camera_x: float) -> bool:
        #retorna se o player colidiu com alguma serra (vertical ou horizontal)
        for serra in self.serras:
            if player_hitbox.colliderect(serra.get_hitbox(camera_x)):
                return True
        return player_hitbox.colliderect(
            self.serra_horizontal.get_hitbox(camera_x))

    def checar_saida(self, player_x: float, screen: pygame.Surface,
                     E_gui: pygame.Surface) -> None:
        
        super().checar_saida(player_x, screen, E_gui)
