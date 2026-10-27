import argparse

from channel_emulator import ChannelEmulator
import socket
from common import TYPE_DATA, TYPE_END, parse_packet, make_ack


class SelectiveRepeatReceiver:
    def __init__(self, window_size=4):
        self.window_size = window_size
        self.base = 0
        self.buffer = {}
        self.received_data = bytearray()

    def receive_packet(self, seq_num, data):
        if self.base <= seq_num < self.base + self.window_size:
            print("Received packet:", seq_num)
            self.buffer[seq_num] = data
            ack = make_ack(seq_num)
            print("Sending ACK:", seq_num)

            while self.base in self.buffer:
                print("Delivering packet:", self.base)
                self.received_data.extend(self.buffer[self.base])
                del self.buffer[self.base]
                self.base += 1

            return ack

        elif seq_num < self.base:
            print("Duplicate packet:", seq_num)
            return make_ack(seq_num)

        else:
            print("Packet outside window:", seq_num)
            return None



def main():
    parser = argparse.ArgumentParser(
        description="Selective Repeat UDP receiver"
    )
    parser.add_argument("--port", type=int, default=9010)
    parser.add_argument(
        "--loss",
        type=float,
        default=0.1,
        help="ACK loss rate between 0.0 and 1.0"
    )
    args = parser.parse_args()

    if not 0.0 <= args.loss <= 1.0:
        parser.error("--loss must be between 0.0 and 1.0")

    host = "0.0.0.0"
    receiver = SelectiveRepeatReceiver(window_size=4)
    emulator = ChannelEmulator(loss_rate=args.loss, seed=1)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, args.port))
        print(
            f"Selective Repeat receiver listening on port {args.port}"
        )
        print(f"ACK loss rate: {args.loss:.0%}")

        while True:
            packet, address = sock.recvfrom(2048)

            try:
                packet_type, seq_num, payload = parse_packet(packet)
            except ValueError as error:
                print("Invalid packet:", error)
                continue

            if packet_type == TYPE_DATA:
                ack = receiver.receive_packet(seq_num, payload)

                if ack is not None:
                    emulator.transmit(sock, ack, address)

            elif packet_type == TYPE_END:
                print("END packet received")

                if seq_num != receiver.base:
                    print(
                        f"END rejected: expected next sequence "
                        f"{receiver.base}, received END sequence "
                        f"{seq_num}. Waiting for missing data."
                    )
                    continue

                with open("received_test.txt", "wb") as output_file:
                    output_file.write(receiver.received_data)

                print("File saved as received_test.txt")
                sock.sendto(make_ack(seq_num), address)
                break

            else:
                print("Ignoring unexpected packet type:", packet_type)


if __name__ == "__main__":
    main()
