import arcade
import random
import math
from datetime import datetime

largura_janela = 800
altura_janela = 600
titulo_janela = "Jogo - Destruidor de Asteróides"

class CampoCombate(arcade.Window):
    def __init__(self, largura, altura, titulo):
        super().__init__(largura, altura, titulo)

        self.sprites_inimigos = arcade.SpriteList()
        self.sprites_projeteis = arcade.SpriteList()
        self.sprites_explosoes = arcade.SpriteList()
        self.sprites = arcade.SpriteList()

    def configurar_jogo(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.arquivo_sprite_nave = "venv/Sprites/sprite_nave_espacial.png"
        self.arquivo_sprite_inimigo = "venv/Sprites/sprite_asteroide.png"
        self.arquivo_sprite_projetil = "venv/Sprites/sprite_projetil.png"

        self.horario_inicio_fase = datetime.now()
        self.jogo_pausado = False

        self.jogador = arcade.Sprite(self.arquivo_sprite_nave)
        self.jogador.center_y = self.height / 2
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
        self.quantidade_particulas = 20
        self.tamanho_particula = 3
        self.chance_particula_brilhar = 0.02
        self.lista_cores_particulas = [arcade.color.GRAY,
                                       arcade.color.YELLOW,
                                       arcade.color.ORANGE,
                                       arcade.color.HARVARD_CRIMSON]

        self.sprites.append(self.jogador)

    def criar_inimigo(self, velocidade):
        inimigo = MovimentacaoInimigo(self.arquivo_sprite_inimigo)

        inimigo.left = random.randint(self.width, self.width + 10)
        inimigo.top = random.randint(10, self.height - 10)

        inimigo.velocity = (velocidade, 0)

        self.sprites_inimigos.append(inimigo)
        self.sprites.append(inimigo)

    def criar_projetil(self, coordenada_x, coordenada_y, velocidade_projetil):
        projetil = MovimentacaoProjetil(self)

        projetil.center_x = coordenada_x
        projetil.center_y = coordenada_y

        projetil.velocity = (velocidade_projetil, 0)

        self.sprites_projeteis.append(projetil)
        self.sprites.append(projetil)

    def on_key_press(self, simbolo, modificadores):
        if simbolo == arcade.key.Q:
            arcade.close_window()

        if simbolo == arcade.key.P:
            self.jogo_pausado = not self.jogo_pausado

        if simbolo == arcade.key.UP:
            self.jogador.change_y = 5

        if simbolo == arcade.key.DOWN:
            self.jogador.change_y = -5

        if simbolo == arcade.key.SPACE:
            self.disparar_projeteis = True

    def on_key_release(self, simbolo, modificadores):
        if simbolo == arcade.key.UP or simbolo == arcade.key.DOWN:
            self.jogador.change_y = 0

        if simbolo == arcade.key.SPACE:
            self.disparar_projeteis = False

    def on_update(self, delta_time):
        if self.jogo_pausado:
            return

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
            self.criar_projetil(coordenada_x, coordenada_y - 30, self.velocidade_movimentacao_projetil)

            self.horario_ultimo_disparo = datetime.now()

        if self.jogador.top > self.height:
            self.jogador.top = self.height

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


class MovimentacaoInimigo(arcade.Sprite):
    def update(self):
        super().update()

        if self.right < 0:
            self.remove_from_sprite_lists()


class MovimentacaoProjetil(arcade.Sprite):
    def __init__(self, campoCombate: CampoCombate):
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


class Fumaca(arcade.SpriteCircle):
    def __init__(self, tamanho, campoCombate: CampoCombate):
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
    def __init__(self, lista_sprites_explosoes, campoCombate: CampoCombate):
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


if __name__ == "__main__":
    space_game = CampoCombate(largura_janela, altura_janela, titulo_janela)
    space_game.configurar_jogo()
    arcade.run()