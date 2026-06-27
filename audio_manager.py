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
    """Gerencia SFX com volume relativo ao master e ao canal de sons."""

    def __init__(self, sons: dict[str, pygame.mixer.Sound]) -> None:
        self._sons = sons

    def tocar(self, nome: str, volume_sons: float = 1.0,
              volume_geral: float = 1.0) -> None:
        """Reproduz um SFX com volume = base * volume_sons * volume_geral."""
        sfx = self._sons.get(nome)
        if sfx is None:
            return
        base = _VOLUMES_BASE.get(nome, 1.0)
        sfx.set_volume(base * volume_sons * volume_geral)
        sfx.play()

    def tocar_sfx_direto(self, sfx: pygame.mixer.Sound, nome: str,
                          volume_sons: float = 1.0,
                          volume_geral: float = 1.0) -> None:
        """Reproduz um objeto Sound avulso usando o volume base pelo nome."""
        base = _VOLUMES_BASE.get(nome, 1.0)
        sfx.set_volume(base * volume_sons * volume_geral)
        sfx.play()

    def get(self, nome: str) -> pygame.mixer.Sound | None:
        return self._sons.get(nome)
