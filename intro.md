# Pac-Bot

You're a robot in a very famous arcade game from the 1980s! Earn points by eating pellets. Don't touch the ghosts unless you've eaten an energizer recently! Eat fruits if they appear for a bonus. Go to the next level by eating all the pellets in the maze.

# Rules

Here are some useful game rules:

 * Eat all the pellets in the level to go to the next map.
 * Fruit bonuses increase on upper levels.
 * Energizer pellets allow you to eat ghosts for 50 turns.
 * Eating ghosts gives a score boost.
 * Ghosts are disabled for a short time after they are eaten.
 * You lose a life if you are touched by a ghost.

# Motion

Available moves: `north`, `south`, `east`, and `west`. Making a blocked move (moving west when a wall is to the west) is the only way to stop moving.

# Game Objects

The following items can appear in the game map:
 * `empty` -- empty space you can move through (if you can reach it)
 * `dot` -- a "standard" dot
 * `power` -- a "power pellet" -- worth more points and makes ghosts edible for 50 turns
 * `ghost` -- one of the four ghosts
 * `edible` -- a ghost made edible by a power pellet
 * `fruit` -- one of the periodically appearing fruit bonuses
 * `player` -- you!
 * `wall` -- a barrier through which you cannot move

# Accessing Game Data

Robot has access to:
 * variables
 * automatic sensors
 * the map array

## Internal variables

Your robot has access to the following internal variables:

 * `lives` -- the number of lives left
 * `level` -- the game level (0 is the first level)
 * `energized` -- the number of turns energized remaining (0 means not energized)
 * `map_width` and `map_height` -- the dimensions of the playfield.
 * `player_x` and `player_y` -- the position of the player in the map. Unlike the coordinate system you may have learned in math class, the **upper-left** corner of the map is (0,0). Values **increase** as you move south (down the screen) and east (to the right). Thus, the **lower-right** corner of the map is (`map_width`, `map_height`) This arrangement is common in computer graphics.

## Automatic Sensors
### Directional Sensors
Robot has access to four directional sensors that tell you what is directly to the north, south, east, and west of you. Those sensors are `sense_n`, `sense_s`, `sense_e`, and `sense_w`, respectively. You can test for any of the items listed above. For example, `if sense_e is ghost` would be true if a `ghost` were directly to your east.

### Distance Sensors
There are eight distance sensors that show the x and y relative distance between you and the item in question. The items are: `dot` (normal pellets), `power` (power pellets or energizers), `fruit` (the bonus items) and the four ghosts: `blinky`, `inky`, `pinky`, and `clyde`. For example, the variables telling you the x and y distance to the closest dot are named `dot_x` and `dot_y`. If the nearest dot was "five spaces up and four spaces to the right" of the player, `dot_x` would be `4` and `dot_y` would be `-5`.

## Map Array

The map array, a two-dimesional array `map_array` contains the entire playfield. To access it, use `map_array[x][y]` where `x` and `y` specify the exact cell you want to examine. Using nested for loops, you can search the entire map. `map_array[0][0]` contains the upper-left corner of the map, while `map_array[map_width][map_height]` contains the lower-right corner of the map. Items in the map array can by anything from the Game Objects list above. (All ghosts and walls behave the same, so they are simply called `ghost` and `wall`.)
