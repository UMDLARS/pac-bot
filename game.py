from __future__ import print_function
from CYLGame import GameLanguage
from CYLGame import Game
from CYLGame import MessagePanel
from CYLGame import MapPanel
from CYLGame import StatusPanel
from CYLGame import PanelBorder


DEBUG = False


class PacBot(Game):
    MAP_WIDTH = 22
    MAP_HEIGHT = 22
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


    PLAYER = '@'
    EMPTY = '\0'
    LWALL = chr(255)
    UWALL = chr(254)
    DWALL = chr(253)
    RWALL = chr(252)
    UCAP = chr(251)
    DCAP = chr(250)
    RCAP = chr(249)
    LCAP = chr(248)
    ULCOR = chr(247)
    URCOR = chr(246)
    BRCOR = chr(245)
    BLCOR = chr(244)
    URXCOR = chr(243)
    BRXCOR = chr(242)
    BLXCOR = chr(241)
    ULXCOR = chr(240)
    LRWALL = chr(239)
    UDWALL = chr(238)
    FULL = chr(224)
    DOT = chr(225)
    POWER = chr(226)
    DOOR = chr(227)
    

    def __init__(self, random):
        self.sensor_coords = [] # variables for adjustable sensors from LP
        self.random = random
        self.running = True
        self.colliding = False
        self.saved_object = None # stores a map item we're "on top of"
        self.last_move = 'w' # need this to restore objects
        self.flying = 0 # set to some value and decrement (0 == on ground)
        self.hp = 1
        self.player_pos = [self.MAP_WIDTH / 2, self.MAP_HEIGHT - 4]
        self.score = 0
        self.objects = []
        self.turns = 0
        self.level = 1
        self.msg_panel = MessagePanel(self.MSG_START, self.MAP_HEIGHT + 1, self.SCREEN_WIDTH - self.MSG_START, 5)
        self.status_panel = StatusPanel(0, self.MAP_HEIGHT + 1, self.MSG_START, 5)
        self.panels = [self.msg_panel, self.status_panel]
        self.msg_panel.add("Velkommen to Robot Backcountry Skiing!")
        self.msg_panel.add("Move left and right! Don't crash!")

        self.__create_map()

    def __create_map(self):
        self.map = MapPanel(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT + 1, self.EMPTY,
                            border=PanelBorder.create(bottom="-"))

        self.panels += [self.map]

        mapmap = {'Q': self.LWALL,
                  'W': self.RWALL,
                  'E': self.UWALL,
                  'R': self.DWALL,
                  'A': self.LCAP,
                  'S': self.RCAP,
                  'D': self.UCAP,
                  'F': self.DCAP,
                  'Z': self.BLCOR,
                  'X': self.ULCOR,
                  'C': self.BRCOR,
                  'V': self.URCOR,
                  '1': self.BLXCOR,
                  '2': self.ULXCOR,
                  '3': self.BRXCOR,
                  '4': self.URXCOR,
                  'U': self.FULL,
                  'I': self.DOT,
                  'O': self.POWER,
                  'P': self.DOOR,
                  'H': self.LRWALL,
                  'J': self.UDWALL}

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
        
        self.map[(9,15)] = self.PLAYER

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


    def handle_key(self, key):
        self.turns += 1
        if self.flying > 0:
            self.score += self.FLYING_POINTS
            self.flying -= 1
            self.msg_panel += ["In flight for " + str(self.flying) + " turns..."]
            if self.flying == 0:
                self.msg_panel += ["Back on the ground!"]
        else:
            self.score += 1

        if self.turns % 30 == 0:
            self.level += 1

        self.map[(self.player_pos[0], self.player_pos[1])] = self.EMPTY
        if key == "a":
            self.player_pos[0] -= 1
        if key == "d":
            self.player_pos[0] += 1
        if key == "w":
            pass
        if key == "t":
            # horizontal-only teleporting code
            self.msg_panel += ["TELEPORT! (-1 HP)"]
            self.hp -= 1
            self.player_pos[0] = self.random.randint(0, self.MAP_WIDTH - 1)

        if key == "Q":
            self.running = False
            return

        self.last_move = key # save last move for saved_object restoration

        # shift the map
        
        self.colliding = False  # reset colliding variable

        # check for various types of collisions (good and bad)
        if self.flying < 1:
            if self.colliding:
                self.map[(self.player_pos[0], self.player_pos[1])] = self.FULL
            else:
                self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

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
