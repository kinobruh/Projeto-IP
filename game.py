import random
import pygame
import pymunk
from enum import Enum

from player import Player
from sala2 import Sala2
from sala3 import Sala3
from fase1 import Fase1
from sala_geral import SalaGeral


class GameState(Enum):
    FASE1     = 1
    SALAGERAL = 2
    SALA2     = 3
    SALA3     = 4


class Game:
    POS_SPAWN_FASE1  = (250, 430)
    POS_SPAWN_PADRAO = (250, 455)

    def __init__(
        self,
        animations,
        sala1_surface, sala_geral_surface, sala3_surface,
        serra_sprite, enemy_sprite,
        fase1_sprites, fase1_textos,
        sala_geral_sprites, sala_geral_textos,
        E_gui,
        sons,
    ):
        self.E_gui = E_gui
        self.sons  = sons

        self.space = pymunk.Space()
        self.space.gravity = (0, 900)
        self.space.damping = 0.9

        self.player = Player(self.space, animations, pos=self.POS_SPAWN_FASE1)

        self._chao_fase1      = self._criar_chao((0, 595), 1280)
        self._chao_sala_geral = self._criar_chao((0, 620), 2560)
        self._chao_sala3      = self._criar_chao((0, 620), sala3_surface.get_width())
        self._chao_sala2      = self._criar_chao((0, 620), sala3_surface.get_width())

        self.space.add(*self._chao_fase1)
        self._chao_atual = self._chao_fase1

        self.fase1      = Fase1(sala1_surface, fase1_sprites, fase1_textos)
        self.sala_geral = SalaGeral(sala_geral_surface, sala_geral_sprites, sala_geral_textos)
        self.sala2      = Sala2(sala3_surface, enemy_sprite)
        self.sala3      = Sala3(sala3_surface, serra_sprite)

        self.state = GameState.FASE1
        self.pausado = False

        self.entrou_na_sala_geral = False
        self.entrou_na_sala2      = False
        self.entrou_na_sala3      = False
        self._trocou_para_sala_geral = False

        self.pos_x = 0
        self.pos_y = 0

        self.transicao_opacity = 255

    @staticmethod
    def _criar_chao(pos, largura):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Segment(body, (0, 0), (largura, 0), 5)
        shape.friction = 1
        shape.elasticity = 0
        return body, shape

    def _trocar_chao(self, novo_chao):
        chao_antigo_body, chao_antigo_shape = self._chao_atual
        novo_body, novo_shape = novo_chao
        if chao_antigo_shape in self.space.shapes:
            self.space.remove(chao_antigo_shape, chao_antigo_body)
        if novo_shape not in self.space.shapes:
            self.space.add(novo_body, novo_shape)
        self._chao_atual = novo_chao

    def handle_keydown(self, event, volume_sons=1.0, volume_geral=1.0):
        if event.key == pygame.K_w or event.key == pygame.K_SPACE:
            self.player.pular()

        if event.key == pygame.K_x:
            self.player.usar_teleporte()

        if event.key == pygame.K_k:
            self.player.life -= 1

        if event.key == pygame.K_c and not self.player.dashing:
            dash_choose = random.choice([self.sons["dash1"], self.sons["dash2"]])
            dash_choose.set_volume(0.1 * volume_sons * volume_geral)
            dash_choose.play()
            self.player.iniciar_dash()

        if (event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN) and not self.fase1.tutorial_acabou:
            self.fase1.avancar_tutorial()
            self.sons["click"].set_volume(0.15 * volume_sons * volume_geral)
            self.sons["click"].play()

        if event.key == pygame.K_ESCAPE:
            self.pausado = not self.pausado

        if event.key == pygame.K_e:
            self._handle_tecla_e(volume_sons, volume_geral)

    def _handle_tecla_e(self, volume_sons, volume_geral):
        if self.state == GameState.FASE1 and self.fase1.range_da_porta:
            self.state = GameState.SALAGERAL
            self.entrou_na_sala_geral = True
            self.player.virado = True

        elif self.state == GameState.SALAGERAL:
            if self.sala_geral.range_porta_saida:
                self.sala_geral.tentar_porta_saida()
            elif self.sala_geral.tentar_porta3():
                self.state = GameState.SALA3
                self.entrou_na_sala3 = True
                self.sala_geral.range_porta3 = False
                self.sala3.range_volta = False
                self.player.virado = True
            elif self.sala_geral.tentar_porta2():
                self.state = GameState.SALA2
                self.entrou_na_sala2 = True
                self.sala_geral.range_porta2 = False
                self.sala2.range_volta = False
                self.player.virado = True

        elif self.state == GameState.SALA3 and self.sala3.range_volta:
            self.sons["open_door"].set_volume(0.25 * volume_sons * volume_geral)
            self.sons["open_door"].play()
            self.state = GameState.SALAGERAL
            self.player.body.position = (1900, 455)
            self._trocar_chao(self._chao_sala_geral)
            self.sala3.range_volta = False
            self.sala_geral.range_porta3 = False
            self.player.virado = True
            self.transicao_opacity = 255

        elif self.state == GameState.SALA2 and self.sala2.range_volta:
            self.sons["open_door"].set_volume(0.25 * volume_sons * volume_geral)
            self.sons["open_door"].play()
            self.state = GameState.SALAGERAL
            self.player.body.position = (1300, 455)
            self._trocar_chao(self._chao_sala_geral)
            self.sala2.range_volta = False
            self.sala_geral.range_porta2 = False
            self.player.virado = True
            self.transicao_opacity = 255

    def _mover(self, keys):
        if keys[pygame.K_d]:
            self.player.body.velocity = (520, self.player.body.velocity.y)
            self.player.virado = True
        if keys[pygame.K_a]:
            self.player.body.velocity = (-375, self.player.body.velocity.y)
            self.player.virado = False
        else:
            self.player.body.velocity = (self.player.body.velocity.x * 0.7, self.player.body.velocity.y)

    def update(self, time_delta, volume_sons=1.0, volume_geral=1.0):
        keys = pygame.key.get_pressed()

        if self.state == GameState.FASE1:
            self._update_fase1(time_delta, volume_sons, volume_geral, keys)
        elif self.state == GameState.SALAGERAL:
            self._update_sala_geral(time_delta, volume_sons, volume_geral, keys)
        elif self.state == GameState.SALA3:
            self._update_sala3(time_delta, volume_sons, volume_geral, keys)
        elif self.state == GameState.SALA2:
            self._update_sala2(time_delta, volume_sons, volume_geral, keys)

        if self.transicao_opacity > 0:
            self.transicao_opacity -= 5

    def _update_fase1(self, time_delta, volume_sons, volume_geral, keys):
        self.fase1.update(self.player, self.space, time_delta)
        self.player.atualizar_animacao()
        self._mover(keys)

    def _update_sala_geral(self, time_delta, volume_sons, volume_geral, keys):
        if self.entrou_na_sala_geral:
            self.entrou_na_sala_geral = False
            self.sons["open_door"].set_volume(0.25 * volume_sons * volume_geral)
            self.sons["open_door"].play()
            self.player.body.position = self.POS_SPAWN_PADRAO
            self._trocar_chao(self._chao_sala_geral)
            self.transicao_opacity = 255
            self.sala_geral.iniciar_cutscene()
            self._trocou_para_sala_geral = True

        self.sala_geral.update(time_delta, self.player, self.space)

        if not self.sala_geral.em_cutscene and not self.sala_geral.em_fala_porta:
            self.player.atualizar_animacao()
            self._mover(keys)

    def consumir_trocou_para_sala_geral(self) -> bool:
        if self._trocou_para_sala_geral:
            self._trocou_para_sala_geral = False
            return True
        return False

    def _update_sala3(self, time_delta, volume_sons, volume_geral, keys):
        if self.entrou_na_sala3:
            self.entrou_na_sala3 = False
            self.sons["open_door"].set_volume(0.25 * volume_sons * volume_geral)
            self.sons["open_door"].play()
            self.player.body.position = self.POS_SPAWN_PADRAO
            self._trocar_chao(self._chao_sala3)
            self.transicao_opacity = 255

        self.sala3.update(time_delta, self.player, self.space)

        camera_x = self.sala3.calcular_camera(self.player.body.position.x)
        pos_x = self.player.body.position.x - camera_x - 110
        pos_y = self.player.body.position.y - 235
        player_hitbox = pygame.Rect(pos_x + 50, pos_y + 60, 70, 200)
        if self.sala3.checar_colisao(player_hitbox, camera_x):
            self.sons["damage"].set_volume(0.8 * volume_sons * volume_geral)
            self.sons["damage"].play()
            self.player.body.position = self.POS_SPAWN_PADRAO
            self.player.body.velocity = (0, 0)
            self.player.has_tp = False

        self.player.atualizar_animacao()
        self._mover(keys)

    def _update_sala2(self, time_delta, volume_sons, volume_geral, keys):
        if self.entrou_na_sala2:
            self.entrou_na_sala2 = False
            self.sons["open_door"].set_volume(0.25 * volume_sons * volume_geral)
            self.sons["open_door"].play()
            self.player.body.position = self.POS_SPAWN_PADRAO
            self._trocar_chao(self._chao_sala2)
            self.transicao_opacity = 255

        self.sala2.update(time_delta, self.player, self.space, self.sons["shoot"], 0.4 * volume_sons * volume_geral)

        camera_x = self.sala2.calcular_camera(self.player.body.position.x)
        pos_x = self.player.body.position.x - camera_x - 110
        pos_y = self.player.body.position.y - 235
        player_hitbox = pygame.Rect(pos_x + 50, pos_y + 60, 70, 200)
        if self.sala2.checar_colisao_balas(player_hitbox, camera_x, self.sons["damage"], 0.8 * volume_sons * volume_geral):
            self.player.life -= 1

        self.player.atualizar_animacao()
        self._mover(keys)

    def draw(self, screen, click_sfx_volume=1.0):
        if self.state == GameState.FASE1:
            self.pos_x, self.pos_y = self.fase1.draw(screen, self.player, self.sons["damage"], click_sfx_volume)

        elif self.state == GameState.SALAGERAL:
            pos_x, pos_y = self.sala_geral.draw(screen, self.player, self.sons["click"], click_sfx_volume)
            if pos_x is not None:
                self.pos_x, self.pos_y = pos_x, pos_y

        elif self.state == GameState.SALA3:
            camera_x = self.sala3.calcular_camera(self.player.body.position.x)
            self.pos_x = self.player.body.position.x - camera_x - 110
            self.pos_y = self.player.body.position.y - 235
            self.sala3.draw(screen, self.player, camera_x, self.pos_x, self.pos_y, 0)
            self.sala3.checar_saida(self.player.body.position.x, screen, self.E_gui)

        elif self.state == GameState.SALA2:
            camera_x = self.sala2.calcular_camera(self.player.body.position.x)
            self.pos_x = self.player.body.position.x - camera_x - 110
            self.pos_y = self.player.body.position.y - 235
            self.sala2.draw(screen, self.player, camera_x, self.pos_x, self.pos_y, 0)
            self.sala2.checar_saida(self.player.body.position.x, screen, self.E_gui)

        return self.pos_x, self.pos_y

    def reset(self):
        self.player.has_tp = False
        self.player.body.position = self.POS_SPAWN_FASE1
        self.player.virado = True
        self.player.life = 3

        self.fase1.reset()
        self.sala_geral.reset()

        self._trocar_chao(self._chao_fase1)
        self.state = GameState.FASE1
        self.pausado = False
        self.entrou_na_sala_geral = False
        self.entrou_na_sala2      = False
        self.entrou_na_sala3      = False
        self._trocou_para_sala_geral = False
        self.transicao_opacity    = 255