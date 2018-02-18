from src.aliceServer import AliceServer
from src.utils import randomBits, Photon
import random

class Alice(AliceServer):

    def protocol(self):
        NUM_PHOTONS = 8

        '''
        # make a string of random bits like "10110"
        bits = randomBits(10)

        # send classical data
        self.sendClassical("11010")  # strings
        self.sendClassical(42)       # numbers
        self.sendClassical(True)     # bools

        # prepare and send photons
        photon = Photon()
        photon.prepH()
        self.sendPhoton(photon)

        # Alice can also receive photons
        photon = self.recvPhoton()
        photon.filterH()
        bit = photon.detect()

        # receive some data from bob
        bob_data = self.recvClassical()

        '''

        # randomly select photons
        photons = [Photon() for i in range(NUM_PHOTONS)]
        gates = []
        for p in photons:
            choice = random.choice("HVDA")
            if choice == "H":
                gates.append("HV")
                p.prepH()
            elif choice == "V":
                p.prepV()
                gates.append("HV")
            elif choice == "D":
                p.prepD()
                gates.append("DA")
            elif choice == "A":
                p.prepA()
                gates.append("DA")
            else:
                raise Exception

        # send photons
        for p in photons:
            self.sendPhoton(p)

        bob_measurements = self.recvClassical()
        
        # alice announces his measurements
        encode = lambda g: 0 if g in "HV" else 1
        encodedGates = [str(encode(g)) for g in gates]
        encodedGates = "".join(encodedGates)
        self.sendClassical(encodedGates)

        agree = [bob_measurements[i]  for i in range(NUM_PHOTONS) if bob_measurements[i] == encodedGates[i]]
        print agree
        protocol_succeeded = True

        if protocol_succeeded:
            # return your secret key
            # Alice and Bob *must* return strings
            # of the same length!
            return "101101"
        else:
            # return an empty string things went wrong
            # e.g. if you're suspicious of the channel
            return ""


if __name__ == "__main__":
    aliceServer = Alice()
    # to set a default ip address, use this:
    # aliceServer = Alice(ip="192.168.1.1")
    aliceServer.connect()
