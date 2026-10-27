import argparse
import hashlib
import socket
from pathlib import Path

from common import TYPE_DATA, TYPE_END, make_ack, parse_packet

BUFFER_SIZE = 4096
LINGER_SECONDS = 2.0


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


def receive_file(bind_ip, port, output_file):
    output_path = Path(output_file)
    temp_path = output_path.with_suffix(output_path.suffix + ".part")

    expected_seq = 0
    total_bytes = 0
    completed = False
    active_client = None

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((bind_ip, port))
        sock.settimeout(None)

        print(f"Listening on {bind_ip}:{port}")
        print(f"Saving received file as: {output_path}")

        with temp_path.open("wb") as f:
            while not completed:
                packet, client = sock.recvfrom(BUFFER_SIZE)

                # Once the first valid packet is accepted, keep this transfer
                # bound to that client. This prevents another UDP sender from
                # interfering with the current file transfer.
                if active_client is not None and client != active_client:
                    print(f"Ignored packet from unexpected client {client}")
                    continue

                try:
                    packet_type, seq, payload = parse_packet(packet)
                except ValueError as e:
                    print(f"Ignored invalid packet: {e}")
                    continue

                if packet_type == TYPE_DATA:
                    if active_client is None:
                        active_client = client

                    if seq == expected_seq:
                        f.write(payload)
                        total_bytes += len(payload)

                        sock.sendto(make_ack(seq), client)

                        print(
                            f"DATA seq={seq} accepted "
                            f"({len(payload)} bytes)"
                        )

                        expected_seq += 1

                    elif seq < expected_seq:
                        # Duplicate packet: ACK it again.
                        sock.sendto(make_ack(seq), client)
                        print(f"DATA seq={seq} duplicate -> ACK resent")

                    else:
                        # Stop-and-Wait should not normally receive future
                        # sequence numbers, so ignore them.
                        print(
                            f"DATA seq={seq} unexpected; "
                            f"expected={expected_seq}"
                        )

                elif packet_type == TYPE_END:
                    if active_client is None:
                        # An END without any DATA is valid for an empty file.
                        active_client = client

                    if seq == expected_seq:
                        sock.sendto(make_ack(seq), client)
                        completed = True
                        print("END accepted -> final ACK sent")

                    elif seq < expected_seq:
                        # Final ACK may have been lost and END retransmitted.
                        sock.sendto(make_ack(seq), client)

                else:
                    print(f"Ignored unsupported packet type: {packet_type}")

        temp_path.replace(output_path)

        digest = sha256_file(output_path)

        print("\nTransfer complete")
        print(f"Bytes received : {total_bytes}")
        print(f"SHA-256        : {digest}")

        # Keep listening briefly so a retransmitted END gets its ACK.
        sock.settimeout(LINGER_SECONDS)

        while True:
            try:
                packet, client = sock.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                break

            if active_client is not None and client != active_client:
                continue

            try:
                packet_type, seq, _ = parse_packet(packet)
            except ValueError:
                continue

            if packet_type == TYPE_END:
                sock.sendto(make_ack(seq), client)


def main():
    parser = argparse.ArgumentParser(
        description="Stop-and-Wait ARQ UDP file receiver"
    )
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("output")

    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")

    receive_file(
        args.bind,
        args.port,
        args.output,
    )


if __name__ == "__main__":
    main()
