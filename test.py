import asyncio
import pickle
import subprocess

from RiotClientHandel import RiotClientService, find_riot_client
from ValLib import authenticate, User, EndPoints


async def main():
    try:
        with open("cookie.d", mode="rb") as file:
            auth = pickle.load(file)
    except FileNotFoundError:
        auth = await authenticate(User("kbon_bot", "ib@nginput", True))
        with open("cookie.d", mode="wb+") as file:
            pickle.dump(auth, file)
    print(auth.user_id)

    path = find_riot_client()

    RiotClientService.kill_RiotClientServices()
    RiotClientService.CreateAuthenticationFile(auth)

    subprocess.run([path, "--launch-product=valorant --launch-patchline=live --insecure --launch-product=valorant"])


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    loop.run_until_complete(main())
    print("ok")
