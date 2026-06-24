import pygame
import pymunk
import pytweening


class Player:
    # Constantes de movimento
    VELOCIDADE_DIREITA  = 520
    VELOCIDADE_ESQUERDA = 375
    VELOCIDADE_PULO     = -500
    DASH_DISTANCE       = 200
    DASH_DURATION       = 0.15

    # Constantes de animação
    IDLE_FRAMES        = 7
    IDLE_COOLDOWN_MAX  = 10
    WALKING_FRAMES     = 2
    WALKING_COOLDOWN_MAX = 20

    def __init__(self, space, animations, pos=(250, 430)):
        self.body = pymunk.Body(1, float('inf'))
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, (64 * 1.5, 128 * 2.5))
        self.shape.friction = 0.9
        self.shape.elasticity = 0
        space.add(self.body, self.shape)

        self.animations = animations
        self.frame_idle    = 0
        self.frame_walking = 0
        self.idle_cooldown    = 0
        self.walking_cooldown = 0

        self.virado = True
        self.life   = 3
        self.estado = "Idle"
        self.image  = self.animations["Idle"][0]

        self.dashing       = False
        self.dash_t        = 0
        self.dash_duration = self.DASH_DURATION
        self.dash_inicial  = 0
        self.dash_final    = 0
        self.dash_distance = self.DASH_DISTANCE
        self.traces        = []

        self.has_tp = False
        self.tp_pos = (0, 0)

    # ------------------------------------------------------------------
    # Propriedades
    # ------------------------------------------------------------------

    @property
    def vivo(self) -> bool:
        return self.life > 0

    # ------------------------------------------------------------------
    # Ações — chamadas pelo main.py no lugar de código inline
    # ------------------------------------------------------------------

    def pular(self) -> None:
        """Executa o pulo se o player estiver no chão."""
        if self.body.velocity.y == 0:
            self.body.velocity = (self.body.velocity.x, self.VELOCIDADE_PULO)

    def iniciar_dash(self) -> None:
        """Prepara o dash na direção em que o player está virado."""
        if self.dashing:
            return
        self.dashing    = True
        self.traces     = []
        self.dash_t     = 0
        self.dash_inicial = self.body.position.x
        offset = self.dash_distance if self.virado else -self.dash_distance
        self.dash_final = self.body.position.x + offset

    def usar_teleporte(self) -> None:
        """Cria ou consome o ponto de teleporte."""
        if not self.has_tp:
            self.tp_pos = (self.body.position.x, self.body.position.y)
            self.has_tp = True
        else:
            self.body.position = self.tp_pos
            self.has_tp = False

    def levar_dano(self, quantidade: int = 1) -> None:
        self.life -= quantidade

    # ------------------------------------------------------------------
    # Atualização de animação — tira do main.py
    # ------------------------------------------------------------------

    def atualizar_animacao(self) -> None:
        """Avança cooldowns e seleciona o frame correto. Chame 1x por frame."""
        self.idle_cooldown += 1
        if self.idle_cooldown >= self.IDLE_COOLDOWN_MAX:
            self.idle_cooldown = 0
            self.frame_idle = (self.frame_idle + 1) % self.IDLE_FRAMES

        self.walking_cooldown += 1
        if self.walking_cooldown >= self.WALKING_COOLDOWN_MAX:
            self.walking_cooldown = 0
            self.frame_walking = (self.frame_walking + 1) % self.WALKING_FRAMES

        if self.estado == "Idle":
            self.image = self.animations["Idle"][self.frame_idle]
        elif self.estado == "Walking":
            self.image = self.animations["Walking"][self.frame_walking]