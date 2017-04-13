from __future__ import print_function
from CYLGame import GameLanguage
from CYLGame import Game
from CYLGame import MessagePanel
from CYLGame import MapPanel
from CYLGame import StatusPanel
from CYLGame import PanelBorder


DEBUG = True


class PacBot(Game):
    MAP_WIDTH = 30
    MAP_HEIGHT = 34
    SCREEN_WIDTH = MAP_WIDTH + 2
    SCREEN_HEIGHT = MAP_HEIGHT + 6
    MSG_START = 20
    MAX_MSG_LEN = SCREEN_WIDTH - MSG_START - 1
    CHAR_WIDTH = 16
    CHAR_HEIGHT = 16
    GAME_TITLE = "Pac-Bot"
    CHAR_SET = "terminal16x16_gs_ro.png"

    SENSE_DIST = 20


    MAX_TURNS = 500
    MAX_FLYING = 10
    FLYING_POINTS = 5
    COIN_POINTS = 25
    HOUSE_ODDS = 500 # e.g., 1/500


    PLAYER_START_X = 14
    PLAYER_START_Y = 24

    PLAYER = '@'
    EMPTY = '\0'
    APPLE = 'O'
    FULL = chr(224)
    DOT = chr(225)
    POWER = chr(226)
    DOOR = chr(227)
    PIPE = chr(228)
    HYPHEN = chr(229)
    J = chr(230)
    L = chr(231)
    F = chr(232)
    SEVEN = chr(233)

    # ghosts
    BLINKY = chr(234)
    PINKY = chr(235)
    INKY = chr(236)
    CLYDE = chr(237)
    EYES = chr(238)
    EDIBLE = chr(239)

    #fruit
    CHERRY = chr(240)
    STRAWBERRY = chr(241)
    ORANGE = chr(242)
    BELL = chr(243)
    APPLE = chr(244)
    MELON = chr(245)
    GALAXIAN = chr(246)
    KEY = chr(247)
    

    def __init__(self, random):
        self.sensor_coords = [] # variables for adjustable sensors from LP
        self.random = random
        self.running = True
        self.colliding = False
        self.saved_object = None # stores a map item we're "on top of"
        self.last_move = 'w' # need this to restore objects
        self.flying = 0 # set to some value and decrement (0 == on ground)
        self.hp = 1
        self.player_pos = [self.PLAYER_START_X, self.PLAYER_START_Y]
        self.score = 0
        self.objects = []
        self.turns = 0
        self.level = 1
        self.msg_panel = MessagePanel(self.MSG_START, self.MAP_HEIGHT + 1, self.SCREEN_WIDTH - self.MSG_START, 5)
        self.status_panel = StatusPanel(0, self.MAP_HEIGHT + 1, self.MSG_START, 5)
        self.panels = [self.msg_panel, self.status_panel]

        self.__create_map()

    def print_ready(self):
        x = 12
        y = 18
        for char in "READY!":
            self.map[(x,y)] = char
            x += 1

    def erase_ready(self):
        x = 12
        y = 18
        for char in "READY!":
            self.map[(x,y)] = ' '
            x += 1



    def __create_map(self):
        self.map = MapPanel(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT + 1, self.EMPTY,
                            border=PanelBorder.create(bottom="-"))

        self.panels += [self.map]

        mapmap = {'|': self.PIPE,
                  '-': self.HYPHEN,
                  'L': self.L,
                  '7': self.SEVEN,
                  'J': self.J,
                  'F': self.F,
                  '.': self.DOT,
                  'O': self.POWER,
                  '=': self.DOOR,
                  '#': self.FULL,
                  ' ': self.EMPTY,
                  'B': self.BLINKY,
                  'P': self.PINKY,
                  'I': self.INKY,
                  'C': self.CLYDE}

        # open map file
        x = 0
        y = 0
        with open("map.txt") as f:
            for line in f:
                x = 0
                for char in line:
                    if char != '\n':
                        self.map[(x, y)] = mapmap[char]
                    x += 1
                y += 1
        
        self.map[(14,24)] = self.PLAYER

        self.print_ready()

        if DEBUG:
            print(self.get_vars_for_bot())  # need sensors before turn

    def place_objects(self, char, count, replace=False):
        placed_objects = 0
        while placed_objects < count:
            x = self.random.randint(0, self.MAP_WIDTH - 1)
            y = self.random.randint(0, self.MAP_HEIGHT - 1)

            if self.map[(x, y)] == self.EMPTY:
                self.map[(x, y)] = char
                placed_objects += 1
            elif replace:
                # we can replace objects that exist
                self.map[(x, y)] = char
                placed_objects += 1

    def save_object(self, obj):
        self.saved_object = obj

    def restore_object_tracks(self):

        # restore an object you went over or make tracks

        # where should the object be restored?
        y = 1 # it's always going to be behind us
        x = 0 # we will set the x value accordingly
        
        if self.last_move == 'a':
            x = 1
        elif self.last_move == 'd':
            x = -1
        elif self.last_move == 'w':
            x = 0

        if self.saved_object:
            if self.last_move == 't':
                # if the player previously teleported when on an
                # obstacle, just destroy the obstacle. We can't put it
                # back where it was because we don't know (x, y) for the
                # player due to map shifting, and we can't draw it under
                # us or we will collide with it twice!
                self.msg_panel += ["Teleporting destroyed the object!"]
                self.saved_object = None
            else:
                # if the player didn't teleport, put object back
                self.map[(self.player_pos[0] + x, self.player_pos[1] + y)] = self.saved_object
                self.saved_object = None
        else:
            if self.flying < 1:
                if self.map[(self.player_pos[0] + x, self.player_pos[1] + y)] == self.EMPTY:
                    self.map[(self.player_pos[0] + x, self.player_pos[1] + y)] = self.TRACKS


    def is_ghost(self, item):
        if item == self.BLINKY or item == self.PINKY or item == self.INKY or item == self.CLYDE:
            return True
        else:
            return False

    def is_fruit(self, item):
        if item == self.APPLE:
            return True
        else:
            return False


    def is_blocked(self, x, y):

        # returns true if the cell in the map is obstructed
        spot = self.map[(x,y)]

        if spot == self.DOT or spot == self.POWER or spot == self.EMPTY or self.is_ghost(spot) or self.is_fruit(spot):
            return False
        else:
            return True

    def handle_key(self, key):

        self.turns += 1
        
        if self.turns == 1:
            self.erase_ready()

        if DEBUG:
            print("turn: %d player started at (%d, %d)" % (self.turns, self.player_pos[0], self.player_pos[1]))

        self.map[(self.player_pos[0], self.player_pos[1])] = self.EMPTY

        if key == "a" and not self.is_blocked(self.player_pos[0] - 1, self.player_pos[1]):
                self.player_pos[0] -= 1
        if key == "d" and not self.is_blocked(self.player_pos[0] + 1, self.player_pos[1]):
            self.player_pos[0] += 1
        if key == "w" and not self.is_blocked(self.player_pos[0], self.player_pos[1] - 1):
            self.player_pos[1] -= 1
        if key == "s" and not self.is_blocked(self.player_pos[0], self.player_pos[1] + 1):
            self.player_pos[1] += 1

        if self.player_pos[0] == 0 and self.player_pos[1] == 15:
            self.player_pos[0] = 28
        elif self.player_pos[0] == 29 and self.player_pos[1] == 15:
            self.player_pos[0] = 1

        if key == "Q":
            self.running = False
            return

        # add score based on new position
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.DOT:
            self.score += 10
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.POWER:
            self.score += 50

        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        if DEBUG:
            print("turn: %d player ended at (%d, %d)" % (self.turns, self.player_pos[0], self.player_pos[1]))
        
        # vars should be gotten at the end of handle_turn, because vars
        # affect the *next* turn...
        if DEBUG:
            print(self.get_vars_for_bot())

    def is_running(self):
        return self.running

    def read_bot_state(self, state):
        # state.get('foo','') <-- set this to a default value that makes
        # sense
        # need to get LP values for:
        # s1x-s7x and s1y-s7y
        self.sensor_coords = []
        for i in range(7):
            x_name = "s" + str(i + 1) + "x"
            y_name = "s" + str(i + 1) + "y"
            self.sensor_coords.append((state.get(x_name, "0"), state.get(y_name, "0")))

    def get_vars_for_bot(self):

        bot_vars = {}

        # go through self.sensor_coords and retrieve the map item at the
        # position relative to the player
        for i in range(7):
            if (i < len(self.sensor_coords)):
                sensor = "s" + str(i + 1)
                x_offset = self.sensor_coords[i][0]
                y_offset = self.sensor_coords[i][1]

                bot_vars[sensor] = ord(self.map[(self.player_pos[0] + int(x_offset), self.player_pos[1] + int(y_offset))])
                if bot_vars[sensor] == 64:
                    bot_vars[sensor] = 0

        bot_vars['hp'] = self.hp
        bot_vars['flying'] = self.flying

        if DEBUG:
            print(bot_vars)

        return bot_vars

    @staticmethod
    def default_prog_for_bot(language):
        if language == GameLanguage.LITTLEPY:
            return open("bot.lp", "r").read()

    @staticmethod
    def get_intro():
        return open("intro.md", "r").read()

    @staticmethod
    def get_move_consts():
        consts = Game.get_move_consts()
        consts.update({"teleport": ord("t")})
        return consts

    @staticmethod
    def get_move_names():
        names = Game.get_move_names()
        names.update({ord("t"): "teleport"})
        return names

    def get_score(self):
        return self.score

    def draw_screen(self, libtcod, console):
        # End of the game
        if self.turns >= self.MAX_TURNS:
            self.running = False
            self.msg_panel.add("You are out of moves.")
        elif self.hp <= 0:
            self.running = False
            self.msg_panel += ["You sustained too much damage!"]
            self.map[(self.player_pos[0], self.player_pos[1])] = self.DEAD

        if not self.running:
            self.msg_panel += ["GAME 0VER: Score:" + str(self.score)]

        libtcod.console_set_default_foreground(console, libtcod.white)

        # Update Status
        self.status_panel["Score"] = self.score
        self.status_panel["Move"] = str(self.turns) + " of " + str(self.MAX_TURNS)

        for panel in self.panels:
            panel.redraw(libtcod, console)


if __name__ == '__main__':
    from CYLGame import run
    run(PacBot)
