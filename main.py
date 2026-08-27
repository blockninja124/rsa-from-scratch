from hashlib import sha256
from math import gcd
import secrets
import socket
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import asyncio

# Cheating
from Crypto.Util import number as cryptoNumber

S_PORT = int(input("Enter server port: "))
C_PORT = int(input("Enter client port: "))
NAME = input("Enter username: ")

def string_to_int(s):
    return int.from_bytes(s.encode("utf-8"), byteorder="big")

def int_to_string(n):
    length = (n.bit_length() + 7) // 8
    return n.to_bytes(length, byteorder="big").decode("utf-8")

class OwnSecrets():
    def __init__(self) -> None:
        p = cryptoNumber.getPrime(2048)
        q = cryptoNumber.getPrime(2048)

        N = p*q
        totient = int((p-1)*(q-1))

        e = -1
        while True:
            e = secrets.randbelow(totient)
            if gcd(e, totient) == 1:
                break

        self.d = pow(e, -1, totient)
        self.N = N
        self.e = e
    
    def decrypt(self, c: int) -> str:
        i = pow(c, self.d, self.N)
        m = int_to_string(i)
        return m

    def signature(self, m: str) -> int:
        h = sha256()
        h.update(m.encode("utf-8"))
        i = int.from_bytes(h.digest())
        return pow(i, self.d, self.N)


class OthersSecrets():
    def __init__(self, N: int, e: int) -> None:
        self.N = N
        self.e = e

    def encrypt(self, m: str) -> int:
        # todo: add padding
        i = string_to_int(m)
        return pow(i, self.e, self.N)

    def verify_signature(self, sig: int, m: str) -> bool:
        h = sha256()
        h.update(m.encode("utf-8"))
        i = int.from_bytes(h.digest())
        return pow(sig, self.e, self.N) == i


me = OwnSecrets()
them = OthersSecrets(-1, -1)

awaiting_verification = ""

async def receive_thread(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global awaiting_verification

    while True:
        data = await reader.readline()
        if not data: # client disconnected
            break

        request = data.decode().strip()
        if request == "quit":
            print("client disconnected")
            break

        try:
            number = int(request)
            if them.N == -1:
                them.N = number
            elif them.e == -1:
                them.e = number
            else:
                if awaiting_verification == "":
                    awaiting_verification = me.decrypt(number)
                    print(awaiting_verification)
                else:
                    verified = them.verify_signature(number, awaiting_verification)
                    if not verified:
                        print("^ invalid signature!")
                    awaiting_verification = ""

        except:
            continue
            
        #print(number, end="")

        await writer.drain()

    writer.close()
    await writer.wait_closed()




async def send_thread():
    while True:
        try:
            reader, writer = await asyncio.open_connection("localhost", S_PORT)
        except:
            continue
        else:
            print("Connected")
            break

    session = PromptSession()
    e = 0
    with patch_stdout():
        writer.write(f"{me.N}\n".encode("utf-8"))
        await writer.drain()
        writer.write(f"{me.e}\n".encode("utf-8"))
        await writer.drain()

        while e != -1:

            e = await session.prompt_async(">> ")
            msg = f"{NAME}: {e}"
            writer.write(f"{them.encrypt(msg)}\n".encode("utf-8"))
            await writer.drain()
            writer.write(f"{me.signature(msg)}\n".encode("utf-8"))
            await writer.drain()

    writer.close()
    await writer.wait_closed()

async def start_receive_thread():
    server = await asyncio.start_server(receive_thread, 'localhost', C_PORT)
    async with server:
        await server.serve_forever()

async def main():
    server_task = asyncio.create_task(start_receive_thread())
    client_task = asyncio.create_task(send_thread())

    await asyncio.gather(server_task, client_task)

asyncio.run(main())
