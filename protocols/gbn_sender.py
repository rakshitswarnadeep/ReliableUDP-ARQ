import socket
import sys
import time

from common import (
    make_data,
    make_end,
    parse_packet,
    TYPE_ACK,
    MAX_PAYLOAD,
)


WINDOW_SIZE = 4
TIMEOUT = 1.0
BUFFER_SIZE = 2048


def send_file(filename, receiver_ip, receiver_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    receiver = (receiver_ip, receiver_port)

    # Read the file and split it into packets
    with open(filename, "rb") as file:
        chunks = []

        while True:
            data = file.read(MAX_PAYLOAD)

            if not data:
                break

            chunks.append(data)

    total_packets = len(chunks)

    base = 0
    next_seq = 0

    print(f"Total packets: {total_packets}")
    print(f"Window size: {WINDOW_SIZE}")

    while base < total_packets:

        # Send packets while the window is not full
        while next_seq < total_packets and next_seq < base + WINDOW_SIZE:
            packet = make_data(next_seq, chunks[next_seq])

            sock.sendto(packet, receiver)

            print(f"Sent DATA {next_seq}")

            next_seq += 1

        try:
            packet, _ = sock.recvfrom(BUFFER_SIZE)

            packet_type, ack_seq, _ = parse_packet(packet)

            if packet_type != TYPE_ACK:
                continue

            print(f"Received ACK {ack_seq}")

            # Cumulative ACK
            if ack_seq >= base:
                base = ack_seq + 1

        except socket.timeout:

            print(f"TIMEOUT - retransmitting from DATA {base}")

            # Go-Back-N:
            # retransmit every unacknowledged packet
            for seq in range(base, next_seq):
                packet = make_data(seq, chunks[seq])

                sock.sendto(packet, receiver)

                print(f"Retransmitted DATA {seq}")

    # Tell receiver that the file is finished
    end_packet = make_end(total_packets)
    sock.sendto(end_packet, receiver)

    print("File transfer complete.")

    sock.close()


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage:")
        print("python gbn_sender.py <file> <receiver_ip> <receiver_port>")
        sys.exit(1)

    filename = sys.argv[1]
    receiver_ip = sys.argv[2]
    receiver_port = int(sys.argv[3])

    send_file(filename, receiver_ip, receiver_port)