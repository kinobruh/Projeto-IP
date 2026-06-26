import pygame
import pytweening


class SalaGeral:
    LARGURA_TELA = 1280
    ALTURA_TELA  = 720

    CLAMP_MIN_X = 220
    CLAMP_MAX_X = 1230 * 2 - 70

    RANGE_SAIDA_X      = 2100
    RANGE_PORTA3_MIN   = 1700
    RANGE_PORTA3_MAX   = 2100
    RANGE_PORTA2_MIN   = 1100
    RANGE_PORTA2_MAX   = 1500

    DURACAO_CUTSCENE      = 300
    DURACAO_FALA_PORTA    = 300

    def __init__(self, superficie, sprites, textos):

        self.superficie = superficie
        self.sprites    = sprites
        self.textos     = textos
        self.largura    = superficie.get_width()

        self.range_volta = False

        self.range_porta_saida = False
        self.range_porta3      = False
        self.range_porta2      = False

        self.todas_chaves = False
        self.checou_porta = False

        self.em_cutscene           = True
        self.cutscene_x            = 0
        self.timer_cutscene        = self.DURACAO_CUTSCENE
        self.timer_cutscene_progress = self.DURACAO_CUTSCENE

        self.em_fala_porta  = False
        self.timer_fala_porta = self.DURACAO_FALA_PORTA


    def reset(self):
        self.range_volta       = False
        self.range_porta_saida = False
        self.range_porta3      = False
        self.range_porta2      = False
        self.todas_chaves      = False
        self.checou_porta      = False

        self.em_cutscene             = True
        self.cutscene_x              = 0
        self.timer_cutscene          = self.DURACAO_CUTSCENE
        self.timer_cutscene_progress = self.DURACAO_CUTSCENE

        self.em_fala_porta   = False
        self.timer_fala_porta = self.DURACAO_FALA_PORTA

    def iniciar_cutscene(self):
        self.em_cutscene             = True
        self.cutscene_x              = 0
        self.timer_cutscene          = self.DURACAO_CUTSCENE
        self.timer_cutscene_progress = self.DURACAO_CUTSCENE

    def calcular_camera(self, player_x):
        camera_x = player_x - self.LARGURA_TELA // 2
        return max(0, min(camera_x, self.largura - self.LARGURA_TELA))

    def tentar_porta_saida(self) -> bool:
        if self.range_porta_saida and not self.todas_chaves:
            self.em_fala_porta   = True
            self.checou_porta    = True
            self.timer_fala_porta = self.DURACAO_FALA_PORTA
            return True
        return False

    def tentar_porta3(self) -> bool:
        return self.range_porta3 and not self.todas_chaves and self.checou_porta

    def tentar_porta2(self) -> bool:
        return self.range_porta2 and not self.todas_chaves and self.checou_porta

    def update(self, time_delta, player, space):
        if self.em_cutscene:
            self._atualizar_cutscene()
            return

        if self.em_fala_porta:
            self._atualizar_fala_porta()
            return

        # estado do player
        vx, vy = player.body.velocity
        if vx == 0 and vy == 0:
            player.estado = "Idle"
        elif vy == 0 and vx != 0:
            player.estado = "Walking"

        # dash
        if player.dashing:
            dash_progress = pytweening.easeOutQuart(player.dash_t)
            new_x = player.dash_inicial + (player.dash_final - player.dash_inicial) * dash_progress
            player.body.position = (new_x, player.body.position.y)
            player.body.velocity = (0, player.body.velocity.y)
            player.dash_t += time_delta / player.dash_duration
            if player.dash_t >= 1:
                player.dash_t = 1
                player.dashing = False

        space.step(1 / 60)

        x = max(self.CLAMP_MIN_X, min(player.body.position.x, self.CLAMP_MAX_X))
        y = max(0, min(player.body.position.y, self.ALTURA_TELA))
        player.body.position = (x, y)

        self._atualizar_ranges_portas(player.body.position.x)

    def _atualizar_cutscene(self):
        progresso = 1 - (self.timer_cutscene_progress / self.DURACAO_CUTSCENE)
        self.cutscene_x = 0 + (-self.LARGURA_TELA - 0) * pytweening.easeOutQuart(progresso)

        self.timer_cutscene -= 1
        if self.timer_cutscene_progress > 0:
            self.timer_cutscene_progress -= 2
        if self.timer_cutscene <= 0:
            self.em_cutscene = False

    def _atualizar_fala_porta(self):
        self.timer_fala_porta -= 1
        if self.timer_fala_porta <= 0:
            self.em_fala_porta   = False
            self.timer_fala_porta = self.DURACAO_FALA_PORTA

    def _atualizar_ranges_portas(self, player_x):
        self.range_porta_saida = player_x > self.RANGE_SAIDA_X

        self.range_porta3 = self.RANGE_PORTA3_MIN < player_x < self.RANGE_PORTA3_MAX

        self.range_porta2 = self.RANGE_PORTA2_MIN <= player_x <= self.RANGE_PORTA2_MAX

        self.range_volta = self.range_porta_saida

    def draw(self, screen, player, click_sfx, volume_sfx):
        if self.em_cutscene:
            self._desenhar_cutscene(screen)
            return None, None

        camera_x = self.calcular_camera(player.body.position.x)
        pos_x = player.body.position.x - camera_x - 110
        pos_y = player.body.position.y - 235

        screen.fill((0, 0, 0))
        screen.blit(self.superficie, (-camera_x, 10))

        player.draw(screen, pos_x, pos_y)

        if self.range_porta_saida:
            screen.blit(self.sprites["E_gui"], (1075, 275))
        if self.range_porta2:
            screen.blit(self.sprites["E_gui"], (pos_x + 40, 275))

        if self.em_fala_porta:
            self._desenhar_fala_porta(screen, click_sfx, volume_sfx)

        return pos_x, pos_y

    def _desenhar_cutscene(self, screen):
        sp = self.sprites
        t  = self.textos

        screen.fill("BLACK")
        screen.blit(self.superficie, (self.cutscene_x, 10))

        base_x = (self.LARGURA_TELA // 2) - (sp["slash_neutro"].get_width() // 2)
        screen.blit(sp["slash_neutro"], (base_x, 520))
        screen.blit(t["slash_name"], (base_x + 150, 530))

        if self.timer_cutscene > 150:
            screen.blit(t["cutscene_fala1"], (base_x + 150, 560))
        else:
            screen.blit(t["cutscene_fala2"], (base_x + 150, 560))

    def _desenhar_fala_porta(self, screen, click_sfx, volume_sfx):
        sp = self.sprites
        t  = self.textos
        base_x = (self.LARGURA_TELA // 2) - (sp["slash_neutro"].get_width() // 2)

        screen.blit(sp["slash_neutro"], (base_x, 520))
        screen.blit(t["slash_name"], (base_x + 150, 530))

        timer = self.timer_fala_porta
        if timer > 200:
            screen.blit(t["porta_fala1"], (base_x + 150, 560))
        elif 200 > timer > 100:
            if timer == 199:
                click_sfx.set_volume(volume_sfx)
                click_sfx.play()
            screen.blit(t["porta_fala2"],   (base_x + 150, 560))
            screen.blit(t["porta_fala2_1"], (base_x + 150, 582))
        elif 100 > timer > 0:
            if timer == 99:
                click_sfx.set_volume(volume_sfx)
                click_sfx.play()
            screen.blit(t["porta_fala3"], (base_x + 150, 560))

    def checar_saida(self, player_x, screen, E_gui):
        self.range_porta_saida = player_x > self.RANGE_SAIDA_X
        self.range_volta = self.range_porta_saida
        if self.range_porta_saida:
            screen.blit(E_gui, (1075, 275))