# Author: Devon Beckett
# email: devonabeckett@gmail.com

import time
from colour import Color
from socket import *
from struct import *

#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# GLOBAL DEFINES
#//////////////////////////////////////////////////////////////////////////////////////////////////////////
LOOP_INTERVAL          = 5      # how often we want to check the time (in seconds)
TILE_NAME              = "Tile" # Set this to what you named your Tile
CLIENT_ID              = 0      # Make Something up
BROADCAST_ADDR         = '255.255.255.255'
LIFX_PORT              = 56700
LIFX_PROTOCOL          = 1024
LIFX_PROTOCOL_TAGGED   = 0b00110100
LIFX_PROTOCOL_UNTAGGED = 0b00010100

# Set this to False to use a 12 hour clock
Clock_Mode_24H = False

# Use one of the following choices for what to do with the center tile.
Center_Tile_Ignore     = 0
Center_Tile_Forground  = 1
Center_Tile_Background = 2
Center_Tile_Colon     = 3

# Set this to one of the above Center_Tile_ choices.
Center_Tile_Use = Center_Tile_Colon



#//////////////////////////////////////////////////////////////////////////////////////////////////////////
# Color Data
#//////////////////////////////////////////////////////////////////////////////////////////////////////////
def hsbk (hue, sat, lum, kel):
        return pack("<HHHH",hue,sat,lum,kel)

c1= Color(rgb=(.5, .5, .5)) # Forground Color
c2= Color(rgb=(0, .25, .25)) # Background Color

# Convert RGB to Hue Saturation Brightnes
hue = int(c1.hue * 65535)
sat = int(c1.saturation * 65535)
brt = int(c1.luminance * 65535)

hue2 = int(c2.hue * 65535)
sat2 = int(c2.saturation * 65535)
brt2 = int(c2.luminance * 65535)

# Convert to HSBK format for Lifx protocol
F = hsbk(hue,sat,brt,0)
B = hsbk(hue2,sat2,brt2,0)


class DeviceMessage:
        GetService = 2
        StateService = 3
        GetHostInfo = 12
        StateHostInfo = 13
        GetHostFirmware = 14
        StateHostFirmware = 15
        GetWifiInfo = 16
        StateWifiInfo = 17
        GetWifiFirmwareLevel = 18
        StateWifiFirmwareLevel = 19
        GetPower = 20
        SetPower = 21
        StatePower = 22
        GetLabel = 23
        SetLabel = 24
        StateLabel = 25
        GetVersion = 32
        StateVersion = 33
        GetInfo = 34
        StateInfo = 35
        Acknowledgement = 45
        GetLocation = 48
        SetLocation = 49
        StateLocation = 50
        GetGroup = 51
        SetGroup = 52
        StateGroup = 53
        EchoRequest = 58
        EchoResponse = 59
# class DeviceMessage

class LightMessage:
        Get = 101
        SetColor = 102
        SetWaveform = 103
        SetWaveFormOptional = 119
        State = 107
        GetPower = 116
        SetPower = 117
        StatePower = 118
        GetInfrared = 120
        StateInfrared = 121
        SetInfrared = 122
# class LightMessage

class MultiZoneMessage:
        NO_APPLY = 0
        APPLY = 1
        APPLY_ONLY = 2

        SetColorZones = 502
        StateZone = 503
        StateMultiZone = 506
# class MultiBoneMessage

class TileMessages:
        GetDeviceChain = 701
        StateDeviceChain = 702
        SetUserPosition = 703
        GetTileState64 = 707
        StateTileState64 = 711
        SetTileState64 = 715
#class TileMessages

##################################################
#        Number Image Data                       #
##################################################

# All the numbers are just arrays of 64 HSBK color values which represent the 8x8 tile
# I have an 'image' for each digit plus one that is all background color. I may add some
# extra characters here like the colon that typically goes between the hours and minutes.
tnull = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,B,B,B,B,B,B,B,
          B,B,B,B,B,B,B,B,
          B,B,B,B,B,B,B,B,
          B,B,B,B,B,B,B,B,
          B,B,B,B,B,B,B,B,
          B,B,B,B,B,B,B,B,
          B,B,B,B,B,B,B,B,
          B,B,B,B,B,B,B,B
         )

