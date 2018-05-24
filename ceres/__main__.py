import argparse
import asyncio
import logging

from ceres.iot import IotCoreClient

logging.basicConfig(level=logging.DEBUG)


def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Ceres Controller.')
    parser.add_argument('--version', action='version', version="0.1")
    parser.add_argument(
        '-k', '--private_key_file',
        required=True, help='Path to private key file.')
    return parser.parse_args()


def main():
    args = parse_command_line_args()

    loop = asyncio.get_event_loop()
    client = IotCoreClient(args.private_key_file, loop)
    try:
        client.connect()
        logging.info("Ceres Controller is running")
        loop.run_forever()
    except KeyboardInterrupt:
        logging.warning("Quit requested")
        client.disconnect()
        loop.close()
        return 0


if __name__ == '__main__':
    main()
