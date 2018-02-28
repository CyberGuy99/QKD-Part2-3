from src.bobClient import BobClient
from src.utils import randomBits, Photon

class Bob(BobClient):

    def protocol(self):
        num_bits = self.recvClassical()
        threshold = 0.85

        bases = ""
        values = ""

        for i in range(num_bits):
            photon = self.recvPhoton()

            basis = randomBits(1)
            bases += basis

            # dual detector trick
            # 00 -> photon lost
            # 10 -> H/D
            # 01 -> V/A
            # 11 -> dark count

            if basis == "0": split = photon.splitOffH()
            if basis == "1": split = photon.splitOffD()

            meas = split.detect() + photon.detect()
            if meas == "00": values += randomBits(1)
            if meas == "10": values += "0"
            if meas == "01": values += "1"
            if meas == "11": values += randomBits(1)


        good_pos = ""
        sifted_key = ""

        # receive pairs of qubits from Alice
        # one of the two is the one that Alice sent!
        for i in range(num_bits):
            pair = self.recvClassical()
            first = pair[0:2]
            secnd = pair[2:4]

            # try to identify which of the states
            if first[0] != bases[i]: couldBeFirst = True
            else: couldBeFirst = first[1] == values[i]

            if secnd[0] != bases[i]: couldBeSecnd = True
            else: couldBeSecnd = secnd[1] == values[i]

            if couldBeFirst and not couldBeSecnd:
                good_pos += "1"
                sifted_key += first[1]
            if not couldBeFirst and couldBeSecnd:
                good_pos += "1"
                sifted_key += secnd[1]

            if couldBeFirst and couldBeSecnd: good_pos += "0"
            # this can't happen but whatever:
            if not couldBeFirst and not couldBeSecnd: good_pos += "0"

        sift_len = len(sifted_key)

        # tell Alice which ones were good
        self.sendClassical(good_pos)

        shareWhich = self.recvClassical()
        aliceShared = self.recvClassical()

        compareBits = ""
        keepBits = ""
        for i in range(sift_len):
            if shareWhich[i] == "0": keepBits += sifted_key[i]
            if shareWhich[i] == "1": compareBits += sifted_key[i]

        compareGood = 0
        for i in range(len(compareBits)):
            if compareBits[i] == aliceShared[i]: compareGood += 1

        if len(compareBits) == 0: fractionGood = 0
        else: fractionGood = float(compareGood) / float(len(compareBits))
        print("Fraction good: " + str(fractionGood))

        if fractionGood < threshold:
            self.sendClassical("abort")
            return ""
        else:
            self.sendClassical("good")
            return keepBits

if __name__ == "__main__":
    bobClient = Bob()
#   # to set a default ip address, use this:
    # bobClient = Bob(ip="192.168.1.1")
    bobClient.connect()
