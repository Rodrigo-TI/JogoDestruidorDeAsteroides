import arcade
import random
from datetime import datetime

largura_janela = 800
altura_janela = 600
titulo_janela = "Jogo - Destruidor de Asteróides"

class CampoCombate(arcade.Window):
    def __init__(self, largura, altura, titulo):
        super().__init__(largura, altura, titulo)

        self.sprites_inimigos = arcade.SpriteList()
        self.sprites_projeteis = arcade.SpriteList()
        self.sprites = arcade.SpriteList()

    def configurar_jogo(self):
        arcade.set_background_color(arcade.color.YELLOW_ORANGE)
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

        self.sprites.append(self.jogador)

    def criar_inimigo(self, velocidade):
        inimigo = MovimentacaoInimigo(self.arquivo_sprite_inimigo)

        inimigo.left = random.randint(self.width, self.width + 10)
        inimigo.top = random.randint(10, self.height - 10)

        inimigo.velocity = (velocidade, 0)

        self.sprites_inimigos.append(inimigo)
        self.sprites.append(inimigo)

    def criar_projetil(self, coordenada_x, coordenada_y, velocidade_projetil):
        projetil = MovimentacaoProjetil(self.arquivo_sprite_projetil, self.sprites_inimigos)

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
    def __init__(self, nome_arquivo_sprite_projetil, sprites_inimigos):
        super().__init__(nome_arquivo_sprite_projetil)

        self.sprites_inimigos = sprites_inimigos

    def update(self):
        super().update()

        if self.collides_with_list(self.sprites_inimigos) or (self.right > largura_janela):
            self.remove_from_sprite_lists()


if __name__ == "__main__":
    space_game = CampoCombate(largura_janela, altura_janela, titulo_janela)
    space_game.configurar_jogo()
    arcade.run()