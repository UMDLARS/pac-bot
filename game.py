from __future__ import print_function
from CYLGame import GameLanguage
from CYLGame import Game
from CYLGame import MessagePanel
from CYLGame import MapPanel
from CYLGame import StatusPanel
from CYLGame import PanelBorder


DEBUG = False


class Ski(Game):
    MAP_WIDTH = 60
    MAP_HEIGHT = 30
    SCREEN_WIDTH = 60
    SCREEN_HEIGHT = MAP_HEIGHT + 6
    MSG_START = 20
    MAX_MSG_LEN = SCREEN_WIDTH - MSG_START - 1
    CHAR_WIDTH = 16
    CHAR_HEIGHT = 16
    GAME_TITLE = "Ski"
    CHAR_SET = "terminal16x16_gs_ro.png"

    SENSE_DIST = 20

    LEVELUP_RESPONSES = ["The forest seems to be getting more dense!", "Are there more trees here or what?", "Watch out!", "Better pay attention!"]

    ROBOT_CRASH_RESPONSES = ["OOF!", "OWWWIE!", "THAT'S GONNA LEAVE A MARK!", "BONK!"]
    ROBOT_HEART_RESPONSES = ["Wow, I feel a lot better!", "Shazam!", "That's the ticket!", "Yes!!!"]
    ROBOT_COIN_RESPONSES = ["Cha-ching!", "Badabing!", "Bling! Bling!", "Wahoo!"]
    ROBOT_FLYING_RESPONSES = ["I'm free as a bird now!", "It's a bird, it's a plane...", "Cowabunga!"]

    NUM_OF_ROCKS_START = 30
    NUM_OF_TREES_START = 30
    NUM_OF_SPIKES_START = 30
    NUM_OF_SNOWMAN_START = 30
    NUM_OF_COINS_START = 1
    NUM_OF_HEARTS_START = 1
    NUM_OF_JUMPS_START = 1
    MAX_TURNS = 500
    MAX_FLYING = 10
    FLYING_POINTS = 5
    COIN_POINTS = 25
    HOUSE_ODDS = 500 # e.g., 1/500


    PLAYER = '@'
    EMPTY = '\0'
    HEART = chr(3)
    COIN = chr(4)
    ROCK = chr(15)
    SPIKE = chr(16)
    SNOWMAN = chr(17)
    TRACKS = chr(29)
    TREE = chr(30)
    JUMP = chr(31)
    DEAD = chr(1)
    FLY = chr(2)
    CRASH = chr(8)
    HOUSE = chr(9)

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
        self.place_objects(self.TREE, self.NUM_OF_ROCKS_START)
        self.place_objects(self.ROCK, self.NUM_OF_TREES_START)
        self.place_objects(self.SNOWMAN, self.NUM_OF_SNOWMAN_START)
        self.place_objects(self.COIN, self.NUM_OF_COINS_START)
        self.place_objects(self.HEART, self.NUM_OF_HEARTS_START)
        self.place_objects(self.JUMP, self.NUM_OF_JUMPS_START)

        # make a clearing for the player
        for y in range(8):
            for x in range(self.MAP_WIDTH):
                self.map[(x, self.MAP_HEIGHT - 1 - y)] = self.EMPTY

        # place player
        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        # place decorative trees
        self.map[(self.player_pos[0] + 5, self.player_pos[1])] = self.TREE
        self.map[(self.player_pos[0] - 5, self.player_pos[1])] = self.TREE

        # place initial hearts
        self.map[(self.player_pos[0], self.player_pos[1] - 2)] = self.HEART
        self.map[(self.player_pos[0], self.player_pos[1] - 3)] = self.HEART

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

    def make_new_row(self):
        for x in range(self.MAP_WIDTH):
            here = self.random.randint(0, self.MAX_TURNS)
            if here <= self.turns:
                which = self.random.randint(0, 2)
                if which == 0:
                    self.map[(x, 0)] = self.ROCK
                elif which == 1:
                    self.map[(x, 0)] = self.TREE
                elif which == 2:
                    self.map[(x, 0)] = self.SNOWMAN

        if self.random.randint(0, 100) > 33:
            self.map[(self.random.randint(0, self.MAP_WIDTH - 1), 0)] = self.HEART

        if self.random.randint(0, 100) > 33:
            self.map[(self.random.randint(0, self.MAP_WIDTH - 1), 0)] = self.COIN

        if self.random.randint(0, 100) > 33:
            self.map[(self.random.randint(0, self.MAP_WIDTH - 1), 0)] = self.JUMP

        if self.random.randint(0, self.HOUSE_ODDS) == 1:
            self.map[(self.random.randint(0, self.MAP_WIDTH - 1), 0)] = self.HOUSE

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


    def shift_map(self):
        # shift all rows down
        dx = (self.MAP_WIDTH / 2) - self.player_pos[0]
        self.map.shift_all((dx, 1), wrap_x=True)
        self.player_pos[0] += dx

        self.make_new_row()

        self.restore_object_tracks()

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
        self.shift_map()
        
        self.colliding = False  # reset colliding variable

        # check for various types of collisions (good and bad)
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.ROCK:
            self.save_object(self.ROCK)
            if self.flying == 0:
                self.colliding = True
                self.hp -= 10
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_CRASH_RESPONSES) - set(self.msg_panel.get_current_messages())))]

        elif self.map[(self.player_pos[0], self.player_pos[1])] == self.TREE:
            self.save_object(self.TREE)
            if self.flying == 0:
                self.colliding = True
                self.hp -= 2
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_CRASH_RESPONSES) - set(self.msg_panel.get_current_messages())))]

        elif self.map[(self.player_pos[0], self.player_pos[1])] == self.SNOWMAN:
            if self.flying == 0:
                self.colliding = True
                self.hp -= 1
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_CRASH_RESPONSES) - set(self.msg_panel.get_current_messages())))]
            else:
                self.save_object(self.SNOWMAN) # flying over snowmen is nondestructive

        elif self.map[(self.player_pos[0], self.player_pos[1])] == self.HEART:
            if self.flying == 0:
                if self.hp < 10:
                    self.hp += 1
                    self.msg_panel += [self.random.choice(list(set(self.ROBOT_HEART_RESPONSES) - set(self.msg_panel.get_current_messages())))]
                else:
                    self.msg_panel += ["Your HP is already full!"]
            else:
                self.save_object(self.HEART)

        elif self.map[(self.player_pos[0], self.player_pos[1])] == self.HOUSE:
            if self.flying == 0:
                self.hp = 10
                self.msg_panel += ["This cabin was very refreshing!"]
            else:
                self.save_object(self.HOUSE)


        elif self.map[(self.player_pos[0], self.player_pos[1])] == self.COIN:
            if self.flying == 0:
                self.score += self.COIN_POINTS
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_COIN_RESPONSES) - set(self.msg_panel.get_current_messages())))]
            else:
                self.save_object(self.COIN)

        elif self.map[(self.player_pos[0], self.player_pos[1])] == self.JUMP:
            if self.flying == 0:
                self.save_object(self.JUMP)
                self.flying += self.random.randint(2, self.MAX_FLYING)
                self.msg_panel += [self.random.choice(list(set(self.ROBOT_FLYING_RESPONSES) - set(self.msg_panel.get_current_messages())))]
            else:
                self.save_object(self.JUMP)

        # draw player
        if self.flying < 1:
            if self.colliding:
                self.map[(self.player_pos[0], self.player_pos[1])] = self.CRASH
            else:
                self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        else:
            self.map[(self.player_pos[0], self.player_pos[1])] = self.FLY

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
        bot_vars = {"jump_x": self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.JUMP, default=(0, 0))[0],
                    "jump_y": self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.JUMP, default=(0, 0))[1],
                    "heart_x": self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.HEART, default=(0, 0))[0],
                    "heart_y": self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.HEART, default=(0, 0))[1],
                    "coin_x": self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.COIN, default=(0, 0))[0],
                    "coin_y": self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.COIN, default=(0, 0))[1],
                    "house_x": self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.HOUSE, default=(0, 0))[0],
                    "house_y": self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.HOUSE, default=(0, 0))[1],
                    "hp": 0, "flying": 0, "s1": 0, "s2": 0, "s3": 0, "s4": 0, "s5": 0, "s6": 0, "s7": 0}

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
        consts.update({"heart": ord(Ski.HEART)})
        consts.update({"coin": ord(Ski.COIN)})
        consts.update({"rock": ord(Ski.ROCK)})
        consts.update({"spikes": ord(Ski.SPIKE)})
        consts.update({"snowman": ord(Ski.SNOWMAN)})
        consts.update({"tracks": ord(Ski.TRACKS)})
        consts.update({"tree": ord(Ski.TREE)})
        consts.update({"jump": ord(Ski.JUMP)})
        consts.update({"house": ord(Ski.HOUSE)})
        return consts

    @staticmethod
    def get_move_names():
        names = Game.get_move_names()
        names.update({ord("t"): "teleport"})
        names.update({ord(Ski.HEART): "heart"})
        names.update({ord(Ski.COIN): "coin"})
        names.update({ord(Ski.ROCK): "rock"})
        names.update({ord(Ski.SPIKE): "spikes"})
        names.update({ord(Ski.SNOWMAN): "snowman"})
        names.update({ord(Ski.TRACKS): "tracks"})
        names.update({ord(Ski.TREE): "tree"})
        names.update({ord(Ski.JUMP): "jump"})
        names.update({ord(Ski.HOUSE): "house"})
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
        self.status_panel["HP"] = self.HEART * self.hp

        for panel in self.panels:
            panel.redraw(libtcod, console)


if __name__ == '__main__':
    from CYLGame import run
    run(Ski)
