import socket, json, threading, math, time
from config import *
from utils import *
from crypto import *

class BobClient():
    def __init__(self, ip=None):
        self.ip = socket.gethostbyname(socket.gethostname())

        self.alice_ip = ip
        if ip is None:
            self.alice_ip = raw_input("Enter Alice's ip: ")

        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((self.ip, bob_port))
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
        # print "Send" + json.dumps(obj)
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
        return json.loads(dat)

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

        self.send({"who": "Bob"})

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
                print "Secure bits: " + bits
                collectedBits += bits
                self.send({"who": "Bob", "finishProtocol": len(bits)})
            elif "done" in dat:
                print("Done!")
                break
            elif "statistics" in dat:
                self.send({"who": "Bob", "bobBits": collectedBits})
                results = self.listen()["statResults"]
                print results
                timeout = None
            elif "message" in dat:

                print ""
                print "============ One Time Pad ==========="
                encrypted = dat["message"]
                print("Got encrypted message: "+ decode(majVote(encrypted)))


                decrypted = majVote(xor(encrypted, collectedBits))

                print("Decrypted message: " + decode(decrypted))

                self.send({"who": "Bob", "finishMessage": True})
            else:
                raise Exception("Invalid message: " + json.dumps(dat))





        self.alice_conn.close()

    def protocol(self):
        raise NotImplementedError

    # Helper functions for Bob

    def recvClassical(self):
        # print "Waiting for classical data."

        dat = self.listen()
        if "classical" not in dat:
            raise Exception("Expected classical message, got " + json.dumps(dat))
        else:
            return dat["classical"]
        pass

    def sendClassical(self, dat):
        # print "Sending classical data"
        self.send({"who": "Bob", "classical": dat})

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
        # print "Sending photon"
        self.send({"who": "Bob", "photon": photon.serialize()})
