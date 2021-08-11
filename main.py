# lichess access token OzWsl6WWkSIkUZEh
from berserk import Client, TokenSession, Variant, Color
from lichess import api
from stockfish import Stockfish
from typing import Tuple
import threading

class ChessIT_Bot():
    def __init__(self):
        self.access_token = "b4ADXmZxLf4kEUOA"
        self.session = TokenSession(self.access_token)
        self.client = Client(self.session)
        self.game_id = ""
        self.my_color = Color.BLACK
        self.connect()
        self.fish_config = {
            "Write Debug Log": "false",
            "Contempt": 0,
            "Min Split Depth": 0,
            "Threads": 1,
            "Ponder": "false",
            "Hash": 16,
            "MultiPV": 1,
            "Skill Level": 20,
            "Move Overhead": 30,
            "Minimum Thinking Time": 20,
            "Slow Mover": 80,
            "UCI_Chess960": "false",
        }
        self.fish = Stockfish(parameters=self.fish_config)
        self.opponent = ""
        self.name = "Chess_IT"

    def connect(self):
        self.session = TokenSession(self.access_token)
        self.client = Client(self.session)

    def set_game_id(self, game_id):
        self.game_id = game_id

    def set_opponent(self, opp):
        self.opponent = opp

    def set_my_color(self, color: Color):
        self.my_color = color

    def get_info(self):
        return self.client.account.get()

    def fish_recommends(self, game_moves):
        self.fish.set_position(game_moves)
        eval = self.fish.get_evaluation()
        if eval['type'] == 'cp':
            centi_pawn = float(eval['value']) / 100.0
            self.client.bots.post_message(self.game_id, f"{centi_pawn}")
        if eval['type'] == 'mate':
            self.client.bots.post_message(self.game_id, f"mate in {abs(eval['value'])}")
        fish_move = self.fish.get_best_move()
        self.client.bots.make_move(self.game_id, fish_move)
        return fish_move

    def handle_state_change(self, game_state):
        pass

    def interpret(self, text: str) -> Tuple[bool, str, int, int, bool, float]:
        """
        :param text:
        :return:
        (bool): is a valid substring
        (str): the substring
        (int): lowest index of the substring in the text
        (int): length of the substring
        (bool): substring is a setting parameter
        (float): The value of the setting
        """
        valid = False
        substr = "noSubstring"
        index = -1
        length = -1
        is_param = False
        param_value = "noParam"

    def handle_chat_line(self, chat_line):
        if chat_line['username'] == self.opponent:
            text : str = chat_line['text']
            valid, substr, index, length, is_param, param_value = self.interpret(text)
            if valid:
                self.client.bots.post_message(self.game_id, "exciting")
            else:
                self.client.bots.post_message(self.game_id, "fuck off")

    def challenge_blitz(self, user: str):
        self.client.challenges.create(username=user,
                                      rated=False,
                                      clock_limit=60 * 10,
                                      clock_increment=0,
                                      days=1,
                                      color=self.my_color,
                                      variant=Variant.STANDARD)

    def play_game_manual(self):
        print(self.get_info())
        first = True
        id = ""
        game_moves = []
        white_list = ['braki', 'rouch3200']
        last_move = ""
        while True:
            for event in bot.client.bots.stream_incoming_events():
                print(event)
                if event['type'] == 'gameStart':
                    if first:
                        self.set_game_id(event['game']['id'])
                        id = event['game']['id']
                        first = False
                    self.client.bots.post_message(bot.game_id,
                                                  "prepare TO DIE !!!! 10101010100101110101100000010101010101000000100101001101110010101111111011001010010010100100001010000011010101000010101")
                    for state in self.client.bots.stream_game_state(id):
                        print(state)
                        if state['type'] == 'gameState':
                            game_moves = state['moves'].split(" ")
                            n_moves = len(game_moves)
                            turn_color = [Color.WHITE if (n_moves % 2) == 0 else Color.BLACK][0]
                            print(turn_color)
                            my_turn = (self.my_color == turn_color)
                            print(my_turn)
                            print(f"the game moves are now:  {game_moves}")
                            if my_turn:
                                move = input("Your move:  ")
                                self.client.bots.make_move(self.game_id, move)
                                last_move = move
                                print(f"the last move is {last_move}")
                        elif state['type'] == 'chatLine':
                            self.handle_chat_line(state)
                elif event['type'] == 'challenge' and (event['challenge']['challenger']['id'] in white_list):
                    self.client.bots.accept_challenge(event['challenge']['id'])
                    self.set_opponent(event['challenge']['challenger']['name'])

    def play_game(self, game_id, move_handler):
        active = True
        while active:
            for state in self.client.bots.stream_game_state(game_id):
                print(state)
                if state['type'] == 'gameState':
                    if state['status'] == 'started':
                        game_moves = state['moves'].split(" ")
                        n_moves = len(game_moves)
                        turn_color = [Color.WHITE if (n_moves % 2) == 0 else Color.BLACK][0]
                        print(turn_color)
                        my_turn = (self.my_color == turn_color)
                        print(my_turn)
                        if my_turn:
                            last_move = move_handler(game_moves)
                elif state['type'] == 'chatLine':
                    self.handle_chat_line(state)
                elif state['type'] == 'gameFull':
                    if state['state']['status'] == 'started':
                        if state['white']['name'] == self.name:
                            self.set_my_color(Color.WHITE)
                        elif state['black']['name'] == self.name:
                            self.set_my_color(Color.BLACK)
                        game_moves = state['state']['moves'].split(" ")
                        print(game_moves)
                        n_moves = len(game_moves)
                        print(n_moves)
                        turn_color = [Color.WHITE if (n_moves % 2) == 0 else Color.BLACK][0]
                        if n_moves == 1:
                            if game_moves[0] == '':
                                turn_color = Color.WHITE
                        print(turn_color)
                        my_turn = (self.my_color == turn_color)
                        print(my_turn)
                        if my_turn:
                            last_move = move_handler(game_moves)
                    elif state['state']['status'] == 'mate':
                        if state['state']['winner'] == self.my_color:
                            last_message = "That is for naming yourself 'master' in home assistant !"
                        else:
                            last_message = "Good job........ until next time =)"
                        self.client.bots.post_message(game_id, last_message)
                        active = False
                    else:
                        active = False

                elif state['type'] == 'gameFinish':
                    active = False

    def play_fishy(self):
        print(self.get_info())
        first = True
        id = ""
        game_moves = []
        white_list = ['braki', 'perspelmann', 'rouch3200']
        last_move = ""
        while True:
            for event in bot.client.bots.stream_incoming_events():
                print(event)
                if event['type'] == 'gameStart':
                    self.set_game_id(event['game']['id'])
                    self.client.bots.post_message(self.game_id,
                                                  "prepare TO DIE !!!! 10101010100101110101100000010101010101000000100101001101110010101111111011001010010010100100001010000011010101000010101")
                    move_handler = self.fish_recommends
                    self.play_game(self.game_id, move_handler)
                elif event['type'] == 'challenge':
                    self.opponent = event['challenge']['challenger']['id']
                    if self.opponent in white_list:
                        self.prep()
                        self.client.bots.accept_challenge(event['challenge']['id'])

    def prep(self):
        self.fish_config = {
            "Write Debug Log": "true",
            "Contempt": 0,
            "Min Split Depth": 0,
            "Threads": 1,
            "Ponder": "false",
            "Hash": 16,
            "MultiPV": 1,
            "Skill Level": 20,
            "Move Overhead": 30,
            "Minimum Thinking Time": 50,
            "Slow Mover": 120,
            "UCI_Chess960": "false",
        }


if __name__ == '__main__':
    bot = ChessIT_Bot()
    bot.play_fishy()
