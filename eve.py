from src.eveClient import EveClient
from src.utils import randomBits, Photon
import random

class Eve(EveClient):

    def protocol(self):

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

        they_chickened_out = False

        if they_chickened_out:
            return ""
        else:
            # return your best guess of the secret key
            # you *must* return a string of the same length
            # so if you don't know, guess randomly!
            return "101010"

if __name__ == "__main__":
    eveClient = Eve()
    # to set a default ip address, use this:
    # eveClient = Eve(ip="192.168.1.1")
    eveClient.connect()