tfull = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          F,F,F,F,F,F,F,F,
          F,F,F,F,F,F,F,F,
          F,F,F,F,F,F,F,F,
          F,F,F,F,F,F,F,F,
          F,F,F,F,F,F,F,F,
          F,F,F,F,F,F,F,F,
          F,F,F,F,F,F,F,F,
          F,F,F,F,F,F,F,F
         )

t0 = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,B,F,F,F,F,F,B,
          B,F,B,B,B,B,B,F,
          B,F,B,B,B,B,B,F,
          B,F,B,B,B,B,B,F,
          B,F,B,B,B,B,B,F,
          B,F,B,B,B,B,B,F,
          B,F,B,B,B,B,B,F,
          B,B,F,F,F,F,F,B
         )

t1 = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,B,B,F,F,B,B,B,
          B,B,B,F,F,B,B,B,
          B,B,B,F,F,B,B,B,
          B,B,B,F,F,B,B,B,
          B,B,B,F,F,B,B,B,
          B,B,B,F,F,B,B,B,
          B,B,B,F,F,B,B,B,
          B,B,B,F,F,B,B,B
         )

t2 = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,F,F,F,F,F,B,B,
          B,B,B,B,B,B,F,B,
          B,B,B,B,B,B,F,B,
          B,B,B,B,B,B,F,B,
          B,B,F,F,F,F,B,B,
          B,F,B,B,B,B,B,B,
          B,F,B,B,B,B,B,B,
          B,B,F,F,F,F,F,B
         )

t3 = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,F,F,F,F,F,B,B,
          B,B,B,B,B,B,F,B,
          B,B,B,B,B,B,F,B,
          B,B,F,F,F,F,B,B,
          B,B,B,B,B,B,F,B,
          B,B,B,B,B,B,F,B,
          B,B,B,B,B,B,F,B,
          B,F,F,F,F,F,B,B
         )

t4 = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,B,B,B,B,F,B,B,
          B,B,B,B,B,F,B,B,
          B,F,B,B,B,F,B,B,
          B,F,B,B,B,F,B,B,
          B,F,F,F,F,F,F,B,
          B,B,B,B,B,F,B,B,
          B,B,B,B,B,F,B,B,
          B,B,B,B,B,F,B,B
         )

t5 = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,F,F,F,F,F,F,B,
          B,F,B,B,B,B,B,B,
          B,F,B,B,B,B,B,B,
          B,F,F,F,F,F,B,B,
          B,B,B,B,B,B,F,B,
          B,B,B,B,B,B,F,B,
          B,B,B,B,B,B,F,B,
          B,F,F,F,F,F,B,B
         )

t6 = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,B,F,B,B,B,B,B,
          B,F,B,B,B,B,B,B,
          B,F,B,B,B,B,B,B,
          B,F,B,F,F,F,B,B,
          B,F,F,B,B,B,F,B,
          B,F,B,B,B,B,F,B,
          B,F,B,B,B,B,F,B,
          B,B,F,F,F,F,B,B
         )

t7 = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,B,F,F,F,F,F,B,
          B,B,B,B,B,B,F,B,
          B,B,B,B,B,F,B,B,
          B,B,B,B,F,B,B,B,
          B,B,B,B,F,B,B,B,
          B,B,B,F,B,B,B,B,
          B,B,B,F,B,B,B,B,
          B,B,B,F,B,B,B,B
         )

t8 = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,B,F,F,F,F,B,B,
          B,F,B,B,B,B,F,B,
          B,F,B,B,B,B,F,B,
          B,B,F,F,F,F,B,B,
          B,F,B,B,B,B,F,B,
          B,F,B,B,B,B,F,B,
          B,F,B,B,B,B,F,B,
          B,B,F,F,F,F,B,B
         )

t9 = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,B,B,F,F,F,B,B,
          B,B,F,B,B,B,F,B,
          B,F,B,B,B,B,F,B,
          B,F,B,B,B,B,F,B,
          B,B,F,F,F,F,F,B,
          B,B,B,B,B,B,F,B,
          B,B,B,B,B,B,F,B,
          B,B,B,B,B,B,F,B
         )

tcolon = pack("8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" +
          "8s8s8s8s8s8s8s8s" ,
          B,B,B,B,B,B,B,B,
          B,B,B,F,F,B,B,B,
          B,B,B,F,F,B,B,B,
          B,B,B,B,B,B,B,B,
          B,B,B,B,B,B,B,B,
          B,B,B,F,F,B,B,B,
          B,B,B,F,F,B,B,B,
          B,B,B,B,B,B,B,B
         )

