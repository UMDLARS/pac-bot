# Pac-Bot

You're a robot in a very famous arcade game from the 1980s! Earn points by eating pellets. Don't touch the ghosts unless you've eaten an energizer recently! Eat fruits if they appear for a bonus. Go to the next level by eating all the pellets in the maze.

# Rules

Here are some useful game rules:

 * Eat all the pellets in the level to go to the next map.
 * Fruit bonuses increase in point value on upper levels.
 * Energizer pellets allow you to eat ghosts for 50 turns.
 * Eating ghosts gives a score boost.
 * Ghosts are disabled for a short time after they are eaten.
 * You lose a life if you are touched by a ghost.
 * The game ends when you run out of lives (or turns).

# Motion

Available moves: `north`, `south`, `east`, and `west`. Making a blocked move (moving west when a wall is to the west) is the only way to stop moving.

# Game Objects

The following items can appear in the game map; you can use these as constants to test your sensors, etc. (see below):
 * `DOT` -- a "standard" dot
 * `POWER` -- a "power pellet" -- worth more points and makes ghosts edible for 50 turns
 * `WALL` -- a barrier through which you cannot move
 * `GHOST` -- any one of the four ghosts (they currently act the same way)
 * `EDIBLE` -- a ghost made edible by a power pellet
 * `FRUIT` -- one of the periodically appearing fruit bonuses
 * `EMPTY` -- empty space you can move through (if you can reach it)
 * `PLAYER` -- you!

# Accessing Game Data

Robot has access to the following information:
 * variables -- variables that tell you about general game state
 * automatic sensors -- things that change depending on where you are
 * the map array -- the entire play field

## Internal variables

Your robot has access to the following internal variables:

 * `lives` -- the number of lives left
 * `level` -- the game level (0 is the first level)
 * `energized` -- the number of turns left after eating a power pellet when you can still eat ghosts (0 means not energized)
 * `map_width` and `map_height` -- the dimensions of the playfield.
 * `player_x` and `player_y` -- the position of the player in the map (see below).

## Automatic Sensors
### Directional Sensors
Robot has access to four directional sensors that tell you what is directly to the north, south, east, and west of you. Those sensors are `sense_n`, `sense_s`, `sense_e`, and `sense_w`, respectively. You can test for any of the items listed above. For example, `if sense_e is GHOST` would be true if a `GHOST` were directly to your east.

### Distance Sensors
There are eight distance sensors named `*_x` and `*_y` that show the x and y relative distance between you and the item in question. The items are: `dot` (normal pellets), `power` (power pellets or energizers), `fruit` (the bonus items) and the four ghosts: `blinky`, `inky`, `pinky`, and `clyde`. **For example**, the variables telling you the x and y distance to the closest dot are named `dot_x` and `dot_y`. If the nearest dot was "five spaces up and four spaces to the right" of the player, `dot_x` would be `4` and `dot_y` would be `-5`. (To understand those numbers, read on.)

## Map Array

`map_array` is a two-dimesional array that contains the entire playfield. To access it, use `map_array[x][y]` where `x` and `y` specify the exact cell you want to examine. You can think of it as a map where you can query a specific (x,y) location. Using nested for loops, you can search the entire map.  

Unlike the coordinate system you may have learned in math class, the **upper-left** corner of the map is (0,0). Values **increase** as you move south (down the screen) and east (to the right). Thus, the **lower-right** corner of the map is (`map_width`, `map_height`) This arrangement is common in computer graphics.

For example, `map_array[0][0]` contains the upper-left corner of the map, while `map_array[map_width][map_height]` contains the lower-right corner of the map. `map_array[player_x][player_y]` should always contain `player`, since that's your location! Items in the map array can by anything from the Game Objects list above. (All ghosts and walls behave the same, so they are simply called `GHOST` and `WALL`.) 
