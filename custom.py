import sys

if len(sys.argv) >= 3:
    arg1 = sys.argv[1]
    arg = sys.argv[2]
else:
    print("missing arguments custom.py")
    sys.exit()


def process(arg1, arg):
    import asyncio

    match arg1:
        case "email":
            from ghunt.modules import email

            asyncio.run(email.hunt(None, arg, True))
        case "gaia":
            from ghunt.modules import gaia

            asyncio.run(gaia.hunt(None, arg, True))
        case "drive":
            from ghunt.modules import drive

            asyncio.run(drive.hunt(None, arg, True))


print(process(arg1, arg))