def BuildSetTileState64(tile, num):
        #print "tile[" + str(tile) + "] = " + str(num)
        if num == 0:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, t0)
        elif num == 1:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, t1)
        elif num == 2:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, t2)
        elif num == 3:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, t3)
        elif num == 4:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, t4)
        elif num == 5:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, t5)
        elif num == 6:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, t6)
        elif num == 7:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, t7)
        elif num == 8:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, t8)
        elif num == 9:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, t9)
        elif num == 10:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, tfull)
        elif num == 11:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, tcolon)
        else:
                return pack("<BBxBBBL512s", tile, 1, 0, 0, 8, 0, tnull)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////

##################################################
#      Packet Parser                             #
##################################################
class LifxPacket:
        def __init__(self, msg):
                self.Message = unpack("<HHLQ6xBB8xHxx", msg[0][0:36])
                self.Address = msg[1]
                # Frame    2+2+4+8+6+2+8+2+3 = 16+16+5 = 36
                self.Size = self.Message[0]
                self.Origin = self.Message[1] #need to modify
                self.Tagged = self.Message[1] #need to modify
                self.Addressable = self.Message[1] #need to modify
                self.Protocol = self.Message[1] #need to modify
                self.Source = self.Message[2]
                # Frame Address
                self.Target = self.Message[3]
                self.ACK_Req = self.Message[4]
                self.RES_Req = self.Message[4]
                self.Sequence = self.Message[5]
                # Protocol Header
                self.Type = self.Message[6]
                self.Data = msg[0][36:]
                # No checking done here - should work on that.

        def ProcessPacket(self):
                global LifxBulbs
                bulb = LifxBulb()
                if self.Type == DeviceMessage.StateLabel:
                        for b in LifxBulbs:
                                if b == self.Source:
                                        bulb = b
                        bulb.Name = self.Data.strip()
                        bulb.Address = self.Address
                        print bulb.Name + ": " + bulb.Address[0]
                        if bulb == 0:
                                LifxBulbs.append(bulb)
                                return bulb
                # Do more here eventually I guess



##################################################
#               Bulb Class                       #
##################################################
class LifxBulb:
        Name = ""
        Location = ""
        Group = ""
        Address = ""
        Socket = socket(AF_INET, SOCK_DGRAM)
        Id = 0
        Hue = 0
        Saturation = 0
        Bright = 0
        Kelvin = 0
        Power = 0
        Seq = 0

        def __repr__(self):
                return self.Name

        def __str__(self):
                return self.Name

        def __eq__(self, identifier):
                return self.Id == identifier

        def Send(self, msg):
                self.Socket.sendto(msg, self.Address)


##############################   Lifx Tile Finder   #####################################

m = []
LifxBulbs = []
getServiceMsg = pack("<HBBLQ6xBB8xH3x",
                    # Frame
                    37, # (H) Total message Size
                    0, # (B) Lower byte of the protocol field
                    LIFX_PROTOCOL_TAGGED, # (B) Flags and upper bits of the protocol field
                    CLIENT_ID, # (L) Source
                    # Frame Address
                    0, # (Q) Target: zero = all
                    # (xxxxxx) Reserved
                    1, # (B) Reserved + Response required flag
                    0, # (B) Sequence number
                    # Protocol Header
                    # (xxxxxxxx) Reserved
                    DeviceMessage.GetLabel) # (H) Type
                    # (xx) Reserved
                    # (x) Empty buffer
cs = socket(AF_INET, SOCK_DGRAM)
cs.bind(('',LIFX_PORT))
cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
cs.sendto(getServiceMsg, (BROADCAST_ADDR, LIFX_PORT))
cs.settimeout(5)

print "Looking for " + TILE_NAME
Tile = 0 #default value to detect bulb data later on
while True:
        m = cs.recvfrom(1048)
        packet = LifxPacket(m)
        bulb = packet.ProcessPacket()
        for bulb in LifxBulbs:
                if bulb.Name.find(TILE_NAME) >= 0:
                        print "Found " + TILE_NAME
                        Tile = bulb
                        break
        if Tile != 0:
                break

