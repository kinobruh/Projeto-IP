from __future__ import annotations
import random
from enum import Enum

import pygame
import pymunk

from player import Player
from fase1 import Fase1
from sala_geral import SalaGeral
from sala2 import Sala2
from sala3 import Sala3
from sala1 import Sala1
from audio_manager import AudioManager


class GameState(Enum):
    FASE1     = 1
    SALAGERAL = 2
    SALA2     = 3
    SALA3     = 4
    SALA1     = 5


SPAWN_FASE1  = (250, 430)
SPAWN_PADRAO = (250, 455)

SPAWN_VOLTA_SALA3 = (1900, 455)
SPAWN_VOLTA_SALA2 = (1300, 455)
SPAWN_VOLTA_SALA1 = (700, 455)

class Game:
    def __init__(
        self,
        animations: dict,
        fase1_surface: pygame.Surface,
        sala_geral_surface: pygame.Surface,
        sala3_surface: pygame.Surface,
        serra_sprite: pygame.Surface,
        enemy_sprite: pygame.Surface,
        bullet_sprite: pygame.Surface,
        fase1_sprites: dict,
        sala_geral_sprites: dict,
        font: pygame.font.Font,
        E_gui: pygame.Surface,
        sons: dict,
    ):
        self.E_gui = E_gui
        self.font = font
        self.audio = AudioManager(sons)

        #Física
        self.space         = pymunk.Space()
        self.space.gravity = (0, 900)
        self.space.damping = 0.9

        #Player
        self.player = Player(self.space, animations, pos=SPAWN_FASE1)

        #Chãos
        self._chao_fase1      = self._criar_chao((0, 595), 1280)
        self._chao_sala_geral = self._criar_chao((0, 620), 2560)
        self._chao_sala3      = self._criar_chao((0, 620), sala3_surface.get_width())
        self._chao_sala2      = self._criar_chao((0, 620), sala3_surface.get_width())
        self._chao_sala1      = self._criar_chao((0, 620), sala3_surface.get_width())

        self.space.add(*self._chao_fase1)
        self._chao_atual = self._chao_fase1

        #Salas
        self.fase1      = Fase1(fase1_surface, fase1_sprites, font)
        self.sala_geral = SalaGeral(sala_geral_surface, sala_geral_sprites,
                                    font)
        self.sala2      = Sala2(sala3_surface, enemy_sprite, bullet_sprite)
        self.sala3      = Sala3(sala3_surface, serra_sprite)
        self.sala1      = Sala1(sala3_surface)

        #Estado
        self.state   = GameState.FASE1
        self.pausado = False

        self._entrou_na_sala_geral = False
        self._entrou_na_sala1      = False
        self._entrou_na_sala2      = False
        self._entrou_na_sala3      = False
        self._trocou_para_sala_geral = False
        self.chaves_coletadas = {"sala1": False, "sala2": False, "sala3": False}

        self.pos_x = 0
        self.pos_y = 0
        self.transicao_opacity = 255

        self.timer_morte = 300
        self.game_over = False

    @staticmethod
    def _criar_chao(pos: tuple, largura: int):
        body  = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Segment(body, (0, 0), (largura, 0), 5)
        shape.friction   = 1
        shape.elasticity = 0
        return body, shape

    def _trocar_chao(self, novo_chao):
        old_body, old_shape = self._chao_atual
        new_body, new_shape = novo_chao
        if old_shape in self.space.shapes:
            self.space.remove(old_shape, old_body)
        if new_shape not in self.space.shapes:
            self.space.add(new_body, new_shape)
        self._chao_atual = novo_chao

    def handle_keydown(self, event: pygame.event.Event, volume_sons: float = 1.0, volume_geral: float = 1.0):
        k = event.key

        if k in (pygame.K_w, pygame.K_SPACE):
            self.player.pular()

        elif k == pygame.K_x:
            self.player.usar_teleporte()

        elif k == pygame.K_k:
            self.player.life -= 1

        elif k == pygame.K_c and not self.player.dashing:
            nome_dash = random.choice(["dash1", "dash2"])
            self.audio.tocar(nome_dash, volume_sons, volume_geral)
            self.player.iniciar_dash()

        elif k in (pygame.K_KP_ENTER, pygame.K_RETURN):
            if not self.fase1.tutorial_acabou:
                self.fase1.avancar_tutorial()
                self.audio.tocar("click", volume_sons, volume_geral)

        elif k == pygame.K_ESCAPE:
            self.pausado = not self.pausado

        elif k == pygame.K_e:
            self._handle_tecla_e(volume_sons, volume_geral)

    def _handle_tecla_e(self, volume_sons: float, volume_geral: float):
        s = self.state

        if s == GameState.FASE1 and self.fase1.range_da_porta:
            self._entrar_sala(GameState.SALAGERAL)

        elif s == GameState.SALAGERAL:
            if self.sala_geral.range_porta_saida:
                self.sala_geral.tentar_porta_saida()
            elif self.sala_geral.tentar_porta3():
                self._entrar_sala(GameState.SALA3)
                self.sala_geral.range_porta3 = False
                self.sala3.range_volta = False
            elif self.sala_geral.tentar_porta2():
                self._entrar_sala(GameState.SALA2)
                self.sala_geral.range_porta2 = False
                self.sala2.range_volta = False
            elif self.sala_geral.tentar_porta1():
                self._entrar_sala(GameState.SALA1)
                self.sala_geral.range_porta1 = False
                self.sala1.range_volta = False

        elif s == GameState.SALA3:
            if self.sala3.range_volta:
                self._voltar_para_sala_geral(SPAWN_VOLTA_SALA3, volume_sons, volume_geral)
                self.sala3.range_volta = False
                self.sala_geral.range_porta3 = False
            elif self.sala3.range_chave:
                self.sala3.pegou_chave = True
                self.chaves_coletadas["sala3"] = True
                self.audio.tocar("click", volume_sons, volume_geral)
               

        elif s == GameState.SALA2:
            if self.sala2.range_volta:
                self._voltar_para_sala_geral(SPAWN_VOLTA_SALA2, volume_sons, volume_geral)
                self.sala2.range_volta = False
                self.sala_geral.range_porta2 = False
            elif self.sala2.range_chave:
                self.sala2.pegou_chave = True
                self.chaves_coletadas["sala2"] = True
                self.audio.tocar("click", volume_sons, volume_geral)

        elif s == GameState.SALA1:
            if self.sala1.range_volta:
                self._voltar_para_sala_geral(SPAWN_VOLTA_SALA1, volume_sons, volume_geral)
                self.sala1.range_volta = False
                self.sala_geral.range_porta1 = False
            elif self.sala1.range_chave:
                self.sala1.pegou_chave = True
                self.chaves_coletadas["sala1"] = True
                self.audio.tocar("click", volume_sons, volume_geral)
    def _entrar_sala(self, novo_estado: GameState):
        self.state = novo_estado
        self.player.virado = True
        if novo_estado == GameState.SALAGERAL:
            self._entrou_na_sala_geral = True
        elif novo_estado == GameState.SALA2:
            self._entrou_na_sala2 = True
        elif novo_estado == GameState.SALA3:
            self._entrou_na_sala3 = True
        elif novo_estado == GameState.SALA1:
            self._entrou_na_sala1 = True

    def _voltar_para_sala_geral(self, spawn_pos: tuple, volume_sons: float, volume_geral: float):
        self.audio.tocar("open_door", volume_sons, volume_geral)
        self.state = GameState.SALAGERAL
        self.player.body.position = spawn_pos
        self._trocar_chao(self._chao_sala_geral)
        self.player.virado    = True
        self.transicao_opacity = 255

    def _mover(self, keys):
        if keys[pygame.K_d]:
            self.player.body.velocity = (self.player.VELOCIDADE_DIREITA, self.player.body.velocity.y)
            self.player.virado = True
        if keys[pygame.K_a]:
            self.player.body.velocity = (-self.player.VELOCIDADE_ESQUERDA, self.player.body.velocity.y)
            self.player.virado = False
        else:
            self.player.body.velocity = (self.player.body.velocity.x * 0.7, self.player.body.velocity.y)

    def update(self, time_delta: float, volume_sons: float = 1.0, volume_geral: float = 1.0):

        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()

        if self.state == GameState.FASE1:
            self._update_fase1(time_delta, volume_sons, volume_geral, keys)
        elif self.state == GameState.SALAGERAL:
            self._update_sala_geral(time_delta, volume_sons, volume_geral, keys)
        elif self.state == GameState.SALA3:
            self._update_sala3(time_delta, volume_sons, volume_geral, keys)
        elif self.state == GameState.SALA2:
            self._update_sala2(time_delta, volume_sons, volume_geral, keys)
        elif self.state == GameState.SALA1:
            self._update_sala1(time_delta, volume_sons, volume_geral, keys)

        if self.transicao_opacity > 0:
            self.transicao_opacity -= 5

        if not self.player.vivo:
            self.game_over = True

    def _update_fase1(self, time_delta, volume_sons, volume_geral, keys):
        self.fase1.update(time_delta, self.player, self.space)
        if self.fase1.tocou_dano:
            self.audio.tocar("damage", volume_sons, volume_geral)
        self.player.atualizar_animacao()
        self._mover(keys)

    def _update_sala_geral(self, time_delta, volume_sons, volume_geral, keys):
        if self._entrou_na_sala_geral:
            self._entrou_na_sala_geral = False
            self.audio.tocar("open_door", volume_sons, volume_geral)
            self.player.body.position = SPAWN_PADRAO
            self._trocar_chao(self._chao_sala_geral)
            self.transicao_opacity = 255
            self.sala_geral.iniciar_cutscene()
            self._trocou_para_sala_geral = True

        self.sala_geral.update(time_delta, self.player, self.space)

        if not self.sala_geral.em_cutscene and not self.sala_geral.em_fala_porta:
            self.player.atualizar_animacao()
            self._mover(keys)

    def consumir_trocou_para_sala_geral(self):
        if self._trocou_para_sala_geral:
            self._trocou_para_sala_geral = False
            return True
        return False

    def _update_sala3(self, time_delta, volume_sons, volume_geral, keys):
        if self._entrou_na_sala3:
            self._entrou_na_sala3 = False
            self.audio.tocar("open_door", volume_sons, volume_geral)
            self.player.body.position = SPAWN_PADRAO
            self._trocar_chao(self._chao_sala3)
            self.transicao_opacity = 255

        self.sala3.update(time_delta, self.player, self.space)

        camera_x    = self.sala3.calcular_camera(self.player.body.position.x)
        pos_x, pos_y = self.sala3.calcular_pos_player(
            self.player.body.position.x, self.player.body.position.y, camera_x)
        player_hitbox = pygame.Rect(pos_x + 50, pos_y + 60, 70, 200)

        if self.sala3.checar_colisao(player_hitbox, camera_x):
            self.audio.tocar("damage", volume_sons, volume_geral)
            self.player.body.position = SPAWN_PADRAO
            self.player.body.velocity = (0, 0)
            self.player.has_tp = False

        self.player.atualizar_animacao()
        self._mover(keys)

    def _update_sala2(self, time_delta, volume_sons, volume_geral, keys):
        if self._entrou_na_sala2:
            self._entrou_na_sala2 = False
            self.audio.tocar("open_door", volume_sons, volume_geral)
            self.player.body.position = SPAWN_PADRAO
            self._trocar_chao(self._chao_sala2)
            self.transicao_opacity = 255

        shoot_sfx  = self.audio.get("shoot")
        volume_sfx = 0.40 * volume_sons * volume_geral
        self.sala2.update(time_delta, self.player, self.space, shoot_sfx, volume_sfx)

        camera_x     = self.sala2.calcular_camera(self.player.body.position.x)
        pos_x, pos_y = self.sala2.calcular_pos_player(self.player.body.position.x, self.player.body.position.y, camera_x)
        player_hitbox = pygame.Rect(pos_x + 50, pos_y + 60, 70, 200)

        damage_sfx  = self.audio.get("damage")
        vol_damage  = 0.80 * volume_sons * volume_geral
        if self.sala2.checar_colisao_balas(player_hitbox, camera_x, damage_sfx, vol_damage):
            self.player.life -= 1

        self.player.atualizar_animacao()
        self._mover(keys)

    def _update_sala1(self, time_delta, volume_sons, volume_geral, keys):
        if self._entrou_na_sala1:
            self._entrou_na_sala1 = False
            self.audio.tocar("open_door", volume_sons, volume_geral)
            self.player.body.position = SPAWN_PADRAO
            self._trocar_chao(self._chao_sala1)
            self.transicao_opacity = 255

        volume_sfx = 0.40 * volume_sons * volume_geral
        self.sala1.update(time_delta, self.player, self.space, volume_sfx)

        camera_x     = self.sala1.calcular_camera(self.player.body.position.x)
        pos_x, pos_y = self.sala1.calcular_pos_player(self.player.body.position.x, self.player.body.position.y, camera_x)
        player_hitbox = pygame.Rect(pos_x + 50, pos_y + 60, 70, 200)

        damage_sfx  = self.audio.get("damage")
        vol_damage  = 0.80 * volume_sons * volume_geral

        self.player.atualizar_animacao()
        self._mover(keys)

    def draw(self, screen: pygame.Surface,
             click_sfx_volume: float = 1.0):
        if self.state == GameState.FASE1:
            self.fase1.draw(screen, self.player)
            self.pos_x = int(self.player.body.position.x - 110)
            self.pos_y = int(self.player.body.position.y - 235)

        elif self.state == GameState.SALAGERAL:
            click_sfx = self.audio.get("click")
            px, py = self.sala_geral.draw(screen, self.player, click_sfx=click_sfx, volume_sfx=click_sfx_volume)
            if px is not None:
                self.pos_x, self.pos_y = px, py

        elif self.state == GameState.SALA3:
            camera_x = self.sala3.calcular_camera(self.player.body.position.x)
            self.pos_x, self.pos_y = self.sala3.calcular_pos_player(self.player.body.position.x, self.player.body.position.y, camera_x)
            self.sala3.draw(screen, self.player, camera_x, self.pos_x, self.pos_y, 0)
            self.sala3.desenhar_chave(screen, self.sala_geral.sprites["chave"], camera_x)
            self.sala3.checar_saida(self.player.body.position.x, screen, self.E_gui)

        elif self.state == GameState.SALA2:
            camera_x = self.sala2.calcular_camera(self.player.body.position.x)
            self.pos_x, self.pos_y = self.sala2.calcular_pos_player(self.player.body.position.x, self.player.body.position.y, camera_x)
            self.sala2.draw(screen, self.player, camera_x, self.pos_x, self.pos_y, 0)
            self.sala2.desenhar_chave(screen, self.sala_geral.sprites["chave"], camera_x)
            self.sala2.checar_saida(self.player.body.position.x, screen, self.E_gui)

        elif self.state == GameState.SALA1:
            camera_x = self.sala1.calcular_camera(self.player.body.position.x)
            self.pos_x, self.pos_y = self.sala1.calcular_pos_player(self.player.body.position.x, self.player.body.position.y, camera_x)
            self.sala1.draw(screen, self.player, camera_x, self.pos_x, self.pos_y, 0)
            self.sala1.desenhar_chave(screen, self.sala_geral.sprites["chave"], camera_x)
            self.sala1.checar_saida(self.player.body.position.x, screen, self.E_gui)

        if self.game_over:
            texto = self.font.render("GAME OVER", True, (255, 0, 0))
            x = screen.get_width() // 2 - texto.get_width() // 2
            y = screen.get_height() // 2 - texto.get_height() // 2

            screen.blit(texto, (x, y))

            self.timer_morte -= 1

            if self.timer_morte <= 0:
                pygame.quit()
                raise SystemExit
                 
        return self.pos_x, self.pos_y

    def reset(self):
        self.player.has_tp = False
        self.player.body.position = SPAWN_FASE1
        self.player.virado = True
        self.player.life   = 3

        self.fase1.reset()
        self.sala_geral.reset()

        self._trocar_chao(self._chao_fase1)
        self.state   = GameState.FASE1
        self.pausado = False

        self._entrou_na_sala_geral   = False
        self._entrou_na_sala2        = False
        self._entrou_na_sala3        = False
        self._entrou_na_sala1        = False
        self._trocou_para_sala_geral = False
        self.transicao_opacity       = 255

        self.game_over = False
        self.timer_morte = 300
