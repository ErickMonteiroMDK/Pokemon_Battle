import random
import time

import pygame
from pygame.locals import *
import requests
import io
from urllib.request import urlopen

pygame.init()

# Criando a janela para o game
game_width = 500
game_height = 500
size = (game_width, game_height)
game = pygame.display.set_mode(size)
pygame.display.set_caption('Pokemon Battle')

# Definindo as cores
black = (0, 0, 0)
gold = (218, 165, 32)
grey = (200, 200, 200)
green = (0, 200, 0)
red = (200, 0, 0)
white = (255, 255, 255)

# URL base da API
base_url = 'https://pokeapi.co/api/v2'

class Move:
    def __init__(self, url):
        # chamando os movimentos da API
        req = requests.get(url)
        self.json = req.json()

        self.name = self.json['name']
        self.power = self.json['power']
        self.type = self.json['type']['name']

class Pokemon(pygame.sprite.Sprite):
    def __init__(self, name, level, x, y):
        pygame.sprite.Sprite.__init__(self)

        # Chamando a API
        req = requests.get(f'{base_url}/pokemon/{name.lower()}')
        self.json = req.json()

        # Setando o nome e level do pokemon
        self.name = name
        self.level = level

        # Setando a posição do sprite na tela
        self.x = x
        self.y = y

        # Número de poções
        self.num_potions = 3

        # Pegando o status do pokemon pela API
        stats = self.json['stats']
        for stat in stats:
            if stat['stat']['name'] == 'hp':
                self.current_hp = stat['base_stat'] + self.level
                self.max_hp = stat['base_stat'] + self.level
            elif stat['stat']['name'] == 'attack':
                self.attack = stat['base_stat']
            elif stat['stat']['name'] == 'defense':
                self.defense = stat['base_stat']
            elif stat['stat']['name'] == 'speed':
                self.speed = stat['base_stat']

        # Setando o tipo de pokemon
        self.types = [type_info['type']['name'] for type_info in self.json['types']]

        # Setando o sprite
        self.set_sprite('front_default')

    def perform_attack(self, other, move):

        display_message(f'{self.name} usou {move.name}')

        #pausa de 2 segundos
        time.sleep(2)

        #calculando o dano
        damage = (2 * self.level + 10) / 250 * self.attack / other.defense * move.power

        # attack bonus
        if move.type in self.types:
            damage *= 1.5

        # dano critico
        random_num = random.randint(1, 10000)
        if random_num <= 625:
            damage *= 1.5

        # arredondando o dano
        damage = math.floor(damage)

        other.take_damage(dagame)

    def take_damage(self, damage):

        self.current_hp -= damage

        # não mostra que o HP foi abaixo de 0
        if self.current_hp < 0:
            self.current_hp = 0

        def use_potion(self):
            # checar se há poções restantes
            if self.num_potions > 0:
                # adicionar 30 de hp
                self.current_hp += 30
                if self.current_hp > self.max_hp:
                    self.current_hp = self.max_hp

        #diminui o numero de poções
        self.num_potions -= 1

    def set_sprite(self, side):
        # Setando o sprite do pokemon
        image_url = self.json['sprites'][side]
        image_stream = urlopen(image_url).read()
        image_file = io.BytesIO(image_stream)
        self.image = pygame.image.load(image_file).convert_alpha()

        # Ajuste da escala da imagem
        scale = 100 / self.image.get_width()  # 100 é a largura desejada
        new_width = int(self.image.get_width() * scale)
        new_height = int(self.image.get_height() * scale)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))

    def set_moves(self):

        self.moves = []

        # passar por todos os movimentos da API
        for i in range(len(self.json['moves'])):

            versions = self.json['moves'][i]['version_group_details']
            for j in range(len(versions)):

                version = versions[j]

                #pegar apenas movimentos da versão red-blue
                if version['version_group']['name'] != 'red-blue':
                    continue

                # apenas resgatar movimentos caso haja aumento de level
                learn_method = version['move_learn_method']['name']
                if learn_method != 'level-up':
                    continue

                #adicionar movimentos caso o level do pokemon seja alto o suficiente
                level_learned = version['level_learned_at']
                if self.level >= level_learned:
                    move = Move(self.json['moves'][i]['move']['url'])

                    #apenas incluir movimentos de ataque
                    if move.power is not None:
                        self.moves.append(move)

                        # selecione até 4 movimentos aleatórios
                        if len(self.moves) > 4:
                            self.moves = random.sample(self.moves, 4)

    def draw(self, surface, alpha=255):
        sprite = self.image.copy()
        sprite.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        surface.blit(sprite, (self.x, self.y))
        game.blit(sprite, (self.x, self.y))

        def draw_hp(self):

            bar_scale = 200 // self.max_hp
            for i in range(self.max_hp):
                bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
                pygame.draw.rect(game, red, bar)

            for i in range(self.current_hp):
                bar = (self.hp_x + bar_scale * i, self.hp_y, bar_scale, 20)
                pygame.draw.rect(game, green, bar)

            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            text = font.render(f'HP: {self.current_hp} / {self.max_hp}', True, black)
            text_rect.x = self.hp_x
            text_rect.y = self.hp_y + 30
            game.blit(text, text_rect)

    def get_rect(self):
        return Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    def display_message(message):
        # Desenhar uma box branca com uma borda preta
        pygame.draw.rect(game, white, (10, 350, 480, 140))
        pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

        # Exibir mensagem
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        text = font.render(message, True, black)
        text_rect = text.get_rect()
        text_rect.x = 30
        text_rect.y = 410
        game.blit(text, text_rect)


