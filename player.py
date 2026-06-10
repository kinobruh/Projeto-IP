import pygame
import pymunk
import pytweening

class Player:
    def __init__(self, space, animations, pos=(250, 430)):
        self.body = pymunk.Body(1, float('inf'))
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, (64 * 1.5, 128 * 2.5))
        self.shape.friction = 0.9
        self.shape.elasticity = 0
        space.add(self.body, self.shape)

        self.animations = animations
        self.frame_idle = 0
        self.frame_walking = 0
        self.idle_cooldown = 0
        self.walking_cooldown = 0

        self.virado = True
        self.life = 3
        self.estado = "Idle"
        self.image = self.animations["Idle"][0]

        self.dashing = False
        self.dash_t = 0
        self.dash_duration = 0.15
        self.dash_inicial = 0
        self.dash_final = 0
        self.dash_distance = 200
        self.traces = []

        self.has_tp = False
        self.tp_pos = (0, 0)