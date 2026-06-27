from __future__ import annotations
import pygame


class Spritesheet:
    """Carrega e fatia uma spritesheet em frames individuais."""

    def __init__(self, image: pygame.Surface) -> None:
        self.sheet = image.convert_alpha()

    def get_image(self, frame: int, row: int, width: int, height: int,
                  scale: float, color: tuple) -> pygame.Surface:
        """Extrai um único frame."""
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0),
                   (frame * width, row * height, width, height))
        image = pygame.transform.scale(image,
                                       (int(width * scale), int(height * scale)))
        image.set_colorkey(color)
        return image

    def get_animation(self, row: int, num_frames: int, width: int,
                      height: int, scale: float,
                      color: tuple) -> list[pygame.Surface]:
        """Extrai todos os frames de uma linha como lista."""
        return [
            self.get_image(frame, row, width, height, scale, color)
            for frame in range(num_frames)
        ]
