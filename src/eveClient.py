import socket, json, threading, time, random
from config import *
from utils import *
from crypto import *

class EveClient():
    def __init__(self, ip=None):
        self.ip = socket.gethostbyname(socket.gethostname())

        self.alice_ip = ip
        if ip is None:
            self.alice_ip = raw_input("Enter Alice's ip: ")

        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((self.ip, eve_port))
        self.lsock.listen(5)

        self.error = False
        self.ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.ssock.connect((self.alice_ip, alice_port))
        except Exception as e:
            print("Connection refused. Try launching Alice first!")
            self.error = True

        self.alice_conn = None
        self.buffer = []
        self.comms_event = threading.Event()

    def send(self, obj):
        time.sleep(message_delay)
        writer = self.ssock.makefile(mode="w")
        writer.write("delim"+json.dumps(obj))
        writer.flush()


    def listen(self):
        if len(self.buffer) == 0:
            self.comms_event.clear()

            self.comms_event.wait(timeout)
            if len(self.buffer) == 0:
                print(self.buffer)
                import pdb; pdb.set_trace()

        dat = self.buffer[0]
        self.buffer = self.buffer[1:]

        try:
            return json.loads(dat)
        except ValueError:
            print(dat)
            raise ValueError

    def listen_thread(self):
        while True:
            buf = self.alice_conn.recv(1024)

            if len(buf) > 0:
                data = str(buf).split("delim")[1:]
                self.buffer += data
                if len(self.buffer) > 0:
                    self.comms_event.set()
            else:
                self.alice_conn = None
                raise Exception("Alice connection lost")


    def connect(self):
        self.main()

    def main(self):
        if self.error: return

        self.send({"who": "Eve"})

        while True:
            conn, address = self.lsock.accept()
            buf = conn.recv(1024)

            if len(buf) > 0:
                self.alice_conn = conn
                print("Alice connected.")
                break

        thread = threading.Thread(target=self.listen_thread, args=())
        thread.daemon = True
        thread.start()

        collectedBits = ""

        # start protocol
        while True:
            dat = self.listen()
            if "startProtocol" in dat:
                bits = self.protocol()
                print "Eavesdropped bits: " + bits
                collectedBits += bits

                # forward bob's "finished" message
                finished = self.listen()
                finished["eveBitLength"] = len(bits)
                self.send(finished)
            elif "done" in dat:
                print("Done!")
                break
            elif "extraBits" in dat:
                collectedBits += randomBits(dat["extraBits"])
                print("I started eavesdropping late, so I'll prepend my key with random bits.")
            elif "statistics" in dat:

                bobMessage = self.listen()
                self.send(bobMessage) # forward to alice

                self.send({"who": "Eve", "eveBits": collectedBits})

                results = self.listen()["statResults"]
                print results

                timeout = None
            elif "message" in dat:
                print ""
                print "============ One Time Pad ==========="
                encrypted = dat["message"]
                # forward to bob
                self.send(dat)

                print("Evesdropped encrypted message: "+ decode(majVote(encrypted)))

                decrypted = majVote(xor(encrypted, collectedBits))
                print("Decoded message: " + decode(decrypted))

                # forward bob's finished message
                finished = self.listen()
                self.send(finished)
            else:
                raise Exception("Invalid message: " + json.dumps(dat))






        self.alice_conn.close()

    def protocol(self):
        raise NotImplementedError

    # Helper functions for Eve

    def recvClassicalAlice(self):
        return self.recvClassicalInternal("Alice")

    def recvClassicalBob(self):
        return self.recvClassicalInternal("Bob")

    def recvClassicalInternal(self, who):
        # print "Waiting for classical data."
        dat = self.listen()
        if "classical" not in dat:
            raise Exception("Expected classical message, got " + json.dumps(dat))
        else:
            if dat["who"] != who:
                raise Exception("Expected message from " + who + " but got message from " + dat["who"])

            self.send(dat) # immediately forward data

            return dat["classical"]

    # Note: she can't send classical data!

    def recvPhotonAlice(self):
        return self.recvPhotonInternal("Alice")

    def recvPhotonBob(self):
        return self.recvPhotonInternal("Bob")

    def recvPhotonInternal(self, who):
        # print "Waiting for photon."
        dat = self.listen()
        if "photon" not in dat:
            raise Exception("Expected photon, got " + json.dumps(dat))
        else:
            if dat["who"] != who:
                raise Exception("Expected photon from " + who + " but got message from " + dat["who"])

            photon = Photon()
            photon.deserialize(dat["photon"])
            return photon

    def sendPhotonAlice(self, photon):
        # Send info to Alice by impersonating Bob
        self.sendPhotonInternal(photon, "Bob")

    def sendPhotonBob(self, photon):
        # Send info to Bob by impersonating Alice
        self.sendPhotonInternal(photon, "Alice")

    def sendPhotonInternal(self, photon, whoami):
        if random.random() < halfChannelLoss:
            photon.present = False
        self.send({"who": whoami, "photon": photon.serialize()})

    def idealDetect(self, photon):
        if photon.present:
            photon.present = False
            return "1"
        else:
            return "0"

