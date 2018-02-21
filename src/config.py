
alice_port = 5000
bob_port = 5001
eve_port = 5002

# how many times to run the protocol
numruns = 10

# for error correction in one-time-pad
blocksize = 3

# sync issues occur if messages are sent too fast
message_delay = 0.01


# drop into a debug console if messages are not
# received in time.
timeout = None

if True:
    halfChannelLoss = 0.01
    halfChannelDepolarize = 0.01

    efficiency = 0.95
    darkChance = 0.05
else:
    halfChannelLoss = 0
    halfChannelDepolarize = 0

    efficiency = 1
    darkChance = 0
