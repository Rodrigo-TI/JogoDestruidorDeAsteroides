import arcade
import random
import math
from datetime import datetime
from pathlib import Path

largura_janela = 800
altura_janela = 600
titulo_janela = "Jogo - Destruidor de Asteroides"

class TelaJogo(arcade.View):
    def __init__(self):
        super().__init__()

        self.sprites_inimigos = arcade.SpriteList()
        self.sprites_projeteis = arcade.SpriteList()
        self.sprites_explosoes = arcade.SpriteList()
        self.sprites = arcade.SpriteList()

    def configurar_jogo(self):
        self.sprites_inimigos = arcade.SpriteList()
        self.sprites_projeteis = arcade.SpriteList()
        self.sprites_explosoes = arcade.SpriteList()
        self.sprites = arcade.SpriteList()

        self.camera_placar = arcade.Camera(largura_janela, altura_janela)

        arcade.set_background_color(arcade.color.BLACK)

        caminho = Path().absolute()

        self.arquivo_sprite_nave = "{}\\venv\\Sprites\\sprite_nave_espacial.png".format(caminho)
        self.arquivo_sprite_inimigo = "{}\\venv\\Sprites\\sprite_asteroide.png".format(caminho)
        self.arquivo_sprite_projetil = "{}\\venv\\Sprites\\sprite_projetil.png".format(caminho)

        self.arquivo_audio_disparo = arcade.sound.load_sound(":resources:sounds/laser2.wav")
        self.arquivo_audio_explosao = arcade.sound.load_sound(":resources:sounds/explosion2.wav")

        self.score = 0
        self.horario_inicio_fase = datetime.now()

        self.jogador = arcade.Sprite(self.arquivo_sprite_nave)
        self.jogador.center_y = altura_janela / 2
        self.jogador.left = 10

        self.horario_criacao_ultimo_inimigo = datetime.now()
        self.milissegundos_para_criacao_proximo_inimigo = 950
        self.velocidade_movimentacao_inimigo = -1

        self.disparar_projeteis = False
        self.horario_ultimo_disparo = datetime.now()
        self.milissegundos_para_proximo_disparo = 150
        self.tempo_minimo_milissegundos_para_proximo_disparo = 80
        self.velocidade_movimentacao_projetil = 3
        self.velocidade_maxima_movimentacao_projetil = 5

        self.taxa_crescimento_fumaca = 0.5
        self.taxa_espalhamento_fumaca = 7
        self.taxa_expansao_fumaca = 0.03
        self.inicio_escala_fumaca = 0.25
        self.chance_ficar_rastro_fumaca = 0.25

        self.gravidade_particula = 0.05
        self.taxa_espalhamento_particula = 8
        self.velocidade_minima_particula = 2.5
        self.faixa_velocidade_particula = 2.5
        self.quantidade_particulas = 30
        self.tamanho_particula = 3
        self.chance_particula_brilhar = 0.02
        self.lista_cores_particulas = [arcade.color.GRAY,
                                       arcade.color.YELLOW,
                                       arcade.color.ORANGE,
                                       arcade.color.HARVARD_CRIMSON]

        self.sprites.append(self.jogador)

    def criar_inimigo(self, velocidade):
        inimigo = Inimigo(self.arquivo_sprite_inimigo)

        inimigo.left = random.randint(largura_janela, largura_janela + 10)
        inimigo.top = random.randint(15, altura_janela - 55)

        inimigo.velocity = (velocidade, 0)

        self.sprites_inimigos.append(inimigo)
        self.sprites.append(inimigo)

    def criar_projetil(self, coordenada_x, coordenada_y, velocidade_projetil):
        projetil = Projetil(self)

        projetil.center_x = coordenada_x
        projetil.center_y = coordenada_y

        projetil.velocity = (velocidade_projetil, 0)

        self.sprites_projeteis.append(projetil)
        self.sprites.append(projetil)

    def on_key_press(self, tecla, modificadores):
        if tecla == arcade.key.P:
            tela_pausa = TelaPausa(self)
            self.window.show_view(tela_pausa)

        if tecla == arcade.key.UP:
            self.jogador.change_y = 5

        if tecla == arcade.key.DOWN:
            self.jogador.change_y = -5

        if tecla == arcade.key.SPACE:
            self.disparar_projeteis = True

    def on_key_release(self, simbolo, modificadores):
        if simbolo == arcade.key.UP or simbolo == arcade.key.DOWN:
            self.jogador.change_y = 0

        if simbolo == arcade.key.SPACE:
            self.disparar_projeteis = False

    def on_update(self, delta_time):
        if self.jogador.collides_with_list(self.sprites_inimigos):
            tela_game_over = TelaGameOver(self.score)
            self.window.show_view(tela_game_over)

        self.sprites.update()

        for sprite in self.sprites:
            sprite.center_x = int(sprite.center_x + sprite.change_x * delta_time)
            sprite.center_y = int(sprite.center_y + sprite.change_y * delta_time)

        milissegundos_desde_ultimo_inimigo = (datetime.now() - self.horario_criacao_ultimo_inimigo).microseconds / 1000

        if milissegundos_desde_ultimo_inimigo >= self.milissegundos_para_criacao_proximo_inimigo:
            self.criar_inimigo(self.velocidade_movimentacao_inimigo)
            self.horario_criacao_ultimo_inimigo = datetime.now()

        milissegundos_desde_ultimo_disparo = (datetime.now() - self.horario_ultimo_disparo).microseconds / 1000

        if self.disparar_projeteis and milissegundos_desde_ultimo_disparo >= self.milissegundos_para_proximo_disparo:
            coordenada_x = self.jogador.center_x + 10
            coordenada_y = self.jogador.center_y + 15

            self.criar_projetil(coordenada_x, coordenada_y, self.velocidade_movimentacao_projetil)
            arcade.sound.play_sound(self.arquivo_audio_disparo)
            self.criar_projetil(coordenada_x, coordenada_y - 30, self.velocidade_movimentacao_projetil)
            arcade.sound.play_sound(self.arquivo_audio_disparo)

            self.horario_ultimo_disparo = datetime.now()

        if self.jogador.top > altura_janela - 40:
            self.jogador.top = altura_janela - 40

        if self.jogador.bottom < 0:
            self.jogador.bottom = 0

        if (datetime.now() - self.horario_inicio_fase).seconds >= 10:
            self.milissegundos_para_criacao_proximo_inimigo = self.milissegundos_para_criacao_proximo_inimigo * 0.75
            self.velocidade_movimentacao_inimigo = self.velocidade_movimentacao_inimigo * 1.25

            if self.milissegundos_para_proximo_disparo > self.tempo_minimo_milissegundos_para_proximo_disparo:
                self.milissegundos_para_proximo_disparo = self.milissegundos_para_proximo_disparo * 0.75

            if self.velocidade_movimentacao_projetil < self.velocidade_maxima_movimentacao_projetil:
                self.velocidade_movimentacao_projetil = self.velocidade_movimentacao_projetil * 1.25

            self.horario_inicio_fase = datetime.now()

    def on_draw(self):
        arcade.start_render()

        self.sprites.draw()

        self.camera_placar.use()
        arcade.draw_text("Pontos : {}".format(self.score), 10, altura_janela - 30, arcade.csscolor.WHITE, 13)
        arcade.draw_text("P : Pause", largura_janela - 89, altura_janela - 30, arcade.csscolor.WHITE, 13)

