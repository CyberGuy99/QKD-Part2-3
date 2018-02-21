from config import blocksize

chars = "abcdefghijklmnopqrstuvwxyz .,?!$"

def encode(message):
    encoding = ""
    for c in message:
        if c in chars:
            ind = chars.index(c)
            for i in range(1,6):
                encoding += str(int((ind % 2**i)/(2**(i-1))))
                ind -= ind % 2**i
        else:
            print ("Invalid character: " + c)
            return ""
    return encoding

def decode(bits):
    decoded = ""
    for i in range(int(len(bits)/5)):
        subs = bits[i*5:(i+1)*5]
        ind = 0
        for i in range(5):
            if subs[i] == '1': ind += 2**i
        decoded += chars[ind]
    return decoded


def xor(bits1, bits2):
    out = ""
    for i in range(len(bits1)):
        if bits2[i] == "0":
            out += bits1[i]
        else:
            if bits1[i] == "0":
                out += "1"
            else: out += "0"
    return out

def padBits(bits):
    out = ""
    for b in bits:
        out += b*blocksize
    return out

def majVote(bits):
    out = ""
    for i in range(int(len(bits)/blocksize)):
        subs = bits[i*blocksize:(i+1)*blocksize]
        if subs.count("0") > subs.count("1"):
            out += "0"
        else: out += "1"
    return out
