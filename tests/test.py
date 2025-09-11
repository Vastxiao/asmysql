import asyncio
from urllib import parse


parsed = parse.urlparse("mysql://root:xiao@192.168.62.195:3306/")

print(parsed)


nob = [0]


async def main():
    now = nob[0]
    # print("start", now)
    nob[0] += 1
    return now


print(asyncio.run(main()))
print(asyncio.run(main()))
print(asyncio.run(main()))
