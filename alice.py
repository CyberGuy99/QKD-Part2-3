from src.aliceServer import AliceServer
from src.utils import randomBits, Photon

class Alice(AliceServer):

    def protocol(self):

        # Instead of implementing BB84 I implemented:
        # https://en.wikipedia.org/wiki/SARG04
        # Good luck!

        num_bits = 200
        self.sendClassical(num_bits)

        # send photons in random bases
        values = randomBits(num_bits)
        bases = randomBits(num_bits)

        for i in range(num_bits):
            photon = Photon()
            if values[i] == "0" and bases[i] == "0": photon.prepH()
            if values[i] == "1" and bases[i] == "0": photon.prepV()
            if values[i] == "0" and bases[i] == "1": photon.prepD()
            if values[i] == "1" and bases[i] == "1": photon.prepA()
            self.sendPhoton(photon)

        # four pairs of qubit states, one in each basis
        # 00 10 = {|H>, |D>}
        # 00 11 = {|H>, |A>}
        # 01 10 = {|V>, |D>}
        # 01 11 = {|V>, |A>}

        for i in range(num_bits):
            # prepare a pair containing my state
            myQubit = bases[i] + values[i]
            randQubit = ("0" if bases[i] == "1" else "1") + randomBits(1)

            # swap with 50% chance so my state is not always first
            if values[i] == "0": send = myQubit + randQubit
            else: send = randQubit + myQubit

            self.sendClassical(send)

        # receieve good positions from Bob
        good_pos = self.recvClassical()
        sifted_key = "".join([values[i] for i in range(num_bits) if good_pos[i] == "1"])
        sift_len = len(sifted_key)


        # share a random half of the bits to Bob
        shareWhich = randomBits(sift_len)
        shareBits = ""
        keepBits = ""
        for i in range(sift_len):
            if shareWhich[i] == "0": keepBits += sifted_key[i]
            if shareWhich[i] == "1": shareBits += sifted_key[i]
        self.sendClassical(shareWhich)
        self.sendClassical(shareBits)

        # Bob decides if we abort
        abort = self.recvClassical()
        if abort == "abort": return ""
        return keepBits


if __name__ == "__main__":
    aliceServer = Alice()
    # to set a default ip address, use this:
    # aliceServer = Alice(ip="192.168.1.1")
    aliceServer.connect()