class Inimigo(arcade.Sprite):
    def update(self):
        super().update()

        if self.right < 0:
            self.remove_from_sprite_lists()


class Projetil(arcade.Sprite):
    def __init__(self, campoCombate: TelaJogo):
        super().__init__(campoCombate.arquivo_sprite_projetil)

        self.sprites_inimigos = campoCombate.sprites_inimigos
        self.campoCombate = campoCombate

    def update(self):
        super().update()

        projetil_saiu_tela = self.right > largura_janela
        inimigos_atingidos = self.collides_with_list(self.sprites_inimigos)

        if projetil_saiu_tela:
            self.remove_from_sprite_lists()
            return

        if len(inimigos_atingidos) > 0:
            self.remove_from_sprite_lists()

            for inimigo_atingido in inimigos_atingidos:
                for i in range(self.campoCombate.quantidade_particulas):
                    particula = Particula(self.campoCombate.sprites_explosoes, self.campoCombate)
                    particula.position = inimigo_atingido.position

                    self.campoCombate.sprites_explosoes.append(particula)
                    self.campoCombate.sprites.append(particula)

                fumaca = Fumaca(50, self.campoCombate)
                fumaca.position = inimigo_atingido.position

                self.campoCombate.sprites_explosoes.append(fumaca)
                self.campoCombate.sprites.append(fumaca)

                inimigo_atingido.remove_from_sprite_lists()
                arcade.sound.play_sound(self.campoCombate.arquivo_audio_explosao)
                self.campoCombate.score += 1


