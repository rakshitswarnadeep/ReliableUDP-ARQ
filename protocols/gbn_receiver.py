import socket
import sys

from common import (
    make_ack,
    parse_packet,
    TYPE_DATA,
    TYPE_END,
)

BUFFER_SIZE = 2048


def receive_file(output_file, receiver_ip, receiver_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((receiver_ip, receiver_port))

    expected_seq = 0
    packet_loss_simulated = False

    print(f"Waiting for data on {receiver_ip}:{receiver_port}")

    with open(output_file, "wb") as file:

        while True:
            packet, sender = sock.recvfrom(BUFFER_SIZE)

            try:
                packet_type, seq, payload = parse_packet(packet)

            except ValueError as error:
                print(f"Invalid packet: {error}")
                continue

            if packet_type == TYPE_DATA:

                # Simulate loss of DATA 1 only once
                if seq == 1 and not packet_loss_simulated:
                    print("SIMULATING PACKET LOSS: DATA 1")
                    packet_loss_simulated = True
                    continue

                if seq == expected_seq:

                    # Correct packet received
                    file.write(payload)

                    print(f"Received DATA {seq}")

                    # Send ACK
                    ack = make_ack(seq)
                    sock.sendto(ack, sender)

                    expected_seq += 1

                elif seq < expected_seq:

                    # Duplicate packet
                    print(f"Duplicate DATA {seq}")

                    # Send ACK again
                    ack = make_ack(seq)
                    sock.sendto(ack, sender)

                else:

                    # Out-of-order packet
                    print(
                        f"Out-of-order DATA {seq}; "
                        f"expected {expected_seq}"
                    )

                    # ACK the last correctly received packet
                    ack = make_ack(expected_seq - 1)
                    sock.sendto(ack, sender)

            elif packet_type == TYPE_END:

                print("Received END")
                break

    sock.close()

    print("File received successfully.")


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage:")
        print(
            "python gbn_receiver.py "
            "<output_file> <receiver_ip> <receiver_port>"
        )
        sys.exit(1)

    output_file = sys.argv[1]
    receiver_ip = sys.argv[2]
    receiver_port = int(sys.argv[3])

    receive_file(
        output_file,
        receiver_ip,
        receiver_port
    )