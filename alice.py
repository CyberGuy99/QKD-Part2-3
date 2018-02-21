from src.aliceServer import AliceServer
from src.utils import randomBits, Photon
import src.config
import random

class Alice(AliceServer):

    def protocol(self):
        NUM_PHOTONS = 300

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
        sent_bits = []
        gates = []
        for p_index in range(0,NUM_PHOTONS,3):
            choice = random.choice("HVDA")
            if choice == "H":
                sent_bits.append(0);
                gates.append("HV") 
                for i in range(3):
                    p = photons[p_index+i]
                    p.prepH()
            elif choice == "V":
                sent_bits.append(1);
                gates.append("HV") 
                for i in range(3):
                    p = photons[p_index+i]
                    p.prepV()
            elif choice == "D":
                sent_bits.append(0);
                gates.append("DA") 
                for i in range(3):
                    p = photons[p_index+i]
                    p.prepD()
            elif choice == "A":
                sent_bits.append(1);
                gates.append("DA") 
                for i in range(3):
                    p = photons[p_index+i]
                    p.prepA()
            else:
                raise Exception

        # send photons, checking that all are received
        for p_i in range(0, len(photons), 3):
            received = "0"
            while received == "0":
                self.sendPhoton(photons[p_i])
                self.sendPhoton(photons[p_i+1])
                self.sendPhoton(photons[p_i+2])
                received = self.recvClassical()

        bob_measurements = self.recvClassical()
        
        # alice announces her measurements
        # 0 for HV, 1 for DA
        encode = lambda g: 0 if g in "HV" else 1
        encodedGates = [str(encode(g)) for g in gates]
        encodedGates = "".join(encodedGates)
        self.sendClassical(encodedGates)

        agree = [sent_bits[i]  for i in range(NUM_PHOTONS/3) if bob_measurements[i] == encodedGates[i]]

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
    aliceServer = Alice(ip="10.148.228.137")
    # to set a default ip address, use this:
    # aliceServer = Alice(ip="192.168.1.1")
    aliceServer.connect()
