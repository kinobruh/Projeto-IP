from __future__ import annotations
import pygame

from sala_base import SalaBase

def _criar_textos_sala_geral(font: pygame.font.Font):
    slash_name = font.render("Slash", False, (235, 52, 116))
    slash_name = pygame.transform.scale_by(slash_name, 1.5)

    return {
        "slash_name":     slash_name,
        "cutscene_fala1": font.render('Aquela deve ser a porta do escritorio do chefe.', False, "White"),
        "cutscene_fala2": font.render('Vamos checar.', False, "White"),
        "porta_fala1":    font.render('Tem 3 leitores aqui.', False, "White"),
        "porta_fala2":    font.render('Parece que voce vai precisar de 3 chaves de acesso', False, "White"),
        "porta_fala2_1":  font.render('pra conseguir abrir a porta.', False, "White"),
        "porta_fala3":    font.render('Vamos checar as outras salas.', False, "White"),
        "final_texto":    font.render('Voce entra no escritorio e asassina o chefe. Missao concluida.', False, "White"),
    }

class SalaGeral(SalaBase):
    CLAMP_MIN_X = 220
    CLAMP_MAX_X = 1230 * 2 - 70

    X_SAIDA      = 2100
    X_PORTA3_MIN = 1700
    X_PORTA3_MAX = 2100
    X_PORTA2_MIN = 1100
    X_PORTA2_MAX = 1500
    X_PORTA1_MIN = 500
    X_PORTA1_MAX = 900

    DURACAO_CUTSCENE   = 300
    DURACAO_FALA_PORTA = 300
    DURACAO_FINAL       = 300

    def __init__(self, superficie: pygame.Surface, sprites: dict, font: pygame.font.Font):
        super().__init__(superficie)
        self.sprites = sprites
        self.textos  = _criar_textos_sala_geral(font)

        self.range_porta_saida = False
        self.range_porta3      = False
        self.range_porta2      = False
        self.range_porta1      = False
        self.todas_chaves      = False
        self.checou_porta      = False

        self.em_cutscene             = True
        self.cutscene_x              = 0.0
        self.timer_cutscene          = self.DURACAO_CUTSCENE
        self.timer_cutscene_progress = self.DURACAO_CUTSCENE

        self.em_fala_porta    = False
        self.timer_fala_porta = self.DURACAO_FALA_PORTA

        self.finalizando = False
        self.timer_final = self.DURACAO_FINAL

    def iniciar_cutscene(self):
        self.em_cutscene             = True
        self.cutscene_x              = 0.0
        self.timer_cutscene          = self.DURACAO_CUTSCENE
        self.timer_cutscene_progress = self.DURACAO_CUTSCENE

    def atualizar_chaves(self, qtd_chaves):
        self.todas_chaves = (qtd_chaves == 3)

    @property
    def deve_fechar(self):
        return self.finalizando and self.timer_final <= 0

    def tentar_porta_saida(self):
        if self.finalizando:
            return True

        if self.range_porta_saida and not self.todas_chaves:
            self.em_fala_porta    = True
            self.checou_porta     = True
            self.timer_fala_porta = self.DURACAO_FALA_PORTA
            return True
        
        elif self.range_porta_saida and self.todas_chaves:
            self.finalizando = True
            self.timer_final = self.DURACAO_FINAL
            return True
        return False
    
    def tentar_porta3(self):
        return self.range_porta3 and not self.todas_chaves and self.checou_porta

    def tentar_porta2(self):
        return self.range_porta2 and not self.todas_chaves and self.checou_porta
    
    def tentar_porta1(self):
        return self.range_porta1 and not self.todas_chaves and self.checou_porta

    def reset(self):
        super().reset()
        self.range_porta_saida = False
        self.range_porta3      = False
        self.range_porta2      = False
        self.range_porta1      = False
        self.todas_chaves      = False
        self.checou_porta      = False
        self.em_cutscene             = True
        self.cutscene_x              = 0.0
        self.timer_cutscene          = self.DURACAO_CUTSCENE
        self.timer_cutscene_progress = self.DURACAO_CUTSCENE
        self.em_fala_porta    = False
        self.timer_fala_porta = self.DURACAO_FALA_PORTA
        self.finalizando = False
        self.timer_final = self.DURACAO_FINAL

    def update(self, time_delta: float, player, space):
        if self.finalizando:
            self.timer_final -= 1
            return

        if self.em_cutscene:
            self._atualizar_cutscene()
            return

        if self.em_fala_porta:
            self._atualizar_fala_porta()
            return

        player.update(space, time_delta)
        self.clamp_player(player)
        self._atualizar_ranges_portas(player.body.position.x)

    def draw(self, screen: pygame.Surface, player, camera_x: int = 0, pos_x: int = 0, pos_y: int = 0, click_sfx=None, volume_sfx: float = 1.0):

        if self.finalizando:
            screen.fill("BLACK")
            texto = self.textos["final_texto"]
            x = self.LARGURA_TELA // 2 - texto.get_width() // 2
            y = self.ALTURA_TELA  // 2 - texto.get_height() // 2
            screen.blit(texto, (x, y))
            return None, None

        if self.em_cutscene:
            self._desenhar_cutscene(screen, click_sfx, volume_sfx)
            return None, None

        camera_x = self.calcular_camera(player.body.position.x)
        pos_x, pos_y = self.calcular_pos_player(
            player.body.position.x, player.body.position.y, camera_x)

        screen.fill((0, 0, 0))
        screen.blit(self.superficie, (-camera_x, 10))
        player.draw(screen, pos_x, pos_y)

        if self.range_porta_saida:
            screen.blit(self.sprites["E_gui"], (1075, 275))

        if self.em_fala_porta:
            self._desenhar_fala_porta(screen, click_sfx, volume_sfx)

        return pos_x, pos_y

    def _atualizar_cutscene(self):
        import pytweening
        progresso = 1 - (self.timer_cutscene_progress / self.DURACAO_CUTSCENE)
        self.cutscene_x = (-self.LARGURA_TELA) * pytweening.easeOutQuart(progresso)
        self.timer_cutscene -= 1
        if self.timer_cutscene_progress > 0:
            self.timer_cutscene_progress -= 2
        if self.timer_cutscene <= 0:
            self.em_cutscene = False

    def _atualizar_fala_porta(self):
        self.timer_fala_porta -= 1
        if self.timer_fala_porta <= 0:
            self.em_fala_porta    = False
            self.timer_fala_porta = self.DURACAO_FALA_PORTA

    def _atualizar_ranges_portas(self, player_x: float):
        self.range_porta_saida = player_x > self.X_SAIDA
        self.range_porta3 = self.X_PORTA3_MIN < player_x < self.X_PORTA3_MAX
        self.range_porta2 = self.X_PORTA2_MIN <= player_x <= self.X_PORTA2_MAX
        self.range_porta1 = self.X_PORTA1_MIN <= player_x <= self.X_PORTA1_MAX
        self.range_volta  = self.range_porta_saida

    def _desenhar_cutscene(self, screen: pygame.Surface, click_sfx=None, volume_sfx: float = 1.0):
        screen.fill("BLACK")
        screen.blit(self.superficie, (self.cutscene_x, 10))
        base_x = (self.LARGURA_TELA // 2) - (self.sprites["slash_neutro"].get_width() // 2)
        screen.blit(self.sprites["slash_neutro"], (base_x, 520))
        screen.blit(self.textos["slash_name"],    (base_x + 150, 530))

        if self.timer_cutscene > 150:
            screen.blit(self.textos["cutscene_fala1"], (base_x + 150, 560))
        else:
            if self.timer_cutscene == 150 and click_sfx:
                click_sfx.set_volume(volume_sfx)
                click_sfx.play()
            screen.blit(self.textos["cutscene_fala2"], (base_x + 150, 560))

    def _desenhar_fala_porta(self, screen: pygame.Surface, click_sfx=None, volume_sfx: float = 1.0):
        timer = self.timer_fala_porta
        base_x = (self.LARGURA_TELA // 2) - (self.sprites["slash_neutro"].get_width() // 2)

        screen.blit(self.sprites["slash_neutro"], (base_x, 520))
        screen.blit(self.textos["slash_name"],    (base_x + 150, 530))

        if timer > 200:
            screen.blit(self.textos["porta_fala1"], (base_x + 150, 560))
        elif timer > 100:
            if timer == 199 and click_sfx:
                click_sfx.set_volume(volume_sfx)
                click_sfx.play()
            screen.blit(self.textos["porta_fala2"],   (base_x + 150, 560))
            screen.blit(self.textos["porta_fala2_1"], (base_x + 150, 582))
        else:
            if timer == 99 and click_sfx:
                click_sfx.set_volume(volume_sfx)
                click_sfx.play()
            screen.blit(self.textos["porta_fala3"], (base_x + 150, 560))

    def checar_saida(self, player_x: float, screen: pygame.Surface, E_gui: pygame.Surface):
        self._atualizar_ranges_portas(player_x)