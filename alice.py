from src.aliceServer import AliceServer
from src.utils import randomBits, Photon

class Alice(AliceServer):

    def protocol(self):

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
