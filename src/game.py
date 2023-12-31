import pygame
import sys

from entity import *
from rider import *
from deck import *
import utilities
from config import *


class GridGame(Entity):
    def __init__(self, image_path, x_y, scale_size, bot_number, volume, state_control):
        super().__init__(image_path, x_y, scale_size)
        self.state_control = state_control

        # Atributos para o estado do jogo
        self.next_menu = "none"
        self._game_turn = 0
        self._mov_stage = -1
        self._clicked = False

        # Cria o deck
        self._deck = Deck(CARDS_PATH, (CARD_X, CARD_Y))

        # Cria o jogador
        self._player = Player(1, (GRID_X / 2 - 1, GRID_Y / 2 - 2), (RIDER_X, RIDER_Y), self._deck)

        # Cria os bots
        __bot_list = []

        for bot in range(bot_number):
            __bot_list.append(Bot(bot + 2, (GRID_X / 2 - 1, GRID_Y / 2 - 2), (RIDER_X, RIDER_Y), self._deck))

        self._bots = pygame.sprite.OrderedUpdates(__bot_list[::-1])

        # Grupo com todos personagens animados (bots e player)
        self._all_riders = pygame.sprite.Group((self._player.sprite()), self._bots.sprites()[::-1])

        # Carrega efeitos sonoros pra memória
        self.volume = volume * 3 / 4
        self.sound = []

        for index in range(SOUND_NUMBER):
            archive = "sound_" + str(index) + ".ogg"
            sound = pygame.mixer.Sound(SOUND_PATH + archive)
            sound.set_volume(self.volume)
            self.sound.append(sound)

        # Cria um canal para tocar os efeitos sonoros
        self.channel = pygame.mixer.Channel(1)
        self.channel.set_volume(self.volume)

    def update(self):
        # Eventos principais deste menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.channel.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state_control.playing = False
                    self.channel.stop()
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self._clicked and self._player:
                    self.__validate_click()

            for rider in self._all_riders:
                if event.type == rider.clock:
                    rider.update()

        # Verifica se sobrou apenas um, que será o vencedor
        if len(self._all_riders) == 1:
            # E então retorna ao state_control as informações pertinentes
            self.state_control.winner = self._all_riders.sprites()[0]._number
            self.state_control.playing = False
            return

        # Se tiver clicado, roda o movimento do jogador ou dos bots e testa colisão
        if self._clicked and self._all_riders:
            rider = self._all_riders.sprites()[self._mov_stage]

            # Só movimenta se o jogador estiver vivo
            if rider.state_alive:
                self.move_player(rider)
                self.check_collision(rider)

        # Verifica se alguém morreu e roda sua animação
        for rider in self._all_riders:
            if not rider.state_alive:
                # Quando acabar continua a rodada
                if rider.update_death():
                    self.__end_death()

        return False

    def draw(self, screen):
        # Desenha o tabuleiro no layer mais baixo
        screen.blit(self.image, self.rect)

        # Desenha as linhas dos riders
        for rider in self._all_riders.sprites():
            pygame.draw.lines(screen, rider._color, False, rider._path + [rider.rect.center], width=6)

        # Desenha o contorno e as cartas
        if self._player:
            self.choice_preview(screen)
            self._player._hand.draw(screen)

        # Faz blit no jogador e nos bots
        self._bots.draw(screen)
        self._player.draw(screen)

        # Se alguém estiver na animação de morte, desenha de acordo
        for rider in self._all_riders.sprites():
            if not rider.state_alive:
                screen.blit(rider.last_image, rider.last_rect)

    def choice_preview(self, screen):
        # Verifica se o mouse está em cima da carta
        for card in self._player._hand.sprites():
            if card.update():
                # Desenha o contorno
                self.__preview_selected_card(card, screen)

                # Se não houver clicado antes, mostra a trajetória da carta
                if not self._clicked:
                    self.__preview_selected_path(card, screen)

    @staticmethod
    def __preview_selected_card(card, screen):
        # Desenha o contorno da carta selecionada
        rect_pos = (card.rect.left - CARD_SELECTED_WIDTH, card.rect.top - CARD_SELECTED_WIDTH)
        rect_size = (card.rect.width + 2 * CARD_SELECTED_WIDTH, card.rect.height + 2 * CARD_SELECTED_WIDTH)

        rectangle = pygame.Rect(rect_pos, rect_size)

        pygame.draw.rect(screen, "#258dc2", rectangle, width=2 * CARD_SELECTED_WIDTH)

    def __preview_selected_path(self, card, screen):
        # Pega o ponto inicial e final da reta
        start = pygame.Vector2(self._player._path[-1])  # Converte para Vector2
        card_value = pygame.Vector2(card.value[0], -card.value[1])

        size_segments = 12  # Defina a distância desejada entre os segmentos da linha tracejada
        num_segments = int(start.distance_to(start + card_value * DISTANCE) / size_segments)

        # Desenha a linha tracejada
        for i in range(0, num_segments, 2):
            segment_start = start + card_value * i * DISTANCE / num_segments
            segment_end = start + card_value * (i + 1) * DISTANCE / num_segments
            pygame.draw.line(screen, self._player._color, segment_start, segment_end, width=5)     
        
    def __validate_click(self):
        # Verifica em qual carta clicou
        player_card = self.__card_clicked()

        # Se tiver clicado, prepara o movimento do player
        if player_card:
            self._clicked = True
            self.__next_player_movement(player_card)

    def __card_clicked(self):
        # Se o jogador clicar na carta, _clicked = True
        for card in self._player._hand.sprites():
            if card.update():
                return card
            
        return None
            
    def move_player(self, rider):
        # Move o rider
        if rider.move_rider(self._deck):
            return
        # Se ficou parado, reseta o movimento
        else:
            self.__next_player_movement()

    def __end_turn(self):
        # Só reverte o estado do jogo e adiciona um turno
        self._game_turn += 1
        self._clicked = False
        self._mov_stage = -1

        # Quando o jogador estiver morto pula sua vez
        if not self._player:
            self._mov_stage += 1
            self._clicked = True

        # Para o som do movimento
        self.channel.stop()

    def __next_player_movement(self, card=None):
        self._mov_stage += 1

        # Se todos jogadores tiverem se movimentado, acaba o turno
        if self._mov_stage == len(self._all_riders):
            self.__end_turn()

            # No raro caso de colidirem no primeiro turno
            if self._game_turn == 1:
                self.__first_turn_collision()

            # Quando o jogador não estiver vivo os bots jogarão entre si
            if self._player:
                return
            
            # Se todos morrerem também retorna
            if not self._all_riders:
                return
        
        # Caso contrário, prepara o jogo para rodar mais uma animação
        next_player = self._all_riders.sprites()[self._mov_stage]

        # Se não tiver passado uma carta, faz o rider escolher (em geral um bot)
        if not card:
            card = next_player.choose_card(self._all_riders)

        # Atualiza o estado do próximo jogador
        next_player.select_card(card)

        # Toca o som de movimento indefinidamente
        self.channel.play(self.sound[1], -1)

    def __first_turn_collision(self):
        # Verifica se alguém colidiu no primeiro turno
        for rider in self._all_riders.sprites()[::-1]:
            # Testa apenas colisão com as linhas pois é impossivel colidir com fronteira
            if utilities.check_line_collision(self._all_riders, rider) and self._game_turn:
                rider.kill_rider()
                self.channel.play(self.sound[0])
                continue

    def check_collision(self, rider):
        # Testa colisão com a fronteira
        if utilities.check_border_collision(rider.rect.center):
            rider.kill_rider()
            self.channel.play(self.sound[0])
            return

        # Testa colisão com as linhas
        if utilities.check_line_collision(self._all_riders, rider) and self._game_turn:
            rider.kill_rider()
            self.channel.play(self.sound[0])
            return

        # Verifica se colidiram entre si
        temp_group = self._all_riders.copy()
        temp_group.remove(rider)

        for enemy in temp_group:
            if utilities.check_riders_collision(rider, enemy) and self._game_turn:
                rider.kill_rider()
                enemy.kill_rider()
                self.sound[0].play()
                return

    def __end_death(self):
        # Termina a rodada se não houver mais nenhuma animação ocorrendo
        for rider in self._all_riders.sprites():
            if not rider.state_alive:
                return

        # Se todos que sobraram estiverem vivos, continua a partida
        self._mov_stage -= 1
        self.__next_player_movement()
