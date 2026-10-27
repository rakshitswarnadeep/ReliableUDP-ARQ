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
    host = "0.0.0.0"
    port = 9010
    receiver = SelectiveRepeatReceiver(window_size=4)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        print(f"Selective Repeat receiver listening on port {port}")
        emulator = ChannelEmulator(loss_rate=0.1, seed=1)
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
                print("ACK sent:", seq_num)

            elif packet_type == TYPE_END:
                print("END packet received")

                # END sequence number is the total number of DATA packets.
                # Only finalize when every preceding DATA packet was delivered.
                if seq_num != receiver.base:
                    print(
                        f"END rejected: expected next sequence {receiver.base}, "
                        f"received END sequence {seq_num}. Waiting for missing data."
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
