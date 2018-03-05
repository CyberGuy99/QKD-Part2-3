from src.eveClient import EveClient
from src.utils import randomBits, Photon
import random

class Eve(EveClient):

    def protocol(self):

        num_bits = self.recvClassicalAlice()

        # how many bits should we look at to remain undetected
        threshold = 0.15

        bases = ""
        values = ""

        should_look = [True if random.random() < threshold 
                        else False for i in range(num_bits)]

        # try to guess some additional w/o setting off the alarm
        for i in range(num_bits):
            if should_look[i]:
                photon = self.recvPhotonAlice()

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

                self.sendPhotonBob(photon)
            else:
                photon = self.recvPhotonAlice()
                self.sendPhotonBob(photon)
                bases += "0"
                values += "0"


        guess_key = ""

        # where alice announces her pairs
        # try to identify which is correct
        for i in range(num_bits):
            pair = self.recvClassicalAlice()
            first = pair[0:2]
            second = pair[2:4]

            # used for bug exploitation
            cantBeFirst = False
            cantBeSecond = False

            if first[1] == "1":
                cantBeFirst = True
            if second[1] == "0":
                cantBeSecond = True

            # mirroring bob's implementation 
            # of reading qubits
            if should_look[i] and first[0] != bases[i]: couldBeFirst = True
            else: couldBeFirst = first[1] == values[i]

            if should_look[i] and second[0] != bases[i]: couldBeSecnd = True
            else: couldBeSecnd = second[1] == values[i]

            # first try to use exploit
            # then try to use measurement if measurement exists
            # if all fails, random bit
            if cantBeFirst and not cantBeSecond:
                guess_key += second[1]
            elif cantBeSecond and not cantBeFirst:
                guess_key += first[1]
            elif should_look[i] and couldBeFirst and not couldBeSecnd:
                guess_key += first[1]
            elif should_look[i] and not couldBeFirst and couldBeSecnd:
                guess_key += second[1]
            else:
                guess_key += randomBits(1)

        # create sifted key from bob's response
        good_pos = self.recvClassicalBob()
        sifted_key = "".join([guess_key[i] for i in range(num_bits) if good_pos[i] == "1"])


        # remove bits used for comparison
        shareWhich = self.recvClassicalAlice()
        aliceShared = self.recvClassicalAlice()

        compareBits = ""
        keepBits = ""

        for i in range(len(sifted_key)):
            if shareWhich[i] == "0": keepBits += sifted_key[i]
            if shareWhich[i] == "1": compareBits += sifted_key[i]


        # Bob decides if we abort
        abort = self.recvClassicalBob()
        if abort == "abort": return ""

        '''
        # receive data from anybody,
        # but you can't send classical data
        string_of_bits = self.recvClassicalAlice()
        answer_to_life = self.recvClassicalAlice()
        quantum_is_fun = self.recvClassicalAlice()

        # intercept photons and just forward them
        photon = self.recvPhotonAlice()
        self.sendPhotonBob(photon)

        # or intercept and subsitute your own
        photon = self.recvPhotonBob()
        photon.filterD()
        bit = self.idealDetect(photon) # use your fancy ideal detector
        new_photon = Photon()
        new_photon.prepH()
        self.sendPhotonAlice(new_photon)

        # every data that's sent goes through you
        # so even if you don't care, still receive it
        dont_care = self.recvClassicalBob()
        '''

        # return your best guess of the secret key
        # you *must* return a string of the same length
        # so if you don't know, guess randomly!
        return keepBits

if __name__ == "__main__":
    eveClient = Eve(ip='10.147.228.138')
    # to set a default ip address, use this:
    # eveClient = Eve(ip="192.168.1.1")
    eveClient.connect()
