from __future__ import annotations
import pygame
import pytweening


class SerraBase:
    """Comportamento compartilhado de todas as serras."""

    TAMANHO_HITBOX: int = 150

    def get_hitbox(self, camera_x: float = 0) -> pygame.Rect:
        raise NotImplementedError

    def draw(self, screen: pygame.Surface,
             sprite_rotacionado: pygame.Surface,
             camera_x: float) -> None:
        raise NotImplementedError

    def _blit_centrado(self, screen: pygame.Surface,
                        sprite: pygame.Surface,
                        world_x: float, world_y: float,
                        camera_x: float) -> None:
        screen_x = world_x - camera_x
        rect = sprite.get_rect(center=(screen_x, world_y))
        screen.blit(sprite, rect)

    def _hitbox_centrada(self, world_x: float, world_y: float,
                          camera_x: float, tamanho: int) -> pygame.Rect:
        screen_x = world_x - camera_x
        s = tamanho
        return pygame.Rect(screen_x - s // 2, world_y - s // 2, s, s)


class SerraVertical(SerraBase):
    """Serra que oscila verticalmente com easing suave."""

    TAMANHO_HITBOX = 150

    def __init__(self, x: float, y_topo: float, y_base: float,
                 vel: float, fase: float) -> None:
        self.x      = x
        self.y_topo = y_topo
        self.y_base = y_base
        self.vel    = vel
        self.t      = fase
        self.y      = y_topo

    def update(self, time_delta: float) -> None:
        self.t += time_delta * self.vel
        ciclo = self.t % 2.0
        progresso = (pytweening.easeInOutSine(ciclo)
                     if ciclo <= 1.0
                     else pytweening.easeInOutSine(2.0 - ciclo))
        self.y = self.y_topo + (self.y_base - self.y_topo) * progresso

    def draw(self, screen: pygame.Surface,
             sprite_rotacionado: pygame.Surface,
             camera_x: float) -> None:
        self._blit_centrado(screen, sprite_rotacionado, self.x, self.y, camera_x)

    def get_hitbox(self, camera_x: float = 0) -> pygame.Rect:
        return self._hitbox_centrada(self.x, self.y, camera_x,
                                      self.TAMANHO_HITBOX)


class SerraHorizontal(SerraBase):
    """Serra que se move horizontalmente de um lado ao outro."""

    TAMANHO_HITBOX = 175

    def __init__(self, x_min: float, x_max: float,
                 y: float, vel: float = 280) -> None:
        self.x_min   = x_min
        self.x_max   = x_max
        self.y       = y
        self.vel     = vel
        self.direcao = 1
        self.x       = x_min

    def update(self, time_delta: float) -> None:
        self.x += self.vel * self.direcao * time_delta
        if self.x >= self.x_max:
            self.x       = self.x_max
            self.direcao = -1
        elif self.x <= self.x_min:
            self.x       = self.x_min
            self.direcao = 1

    def draw(self, screen: pygame.Surface,
             sprite_rotacionado: pygame.Surface,
             camera_x: float) -> None:
        self._blit_centrado(screen, sprite_rotacionado, self.x, self.y, camera_x)

    def get_hitbox(self, camera_x: float = 0) -> pygame.Rect:
        return self._hitbox_centrada(self.x, self.y, camera_x,
                                      self.TAMANHO_HITBOX)