class Fumaca(arcade.SpriteCircle):
    def __init__(self, tamanho, campoCombate: TelaJogo):
        super().__init__(tamanho, arcade.color.LIGHT_GRAY, soft=True)

        self.inicio_escala_fumaca = campoCombate.inicio_escala_fumaca
        self.taxa_crescimento_fumaca = campoCombate.taxa_crescimento_fumaca
        self.taxa_expansao_fumaca = self.scale
        self.campoCombate = campoCombate
        self.centro_posicao_x = self.center_x
        self.centro_posicao_y = self.center_y

    def update(self):
        if self.alpha <= self.campoCombate.taxa_espalhamento_particula:
            self.remove_from_sprite_lists()
        else:
            self.alpha -= self.campoCombate.taxa_espalhamento_fumaca
            self.centro_posicao_x += self.change_x
            self.centro_posicao_y += self.change_y
            self.taxa_expansao_fumaca += self.campoCombate.taxa_expansao_fumaca


class Particula(arcade.SpriteCircle):
    def __init__(self, lista_sprites_explosoes, campoCombate: TelaJogo):
        cor_particula = random.choice(campoCombate.lista_cores_particulas)

        super().__init__(campoCombate.tamanho_particula, cor_particula)

        self.particula_texture = self.texture
        self.lista_sprites_explosoes = lista_sprites_explosoes
        self.campoCombate = campoCombate

        velocidade = random.random() * campoCombate.faixa_velocidade_particula + campoCombate.velocidade_minima_particula
        direcao = random.randrange(360)

        self.change_x = math.sin(math.radians(direcao)) * velocidade
        self.change_y = math.cos(math.radians(direcao)) * velocidade

        self.particula_alpha = 255

        self.lista_sprites_explosoes = lista_sprites_explosoes

    def update(self):
        if self.particula_alpha <= self.campoCombate.taxa_espalhamento_particula:
            self.remove_from_sprite_lists()
        else:
            self.particula_alpha -= self.campoCombate.taxa_espalhamento_particula
            self.alpha = self.particula_alpha
            self.center_x += self.change_x
            self.center_y += self.change_y
            self.change_y -= self.campoCombate.gravidade_particula

            if random.random() <= self.campoCombate.chance_particula_brilhar:
                self.alpha = 255
                self.texture = arcade.make_circle_texture(int(self.width), arcade.color.WHITE)
            else:
                self.texture = self.particula_texture

            if random.random() <= self.campoCombate.chance_ficar_rastro_fumaca:
                fumaca = Fumaca(5, self.campoCombate)
                fumaca.position = self.position
                self.lista_sprites_explosoes.append(fumaca)


