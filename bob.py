from src.bobClient import BobClient
from src.utils import randomBits, Photon
import random

class Bob(BobClient):

    def protocol(self):
        NUM_PHOTONS = 8 
        '''
        # receive stuff from alice
        string_of_bits = self.recvClassical()
        answer_to_life = self.recvClassical()
        quantum_is_fun = self.recvClassical()

        # receive and process photons
        photon = self.recvPhoton()
        split = photon.splitOffV()
        bit1 = photon.detect()
        bit2 = split.detect()

        # Bob can also send photons
        photon = Photon()
        photon.prepH()
        self.sendPhoton(photon)

        # send data to alice
        bob_data = randomBits(64)
        self.sendClassical(bob_data)
        '''

        photons = [self.recvPhoton() for i in range(NUM_PHOTONS)]
        gates = [random.choice(["HV", "DA"]) for i in range(NUM_PHOTONS)]

        # measure photons
        measurements = []
        for i in range(NUM_PHOTONS):
            if gates[i] == "HV":
                photons[i].filterH()
                measurements.append(photons[i].detect())
            if gates[i] == "DA":
                photons[i].filterD()
                measurements.append(photons[i].detect())

        
        # bob announces his measurements
        encode = lambda g: 0 if g == "HV" else 1
        encodedGates = [str(encode(g)) for g in gates]
        encodedGates = "".join(encodedGates)
        self.sendClassical(encodedGates)

        # get alices
        alice_measurements = self.recvClassical()

        agree = [alice_measurements[i] for i in range(NUM_PHOTONS) if alice_measurements[i] == encodedGates[i] ]
        print agree

        success = True

        if success:
            # return the string of the same
            # length as Alice's
            return "100011"
        else:
            # abort
            return ""

if __name__ == "__main__":
    bobClient = Bob()
#   # to set a default ip address, use this:
    # bobClient = Bob(ip="192.168.1.1")
    bobClient.connect()
