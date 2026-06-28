from __future__ import annotations
import pygame

from sala_base import SalaBase


def _criar_textos_sala_geral(font: pygame.font.Font) -> dict[str, pygame.Surface]:
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
    }


class SalaGeral(SalaBase):
    #Hub central: cutscene de entrada, portas para salas 2 e 3.

    CLAMP_MIN_X = 220
    CLAMP_MAX_X = 1230 * 2 - 70

    # Thresholds de posição para ativar portas (em coords de mundo)
    _X_SAIDA      = 2100
    _X_PORTA3_MIN = 1700
    _X_PORTA3_MAX = 2100
    _X_PORTA2_MIN = 1100
    _X_PORTA2_MAX = 1500

    # Durações em frames (a 60 fps)
    _DURACAO_CUTSCENE   = 300
    _DURACAO_FALA_PORTA = 300

    def __init__(self, superficie: pygame.Surface,
                 sprites: dict, font: pygame.font.Font) -> None:
        super().__init__(superficie)
        self.sprites = sprites
        # Textos de cutscene/porta agora são gerados aqui dentro, a partir
        # da fonte, em vez de virem prontos do main.py.
        self.textos  = _criar_textos_sala_geral(font)

        self.range_porta_saida = False
        self.range_porta3      = False
        self.range_porta2      = False
        self.todas_chaves      = False
        self.checou_porta      = False

        self.em_cutscene             = True
        self.cutscene_x              = 0.0
        self.timer_cutscene          = self._DURACAO_CUTSCENE
        self.timer_cutscene_progress = self._DURACAO_CUTSCENE

        self.em_fala_porta    = False
        self.timer_fala_porta = self._DURACAO_FALA_PORTA



    def iniciar_cutscene(self) -> None:
        self.em_cutscene             = True
        self.cutscene_x              = 0.0
        self.timer_cutscene          = self._DURACAO_CUTSCENE
        self.timer_cutscene_progress = self._DURACAO_CUTSCENE

    def tentar_porta_saida(self) -> bool:
        if self.range_porta_saida and not self.todas_chaves:
            self.em_fala_porta    = True
            self.checou_porta     = True
            self.timer_fala_porta = self._DURACAO_FALA_PORTA
            return True
        return False

    def tentar_porta3(self) -> bool:
        return self.range_porta3 and not self.todas_chaves and self.checou_porta

    def tentar_porta2(self) -> bool:
        return self.range_porta2 and not self.todas_chaves and self.checou_porta

    def reset(self) -> None:
        super().reset()
        self.range_porta_saida = False
        self.range_porta3      = False
        self.range_porta2      = False
        self.todas_chaves      = False
        self.checou_porta      = False
        self.em_cutscene             = True
        self.cutscene_x              = 0.0
        self.timer_cutscene          = self._DURACAO_CUTSCENE
        self.timer_cutscene_progress = self._DURACAO_CUTSCENE
        self.em_fala_porta    = False
        self.timer_fala_porta = self._DURACAO_FALA_PORTA

 

    def update(self, time_delta: float, player, space) -> None:
        if self.em_cutscene:
            self._atualizar_cutscene()
            return

        if self.em_fala_porta:
            self._atualizar_fala_porta()
            return

        # player.update() cuida de dash + física
        player.update(space, time_delta)
        self.clamp_player(player)
        self._atualizar_ranges_portas(player.body.position.x)

    def draw(self, screen: pygame.Surface, player,
             camera_x: int = 0, pos_x: int = 0,
             pos_y: int = 0, click_sfx=None,
             volume_sfx: float = 1.0) -> tuple[int | None, int | None]:
        
        # Renderiza a sala geral. Retorna pos_x, pos_y do player para o draw externo.
    
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

    

    def _atualizar_cutscene(self) -> None:
        import pytweening
        progresso = 1 - (self.timer_cutscene_progress / self._DURACAO_CUTSCENE)
        self.cutscene_x = (-self.LARGURA_TELA) * pytweening.easeOutQuart(progresso)
        self.timer_cutscene -= 1
        if self.timer_cutscene_progress > 0:
            self.timer_cutscene_progress -= 2
        if self.timer_cutscene <= 0:
            self.em_cutscene = False

    def _atualizar_fala_porta(self) -> None:
        self.timer_fala_porta -= 1
        if self.timer_fala_porta <= 0:
            self.em_fala_porta    = False
            self.timer_fala_porta = self._DURACAO_FALA_PORTA

    def _atualizar_ranges_portas(self, player_x: float) -> None:
        self.range_porta_saida = player_x > self._X_SAIDA
        self.range_porta3 = self._X_PORTA3_MIN < player_x < self._X_PORTA3_MAX
        self.range_porta2 = self._X_PORTA2_MIN <= player_x <= self._X_PORTA2_MAX
        self.range_volta  = self.range_porta_saida

   
    #resetar a sala geral, incluindo cutscene e fala da porta

    def _desenhar_cutscene(self, screen: pygame.Surface,
                            click_sfx=None,
                            volume_sfx: float = 1.0) -> None:
        screen.fill("BLACK")
        screen.blit(self.superficie, (self.cutscene_x, 10))
        base_x = (self.LARGURA_TELA // 2) - (self.sprites["slash_neutro"].get_width() // 2)
        screen.blit(self.sprites["slash_neutro"], (base_x, 520))
        screen.blit(self.textos["slash_name"],    (base_x + 150, 530))

        if self.timer_cutscene > 150:
            screen.blit(self.textos["cutscene_fala1"], (base_x + 150, 560))
        else:
            # Toca o click exatamente no frame em que a fala troca pra "Vamos checar."
            if self.timer_cutscene == 150 and click_sfx:
                click_sfx.set_volume(volume_sfx)
                click_sfx.play()
            screen.blit(self.textos["cutscene_fala2"], (base_x + 150, 560))

    def _desenhar_fala_porta(self, screen: pygame.Surface,
                               click_sfx=None,
                               volume_sfx: float = 1.0) -> None:
        
        sp    = self.sprites
        t     = self.textos
        timer = self.timer_fala_porta
        base_x = (self.LARGURA_TELA // 2) - (sp["slash_neutro"].get_width() // 2)

        screen.blit(sp["slash_neutro"], (base_x, 520))
        screen.blit(t["slash_name"],    (base_x + 150, 530))

        if timer > 200:
            screen.blit(t["porta_fala1"], (base_x + 150, 560))
        elif timer > 100:
            if timer == 199 and click_sfx:
                click_sfx.set_volume(volume_sfx)
                click_sfx.play()
            screen.blit(t["porta_fala2"],   (base_x + 150, 560))
            screen.blit(t["porta_fala2_1"], (base_x + 150, 582))
        else:
            if timer == 99 and click_sfx:
                click_sfx.set_volume(volume_sfx)
                click_sfx.play()
            screen.blit(t["porta_fala3"], (base_x + 150, 560))

    def checar_saida(self, player_x: float, screen: pygame.Surface,
                     E_gui: pygame.Surface) -> None:
       #Compatibilidade: atualiza range e desenha ícone E
        self._atualizar_ranges_portas(player_x)