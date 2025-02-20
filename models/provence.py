from models import dbCon as db
import time
import random
from models import paillierObj as pObj

class provence:

    def __init__(self, pop, name, g, n, canidates, bias) -> None:
        self.pop = pop
        print(pop)
        self.name = name
        self.canidates = canidates
        self.bias = bias
        self.db = db.DBCon() # Connects to the data base
        self.g = g 
        self.n = n

    def runSimulation(self, delay, variance):
        while self.pop > 0:
            waitTime = random.randint(0, delay - random.randint(0, variance))
            votes = random.randint(1, self.pop)
            self.pop -= votes
            canidate = random.randint(1,100)
            # Decides what canidate to choose
            if canidate <= self.bias[0]:
                canidate = self.canidates[0]
            else:
                canidate = self.canidates[1]
            if waitTime > 0:
                time.sleep(waitTime)
            Secret = pObj.paillerObj(self.n, self.g)
            Secret.encrpt(votes)
            
            self.db.insertVotesPT(canidate, self.name, votes)
            self.db.insertVotesEnc(canidate, self.name, Secret.cipherText) # Why break?
        self.db.closeDB()

        pass