# RSA from scratch

My aim with this project was to implement a fully secure p2p chat using RSA. 
I wanted to implement it in python without using any libraries (which I mostly achieved).

## Libraries
While I succeeded in implementing the RSA itself with no external libraries, 
I did use the `Crypto` package for the sole purpose of finding a large (and random) prime number.

I also used the `prompt_toolkit` for the console interface.

```bash
pip install pycryptodome prompt_toolkit
```

## Usage
Run the `main.py` script twice. You will be asked for two ports, 
these should be the same but swapped when you run the script a second time.

The initial connection after both scripts have selected ports may take a while,
sometimes up to a minute. I believe this is due to the computational difficulty 
the initial key generation requires.

Example usage:
```bash
python3 main.py
>> Enter server port: 3141
>> Enter client port: 3142
>> Enter username: Alice
# (wait for other client)
>> Hello
Bob: Why hello
>> 
```
```bash
python3 main.py
>> Enter server port: 3142
>> Enter client port: 3141
>> Enter username: Bob
# (wait for other client)
Alice: Hello
>> Why hello
>> 
```

## Security details

I believe I've implemented RSA correctly such that it is fully secure from an eavesdropper.
It includes secure key exchange, message encryption, and message signing.

However, I do know of two security weaknesses in the current implementation:
1. Padding is not appended to the beginning of messages, so a replay attack could be performed
2. There is no certificate authority for public keys, a man in the middle could pretend to be Bob from the beginning.
