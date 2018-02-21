#! python2.7
import socket, threading, json, time, math, random
from config import *
from crypto import *
from utils import Photon

class AliceServer():
    def __init__(self, ip=None):
        self.ip = ip
        if ip is None:
            self.ip = socket.gethostbyname(socket.gethostname())

        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((self.ip, alice_port))
        self.lsock.listen(5)

        self.bob_ssock = None
        self.eve_ssock = None

        self.bob_conn = None
        self.eve_conn = None
        self.eve_ready = False

        self.buffer = []

        self.comms_event = threading.Event()

        self.photon_count = 0


    def send_bob(self, obj):
        time.sleep(message_delay)
        writer = self.bob_ssock.makefile(mode="w")
        writer.write("delim"+json.dumps(obj))
        writer.flush()

    def send_eve(self, obj):
        time.sleep(message_delay)
        writer = self.eve_ssock.makefile(mode="w")
        writer.write("delim"+json.dumps(obj))
        writer.flush()


    # Blocking call that receives messages from anywhere.
    def listen(self):
        # wait for messages
        if len(self.buffer) == 0:
            self.comms_event.clear()

            self.comms_event.wait(timeout)
            if len(self.buffer) == 0:
                print(self.buffer)
                import pdb; pdb.set_trace()

        dat = self.buffer[0]
        self.buffer = self.buffer[1:]
        return json.loads(dat)

    # Bob's listener thread
    def listen_bob(self):
        # Bob is defs there, no need to wait.

        while True:
            buf = self.bob_conn.recv(1024)

            if len(buf) > 0:
                data = str(buf).split("delim")[1:]
                if self.eve_conn is not None and self.eve_ready:
                    for dat in data: self.send_eve(json.loads(dat))
                else:
                    self.buffer += data
                    if len(self.buffer) > 0:
                        self.comms_event.set()
            else:
                if self.bob_conn == None: break
                raise Exception("Bob connection lost")

    # Eve's listener thread
    def listen_eve(self):
        while self.eve_conn is None:
            conn, address = self.lsock.accept()
            buf = conn.recv(1024)

            if len(buf) > 0:
                dat = str(buf).split("delim")[-1]
                cmd = json.loads(dat)
                if cmd.get("who") == "Eve":
                    self.eve_handshake(conn, address)
                    break

        while True:
            buf = self.eve_conn.recv(1024)

            if len(buf) > 0:
                data = str(buf).split("delim")[1:]
                for dat in data:
                    try:
                        cmd = json.loads(dat)
                        # forward mesages to Bob
                        if cmd["who"] == "Alice":
                            self.send_bob(cmd)
                        else:
                            self.buffer += [dat]

                    except ValueError:
                        print(dat)

                if len(self.buffer) > 0:
                    self.comms_event.set()
            else:
                if self.eve_conn == None: break
                raise Exception("Eve connection lost")


    def bob_handshake(self, conn, address):
        self.bob_conn = conn
        print("Bob connected.")

        self.bob_ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bob_ssock.connect((address[0], bob_port))
        self.send_bob({"who": "Alice"})

    def eve_handshake(self, conn, address):
        self.eve_conn = conn
        print("Eve connected.")

        self.eve_ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.eve_ssock.connect((address[0], eve_port))
        self.send_eve({"who": "Alice"})

    def connect(self):
        self.main()

    def main(self):
        print "Listening on " + self.ip

        while True:
            conn, address = self.lsock.accept()
            buf = conn.recv(1024)

            if len(buf) > 0:
                data = str(buf).split("delim")[-1]
                cmd = json.loads(data)
                if cmd.get("who") == "Bob":
                    self.bob_handshake(conn, address)
                    break
                elif cmd.get("who") == "Eve":
                    self.eve_handshake(conn, address)
                    break

        # start Eve thread
        thread = threading.Thread(target=self.listen_eve, args=())
        thread.daemon = True
        thread.start()

        while self.bob_conn is None:
            conn, address = self.lsock.accept()
            buf = conn.recv(1024)

            if len(buf) > 0:
                data = str(buf).split("delim")[-1]
                cmd = json.loads(data)
                if cmd.get("who") == "Bob":
                    self.bob_handshake(conn, address)
                    break

        # start Bob thread
        thread = threading.Thread(target=self.listen_bob, args=())
        thread.daemon = True
        thread.start()

        aliceBits = ""
        needPadding = self.eve_conn is None

        # ====================== Key Collection

        # bob now connected, start protocol
        for i in range(numruns):
            time.sleep(0.1)
            if self.eve_conn is not None:
                self.eve_ready = True
                if needPadding:
                    self.send_eve({"who": "Alice", "extraBits": len(aliceBits)})
                    needPadding = False


            if self.eve_conn is not None:
                self.send_eve({"who": "Alice", "startProtocol": True})
            self.send_bob({"who": "Alice", "startProtocol": True})
            bits = self.protocol()
            print "Secure bits: " + bits
            aliceBits += bits

            # process bob's finished message
            finished = self.listen()
            if len(bits) != finished["finishProtocol"]:
                raise Exception("Bob collected a different number of bits than Alice!")

            if self.eve_conn is not None and self.eve_ready:
                if len(bits) != finished["eveBitLength"]:
                    raise Exception("Eve collected a different number of bits than Alice and Bob!")


        # ======================= Statistics

        if self.eve_conn is not None:
            self.send_eve({"who": "Alice", "statistics": True})
        self.send_bob({"who": "Alice", "statistics": True})

        bobBits = self.listen()["bobBits"]

        if self.eve_conn is not None:
            eveBits = self.listen()["eveBits"]

        aliceBobGood = 0
        eveGood = 0
        for i in range(len(aliceBits)):
            if aliceBits[i] == bobBits[i]:
                aliceBobGood += 1
                if self.eve_conn is not None:
                    if aliceBits[i] == eveBits[i]:
                        eveGood += 1

        stats = "\n"
        stats += "============ Statistics ===========\n"
        stats += "Total photons sent: " + str(self.photon_count) + "\n"
        stats += "Total bits exchanged: " + str(len(aliceBits)) + "\n"
        stats += "Number of correct bits: " + str(aliceBobGood) + "\n"

        if self.eve_conn is not None:
            stats += "Number of bits correctly eavesdropped: " + str(eveGood)

        print stats
        if self.eve_conn is not None:
            self.send_eve({"who": "Alice", "statResults": stats})
        self.send_bob({"who": "Alice", "statResults": stats})

        # ====================== Messaging Test

        timeout = None

        bitsperchar = blocksize*int(math.log(len(chars),2))

        print ""
        print "============ One Time Pad ==========="
        print "Collected " + str(len(aliceBits)) + " bits of secure key, enough to send a " + str(int(math.floor(len(aliceBits)/bitsperchar))) + " character message."
        print "Enter a message using only the letters '" + str(chars) + "'."

        encoding = ""
        while encoding == "":
            message = raw_input("Message: ")
            message = message.replace("\n", "")

            encoding = padBits(encode(message))
            if len(encoding) > len(aliceBits):
                print "Message too long!"
                encoding = ""

        encrypted = xor(encoding, aliceBits)

        print "Encrypted message: " + decode(majVote(encrypted))

        if self.eve_conn is not None:
            self.send_eve({"who": "Alice", "message": encrypted})
        else:
            self.send_bob({"who": "Alice", "message": encrypted})

        dat = self.listen()
        # process bob's finished message

        self.send_bob({"who": "Alice", "done": True})
        self.bob_conn.close()
        self.bob_conn = None

        if self.eve_conn is not None:
            self.send_eve({"who": "Alice", "done": True})
            self.eve_conn.close()
            self.eve_conn = None


    def protocol(self):
        raise NotImplementedError

    # Helper functions for Alice

    def recvClassical(self):
        # print "Waiting for classical data."
        dat = self.listen()
        if "classical" not in dat:
            raise Exception("Expected classical message, got " + json.dumps(dat))
        else:
            return dat["classical"]

    def sendClassical(self, dat):
        # print "Sending classical data."
        if self.eve_conn is not None and self.eve_ready:
            self.send_eve({"who": "Alice", "classical": dat})
        else:
            self.send_bob({"who": "Alice", "classical": dat})

    def recvPhoton(self):
        # print "Waiting for photon."
        dat = self.listen()
        if "photon" not in dat:
            raise Exception("Expected photon, got " + json.dumps(dat))
        else:
            photon = Photon()
            photon.deserialize(dat["photon"])
            return photon

    def sendPhoton(self, photon):
        self.photon_count += 1
        # print "Sending photon"
        if self.eve_conn is not None and self.eve_ready:
            photon.depolarize(halfChannelDepolarize)
            if random.random() < halfChannelLoss:
                photon.present = False
            self.send_eve({"who": "Alice", "photon": photon.serialize()})
        else:
            photon.depolarize(halfChannelDepolarize)
            photon.depolarize(halfChannelDepolarize)
            if random.random() < halfChannelLoss:
                photon.present = False
            if random.random() < halfChannelLoss:
                photon.present = False

            self.send_bob({"who": "Alice", "photon": photon.serialize()})


