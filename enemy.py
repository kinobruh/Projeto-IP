from __future__ import annotations
import random
import pygame
import pytweening


class Bullet:
    #bala disparada

    def __init__(self, x: float, y: float, direcao: int, sprite: pygame.Surface, velocidade: float = 650):
        self.x          = x
        self.y          = y
        self.direcao    = direcao
        self.velocidade = velocidade
        self.vivo       = True

        self.sprite_original = sprite
        self.largura = sprite.get_width()
        self.altura  = sprite.get_height()
        self.sprite  = (pygame.transform.flip(sprite, True, False) if direcao < 0 else sprite)

    def update(self, time_delta: float):
        self.x += self.velocidade * self.direcao * time_delta

    def get_rect(self, camera_x: float = 0):
        return pygame.Rect(
            self.x - camera_x - self.largura // 2,
            self.y - self.altura // 2,
            self.largura,
            self.altura,
        )

    def draw(self, screen: pygame.Surface, camera_x: float = 0):
        screen.blit(self.sprite, self.get_rect(camera_x).topleft)


class Enemy:
    #inimigo que atira e flutua

    def __init__(
        self,
        x: float,
        y: float,
        patrulha_min: float,
        patrulha_max: float,
        velocidade_patrulha: float = 120,
        alcance_visao: float = 550,
        tolerancia_y: float = 260,
        cooldown_tiro: float = 1.5,
        sprite: pygame.Surface | None = None,
        bullet_sprite: pygame.Surface | None = None,
        altura_flutuacao: float = 70,
        amplitude_flutuacao: float = 18,
        velocidade_flutuacao: float = 1.6,
        distancia_recoil: float = 22,
        duracao_recoil: float = 0.18,
    ):
        self.x = x
        self.y = y
        self.patrulha_min = patrulha_min
        self.patrulha_max = patrulha_max
        self.velocidade_patrulha  = velocidade_patrulha
        self.alcance_visao        = alcance_visao
        self.tolerancia_y         = tolerancia_y
        self.cooldown_tiro        = cooldown_tiro

        self.sprite_original = sprite
        self.LARGURA: int = sprite.get_width()
        self.ALTURA:  int = sprite.get_height()
        self.bullet_sprite = bullet_sprite

        #Estado
        self.direcao_patrulha = 1
        self.virado           = True
        self.estado           = "patrulhando"
        self.tiro_timer       = 0.0
        self.vivo             = True
        self.life             = 3
        self.bullets: list[Bullet] = []

        self.tempo_alerta     = 0.0
        self.tempo_alerta_max = 0.08

        #Flutuação
        self.altura_flutuacao    = altura_flutuacao
        self.amplitude_flutuacao = amplitude_flutuacao
        self.velocidade_flutuacao = velocidade_flutuacao
        self.flutuacao_t         = random.uniform(0, 2.0)
        self.flutuacao_offset    = 0.0

        #Recoil ao disparar
        self.distancia_recoil = distancia_recoil
        self.duracao_recoil   = duracao_recoil
        self.em_recoil        = False
        self.recoil_t         = 0.0
        self.recoil_offset    = 0.0

    def update(self, time_delta: float, player_x: float, player_y: float, sfx_tiro: pygame.mixer.Sound | None = None, volume_sfx: float = 1.0):
        if not self.vivo:
            return

        if self._ve_o_player(player_x, player_y):
            self._reagir_ao_player(time_delta, player_x, sfx_tiro, volume_sfx)
        else:
            if self.estado == "atirando":
                self.estado = "patrulhando"
            self._patrulhar(time_delta)

        self._atualizar_flutuacao(time_delta)
        self._atualizar_recoil(time_delta)

        for bullet in self.bullets:
            bullet.update(time_delta)
        self.bullets = [
            b for b in self.bullets
            if abs(b.x - self.x) < self.alcance_visao + 400
        ]

    def _ve_o_player(self, player_x: float, player_y: float):
        dist_y = abs(player_y - self.y)
        if dist_y > self.tolerancia_y:
            return False
        return abs(player_x - self.x) <= self.alcance_visao

    def _reagir_ao_player(self, time_delta: float, player_x: float,
                           sfx_tiro, volume_sfx: float) -> None:
        self.virado = player_x > self.x
        if self.estado == "patrulhando":
            self.estado       = "atirando"
            self.tempo_alerta = 0.0
            self.tiro_timer   = 0.0
        elif self.estado == "atirando":
            self.tempo_alerta += time_delta
            if self.tempo_alerta >= self.tempo_alerta_max:
                self.tiro_timer += time_delta
                if self.tiro_timer >= self.cooldown_tiro:
                    self.tiro_timer = 0.0
                    self._disparar(sfx_tiro, volume_sfx)

    def _patrulhar(self, time_delta: float) -> None:
        self.x += self.velocidade_patrulha * self.direcao_patrulha * time_delta
        if self.x >= self.patrulha_max:
            self.x = self.patrulha_max
            self.direcao_patrulha = -1
            self.virado = False
        elif self.x <= self.patrulha_min:
            self.x = self.patrulha_min
            self.direcao_patrulha = 1
            self.virado = True

    def _atualizar_flutuacao(self, time_delta: float) -> None:
        if self.em_recoil:
            return
        self.flutuacao_t += time_delta * self.velocidade_flutuacao
        ciclo = self.flutuacao_t % 2.0
        progresso = (pytweening.easeInOutSine(ciclo)
                     if ciclo <= 1.0
                     else pytweening.easeInOutSine(2.0 - ciclo))
        self.flutuacao_offset = (progresso - 0.5) * 2 * self.amplitude_flutuacao

    def _atualizar_recoil(self, time_delta: float) -> None:
        if not self.em_recoil:
            self.recoil_offset = 0.0
            return

        self.recoil_t += time_delta
        progresso = min(1.0, self.recoil_t / self.duracao_recoil)
        direcao_recoil = -1 if self.virado else 1

        if progresso < 0.5:
            curva = pytweening.easeOutQuad(progresso / 0.5)
            self.recoil_offset = direcao_recoil * self.distancia_recoil * curva
        else:
            curva = pytweening.easeOutQuad((progresso - 0.5) / 0.5)
            self.recoil_offset = direcao_recoil * self.distancia_recoil * (1 - curva)

        if progresso >= 1.0:
            self.em_recoil    = False
            self.recoil_t     = 0.0
            self.recoil_offset = 0.0

    def _disparar(self, sfx_tiro, volume_sfx: float) -> None:
        direcao  = 1 if self.virado else -1
        origem_x = self.x + self.recoil_offset
        origem_y = self.y - self.altura_flutuacao + self.flutuacao_offset
        bullet_x = origem_x + (self.LARGURA // 2) * direcao
        bullet_y = origem_y - self.ALTURA * 0.45
        self.bullets.append(Bullet(bullet_x, bullet_y, direcao, self.bullet_sprite))

        if sfx_tiro is not None:
            sfx_tiro.set_volume(volume_sfx)
            sfx_tiro.play()

        self.em_recoil = True
        self.recoil_t  = 0.0


    def levar_dano(self, quantidade: int = 1) -> None:
        self.life -= quantidade
        if self.life <= 0:
            self.vivo = False

    def get_rect(self, camera_x: float = 0) -> pygame.Rect:
        return pygame.Rect(
            self.x - camera_x - self.LARGURA // 2,
            self.y - self.altura_flutuacao - self.ALTURA,
            self.LARGURA,
            self.ALTURA,
        )

    def get_visual_rect(self, camera_x: float = 0) -> pygame.Rect:
        desenho_x = self.x + self.recoil_offset
        desenho_y = self.y - self.altura_flutuacao + self.flutuacao_offset
        return pygame.Rect(
            desenho_x - camera_x - self.LARGURA // 2,
            desenho_y - self.ALTURA,
            self.LARGURA,
            self.ALTURA,
        )

    def draw(self, screen: pygame.Surface, camera_x: float = 0) -> None:
        if not self.vivo:
            return
        rect   = self.get_visual_rect(camera_x)
        imagem = self.sprite_original
        if self.virado:
            imagem = pygame.transform.flip(imagem, True, False)
        screen.blit(imagem, rect.topleft)
        for bullet in self.bullets:
            bullet.draw(screen, camera_x)
