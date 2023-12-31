import pygame

from menu import *
from game import *
from deck import *
from config import *


class StateControl():
    def __init__(self):
        # Iniciação das variáveis de controle
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY = False, False, False, False, False
        self.BUTTON_CLICKED = False
        self.first_time = True

        # Cria a tela do jogo
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Vectrun")
        pygame.display.set_icon(pygame.image.load(TEXTURE_PATH + "icon.png"))
        
        # Cria o relógio interno do FPS
        self.fps_clock = pygame.time.Clock()

        # Cria um objeto para cada uma das telas
        self.main_menu = MainMenu(self, (TEXTURE_MENU_PATH + "vectrun_logo.png"), (WIDTH/2, HEIGHT/5), (LOGO_X, LOGO_Y))
        self.options_menu = OptionsMenu(self, (TEXTURE_MENU_PATH + "options_button.png"), (WIDTH / 2, (HEIGHT / 6 - 50)), (2 * BUTTON_X, 2 * BUTTON_Y))
        self.credits_menu = CreditsMenu(self, (TEXTURE_MENU_PATH + "credits_button.png"), (WIDTH / 2, (HEIGHT / 6 - 50)), (2 * BUTTON_X, 2 * BUTTON_Y))

        # Cria a tela de vitória e derrota
        self.win_screen = ResultScreen(self, (TEXTURE_MENU_PATH + "you_win.png"), (WIDTH/2, HEIGHT/5), (LOGO_X,LOGO_Y))
        self.lose_screen = ResultScreen(self, (TEXTURE_MENU_PATH + "you_lose.png"), (WIDTH/2, HEIGHT/5), (LOGO_X,LOGO_Y))
        self.winner = 0

        # Tela do tutorial
        self.tutorial_screen = TutorialScreen(self, (TEXTURE_MENU_PATH + "tutorial_text.png"), (WIDTH / 2, HEIGHT / 6 - 50), (2 * BUTTON_X, 2 * BUTTON_Y))

        # Define a tela inicial
        self.curr_menu = self.main_menu

        # Carrega a música pra memória
        self.volume = VOLUME_START
        self.__change_music("title.ogg", self.volume)

        # Holder pro jogo: só será criado de fato quando começar a partida
        self.game_run = None

    def game_loop(self):
        # Muda a música e cria o jogo
        self.__change_music("grid_1.ogg", self.volume)
        pygame.mixer.music.play(-1, 0, 2)

        self.game_run = GridGame(TEXTURE_PATH + "grid.png", (0, 0), (GRID_X, GRID_Y), 3, self.volume, self)

        # Loop principal
        while self.playing:
            # Preenche a tela
            self.screen.fill(BLACK)

            # Atualiza e exibe o jogo na tela
            self.game_run.update()
            self.game_run.draw(self.screen)

            # Enfim mostra o diplay
            pygame.display.update()
            self.fps_clock.tick(30)

        # Se o jogador não saiu no meio da partida então alguém venceu
        if self.winner:
            # Se for o jogador, ele ganha
            if self.winner == 1:
                self.curr_menu = self.win_screen
            # Se for algum dos bots, ele perde
            else:
                self.curr_menu = self.lose_screen

            # Reinicia o estado para exibir a tela
            self.start()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.curr_menu.run_display = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.ESC_KEY = True
                    self.playing = False
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY = False, False, False, False, False
        self.BUTTON_CLICKED = False

    def start(self):
        pygame.mixer.music.play(-1, 0, 2)

        # Mostra os menus e, quando decidir jogar ou sair, sai deste loop
        while not self.playing:
            self.curr_menu.display_menu()

            if not self.running:
                return

        # Entra no jogo
        self.game_loop()

        # Se não houve ganhador é porque o jogador voltou ao menu principal
        # Então é válido recomeçar o estado de jogo
        if not self.winner:
            self.restart()

    def restart(self):
        # Volta para o menu principal
        self.curr_menu = self.main_menu
        self.__change_music("grid_1.ogg", self.volume)

        # Apaga o jogador antigo
        del self.game_run._player

        self.start()

    @staticmethod
    def __change_music(title, volume):
        pygame.mixer.music.load(MUSIC_PATH + title)
        pygame.mixer.music.set_volume(volume)