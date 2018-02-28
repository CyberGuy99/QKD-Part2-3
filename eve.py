from src.eveClient import EveClient
from src.utils import randomBits, Photon
import random

class Eve(EveClient):

    def protocol(self):

        num_bits = self.recvClassicalAlice()

        for i in range(num_bits):
            photon = self.recvPhotonAlice()
            self.sendPhotonBob(photon)

        guess_key = ""
        # where alice announces her pairs
        # try to identify which is correct
        for i in range(num_bits):
            pair = self.recvClassicalAlice()
            first = pair[0:2]
            second = pair[2:4]

            cantBeFirst = False
            cantBeSecond = False

            if first[1] == 1:
                cantBeFirst = True
            if second[1] == 0:
                cantBeSecond = True

            if cantBeFirst and not cantBeSecond:
                guess_key += second[1]
            elif cantBeSecond and not cantBeFirst:
                guess_key += first[1]
            else:
                guess_key += randomBits(1)

        good_pos = self.recvClassicalBob()
        sifted_key = "".join([guess_key[i] for i in range(num_bits) if good_pos[i] == "1"])


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
    eveClient = Eve()
    # to set a default ip address, use this:
    # eveClient = Eve(ip="192.168.1.1")
    eveClient.connect()
