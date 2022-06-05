import arcade
import random

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

        self.jogo_pausado = False
        self.disparar_projeteis = False
        self.tempo_desde_ultimo_disparo = 0
        self.tempo_espera_proximo_disparo = 10
        self.velocidade_projetil = 5

        self.arquivo_sprite_nave = "venv/Sprites/sprite_nave_espacial.png"
        self.arquivo_sprite_inimigo = "venv/Sprites/sprite_asteroide.png"
        self.arquivo_sprite_projetil = "venv/Sprites/sprite_projetil.png"

        self.jogador = arcade.Sprite(self.arquivo_sprite_nave)

        self.jogador.center_y = self.height / 2
        self.jogador.left = 10

        self.sprites.append(self.jogador)

        arcade.schedule(self.criar_inimigo, 1.0)

    def criar_inimigo(self, delta_time: float):
        inimigo = MovimentacaoInimigo(self.arquivo_sprite_inimigo)

        inimigo.left = random.randint(self.width, self.width + 10)
        inimigo.top = random.randint(10, self.height - 10)

        inimigo.velocity = (-1, 0)

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

        if simbolo == arcade.key.LEFT:
            self.jogador.change_x = -5

        if simbolo == arcade.key.RIGHT:
            self.jogador.change_x = 5

        if simbolo == arcade.key.SPACE:
            self.disparar_projeteis = True

    def on_key_release(self, simbolo, modificadores):
        if simbolo == arcade.key.UP or simbolo == arcade.key.DOWN:
            self.jogador.change_y = 0

        if simbolo == arcade.key.LEFT or simbolo == arcade.key.RIGHT:
            self.jogador.change_x = 0

        if simbolo == arcade.key.SPACE:
            self.disparar_projeteis = False

    def on_update(self, delta_time):
        if self.jogo_pausado:
            return

        self.sprites.update()

        for sprite in self.sprites:
            sprite.center_x = int(sprite.center_x + sprite.change_x * delta_time)
            sprite.center_y = int(sprite.center_y + sprite.change_y * delta_time)

        if self.tempo_desde_ultimo_disparo < self.tempo_espera_proximo_disparo:
            self.tempo_desde_ultimo_disparo += 1

        if self.disparar_projeteis and self.tempo_desde_ultimo_disparo == self.tempo_espera_proximo_disparo:
            coordenada_x = self.jogador.center_x + 10
            coordenada_y = self.jogador.center_y + 15

            self.criar_projetil(coordenada_x, coordenada_y, 3)
            self.criar_projetil(coordenada_x, coordenada_y - 30, 3)

            self.tempo_desde_ultimo_disparo = 0

        if self.jogador.top > self.height:
            self.jogador.top = self.height

        if self.jogador.right > self.width:
            self.jogador.right = self.width

        if self.jogador.bottom < 0:
            self.jogador.bottom = 0

        if self.jogador.left < 0:
            self.jogador.left = 0

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