pygame.display.update()

def create_button(left, top, width, height, label, text_cx, text_cy):
    # posição do cursor do mouse
    mouse_cursor = pygame.mouse.get_pos()

    button = Rect(left, top, width, height)

    if button.collidepoint(mouse_cursor):
        pygame.draw.rect(game, gold, button)
    else:
        pygame.draw.rect(game, white, button)

    # adicionar a label no button
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render(f'{label}', True, black)
    text_rect = text.get_rect(center=(text_cx, text_cy))
    game.blit(text, text_rect)

    return button


# Exemplo de uso
if __name__ == "__main__":
    # Criando instâncias de Pokemon
    level = 30
    bulbasaur = Pokemon('Bulbasaur', level, 25, 150)
    charmander = Pokemon('Charmander', level, 175, 150)
    squirtle = Pokemon('Squirtle', level, 325, 150)
    pokemons = [bulbasaur, charmander, squirtle]

    # Os players escolhem os pokemons
    player_pokemon = None
    rival_pokemon = None

    # Loop do game
    game_status = 'Selecione um Pokemon'
    while game_status != 'quit':
        mouse_click = None

        for event in pygame.event.get():
            if event.type == QUIT:
                game_status = 'quit'

            if event.type == KEYDOWN:
                # Jogue Novamente
                if event.key == K_y:
                    # resetar os pokemons
                    bulbasaur = Pokemon('Bulbasaur', level, 25, 150)
                    charmander = Pokemon('Charmander', level, 175, 150)
                    squirtle = Pokemon('Squirtle', level, 325, 150)
                    pokemons = [bulbasaur, charmander, squirtle]
                    game_status = 'Selecione um Pokemon'
                elif event.key == K_n:
                    game_status = 'quit'
            elif event.type == MOUSEBUTTONDOWN:
                mouse_click = event.pos

        if game_status == 'Selecione um Pokemon':
            game.fill(white)

            for pokemon in pokemons:
                pokemon.draw(game)

            if mouse_click:
                for i, pokemon in enumerate(pokemons):
                    if pokemon.get_rect().collidepoint(mouse_click):
                        player_pokemon = pokemon
                        rival_pokemon = pokemons[(i + 1) % len(pokemons)]
                        rival_pokemon.level = int(rival_pokemon.level * 0.75)
                        player_pokemon.hp_x = 275
                        player_pokemon.hp_y = 250
                        rival_pokemon.hp_x = 100
                        rival_pokemon.hp_y = 75
                        game_status = 'Pre Batalha'

            # para selecionar a luta ou usar a poção
            if game_status == 'Turno do Player':
                # checar se o botão de luta foi acionado
                if fight_button.collidepoint(mouse_click):
                    game_status = 'Player'

                # checar se o botão de poção foi acionado
                elif potion_button.collidepoint(mouse_click):
                    if player_pokemon.num_potions == 0:
                        display_message('Não há mais poções')
                        time.sleep(2)
                        game_status = 'Movimento do Player'
                    else:
                        player_pokemon.use_potion()
                        display_message(f'{player_pokemon.name} usou poção')
                        time.sleep(2)
                        game_status = 'Turno do Rival'

                # para selecionar um movimento
                elif game_status == 'Movimento do Player':

                    # checar se algum botão de mover foi acionado
                    for i in range(len(move_buttons)):
                        button = move_buttons[i]

                        if button.collidepoint(mouse_click):
                            move = player_pokemon.moves[i]
                            player_pokemon.perform_attack(rival_pokemon, move)

                            #checar se o pokemon rival desmaiou
                            if rival_pokemon.current_hp == 0:
                                game_status = 'Fainted'
                            else:
                                game_status = 'Turno do Rival'

            # desenhar uma box ao redor do pokemon quando o cursor selecionar o pokemon
            mouse_cursor = pygame.mouse.get_pos()
            for pokemon in pokemons:
                if pokemon.get_rect().collidepoint(mouse_cursor):
                    pygame.draw.rect(game, black, pokemon.get_rect(), 2)

            pygame.display.update()

    # pega movimentos da API e reposiciona os pokemons
    if game_status ==  'Pre batalha':
        # desenhando o pokemon selecionado
        game.fill(white)
        player_pokemon.draw()
        pygame.display.update()

        player_pokemon.set_moves()
        rival_pokemon.set_moves()

        # reposicionando os pokemons
        player_pokemon.x = -50
        player_pokemon.y = 100
        rival_pokemon.x = 250
        rival_pokemon.y = -50

        # redimensionar os sprites
        player_pokemon.size = 300
        rival_pokemon.size = 300
        player_pokemon.set_sprite('back_default')
        rival_pokemon.set_sprite('front_default')

        game_status = 'Iniciar Batalha'

        # start da animação da batalha
        if game_status == 'Iniciar Batalha':
            # player rival joga seu pokemon
            alpha = 0
            while alpha < 255:
                game.fill(white)
                rival_pokemon.draw(alpha)
                display_message(f'Rival joga {rival_pokemon.name}!')
                alpha += .4

                pygame.display.update()

                #pausa de 1 segundo
                time.sleep(1)

                # player envia seu pokemon
                alpha = 0
                while alpha < 255:

                    game.fill(white)
                    rival_pokemon.draw()
                    player_pokemon.draw(alpha)
                    display_message(f'Vai {player_pokemon,name}!')
                    alpha += .4

                    pygame.display.update()

                # desenhar as barras de hp
                player_pokemon.draw_hp()
                rival_pokemon.draw_hp()

                #determinando quem avança primeiro
                if rival_pokemon.speed > player_pokemon.speed:
                    game_status = 'Turno do Rival'
                else:
                    game_status = 'Turno do Player'

                    pygame.display.update()

                # pausa por 1 segundo
                time.sleep(1)

                #display da luta e botton de poções
                if game_status == 'Turno do Player':

                    game.fill(white)
                    player_pokemon.draw()
                    rival_pokemon.draw()
                    player_pokemon.draw_hp()
                    rival_pokemon.draw_hp()

                figth_button = create_button(240,140,10,350,130,412,'Figth')
                potion_button = create_button(240,140,10,350,130,412,f'Usar Poção({player_pokemon.num_potions})')


               #desenhar a borda preta
                pygame.draw.rect(game, black, (10, 350, 480, 140), 3)

                pygame.display.update()

            # display dos botões de move
            if game_status == 'Vez do Player':

                game.fill(white)
                player_pokemon.draw()
                rival_pokemon.draw()
                player_pokemon.draw_hp()
                rival_pokemon.draw_hp()

            # criar botão para cada movimento
            move_buttons = []
            for i in range(len(player_pokemon.moves)):
                move = player_pokemon.moves[i]
                button_width = 240
                button_height = 70
                left = 10 + i % 2 * button_width
                top = 350 + i // 2 * button_height
                text_center_x = left + 120
                text_center_y = top + 35
                button = create_button(button_width, button_height, left, top, text_center_x, text_center_y,
                                       move.name.capitalize())
                move_buttons.append(button)

            #desenhar a borda preta
            pygame.draw.rect(game, black, (10,350,480,140), 3)

            pygame.display.update()

            # rival seleciona um movimento aleatório
            if game_status == 'Turno do Rival':

                game.fill(white)
                player_pokemon.draw()
                rival_pokemon.draw()
                player_pokemon.draw_hp()
                rival_pokemon.draw_hp()

                # esvazie a caixa de exibição e faça uma pausa por 2 segundos antes de atacar
                display_message('')
                time.sleep(2)

                # selecione um movimento aleatório
                move = random.choice(rival_pokemon.moves)
                rival_pokemon.perform_attack(player_pokemon, move)

                # checar se o pokemon do Player foi desmaiado
                if player_pokemon.current_hp == 0:
                    game_status = 'Fainted'
                else:
                    game_status = 'Turno do Player'

                pygame.display.update()

                # um dos pokemons foi desmaiado
                if game_status == 'Fainted':

                    alpha = 255
                    while alpha > 0:

                        game.fill(white)
                        player_pokemon.draw_hp()
                        rival_pokemon.draw_hp()

                        # determinando qual pokemon foi desmaiado
                        if rival_pokemon.current_hp == 0:
                            player_pokemon.draw()
                            rival_pokemon.draw(alpha)
                            display_message(f'{rival_pokemon.name} desmaiou!')
                        else:
                            player_pokemon.draw(alpha)
                            rival_pokemon.draw()
                            display_message(f'{player_pokemon.name} desmaiou!')
                        alpha -= .4

                        pygame.display.update()

                        game_status = 'Game Over'

                        # tela de Game Over
                        if game_status == 'Game Over':

                            display_message('Jogue Novamente (Y/N)')

    pygame.quit()