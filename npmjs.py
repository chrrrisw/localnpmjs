import argparse
from localnpmjs.server import run


def main():
    parser = argparse.ArgumentParser(
        description='Offline npmjs.org registry emulator.')
    parser.add_argument(
        '-p',
        '--port',
        dest='port',
        type=int,
        default=8000,
        help='The port number.')
    parser.add_argument(
        '-c',
        '--cache',
        dest='cache_dir',
        default='./cache',
        help='The cache directory.')
    args = parser.parse_args()

    run(args.port, args.cache_dir)


if __name__ == '__main__':
    main()
