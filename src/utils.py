import random, math
from config import *

def randomBits(n):
    if n == 0: return ""
    return randomBits(n-1) + random.choice(["0","1"])

class Photon():
    def __init__(self):
        self.state = [[1,0],[0,0]] # density matrix
        self.present = True


    # ================== Serialization
    def serialize(self):
        dat = {"state": self.state, "present": self.present}
        self.present = False # photon is gone because it's sent!
        return dat

    def deserialize(self, dat):
        self.state = dat["state"]
        self.present = dat["present"]


    # ================== State prepration

    def prepH(self):
        self.state = [[1,0],[0,0]]
        self.present = True

    def prepV(self):
        self.state = [[0,0],[0,1]]
        self.present = True

    def prepD(self):
        self.state = [[0.5,0.5],[0.5,0.5]]
        self.present = True

    def prepA(self):
        self.state = [[0.5,-0.5],[-0.5,0.5]]
        self.present = True

    # ================== Polarizing Filters

    def filterH(self):
        p = self.state[0][0]
        if random.random() < p:
            self.state = [[1,0],[0,0]]
        else:
            self.state = [[0,0],[0,1]]
            self.present = False

    def filterV(self):
        p = self.state[1][1]
        if random.random() < p:
            self.state = [[0,0],[0,1]]
        else:
            self.state = [[1,0],[0,0]]
            self.present = False

    def filterD(self):
        p = self.state[0][1] + 0.5
        if random.random() < p:
            self.state = [[0.5,0.5],[0.5,0.5]]
        else:
            self.state = [[0.5,-0.5],[-0.5,0.5]]
            self.present = False

    def filterA(self):
        p = self.state[0][1] + 0.5
        if random.random() > p:
            self.state = [[0.5,-0.5],[-0.5,0.5]]
        else:
            self.state = [[0.5,0.5],[0.5,0.5]]
            self.present = False

    # ================== Polarizing Beam Splitters

    def splitOffH(self):
        split = Photon()
        split.prepH()

        p = self.state[0][0]
        if random.random() < p:
            split.present = self.present
            self.present = False
        else:
            split.present = False
        self.state = [[0,0],[0,1]]
        return split

    def splitOffV(self):
        split = Photon()
        split.prepV()

        p = self.state[1][1]
        if random.random() < p:
            split.present = self.present
            self.present = False
        else:
            split.present = False
        self.state = [[1,0],[0,0]]
        return split

    def splitOffD(self):
        split = Photon()
        split.prepD()

        p = self.state[0][1] + 0.5
        if random.random() < p:
            split.present = self.present
            self.present = False
        else:
            split.present = False
        self.state = [[0.5,-0.5],[-0.5,0.5]]
        return split

    def splitOffA(self):
        split = Photon()
        split.prepA()

        p = self.state[0][1] + 0.5
        if random.random() > p:
            split.present = self.present
            self.present = False
        else:
            split.present = False
        self.state = [[0.5,0.5],[0.5,0.5]]
        return split


    # ================== Noise and detection

    # become a maximally mixed state with probability p
    def depolarize(self, p):
        for i in [0,1]:
            for j in [0,1]:
                self.state[i][j] *= 1-p
                if i == j: self.state[i][j] += p/2

    def detect(self):
        if self.present:
            self.present = False  # delete photon
            if random.random() < efficiency: return "1"
            else: return "0"
        else:
            if random.random() < darkChance: return "1"
            else: return "0"
