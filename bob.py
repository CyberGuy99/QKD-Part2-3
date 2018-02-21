from src.bobClient import BobClient
from src.utils import randomBits, Photon
import src.config
import random

class Bob(BobClient):

    def protocol(self):
        NUM_PHOTONS = 300 

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

        photons = []
        for i in range(0, NUM_PHOTONS-1, 3):
            while True:
                photons_temp = [self.recvPhoton() for i in range(3)]
                if len(photons_temp) == 3:
                    photons.extend(photons_temp)
                    self.sendClassical("1")
                    break
                else:
                    self.sendClassical("0")

        gates = [random.choice(["HV", "DA"]) for i in range(NUM_PHOTONS/3)]

        # measure photons
        measurements = []
        for i in range(len(gates)):
            if gates[i] == "HV":
                measurements_temp = []
                for p_i in range(3):
                    photons[i*3+p_i].filterV()
                    measurements_temp.append(photons[i*3+p_i].detect())
                measurements.append(max(set(measurements_temp), key=measurements_temp.count))
            if gates[i] == "DA":
                measurements_temp = []
                for p_i in range(3):
                    photons[i*3+p_i].filterA()
                    measurements_temp.append(photons[i*3+p_i].detect())
                measurements.append(max(set(measurements_temp), key=measurements_temp.count))
        
        # bob announces his measurements
        encode = lambda g: 0 if g == "HV" else 1
        encodedGates = [str(encode(g)) for g in gates]
        encodedGates = "".join(encodedGates)
        self.sendClassical(encodedGates)

        # get alices
        alice_measurements = self.recvClassical()

        agree = [measurements[i] for i in range(NUM_PHOTONS/3) if alice_measurements[i] == encodedGates[i] ]
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
    bobClient = Bob(ip="10.148.228.137")
#   # to set a default ip address, use this:
    # bobClient = Bob(ip="192.168.1.1")
    bobClient.connect()
