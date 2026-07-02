from __future__ import annotations
import pygame
import pymunk
import pytweening


class Player:
    # Velocidades de movimento
    VELOCIDADE_DIREITA:  int = 520
    VELOCIDADE_ESQUERDA: int = 375
    VELOCIDADE_PULO:     int = -500

    # Dash
    DASH_DISTANCE: int   = 200
    DASH_DURATION: float = 0.15

    # Animação
    IDLE_FRAMES:           int = 7
    IDLE_COOLDOWN_MAX:     int = 10
    WALKING_FRAMES:        int = 2
    WALKING_COOLDOWN_MAX:  int = 20

    def __init__(self, space: pymunk.Space,
                 animations: dict[str, list[pygame.Surface]],
                 pos: tuple[float, float] = (250, 430)) -> None:

        # Física
        self.body  = pymunk.Body(1, float("inf"))
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, (64 * 1.5, 128 * 2.5))
        self.shape.friction   = 0.9
        self.shape.elasticity = 0
        space.add(self.body, self.shape)

        # Animações
        self.animations       = animations
        self.frame_idle       = 0
        self.frame_walking    = 0
        self.idle_cooldown    = 0
        self.walking_cooldown = 0

        # Estado
        self.virado = True
        self.life   = 3
        self.estado = "Idle"
        self.image  = self.animations["Idle"][0]
        self.atacando = False
        self.tempo_ataque = 0
        self.duracao_ataque = 0.2
        self.acertou_ataque = False
        
        self.hitbox_ataque = None

        # Dash
        self.dashing       = False
        self.dash_t        = 0.0
        self.dash_duration = self.DASH_DURATION
        self.dash_inicial  = 0.0
        self.dash_final    = 0.0
        self.dash_distance = self.DASH_DISTANCE
        self.traces: list[list] = []

        # Teleporte
        self.has_tp = False
        self.tp_pos: tuple[float, float] = (0.0, 0.0)

        # Efeito visual (fase 1)
        self.shadow_opacity = 0

    #usa o @property para criar um método que pode ser acessado como um atributo
    #ai pode verificar se o player está vivo com base na quantidade de vida restante
    @property
    def vivo(self) -> bool:
        return self.life > 0

   #atualiza o estado do player, processa o dash e aplica a física do pymunk

    def update(self, space: pymunk.Space, time_delta: float) -> None:
        
        self._atualizar_estado()
        if self.dashing:
            self._processar_dash(time_delta)
        space.step(1 / 60)

        if self.atacando:
            largura = self.hitbox_ataque.width
            if self.virado:
                 self.hitbox_ataque.x = self.body.position.x + 40
            else:
                 self.hitbox_ataque.x = self.body.position.x - largura - 40
            self.hitbox_ataque.y = self.body.position.y - 120
            
            self.tempo_ataque -= time_delta

            if self.tempo_ataque <= 0:
                self.atacando = False
                self.hitbox_ataque = None

    def _atualizar_estado(self) -> None:
        
        vx, vy = self.body.velocity
        if vx == 0 and vy == 0:
            self.estado = "Idle"
        elif vy == 0 and vx != 0:
            self.estado = "Walking"

    def _processar_dash(self, time_delta: float) -> None:
        
        progresso = pytweening.easeOutQuart(self.dash_t)
        new_x = (self.dash_inicial
                 + (self.dash_final - self.dash_inicial) * progresso)
        self.body.position = (new_x, self.body.position.y)
        self.body.velocity = (0, self.body.velocity.y)
        self.dash_t += time_delta / self.dash_duration
        if self.dash_t >= 1:
            self.dash_t  = 1.0
            self.dashing = False

   #acoes do player

    def pular(self) -> None:
        if self.body.velocity.y == 0:
            self.body.velocity = (self.body.velocity.x, self.VELOCIDADE_PULO)

    def iniciar_dash(self) -> None:
        if self.dashing:
            return
        self.dashing      = True
        self.traces       = []
        self.dash_t       = 0.0
        self.dash_inicial = self.body.position.x
        offset = self.dash_distance if self.virado else -self.dash_distance
        self.dash_final = self.body.position.x + offset

    def usar_teleporte(self) -> None:
        if not self.has_tp:
            self.tp_pos = (self.body.position.x, self.body.position.y)
            self.has_tp = True
        else:
            self.body.position = self.tp_pos
            self.has_tp = False
    
    def atacar(self):
        
        if self.atacando:
            return
        
        self.atacando = True
        self.tempo_ataque = self.duracao_ataque
        
        largura = 80
        altura = 120
        
        if self.virado:
            x = self.body.position.x + 40
        
        else:
            x = self.body.position.x - largura - 40

        y = self.body.position.y - 120

        self.hitbox_ataque = pygame.Rect(x, y, largura, altura)

        self.acertou_ataque = False

    def levar_dano(self, quantidade: int = 1) -> None:
        if self.life > 0:
            self.life -= quantidade


    def atualizar_animacao(self) -> None:
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

  
    def draw(self, screen: pygame.Surface, pos_x: int, pos_y: int,
             efeitos_fase1: bool = False) -> None:
        imagem = self.image

        if self.dashing:
            imagem = pygame.transform.scale(imagem, (170, 349))
            self.traces.append([pos_x, pos_y, 180])

            for trace in self.traces:
                trace_surf = pygame.transform.scale(imagem, (200, 349))
                trace_surf.fill("maroon1", special_flags=pygame.BLEND_ADD)
                trace_surf.set_alpha(trace[2])
                if not self.virado:
                    screen.blit(trace_surf, (trace[0], trace[1]))
                else:
                    trace_surf = pygame.transform.flip(trace_surf, True, False)
                    screen.blit(trace_surf, (trace[0] - 25, trace[1]))
                trace[2] -= 30

            self.traces = [t for t in self.traces if t[2] > 0]

        if self.virado:
            imagem = pygame.transform.flip(imagem, True, False)
            print(self.body.position.x)

        screen.blit(imagem, (pos_x, pos_y))

        if self.hitbox_ataque:
            largura = self.hitbox_ataque.width
            altura = self.hitbox_ataque.height
            
            if self.virado:
                x = pos_x + 120
            else:
                x = pos_x - largura + 20

            y = pos_y + 110

            pygame.draw.rect(screen, "red", (x, y, largura, altura), 2)

        if efeitos_fase1:
            self._desenhar_efeitos_fase1(screen, imagem, pos_x, pos_y)

    def _desenhar_efeitos_fase1(self, screen: pygame.Surface,
                                 imagem: pygame.Surface,
                                 pos_x: int, pos_y: int) -> None:
        purple_overlay = imagem.copy()
        purple_overlay.fill("Purple", special_flags=pygame.BLEND_MULT)
        purple_overlay.set_alpha(40)
        screen.blit(purple_overlay, (pos_x, pos_y))

        blue_overlay = imagem.copy()
        blue_overlay.fill("Blue", special_flags=pygame.BLENDMODE_BLEND)
        blue_overlay.set_alpha(30)
        screen.blit(blue_overlay, (pos_x, pos_y))

        shadow_overlay = imagem.copy()
        shadow_overlay.fill((52, 9, 127), special_flags=pygame.BLENDMODE_MOD)
        shadow_overlay.set_alpha(self.shadow_opacity)
        zonas_sombra = [(450, 510), (20, 100), (795, 865), (1105, 1200)]
        em_zona = any(lo <= pos_x <= hi for lo, hi in zonas_sombra)
        if em_zona:
            screen.blit(shadow_overlay, (pos_x, pos_y))
            if self.shadow_opacity < 100:
                self.shadow_opacity += 25
        else:
            self.shadow_opacity = 0
