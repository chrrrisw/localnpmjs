import argparse
from localnpmjs.server import run


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        description='Offline npmjs.org registry emulator.')
    parser.add_argument(
        '-a',
        '--address',
        dest='host',
        type=str,
        default='127.0.0.1',
        help='The hostname or IP address.')
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

    # Run the web server
    run(args.host, args.port, args.cache_dir)


if __name__ == '__main__':
    main()
