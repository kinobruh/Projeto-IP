from __future__ import annotations
import pygame

from sala_base import SalaBase


class Sala1(SalaBase):

    CLAMP_MIN_X = 190
    def __init__(self, superficie: pygame.Surface, sprite_raio: pygame.Surface):
        super().__init__(superficie)
        self.CLAMP_MAX_X = self.largura - 70
        
        self.sprite_raio = sprite_raio
        self.booster_x = self.largura // 2  # meio da sala
        
        #altura
        self.booster_y = 450
        
        self.booster_largura = self.sprite_raio.get_width()
        self.booster_altura = self.sprite_raio.get_height()
        self.booster_coletado = False

    def update(self, time_delta: float, player, space, volume_sfx: float = 1.0):
        player.update(space, time_delta)
        self.clamp_player(player)

        #colisao
        if not self.booster_coletado:
            booster_rect = pygame.Rect(
                self.booster_x - self.booster_largura // 2,
                self.booster_y - self.booster_altura // 2,
                self.booster_largura,
                self.booster_altura
            )
            
            player_rect = pygame.Rect(
                player.body.position.x - 48,
                player.body.position.y - 160,
                96,
                320
            )
            
            #tempo de duração
            if player_rect.colliderect(booster_rect):
                self.booster_coletado = True
                player.booster_ativo = True
                player.booster_timer = 5.0  

    def draw(self, screen: pygame.Surface, player, camera_x: int, pos_x: int, pos_y: int, time_delta: float = 0):
        screen.fill((0, 0, 0))
        screen.blit(self.superficie, (-camera_x, 10))
        
        if not self.booster_coletado:
            x_tela = (self.booster_x - self.booster_largura // 2) - camera_x
            y_tela = self.booster_y - self.booster_altura // 2
            
            screen.blit(self.sprite_raio, (x_tela, y_tela))

        player.draw(screen, pos_x, pos_y)

    def checar_saida(self, player_x: float, screen: pygame.Surface, E_gui: pygame.Surface):
        super().checar_saida(player_x, screen, E_gui)