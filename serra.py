import random
import pygame
import pytweening


class SerraVertical:
    TAMANHO_HITBOX = 150

    def __init__(self, x, y_topo, y_base, vel, fase):
        self.x      = x
        self.y_topo = y_topo
        self.y_base = y_base
        self.vel    = vel
        self.t      = fase
        self.y      = y_topo

    def update(self, time_delta):
        self.t += time_delta * self.vel
        ciclo = self.t % 2.0
        if ciclo <= 1.0:
            progresso = pytweening.easeInOutSine(ciclo)
        else:
            progresso = pytweening.easeInOutSine(2.0 - ciclo)
        self.y = self.y_topo + (self.y_base - self.y_topo) * progresso

    def draw(self, screen, sprite_rotacionado, camera_x):
        screen_x = self.x - camera_x
        rect = sprite_rotacionado.get_rect(center=(screen_x, self.y))
        screen.blit(sprite_rotacionado, rect)

    def get_hitbox(self, camera_x):
        s        = self.TAMANHO_HITBOX
        screen_x = self.x - camera_x
        return pygame.Rect(screen_x - s // 2, self.y - s // 2, s, s)


class SerraHorizontal:
    TAMANHO_HITBOX = 175

    def __init__(self, x_min, x_max, y, vel=280):
        self.x_min   = x_min
        self.x_max   = x_max
        self.y       = y
        self.vel     = vel
        self.direcao = 1
        self.x       = x_min

    def update(self, time_delta):
        self.x += self.vel * self.direcao * time_delta
        if self.x >= self.x_max:
            self.x       = self.x_max
            self.direcao = -1
        elif self.x <= self.x_min:
            self.x       = self.x_min
            self.direcao = 1

    def draw(self, screen, sprite_rotacionado, camera_x):
        screen_x = self.x - camera_x
        rect = sprite_rotacionado.get_rect(center=(screen_x, self.y))
        screen.blit(sprite_rotacionado, rect)

    def get_hitbox(self, camera_x):
        s        = self.TAMANHO_HITBOX
        screen_x = self.x - camera_x
        return pygame.Rect(screen_x - s // 2, self.y - s // 2, s, s)
