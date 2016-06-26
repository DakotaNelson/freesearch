import random

import math
import numpy as np
from scipy.integrate import odeint

class bordertile(object):
    '''dummy class for border tiles. gets rid of edge cases.'''
    def __init__(self, loc):
        self.x = loc[0]
        self.y = loc[1]
        self.isedge = True
        self.explored = 0
        self.hasTarg = False

    def color(self):
        return [0, 0, 0]

    def popadd(self,pop):
        self.hum = 0
        self.zom = 0
        self.ded = 0

    def hzrat(self):
        #return is the same as it is for all water tiles
        return 0.0

    def hzdef(self):
        return 0.0

    def setTarget(self, targ):
        self.hasTarg = False

    def hasTarget(self):
        return self.hasTarg

class tile(object):
    '''class for tiles on the map. each tile has a population. sometimes it is water'''
    def __init__(self, targ, loc):
        '''initializes each tile with a location, a population, and a water state'''
        self.x = loc[0]
        self.y = loc[1]
        self.isedge = False
        self.explored = 0
        self.hasTarg = targ

    def setTarget(self, targ):
        self.hasTarg = targ

    def hasTarget(self):
        return self.hasTarg

    def hzd(self):
        if self.isedge:
            return [0, 0, 0]
        alpha = 1.3 # rate at which humans become zombies
        # (i.e. probability of being infected when you come in contact with the infected)
        beta = 1  # rate at which zombies die
        # (i.e. probability of dying when you come in contact with a human)
        gamma = .00002 # rate at which humans die (without becoming zombies)
        # (i.e. probability of dying when you come in contact with another human)
        N = self.oldZom + self.oldHum + self.oldDed
        h2z = (alpha * self.oldZom * self.oldHum) // N  # humans -> zombies
        z2d = (beta * self.oldHum * self.oldZom) // N # zombies -> dead
        h2d = (gamma * self.oldHum * self.oldHum) // N # humans -> dead

        #if self.x == 20 and self.y == 20:
            #print N

        if random.random() < alpha: h2z = math.ceil(h2z)
        else: h2z = math.floor(h2z)

        if random.random() < beta: z2d = math.ceil(z2d)
        else: z2d = math.floor(z2d)

        if random.random() < gamma: h2d = math.ceil(h2d)
        else: h2d = math.floor(h2d)

        # don't create more zombies than there are humans
        if h2z+h2d > self.hum: h2z = self.hum - h2d # give priority to humans killing each other

        if z2d > self.zom: z2d = -self.zom

        deltaH = -h2z-h2d
        deltaZ = h2z-z2d

        # never kill more humans or zombies than exist
        if self.oldHum+deltaH < 0: deltaH = -self.oldHum
        if self.oldZom+deltaZ < 0: deltaZ = -self.oldZom

        return [deltaH, deltaZ, z2d+h2d]

    def update(self):
        '''spits out a new population one time step in the future'''

        self.oldHum = self.hum
        self.oldZom = self.zom
        self.oldDed = self.ded

        # then apply the hzd model
        step = self.hzd()
        self.hum += int(step[0])
        self.zom += int(step[1])
        self.ded += int(step[2])

    def findneighbors(self,tilegrid):
        '''once the entire grid is populated with tiles, find the neighbors'''
        self.left = tilegrid[self.x-1][self.y]
        self.up = tilegrid[self.x][self.y-1]
        self.down = tilegrid[self.x][self.y+1]
        self.right = tilegrid[self.x+1][self.y]
        horiz = [self.left.isedge, self.right.isedge]
        vert = [self.up.isedge, self.down.isedge]
        
##        #lowpass filter
##        if horiz == [True, True] or vert == [True, True]:
##            if self.isedge == False:
##                self.isedge = True
##        if horiz == [False, False] or vert == [False, False]:
##            if self.isedge == True:
##                self.isedge == False

##        self.oldHzrat = self.hzrat()
##        self.oldLeftHzrat = self.left.hzrat()
##        self.oldUpHzrat = self.up.hzrat()
##        self.oldRightHzrat = self.right.hzrat()
##        self.oldDownHzrat = self.down.hzrat()
##        self.oldZom = self.zom
##        self.oldHum = self.hum

    def popadd(self, pop):
        '''add population from people moving when neighbors run popout()'''
        if not self.isedge:
            self.hum += pop[0]
            self.zom += pop[1]
            self.ded += pop[2]
        else:
            pass

    def hzdef(self):
        '''calculate the human-zombie difference. used for math later'''
        return self.hum - self.zom

    def popout(self):
        '''simulates population emigration'''
        #get ratios
        lefthzf = self.oldLeftHzrat
        uphzf = self.oldUpHzrat
        downhzf = self.oldDownHzrat
        righthzf = self.oldRightHzrat
        neighbhzf = lefthzf + uphzf + downhzf + righthzf
        if neighbhzf == 0:
            neighbhzf = 1
        #calculate outflow
        outflow = (0.5/(self.oldHzrat+1))
        zout = math.ceil(outflow*self.oldZom)
        hout = math.ceil(outflow*self.oldHum)
        #comment on american consumerism
        leftpop = [hout*lefthzf//neighbhzf, zout*lefthzf//neighbhzf, 0]
        uppop = [hout*uphzf//neighbhzf, zout*uphzf//neighbhzf, 0]
        downpop = [hout*downhzf//neighbhzf, zout*downhzf//neighbhzf, 0]
        rightpop = [hout*righthzf//neighbhzf, zout*righthzf//neighbhzf, 0]
        outpop = [0, 0, 0]
        for i in range(3):
            outpop[i] = -1*(leftpop[i] + uppop[i] + downpop[i] + rightpop[i])
        # store current variables for next time
        self.oldHzrat = self.hzrat()
        self.oldLeftHzrat = self.left.hzrat()
        self.oldUpHzrat = self.up.hzrat()
        self.oldRightHzrat = self.right.hzrat()
        self.oldDownHzrat = self.down.hzrat()
        self.oldZom = self.zom
        self.oldHum = self.hum
        #now increment everything
        self.left.popadd(leftpop)
        self.up.popadd(uppop)
        self.down.popadd(downpop)
        self.right.popadd(rightpop)
        self.popadd(outpop)

    def hzrat(self):
        '''calculate the human-zombie ratio. used for math later'''
        if False:
           pass
        #if self.hum == 0 and self.zom == 0:
        #    return 0.1
        else:
            try:
                return (float(self.hum + 1))/(float(self.zom)+float(self.hum))
            except ZeroDivisionError:
                return 0.0

    def color(self):
        '''generate a color for the tile. to be used in pygame'''
        if self.hasTarg:
            return [255, 0, 0]
        elif not self.isedge:
            return [0,0,255]
        else:
            return [105,105,105]



