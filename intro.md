# Pac-Bot

You're a robot in a very famous arcade game from the 1980s! Earn points by eating pellets. Don't touch the ghosts unless you've eaten an energizer recently! Eat fruits if they appear for a bonus. Go to the next level by eating all the pellets in the maze.

# Rules

Here are some useful game rules:

 * Eat all the pellets in the level to go to the next map.
 * Fruit bonuses increase on upper levels.
 * Energizer pellets allow you to eat ghosts for 50 turns.
 * Eating ghosts gives a score boost.
 * Ghosts are disabled for a short time after they are eaten. 

# Motion

Available moves: `north`, `south`, `east`, and `west`.

# Sensors

Robot can access three types of information: variables, the player's x/y location in the maze, and distance sensors to various types of objects.

## Internal variables

Your robot has access to two internal variables:

 * `lives` -- the number of lives
 * `level` -- the game level (0 is the first level)
 * `energized` -- the number of turns energized remaining (0 means not energized)

## Player position

The position of the player in the map is available in the variables `player_x` and `player_y`. The upper-left corner of the visible screen is 0,0. Unlike in a traditional coordinates system, values increase as you move south (down the screen) and east (to the right). (This arrangement is common in video games.)

## Distance sensors

There are eight distance sensors that show the x and y relative distance between you and the item in question. The items are: `dot` (normal pellets), `power` (power pellets or energizers), `fruit` (the bonus items) and the four ghosts: `blinky`, `inky`, `pinky`, and `clyde`. For example, the variables telling you the x and y distance to the closest dot are named `dot_x` and `dot_y`.
