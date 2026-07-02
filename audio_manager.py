#o audio manager é responsável por gerenciar os efeitos sonoros do jogo
#permitindo tocar sons com volumes ajustados de acordo com o volume geral e o volume específico de cada efeito
#ele utiliza um dicionário para armazenar os sons e seus volumes base, e fornece métodos para tocar sons pelo nome ou 
#diretamente por um objeto Sound.

# um objeto é uma instância de uma classe, que possui atributos e métodos definidos pela classe

from __future__ import annotations
import pygame

# Volume base de cada SFX (0.0 – 1.0).
# Ajuste aqui para balancear sem tocar em nenhuma sala.
_VOLUMES_BASE: dict[str, float] = {
    "open_door": 0.25,
    "shoot":     0.40,
    "damage":    0.80,
    "click":     0.15,
    "dash1":     0.10,
    "dash2":     0.10,
    "hover":     1.50,
    "press":     0.35,
}

class AudioManager:
    #Gerencia SFX com volume relativo ao master e ao canal de sons.
    def __init__(self, sons: dict[str, pygame.mixer.Sound]):
        self._sons = sons

    def tocar(self, nome: str, volume_sons: float = 1.0, volume_geral: float = 1.0):
        #reproduz um SFX com volume = base * volume_sons * volume_geral.
        sfx = self._sons.get(nome)
        if sfx is None:
            return
        base = _VOLUMES_BASE.get(nome, 1.0)
        sfx.set_volume(base * volume_sons * volume_geral)
        sfx.play()

    def tocar_sfx_direto(self, sfx: pygame.mixer.Sound, nome: str, volume_sons: float = 1.0, volume_geral: float = 1.0):
        #reproduz um objeto Sound avulso usando o volume base pelo nome.
        sfx.set_volume(base * volume_sons * volume_geral)
        sfx.play()

    def get(self, nome: str):
        return self._sons.get(nome)