print "Running clock now."
				
# run loop
minute = -1 # initializing the variable so that the update will trigger right away
while Tile != 0:
        #Check time
        localtime = time.localtime(time.time())

        if minute != localtime.tm_min:
                #print str(localtime.tm_hour) + ':' + str(localtime.tm_min)
                minute = localtime.tm_min
                hour = localtime.tm_hour
                if (Clock_Mode_24H == False) and (hour > 12):
                    hour = hour - 12

                # Hour 10s
                TileState64 = BuildSetTileState64(0,hour / 10)
                TileState64size = len(TileState64)
                msg = pack("<HBBLQ6xBB8xH2x522s",
                           # Frame
                           8 + 16 + 12 + TileState64size, # Size(Frame + Frame Address + Protocol Header + payload
                           0,
                           0b00110100,
                           CLIENT_ID,
                           # Frame Address
                           0,
                           0,
                           Tile.Seq,
                           # Protocol Header
                           TileMessages.SetTileState64,
                           TileState64)

                Tile.Send(msg)
                Tile.Seq += 1
                if Tile.Seq >= 256:
                        Tile.Seq = 0

                # Hour 1s
                TileState64 = BuildSetTileState64(1,hour % 10)
                TileState64size = len(TileState64)
                msg = pack("<HBBLQ6xBB8xH2x522s",
                           # Frame
                           8 + 16 + 12 + TileState64size, # Size(Frame + Frame Address + Protocol Header + payload
                           0,
                           0b00110100,
                           CLIENT_ID,
                           # Frame Address
                           0,
                           0,
                           Tile.Seq,
                           # Protocol Header
                           TileMessages.SetTileState64,
                           TileState64)

                Tile.Send(msg)
                Tile.Seq += 1
                if Tile.Seq >= 256:
                        Tile.Seq = 0

                # Center Tile
                if Center_Tile_Use != Center_Tile_Ignore:
                        if Center_Tile_Use == Center_Tile_Forground:
                                TileState64 = BuildSetTileState64(2,10)
                        if Center_Tile_Use == Center_Tile_Colon:
                                TileState64 = BuildSetTileState64(2,11)
                        else:
                                TileState64 = BuildSetTileState64(2,-1)
                        TileState64size = len(TileState64)
                        msg = pack("<HBBLQ6xBB8xH2x522s",
                                   # Frame
                                   8 + 16 + 12 + TileState64size, # Size(Frame + Frame Address + Protocol Header + payload
                                   0,
                                   0b00110100,
                                   CLIENT_ID,
                                   # Frame Address
                                   0,
                                   0,
                                   Tile.Seq,
                                   # Protocol Header
                                   TileMessages.SetTileState64,
                                   TileState64)

                Tile.Send(msg)
                Tile.Seq += 1
                if Tile.Seq >= 256:
                        Tile.Seq = 0

                # Minute 10s
                TileState64 = BuildSetTileState64(3,minute / 10)
                TileState64size = len(TileState64)
                msg = pack("<HBBLQ6xBB8xH2x522s",
                           # Frame
                           8 + 16 + 12 + TileState64size, # Size(Frame + Frame Address + Protocol Header + payload
                           0,
                           0b00110100,
                           CLIENT_ID,
                           # Frame Address
                           0,
                           0,
                           Tile.Seq,
                           # Protocol Header
                           TileMessages.SetTileState64,
                           TileState64)

                Tile.Send(msg)
                Tile.Seq += 1
                if Tile.Seq >= 256:
                        Tile.Seq = 0

                # Minute 1s
                TileState64 = BuildSetTileState64(4,minute % 10)
                TileState64size = len(TileState64)
                msg = pack("<HBBLQ6xBB8xH2x522s",
                           # Frame
                           8 + 16 + 12 + TileState64size, # Size(Frame + Frame Address + Protocol Header + payload
                           0,
                           0b00110100,
                           CLIENT_ID,
                           # Frame Address
                           0,
                           0,
                           Tile.Seq,
                           # Protocol Header
                           TileMessages.SetTileState64,
                           TileState64)

                Tile.Send(msg)
                Tile.Seq += 1
                if Tile.Seq >= 256:
                        Tile.Seq = 0

        #wake up ever so often and perform this ...
        time.sleep(LOOP_INTERVAL)
