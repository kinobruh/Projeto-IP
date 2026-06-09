import pygame

class Spritesheet():
    def __init__(self, image):
        self.sheet = image.convert_alpha()

    def get_image(self, frame, row, width, height, scale, color):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (frame * width, row * height, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(color)
        return image
    
    def get_animation(self, row, num_frames, width, height, scale, color):
        frames = []

        for frame in range(num_frames):
            image = self.get_image(frame, row, width, height, scale, color)
            frames.append(image)
        return frames