# Ski Game -- see how far you can get down the mountain
# Name: Example Bot
# VALID MOVES: east, west, north, or teleport (costs 1 HP). Any invalid move will be taken as no move.
# SENSOR TYPES: "distance to" and point sensors
# DISTANCE TO: show distance from YOU to closest item of some type.
#   heart_x, heart_y, coin_x, coin_y, jump_x, jump_y, house_x, house_y
#   Note: negative values represent north or west!
# POINT SENSORS: s1-s7 return value of item over a configurable location
#   Set value of sNx and sNy (where N = 1-7) as offsets from player location; test value of sN to know what is at that point. Value 0 means empty (snow). Other values include: coin, heart, jump, rock, tree, snowman.
# OTHER VARS: hp: your hitpoints (max 10); flying: air time after jump
# COLLISIONS and HP cost: snowman: -1; tree: -2; rock: -10;
# Jumps allow you to fly over obstacles for a random number of turns.

# directly in front of robot
s1x = 0
s1y = -1

# ahead and to left
s2x = -1
s2y = -1

# ahead and to right
s3x = 1
s3y = -1

# remember sensors s4-s7!

move = north

if s1 is not 0 and s1 is not coin and s1 is not heart and s1 is not jump {
   # i need to turn! but which way?
   if s2 is 0 {
	   move = west
   }
   if s3 is 0 {
	   move = east
   }
}

# don't forget about teleport!