class TelaGameOver(arcade.View):
    def __init__(self, pontuacao):
        super().__init__()
        self.pontuacao = pontuacao

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        arcade.set_viewport(0, largura_janela, 0, altura_janela)

    def on_draw(self):
        self.clear()
        arcade.draw_text("GAME OVER",
                         self.window.width / 2,
                         self.window.height - 100,
                         arcade.color.WHITE,
                         font_size=50,
                         anchor_x="center")

        arcade.draw_text("Pontuação : {}".format(self.pontuacao),
                         self.window.width / 2,
                         self.window.height - 250,
                         arcade.color.WHITE,
                         font_size=25,
                         anchor_x="center")

        arcade.draw_text("Pressione ENTER para jogar novamente",
                         self.window.width / 2,
                         self.window.height - 500,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")

        arcade.draw_text("Pressione Q para fechar o jogo",
                         self.window.width / 2,
                         self.window.height - 540,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")

    def on_key_press(self, tecla, modificadores):
        if tecla == arcade.key.ENTER:
            tela_jogo = TelaJogo()
            tela_jogo.configurar_jogo()
            self.window.show_view(tela_jogo)

        if tecla == arcade.key.Q:
            tela_inicial = TelaInicial()
            self.window.show_view(tela_inicial)


class TelaPausa(arcade.View):
    def __init__(self, tela_jogo):
        super().__init__()
        self.tela_jogo = tela_jogo

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        arcade.set_viewport(0, largura_janela, 0, altura_janela)

    def on_draw(self):
        self.clear()
        arcade.draw_text("JOGO PAUSADO",
                         self.window.width / 2,
                         self.window.height - 100,
                         arcade.color.WHITE,
                         font_size=50,
                         anchor_x="center")

        arcade.draw_text("CONTROLES",
                         self.window.width / 2,
                         self.window.height - 180,
                         arcade.color.WHITE,
                         font_size=25,
                         anchor_x="center")

        arcade.draw_text("Espaço{}Atirar".format("." * 58),
                         80,
                         self.window.height - 240,
                         arcade.color.WHITE,
                         font_size=20)

        arcade.draw_text("Seta para cima{}Subir a nave".format("." * 36),
                         80,
                         self.window.height - 280,
                         arcade.color.WHITE,
                         font_size=20)

        arcade.draw_text("Seta para baixo{}Descer a nave".format("." * 32),
                         80,
                         self.window.height - 320,
                         arcade.color.WHITE,
                         font_size=20)

        arcade.draw_text("Pressione P para voltar ao jogo",
                         self.window.width / 2,
                         self.window.height - 500,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")

        arcade.draw_text("Pressione Q para sair do jogo",
                         self.window.width / 2,
                         self.window.height - 540,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")

    def on_key_press(self, tecla, modificadores):
        if tecla == arcade.key.P:
            self.window.show_view(self.tela_jogo)

        if tecla == arcade.key.Q:
            tela_inicial = TelaInicial()
            self.window.show_view(tela_inicial)


class TelaInicial(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        arcade.set_viewport(0, largura_janela, 0, altura_janela)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Destruidor de",
                         self.window.width / 2,
                         self.window.height - 150,
                         arcade.color.WHITE,
                         font_size=50,
                         anchor_x="center")

        arcade.draw_text("Asteroides",
                         self.window.width / 2,
                         self.window.height - 230,
                         arcade.color.WHITE,
                         font_size=50,
                         anchor_x="center")

        arcade.draw_text("Pressione ENTER para jogar",
                         self.window.width / 2,
                         self.window.height - 500,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")

        arcade.draw_text("Pressione Q para fechar o jogo",
                         self.window.width / 2,
                         self.window.height - 540,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")

    def on_key_press(self, tecla, modificadores):
        if tecla == arcade.key.ENTER:
            tela_jogo = TelaJogo()
            tela_jogo.configurar_jogo()
            self.window.show_view(tela_jogo)

        if tecla == arcade.key.Q:
            self.window.close()


if __name__ == "__main__":
    janela = arcade.Window(largura_janela, altura_janela, titulo_janela)
    tela_inicial = TelaInicial()
    janela.show_view(tela_inicial)
    arcade.run()