import argparse
import socket
import time
from pathlib import Path

from common import (
    MAX_PAYLOAD,
    TYPE_ACK,
    TYPE_END,
    make_data,
    make_end,
    parse_packet,
)

DEFAULT_TIMEOUT = 1.0
MAX_RETRIES = 10


def wait_for_ack(sock, server, expected_seq, timeout):
    sock.settimeout(timeout)

    while True:
        try:
            packet, sender = sock.recvfrom(4096)

            # Ignore valid packets that did not come from the server we are
            # currently communicating with.
            if sender != server:
                continue

            packet_type, seq, _ = parse_packet(packet)

            if packet_type == TYPE_ACK and seq == expected_seq:
                return True

        except socket.timeout:
            return False
        except ValueError:
            # Ignore corrupted/invalid ACK packets.
            continue


def send_reliably(sock, server, packet, seq, timeout, label):
    for attempt in range(1, MAX_RETRIES + 1):
        sock.sendto(packet, server)

        if wait_for_ack(sock, server, seq, timeout):
            print(f"{label} seq={seq} acknowledged (attempt {attempt})")
            return True

        print(f"{label} seq={seq} timeout -> retransmitting")

    return False


def send_file(server_ip, port, file_path, timeout):
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(path)

    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")

    server = (server_ip, port)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        seq = 0
        total_bytes = 0

        with path.open("rb") as f:
            while True:
                chunk = f.read(MAX_PAYLOAD)
                if not chunk:
                    break

                packet = make_data(seq, chunk)

                if not send_reliably(
                    sock, server, packet, seq, timeout, "DATA"
                ):
                    raise RuntimeError(
                        f"Failed to deliver sequence {seq} after "
                        f"{MAX_RETRIES} attempts"
                    )

                total_bytes += len(chunk)
                seq += 1

        end_packet = make_end(seq)

        if not send_reliably(
            sock, server, end_packet, seq, timeout, "END"
        ):
            raise RuntimeError("Failed to complete file transfer")

        print(
            f"\nTransfer complete: {path.name} "
            f"({total_bytes} bytes, {seq} data packets)"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Reliable file transfer using Stop-and-Wait ARQ over UDP"
    )
    parser.add_argument("server_ip")
    parser.add_argument("file")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)

    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    if args.timeout <= 0:
        parser.error("timeout must be greater than 0")

    start = time.perf_counter()

    send_file(
        args.server_ip,
        args.port,
        args.file,
        args.timeout,
    )

    print(f"Elapsed time: {time.perf_counter() - start:.3f} seconds")


if __name__ == "__main__":
    main()
