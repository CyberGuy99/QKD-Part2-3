# QKD-Part2-3

QKD Project

Part 2:

Implement alice.py and bob.py.

The template shows how to receive and send classical data and photons.
Photons support a variety of methods. Read up photons in src/utils.py.
Python doesn't support private variables, so don't access those.

Run the project like this:
On one computer: $ python2.7 alice.py
On a different computer: $ python2.7 bob.py

You will be prompted for an ip address every time. 
To set a default, see the comment at the end of alice.py and bob.py

Do not modify anything in src/, except maybe src/config.py.
We'll reset everything in src/ when we grade your project.

Be super careful with the messaging code.
If you forget to receive a message, or receive classical data when
anticipating a photon, your code will crash. I made the exceptions
as helpful as I can, but I'm not perfect. 

If your messages come in out of sync, try increasing the message
delay in src/config.py

If you have any questions message Patrick at patrickjrall@gmail.com
or come to GDC 4.408D from 12 to 3 on Monday or Wednesday.


Part 3:

Study the other team's alice.py and bob.py very very carefully!
Maybe make a diagram of what messages are sent in what order.

Implement eve.py, collecting classical data and intercepting and
re-sending photons. First try to just make Eve wiretap without
causing Alice and Bob's protocol to break completely.

Run Alice first: $ python2.7 alice.py
Run Eve second: $ python2.7 eve.py
Run Bob last: $ python2.7 bob.py

You *can* run Eve after Alice and Bob have started communicating,
but she'll have to guess what they sent beforehand.
The code does this automatically.

Once you can intercept data without breaking, then try to
extract some data from it. If you're not sure, you can always
guess bits at random for 50% success rate! If you can do
better than guessing, e.g. 60% or 70% that's already pretty good.
