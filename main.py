import pygame
import sys

# Adiciona a pasta /src/ pro PYTHONPATH
sys.path.append("src/")

# Importa todo o pacote de src/
from src import *


# Define caminho de todas as pastas que usaremos
ASSET_PATH = "assets/"
TEXTURE_PATH = ASSET_PATH + "textures/"
MUSIC_PATH = ASSET_PATH + "music/"
SOUNDS_PATH = ASSET_PATH + "sounds/"
FONTS_PATH = ASSET_PATH + "fonts/"

# Tamanho da tela
WIDTH = 1000
HEIGHT = 750

# Tamanho do tabuleiro
GRID_X = 750
GRID_Y = 750

# Tamanho da moto
RIDER_X = 50
RIDER_Y = 25

# Tamanho da carta
CARD_X = 150
CARD_Y = 100

# Inicializa
pygame.init()

# Cria algumas configurações do display   
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vectrun")
pygame.display.set_icon(pygame.image.load(TEXTURE_PATH + "icon.png"))

# Cria o relógio interno do FPS
fps_clock = pygame.time.Clock()

# Grid_Game já cria todos objetos internamente (jogador, bots, cartas)
grid_game = game.Grid_Game(TEXTURE_PATH + "grid.png", (0, 0), (GRID_X, GRID_Y), 1)

# Loop do jogo
while True:
    # Aqui vão ser atualizados os menus (que atualizam tudo)
    grid_game.update()

    # Faz blit no tabuleiro e nas linhas
    screen.blit(grid_game.image, grid_game.rect)
    for bot in grid_game._bots.sprites():
        pygame.draw.lines(screen, bot._color, False, bot._path, width=6)

    pygame.draw.lines(screen, grid_game._player.sprite._color, False, grid_game._player.sprite._path, width=6)

    # Faz blit no jogador e nos bots
    grid_game._player.draw(screen)
    grid_game._bots.draw(screen)

    # Enfim atualiza o display
    pygame.display.update()
    fps_clock.tick(30)
