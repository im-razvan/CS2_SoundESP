import pyMeow as pm
from math import sqrt, inf
from winsound import Beep
from time import sleep
from requests import get
from os import system

class Config:
    distance = 1300

class Offsets:
    def offset(a):
        return get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/generated/offsets.json").json()['client_dll']['data'][a]['value']

    def client(a, b):
        return get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/generated/client.dll.json").json()[a]['data'][b]['value']

    dwEntityList = offset("dwEntityList")
    dwLocalPlayerPawn = offset("dwLocalPlayerPawn")
    m_iTeamNum = client("C_BaseEntity", "m_iTeamNum")
    m_iHealth = client("C_BaseEntity", "m_iHealth")
    m_vOldOrigin = client("C_BasePlayerPawn", "m_vOldOrigin")
    m_hPlayerPawn = client("CCSPlayerController", "m_hPlayerPawn")

class Entity:
    def __init__(self, proc, pawn):
        self.proc = proc
        self.pawn = pawn
    
    @property
    def team(self):
        return pm.r_int(self.proc, self.pawn + Offsets.m_iTeamNum)
    
    @property
    def health(self):
        return pm.r_int(self.proc, self.pawn + Offsets.m_iHealth)

    @property
    def position(self):
        return pm.r_vec3(self.proc, self.pawn + Offsets.m_vOldOrigin)

def distance(player, entity):
    return sqrt((player["x"] - entity["x"])**2 + (player["y"] - entity["y"])**2 + (player["z"] - entity["z"])**2)

def main():
    while 1:
        system("cls||clear")
        try:
            proc = pm.open_process("cs2.exe")
            base = pm.get_module(proc, "client.dll")["base"]

            print("Started CS2 Sound ESP.")

            while True:
                EntityList = pm.r_uint64(proc, base + Offsets.dwEntityList)

                localPlayer = Entity(proc, pm.r_uint64(proc, base + Offsets.dwLocalPlayerPawn))

                lowestDist = inf

                for i in range(1,64):
                    listEntry = pm.r_uint64(proc, EntityList + (8 * (i & 0x7FFF) >> 9) + 16)
                    if listEntry == 0: continue   
                    entity = pm.r_uint64(proc, listEntry + 120 * (i & 0x1FF))
                    if entity == 0: continue                          
                    entityCPawn = pm.r_uint(proc, entity + Offsets.m_hPlayerPawn)
                    if entityCPawn == 0: continue   
                    listEntry2  = pm.r_uint64(proc, EntityList + 0x8 * ((entityCPawn & 0x7FFF) >> 9) + 16)
                    if listEntry2 == 0: continue 
                    entityPawn = pm.r_uint64(proc, listEntry2 + 120 * (entityCPawn & 0x1FF))
                    if entityPawn == 0: continue 

                    player = Entity(proc, entityPawn)

                    if localPlayer.team != player.team and player.health > 0:
                        dist = distance(localPlayer.position, player.position)
                        if dist < lowestDist:
                            lowestDist = dist

                if lowestDist < Config.distance:
                    pitch = max(1500, 3300 - lowestDist)
                    duration = max(150, lowestDist / 2)
                    Beep(int(pitch), int(duration))
                    sleep(duration/2500)
                else:
                    sleep(.5)
        except:
            print("Process 'cs2.exe' not found, please run 'cs2.exe'\n")
            sleep(3)


if __name__ == "__main__":
    main()
