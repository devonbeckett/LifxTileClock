# LifxTileClock
A Python Program that can turn a Lifx Tile into a digital wall clock.

To run this program you will nedd to update the variable that stores the name of your Lifx Tile. Optionally you can provide a client id
(you can make this up). By default the program will check the time every second and update the tiles only when the minute digits have 
changed. You can reduce this to check less frequently if you want it to.

This program works by broadcasting to the network on the Lifx port, and requsting that all the bulbs report their Label. As responses come
in, the program will check the label against the TILE_NAME I mentioned above. Once the Tile has been identified, it sends the time to the 
device and updates that every minute.

The way the numbers are drawn on the tiles, is by statically storing a bitmap of the color data for each pixel in an array. When the time 
needs to be updated, each tile gets sent a single digit as read from the matching bitmap array. 

The Program was designed around a linear arrangement of 5 Lifx Tiles with the first tile being on the left and then four more to the 
right in a straight row. The center tile is not used and can be freely modified without inturrupting the clock.
