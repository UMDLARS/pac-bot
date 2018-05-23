from __future__ import print_function, division

from CYLGame import GameLanguage, GridGame
from CYLGame import MapPanel
from CYLGame import StatusPanel
from CYLGame.Game import ConstMapping
from CYLGame.Player import DefaultGridPlayer
import sys


DEBUG = False
DUMP_BOT_VARS = False


class Ghost:
    def __init__(self, name, char, edible_char, start_x, start_y, in_house=True):
        self.name = name
        self.char = char
        self.edible_char = edible_char
        self.start_x = start_x
        self.start_y = start_y
        self.pos = [start_x, start_y]
        self.direction = 'a'
        self.alive = True
        self.in_house = in_house  # set to True by default
        self.saved_object = None  # stores a map item we're "on top of"
        self.vulnerable = 0
        self.mode = "frightened"  # scatter, chase, or frightened
        # self.mode = None # scatter, chase, or frightened


class PacBot(GridGame):
    MAP_WIDTH = 30
    MAP_HEIGHT = 33
    SCREEN_WIDTH = MAP_WIDTH
    SCREEN_HEIGHT = MAP_HEIGHT + 6
    MSG_START = 20
    MAX_MSG_LEN = SCREEN_WIDTH - MSG_START - 1
    CHAR_WIDTH = 16
    CHAR_HEIGHT = 16
    GAME_TITLE = "Pac-Bot"
    CHAR_SET = "terminal16x16_gs_ro.png"
    LIVES_START = 4

    SENSE_DIST = 20

    MAX_TURNS = 5000

    # starting positions
    PLAYER_START_X = 14
    PLAYER_START_Y = 24
    BLINKY_START_X = 14
    BLINKY_START_Y = 14
    # start in house for real
    PINKY_START_X = 14
    PINKY_START_Y = 15
    INKY_START_X = 15
    INKY_START_Y = 15
    CLYDE_START_X = 16
    CLYDE_START_Y = 15

    #    # start in hallway for testing
    #    PINKY_START_X = 15
    #    PINKY_START_Y = 12
    #    INKY_START_X = 16
    #    INKY_START_Y = 12
    #    CLYDE_START_X = 17
    #    CLYDE_START_Y = 12

    PLAYER = '@'
    EMPTY = '\0'
    # APPLE = 'O'
    FULL = chr(224)
    DOT = chr(225)
    POWER = chr(226)
    DOOR = chr(227)
    WALL = chr(228)
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
    EDIBLE_BLINKY = chr(218)
    EDIBLE_PINKY = chr(219)
    EDIBLE_INKY = chr(220)
    EDIBLE_CLYDE = chr(221)
    EYES = chr(238)
    EDIBLE = chr(239)

    # fruit
    CHERRY = chr(240)
    STRAWBERRY = chr(241)
    ORANGE = chr(242)
    BELL = chr(243)
    APPLE = chr(244)
    MELON = chr(245)
    GALAXIAN = chr(246)
    KEY = chr(247)
    STAR = chr(43)
    FRUITS = [CHERRY, STRAWBERRY, ORANGE, ORANGE, APPLE, APPLE, MELON, MELON, GALAXIAN, GALAXIAN, BELL, BELL, KEY]
    FRUIT_POINTS = {CHERRY: 100, STRAWBERRY: 300, ORANGE: 500, APPLE: 700,
                    MELON: 1000, GALAXIAN: 2000, BELL: 3000, KEY: 5000}

    # points
    DOT_POINTS = 10
    POWER_POINTS = 50
    GHOST_BASE_POINTS = 200
    ENERGIZED_TURNS = 50
    TOTAL_PELLETS = 253

    # classes of objects for sensors
    GHOST = chr(254)
    FRUIT = chr(255)

    def __init__(self, random):
        self.sensor_coords = []  # variables for adjustable sensors from LP
        self.random = random
        self.running = True
        self.colliding = False
        self.energized = 0  # positive means energized for that many turns
        self.ghost_multiplier = 1
        self.lives = 3
        self.player_pos = [self.PLAYER_START_X, self.PLAYER_START_Y]
        self.score = 0
        self.extra_life = False
        self.objects = []
        self.turns = 0
        self.level = 0
        self.score_panel = StatusPanel(0, 0, self.MAP_WIDTH, 3)
        self.panels = [self.score_panel]
        self.pellets_eaten = 0
        self.fruit_visible = -1

        # array of ghost objects
        # ghosts use the functions in the PacBot object
        self.ghosts = {}
        self.ghosts['blinky'] = Ghost("blinky", self.BLINKY, self.EDIBLE_BLINKY, self.BLINKY_START_X, self.BLINKY_START_Y)
        self.ghosts['pinky'] = Ghost("pinky", self.PINKY, self.EDIBLE_PINKY, self.PINKY_START_X, self.PINKY_START_Y)
        self.ghosts['inky'] = Ghost("inky", self.INKY, self.EDIBLE_INKY, self.INKY_START_X, self.INKY_START_Y)
        self.ghosts['clyde'] = Ghost("clyde", self.CLYDE, self.EDIBLE_CLYDE, self.CLYDE_START_X, self.CLYDE_START_Y)

        # self.__create_map()

    def get_fruit_for_level(self):

        if self.level > len(self.FRUITS):
            return self.KEY
        else:
            return self.FRUITS[self.level]

    def print_ready(self):
        x = 12
        y = 18
        for char in "READY!":
            self.map[(x, y)] = char
            x += 1

    def print_game_over(self):
        x = 10
        y = 18
        for char in "GAME OVER":
            self.map[(x, y)] = char
            x += 1

    def erase_ready(self):
        x = 12
        y = 18
        for char in "READY!":
            self.map[(x, y)] = self.EMPTY
            x += 1

    def redraw_lives(self):

        # erase status line
        for x in range(self.MAP_WIDTH - 1):
            self.map[(1 + x, 33)] = self.EMPTY

        # redraw lives
        for x in range(self.LIVES_START):
            if self.lives > x:
                self.map[(1 + x, 33)] = self.PLAYER

        # redraw the lower-right bar of fruits

        x = self.MAP_WIDTH - 2 - self.level + 1
        for level in range(self.level + 1):
            self.map[(x, 33)] = self.FRUITS[level]
            x = x + 1

    def reset_positions(self):

        self.map[(self.player_pos[0], self.player_pos[1])] = self.EMPTY

        self.player_pos[0] = self.PLAYER_START_X
        self.player_pos[1] = self.PLAYER_START_Y

        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        self.energized = 0

        for g in self.ghosts:

            ghost = self.ghosts[g]

            ghost.vulnerable = 0

            # remove ghosts from their current locations on the map
            # make sure to drop anything they're "carrying"
            if ghost.saved_object:
                self.map[(ghost.pos[0], ghost.pos[1])] = ghost.saved_object
                ghost.saved_object = None
            else:
                self.map[(ghost.pos[0], ghost.pos[1])] = self.EMPTY

            ghost.alive = True
            ghost.mode = "frightened"  # FIXME should be 'scatter'
            if ghost.name == "blinky":
                ghost.pos[0] = ghost.start_x
                ghost.pos[1] = ghost.start_y
                ghost.in_house = True
            elif ghost.name == "pinky":
                ghost.pos[0] = ghost.start_x
                ghost.pos[1] = ghost.start_y
                ghost.in_house = True
            elif ghost.name == "inky":
                ghost.pos[0] = ghost.start_x
                ghost.pos[1] = ghost.start_y
                ghost.in_house = True
            elif ghost.name == "clyde":
                ghost.pos[0] = ghost.start_x
                ghost.pos[1] = ghost.start_y
                ghost.in_house = True

        self.redraw_ghosts()

    def init_board(self):
        self.map = MapPanel(0, 3, self.MAP_WIDTH, self.MAP_HEIGHT + 1, self.EMPTY)
        #                            border=PanelBorder.create(bottom="-"))

        self.panels += [self.map]

        mapmap = {'|': self.WALL,
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

        # reset positions first so ghosts not in maze when filled
        self.reset_positions()

        # make fruit counter negative to eliminate the case when you
        # switch levels when a fruit is visible
        self.fruit_visible = -1

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

        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        self.redraw_ghosts()

        self.redraw_lives()

        self.print_ready()


    def create_new_player(self, prog):
        self.player = DefaultGridPlayer(prog, self.get_move_consts())

        return self.player

    def start_game(self):
        pass

    def do_turn(self):
        self.handle_key(self.player.move)
        self.update_vars_for_player()

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

    def is_ghost(self, item):
        if item == self.BLINKY or item == self.PINKY or item == self.INKY or item == self.CLYDE or item == self.EDIBLE_BLINKY or item == self.EDIBLE_PINKY or item == self.EDIBLE_INKY or item == self.EDIBLE_CLYDE:
            return True
        else:
            return False

    def is_fruit(self, item):
        if item in self.FRUITS:
            return True
        else:
            return False

    def is_blocked(self, item):
        # returns true if the cell in the map is obstructed

        if item == self.DOT or item == self.POWER or item == self.EMPTY or self.is_ghost(item) or self.is_fruit(item) or item == self.PLAYER:
            # since ghosts use is_blocked, players need to be included
            # in things that do not block motion. Strange but true!
            return False
        else:
            return True

    def get_ghost_by_xy(self, x, y):
        for ghost in self.ghosts:
            this_ghost = self.ghosts[ghost]
            if this_ghost.pos[0] == x and this_ghost.pos[1] == y:
                return this_ghost

    def redraw_ghost(self, ghost):
        if ghost.alive:
            if ghost.vulnerable > 10:
                self.map[(ghost.pos[0], ghost.pos[1])] = ghost.edible_char
            elif ghost.vulnerable > 0:
                # blink to "warn" pac-bot of their impending switch
                if self.turns % 2:
                    self.map[(ghost.pos[0], ghost.pos[1])] = ghost.edible_char
                else:
                    self.map[(ghost.pos[0], ghost.pos[1])] = ghost.char
            else:
                self.map[(ghost.pos[0], ghost.pos[1])] = ghost.char

    def redraw_ghosts(self):
        for g in self.ghosts:
            ghost = self.ghosts[g]
            self.redraw_ghost(ghost)

    def check_ghost_collisions(self):
        # detect collisions -- is there a ghost at player's location?
        if self.is_ghost(self.map[(self.player_pos[0], self.player_pos[1])]):

            # figure out which ghost the player has collided with to see
            # if they are vulnerable
            ghost = self.get_ghost_by_xy(self.player_pos[0], self.player_pos[1])

            if ghost.vulnerable > 0:

                ghost.alive = False  # ghost has been eaten!
                self.score += self.ghost_multiplier * self.GHOST_BASE_POINTS

                # check to see if ghost is "holding" a dot / power
                if ghost.saved_object == self.DOT:
                    self.score += self.DOT_POINTS
                    self.pellets_eaten += 1
                    ghost.saved_object = None
                elif ghost.saved_object == self.POWER:
                    self.score += self.POWER_POINTS
                    self.pellets_eaten += 1
                    ghost.saved_object = None

                # increase the score multiplier for ghosts eaten in this
                # round
                self.ghost_multiplier += 1

            else:

                # touching ghosts is bad for you
                self.lives -= 1
                self.reset_positions()

    def move_ghost(self, ghost):
        if ghost.alive == False:
            # if the ghost is "dead" then we should teleport it back to
            # its starting location in the house. 
            ghost.pos[0] = ghost.start_x
            ghost.pos[1] = ghost.start_y
            ghost.vulnerable = 0
            ghost.alive = True
            ghost.in_house = True

        if ghost.mode == "chase":
            # chase pac-bot
            None
        elif ghost.mode == "scatter":
            # go to individual corners
            None
        else:  # mode is frightened
            # run away from pac-bot

            dirs = []  # list of directions we can go

            # determine which directions are open
            item = self.map[(ghost.pos[0] + 1, ghost.pos[1])]
            if not self.is_blocked(item) and not self.is_ghost(item):
                dirs.append("d")

            item = self.map[(ghost.pos[0] - 1, ghost.pos[1])]
            if not self.is_blocked(item) and not self.is_ghost(item):
                dirs.append("a")

            item = self.map[(ghost.pos[0], ghost.pos[1] + 1)]
            if not self.is_blocked(item) and not self.is_ghost(item):
                dirs.append("s")

            item = self.map[(ghost.pos[0], ghost.pos[1] - 1)]
            if ghost.in_house and item == self.DOOR or not self.is_blocked(item) and not self.is_ghost(item):
                dirs.append("w")

            if len(dirs) > 0:

                # if current direction is available, keep going that way
                # (this is historical ghost behavior)

                if ghost.direction in dirs and ghost.in_house == False:

                    choice = ghost.direction

                else:

                    direction = self.random.randint(0, len(dirs) - 1)
                    choice = dirs[direction]

                    ghost.direction = choice

                # if ghost saved an object, drop the object before
                # moving the ghost to the new location, otherwise, 
                # erase the ghost's current location
                if ghost.saved_object:
                    self.map[(ghost.pos[0], ghost.pos[1])] = ghost.saved_object
                    ghost.saved_object = None
                else:
                    self.map[(ghost.pos[0], ghost.pos[1])] = self.EMPTY

                if choice == 'a':
                    ghost.pos[0] -= 1
                elif choice == 'd':
                    ghost.pos[0] += 1
                elif choice == 'w':
                    ghost.pos[1] -= 1
                elif choice == 's':
                    ghost.pos[1] += 1

                # if there is already something at the ghost's new
                # location (a fruit, pellet, or energizer), save it by
                # having the ghost "pick it up"
                if self.map[(ghost.pos[0], ghost.pos[1])] not in [self.EMPTY, self.PLAYER]:
                    ghost.saved_object = self.map[(ghost.pos[0], ghost.pos[1])]

                # if the ghost is just north of the door, set it so that
                # they can't go back into the house
                if self.map[(ghost.pos[0], ghost.pos[1] + 1)] == self.DOOR:
                    ghost.in_house = False

        if ghost.pos[0] == 0 and ghost.pos[1] == 15:
            ghost.pos[0] = 28
        elif ghost.pos[0] == 29 and ghost.pos[1] == 15:
            ghost.pos[0] = 1

        ghost.vulnerable -= 1  # draw down the time the ghost is vulnerable

        # draw the ghost into the map spot so that other ghosts
        # won't share the same spot
        self.redraw_ghost(ghost)
        self.check_ghost_collisions()

    def handle_key(self, key):

        self.turns += 1

        if self.energized > 0:  # count down powered turns
            self.energized -= 1
            if self.energized == 0:
                self.ghost_multiplier = 1  # reset for next time

        if self.pellets_eaten == 1:
            self.erase_ready()

        if DEBUG:
            print("turn: %d player started at (%d, %d)" % (self.turns, self.player_pos[0], self.player_pos[1]))

        self.map[(self.player_pos[0], self.player_pos[1])] = self.EMPTY

        item = self.map[(self.player_pos[0] - 1, self.player_pos[1])]
        if key == "a" and not self.is_blocked(item):
            self.player_pos[0] -= 1

        item = self.map[(self.player_pos[0] + 1, self.player_pos[1])]
        if key == "d" and not self.is_blocked(item):
            self.player_pos[0] += 1

        item = self.map[(self.player_pos[0], self.player_pos[1] - 1)]
        if key == "w" and not self.is_blocked(item):
            self.player_pos[1] -= 1

        item = self.map[(self.player_pos[0], self.player_pos[1] + 1)]
        if key == "s" and not self.is_blocked(item):
            self.player_pos[1] += 1

        if key == "Q":
            self.running = False
            return

        self.check_ghost_collisions()

        # add score based on new position
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.DOT:
            self.score += self.DOT_POINTS
            self.pellets_eaten += 1
        if self.map[(self.player_pos[0], self.player_pos[1])] == self.POWER:
            self.score += self.POWER_POINTS
            self.energized = self.ENERGIZED_TURNS
            self.pellets_eaten += 1

            # make all ghosts vulnerable:

            for g in self.ghosts:
                ghost = self.ghosts[g]
                ghost.vulnerable = self.ENERGIZED_TURNS
                self.redraw_ghosts()

            self.pellets_eaten += 1

        # make fruit appear
        if self.pellets_eaten == 70 or self.pellets_eaten == 170:
            self.map[(14, 18)] = self.get_fruit_for_level()
            self.fruit_visible = 50
        
        # make fruit disappear
        if self.fruit_visible > 0:
            self.fruit_visible = self.fruit_visible - 1
            
        if self.fruit_visible == 0:
            self.map[(14, 18)] = self.EMPTY

        # handle eating fruit
        item = self.map[(self.player_pos[0], self.player_pos[1])]
        if item in self.FRUITS:
            self.score += self.FRUIT_POINTS[item]
            self.fruit_visible = 0

        # handle clearing the board
        if (self.pellets_eaten != 0 and ((self.pellets_eaten % self.TOTAL_PELLETS) == 0)):
            self.level += 1
            self.pellets_eaten = 0
            self.init_board()
            # self.__create_map()

        # handle extra life
        if self.score >= 10000 and self.extra_life == False:
            extra_life = True
            self.lives += 1

        # handle traveling through tunnels in either direction
        if self.player_pos[0] == 0 and self.player_pos[1] == 15:
            self.player_pos[0] = 28
        elif self.player_pos[0] == 29 and self.player_pos[1] == 15:
            self.player_pos[0] = 1

        # put the player in the new position
        self.map[(self.player_pos[0], self.player_pos[1])] = self.PLAYER

        # draw the life meter at the bottom
        self.redraw_lives()

        # move ghosts -- speed based on level
        if self.level == 0 and self.turns % 3 == 0 or self.level == 1 and self.turns % 2 == 0 or self.level > 2:
            for g in self.ghosts:
                ghost = self.ghosts[g]
                self.move_ghost(ghost)

        if DEBUG:
            print("turn: %d player ended at (%d, %d)" % (self.turns, self.player_pos[0], self.player_pos[1]))

        # vars should be gotten at the end of handle_turn, because vars
        # affect the *next* turn...

    def is_running(self):
        return self.running

    def read_bot_state(self, state):
        None

    def get_map_array_tuple(self):
        map_arr = []
        for w in range(0, self.MAP_WIDTH):
            w_arr = []
            for h in range(0, self.MAP_HEIGHT):
#                 item = self.map[(w,h)]
#                 if self.is_blocked(item):
#                     item = ord(self.WALL)
#                 elif self.is_ghost(item):
#                     item = ord(self.GHOST)
#                 elif self.is_fruit(item):
#                     item = ord(self.FRUIT)
#                 else:
#                     item = ord(item)
# 
#                 w_arr.append(item)
#                item = ord(self.map.p_to_char[(w,h)])
#                if self.is_blocked(chr(item)):
#                    item = ord(self.WALL)
                w_arr.append(ord(self.map.p_to_char[(w,h)]))
            map_arr.append(tuple(w_arr))

        return tuple(map_arr)

    

    def update_vars_for_player(self):
        bot_vars = {}

        # what borders player?
        dirmod = {'sense_w': [-1, 0], 'sense_e': [1, 0], 'sense_n': [0, -1], 'sense_s': [0, 1]}

        for sense in dirmod:
            xmod = dirmod[sense][0]
            ymod = dirmod[sense][1]
            obj = self.map[(self.player_pos[0] + xmod, self.player_pos[1] + ymod)]

            if self.is_blocked(obj):
                bot_vars[sense] = ord(self.WALL)
            elif self.is_ghost(obj):
                bot_vars[sense] = ord(self.GHOST)
            elif self.is_fruit(obj):
                bot_vars[sense] = ord(self.FRUIT)
            elif obj == self.DOT:
                bot_vars[sense] = ord(self.DOT)
            elif obj == self.POWER:
                bot_vars[sense] = ord(self.POWER)
            else:
                bot_vars[sense] = ord(self.EMPTY)

        bot_vars['lives'] = self.lives
        bot_vars['energized'] = self.energized
        bot_vars['level'] = self.level
        bot_vars["dot_x"] = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.DOT, default=(0, 0))[0]
        bot_vars["dot_y"] = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.DOT, default=(0, 0))[1]
        bot_vars["power_x"] = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.POWER, default=(0, 0))[0]
        bot_vars["power_y"] = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.POWER, default=(0, 0))[1]
        bot_vars["player_x"] = self.player_pos[0]
        bot_vars["player_y"] = self.player_pos[1]
        
        # get locations for ghosts -- edible or not
        offset = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.BLINKY, default=(0, 0))

        if offset[0] == 0 and offset[1] == 0:
            # blinky doesn't exist, so he must be edible_blinky!
            offset = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.EDIBLE_BLINKY, default=(0, 0))

        bot_vars["blinky_x"] = offset[0]
        bot_vars["blinky_y"] = offset[1]
        
        # rinse and repeat for other ghosts

        offset = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.INKY, default=(0, 0))

        if offset[0] == 0 and offset[1] == 0:
            offset = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.EDIBLE_INKY, default=(0, 0))

        bot_vars["inky_x"] = offset[0]
        bot_vars["inky_y"] = offset[1]
        
        offset = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.PINKY, default=(0, 0))

        if offset[0] == 0 and offset[1] == 0:
            offset = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.EDIBLE_PINKY, default=(0, 0))

        bot_vars["pinky_x"] = offset[0]
        bot_vars["pinky_y"] = offset[1]
        
        offset = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.CLYDE, default=(0, 0))

        if offset[0] == 0 and offset[1] == 0:
            offset = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), self.EDIBLE_CLYDE, default=(0, 0))

        bot_vars["clyde_x"] = offset[0]
        bot_vars["clyde_y"] = offset[1]
        
        # map_array is broken so why slow things down?
        #bot_vars["map_array"] = self.get_map_array_tuple()


        # find closest fruit -- if one exists
        cand_x = 0
        cand_y = 0
        bot_vars['fruit_x'] = 0
        bot_vars['fruit_y'] = 0
        lastfruit = None

        for fruit in self.FRUITS:

            # if we've seen this fruit already, skip it
            if fruit == lastfruit:
                continue
            else:
                lastfruit = fruit

            cand_x = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), fruit, default=(0, 0))[0]
            cand_y = self.map.get_x_y_dist_to_foo(tuple(self.player_pos), fruit, default=(0, 0))[1]

            if cand_x != 0 or cand_y != 0:
                bot_vars['fruit_x'] = cand_x
                bot_vars['fruit_y'] = cand_y
                break

        if DEBUG:
            print("bot_vars:")
            for key in bot_vars.keys():
                if key != "map_array":
                    print("%s : %s" % (key, bot_vars[key]))

        if DUMP_BOT_VARS:
            if "map_array" in bot_vars:
                print("map_array:")
                for row in bot_vars['map_array']:
                    print(row)


        self.player.bot_vars = bot_vars

    @staticmethod
    def default_prog_for_bot(language):
        if language == GameLanguage.LITTLEPY:
            return open("bot.lp", "r").read()

    @staticmethod
    def get_intro():
        return open("intro.md", "r").read()

    @staticmethod
    def get_move_consts():
        return ConstMapping({"west": ord("a"),
                             "east": ord("d"),
                             "south": ord("s"),
                             "north": ord("w"),
                             "DOT": ord(PacBot.DOT),
                             "POWER": ord(PacBot.POWER),
                             "WALL": ord(PacBot.WALL),
                             "GHOST": ord(PacBot.GHOST),
                             "INKY": ord(PacBot.INKY),
                             "PINKY": ord(PacBot.PINKY),
                             "BLINKY": ord(PacBot.BLINKY),
                             "CLYDE": ord(PacBot.CLYDE),
                             "EDIBLE": ord(PacBot.EDIBLE),
                             "EDIBLE_INKY": ord(PacBot.EDIBLE_INKY),
                             "EDIBLE_PINKY": ord(PacBot.EDIBLE_PINKY),
                             "EDIBLE_BLINKY": ord(PacBot.EDIBLE_BLINKY),
                             "EDIBLE_CLYDE": ord(PacBot.EDIBLE_CLYDE),
                             "FRUIT": ord(PacBot.FRUIT),
                             "FRUIT": ord(PacBot.CHERRY),
                             "FRUIT": ord(PacBot.STRAWBERRY),
                             "FRUIT": ord(PacBot.ORANGE),
                             "FRUIT": ord(PacBot.BELL),
                             "FRUIT": ord(PacBot.APPLE),
                             "FRUIT": ord(PacBot.MELON),
                             "FRUIT": ord(PacBot.GALAXIAN),
                             "FRUIT": ord(PacBot.KEY),
                             "FRUIT": ord(PacBot.STAR),
                             "EMPTY": ord(PacBot.EMPTY),
                             "PLAYER": ord(PacBot.PLAYER),
                             "map_height": PacBot.MAP_HEIGHT,
                             "map_width": PacBot.MAP_WIDTH,
                             })

    def get_score(self):
        return self.score

    def draw_screen(self, frame_buffer):
        # End of the game
        if self.turns >= self.MAX_TURNS:
            self.running = False
        elif self.lives <= 0:
            self.running = False
            self.print_game_over()
            # self.map[(self.player_pos[0], self.player_pos[1])] = self.DEAD

        # Update Status
        self.score_panel["Score"] = self.score

        for panel in self.panels:
            panel.redraw(frame_buffer)


if __name__ == '__main__':
    from CYLGame import run

    run(PacBot, avg_game_func=max)
