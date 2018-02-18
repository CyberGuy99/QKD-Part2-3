from src.bobClient import BobClient
from src.utils import randomBits, Photon

class Bob(BobClient):

    def protocol(self):

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
