# Robots Example Bot
# Name: Example Bot
# You must set move to teleport, east, west, south, north, northeast, northwest, southeast, or southwest to move in the respective directions.
# Any invalid move will be taken as no move.
# You have three types of sensors: stairs, bots, and wreckage
# STAIRS: the stairs are pointed to by x_dir and y_dir
# BOTS: You have 8 sensor zones; directly north, south, east and west of you and the remaining diagonal regions (sense_n, sense_e, sense_w, sense_s, sense_ne, sense_nw, sense_se, sense_sw). The value of the sensor is the distance to the closest bot in the sensor. (Please note LP supports the inequality operators >, <, >=, and <=.
# WRECKAGE: When bots crash, they leave wreckage. The var 'junk_X' is set to 1 when wreckage is directly adjacent to the player (where X is one of n, s, e, w, ne, se, sw, or se).
# The variable 'numbots' holds the number of bots left on the level.

a = rand % 4

if a is 0 {
  move = east
}
if a is 1 {
  move = west
}
if a is 2 {
  move = north
}
if a is 3 {
  move = south
}
