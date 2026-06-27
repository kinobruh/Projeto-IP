#Sala base: resolvi criar uma classe base para as salas, 
# com métodos compartilhados e contrato de implementação (boa pratica e facilita  manutenção). 



from __future__ import annotations
from abc import ABC, abstractmethod
import pygame


class SalaBase(ABC):
    """Contrato e comportamentos compartilhados de todas as salas."""

    #resolução fixa do jogo
    LARGURA_TELA: int = 1280
    ALTURA_TELA: int = 720

    # Offsets de renderização do player com relação à câmera (para centralizar o sprite)
    OFFSET_CAM_X: int = 110
    OFFSET_CAM_Y: int = 235

    # Limites padrão de clamp (podem ser sobrescritos)
    CLAMP_MIN_X: int = 190
    CLAMP_MAX_X: int = 9999  # sobrescrito pelas subclasses

    def __init__(self, superficie: pygame.Surface) -> None:
        self.superficie = superficie
        self.largura: int = superficie.get_width()
        self.range_volta: bool = False

    # Esses @, são métodos abstratos que obrigam as subclasses a implementá-los, garantindo consistência
    #@abstractmethod funciona como um contrato, forçando as subclasses a implementar esses métodos
    #quando as salas herderarem a sala base, elas devem implementar esses métodos, garantindo que todas as salas tenham a mesma interface e comportamento esperado.


    @abstractmethod
    def update(self, time_delta: float, player, space) -> None:
        """Atualiza lógica da sala a cada frame."""
        ...

    @abstractmethod
    def draw(self, screen: pygame.Surface, player, camera_x: int,
             pos_x: int, pos_y: int) -> None:
        """Renderiza a sala."""
        ...

    #metodos utilitarios compartilhados entre as salas, como calcular a posição da câmera

    def calcular_camera(self, player_x: float) -> int:
        #Câmera centralizada no player, com clamp nas bordas do mapa.
        camera_x = player_x - self.LARGURA_TELA // 2
        return int(max(0, min(camera_x, self.largura - self.LARGURA_TELA)))

    def calcular_pos_player(self, player_x: float, player_y: float,
                             camera_x: int) -> tuple[int, int]:
        #Converte posição de mundo em posição de tela para o sprite.
        pos_x = int(player_x - camera_x - self.OFFSET_CAM_X)
        pos_y = int(player_y - self.OFFSET_CAM_Y)
        return pos_x, pos_y

    def clamp_player(self, player, clamp_min_x: int | None = None,
                     clamp_max_x: int | None = None) -> None:
        #Impede o player de sair dos limites da sala.
        min_x = clamp_min_x if clamp_min_x is not None else self.CLAMP_MIN_X
        max_x = clamp_max_x if clamp_max_x is not None else self.CLAMP_MAX_X
        x = max(min_x, min(player.body.position.x, max_x))
        y = max(0, min(player.body.position.y, self.ALTURA_TELA))
        player.body.position = (x, y)

    def checar_saida(self, player_x: float, screen: pygame.Surface,
                     E_gui: pygame.Surface) -> None:
       #verifica se o player está na área de saída da sala e desenha o ícone "E" na tela.
        if player_x < 400:
            screen.blit(E_gui, (140, 275))
            self.range_volta = True
        else:
            self.range_volta = False

    def reset(self) -> None:
       #Reseta estado da sala. Subclasses devem chamar super().reset().
        self.range_volta = False
