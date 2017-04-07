# Robot Backcountry Skiing

You're a robot skiing in the woods! Turn left or right to avoid obstacles. Don't crash!

# Rules

Every turn you will move downhill one row and earn a point. You decide whether to go left, right, or stay straight ahead. 

A variety of obstacles stand in your way; hitting them will deplete your hitpoints (available in the var `hp`). Hitting a `snowman` costs 1 point. Hitting a `tree` costs 2 points. Hitting a `rock` costs 10 points.

You can add hitpoints by skiing over a `heart` or through a `house`.  Houses are extremely rare.

You can gain 25 extra points by skiing over a `coin`. 

You can fly through the air for a random number of turns by skiing over a rainbow colored `jump`. Each turn in flight is worth 5 points.

The variable `flying` tells you how many more turns you'll be above the ground (0 means you will hit obstacles).

You can teleport, but it costs a hitpoint (and is not guaranteed to put you in a safe position).

# Motion

Available moves: `north`, `west`, `east`, and `teleport`.

# Sensors

Robot can access three types of information: variables, distance sensors, and configurable point sensors.

## Internal variables

Your robot has access to two internal variables:

`hp` -- your current number of hitpoints. You cannot have more than 10 HP.

`flying` -- your height above ground. You won't hit obstacles as long as flying is greater than 0. You fall one unit per turn.

## Distance sensors

Distance sensors tell you the `x` and `y` distance to the closest heart (`heart_x` and `heart_y`), coin (`coin_x` and `coin_y`), jump (`jump_x` and `jump_y`), or house (`house_x` and `house_y`). Just because it is the closest doesn't mean you can get to it. If there is no object in question (e.g., no house on the map) the sensors are set to `0`.

For historical reasons, the coordinates (0,0) represent the upper-left corner of the screen in many graphics applications. This means that a negative `object_x` value means the object is to your left (west) and a negative `object_y` value means the object is ahead of you (to the north).

## Configurable point sensors

Your robot has seven configurable point sensors (`s1`, `s2`, `s3`, `s4`, `s5`, `s6`, and `s7`) that tell you what is located at that point on the map. Common values include: `0` (snow), `rock`, `tree`, `snowman`, `coin`, `heart`, `house`, or `jump`.

You can choose where you want the sensor to "look" (relative to your own position) by setting the variables `sNx` and `sNy` (where `N` is the sensor number 1-7). For example, if you set `s1x` to 0 and `s1y` to -1, the sensor `s1` will tell you what is directly ahead of you. See the sample code for other examples.

