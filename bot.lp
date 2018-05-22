# Robots Example Bot
# Name: Example Bot
# Game: Pac-Bot -- eat the dots to clear the board; eat ghosts after power pellet!
# Things in the game: DOT, POWER, WALL, GHOST, EDIBLE, FRUIT, EMPTY, PLAYER
# Variables: lives, level, energized, map_width, map_height, player_x, player_y
# Point Sensors: sense_n, sense_s, sense_e, sense_w
# Closest Location (x/y) Sensors: dot, power, fruit, blinky, inky, pinky, clyde 
#   e.g.: dot_x and dot_y contain the location of the closest dot relative to player
# Map Array: map_array contains entire map state of things (see above)
#   access using map_array[x][y] to see the thing at location (x,y)
# See 'Intro' tab for more comprehensive documentation!

randmove = 0 # by default we don't want to move randomly

if move is 0 {
    randmove = 1 # pick a random direction if we have never moved
}


# if there is a wall directly in front of us, pick a new random direction
if move is east and sense_e is WALL {
    randmove = 1
}

if move is west and sense_w is WALL {
    randmove = 1
}

if move is north and sense_n is WALL {
    randmove = 1
}

if move is south and sense_s is WALL {
    randmove = 1
}

# what direction should we go?
if randmove is 1 {

	# we want to pick a random direction

    rnd = rand % 4

    if rnd is 0 {
      move = east
    }
    if rnd is 1 {
      move = west
    }
    if rnd is 2 {
      move = north
    }
    if rnd is 3 {
      move = south
    }

} else {
 
	# keep going in current direction
    move = move # sets new value of move to previous value
}

