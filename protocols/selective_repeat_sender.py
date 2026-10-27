from email import parser

from channel_emulator import ChannelEmulator
import argparse
import socket
import time
import hashlib

from common import (
    MAX_PAYLOAD,
    TYPE_ACK,
    TYPE_END,
    make_data,
    make_end,
    parse_packet,
)

WINDOW_SIZE = 4
TIMEOUT = 1.0
MAX_RETRIES = 10
def send_file(filename, receiver_ip, receiver_port, loss_rate=0.1):
    receiver = (receiver_ip, receiver_port)
    emulator = ChannelEmulator(loss_rate= loss_rate, seed=1)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0.1)

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
        acked = set()
        sent_times = {}
        packets = {}
        retries = {}
        srtt = None
        rttvar = None
        rto = 1.0
        retransmitted = set()

        print("Total packets:", total_packets)
        print("Window size:", WINDOW_SIZE)

             # TODO 1: Send packets within the window.
        while base < total_packets:
            while (
                next_seq < total_packets
                and next_seq < base + WINDOW_SIZE
            ):
              packet = make_data(next_seq, chunks[next_seq])
              packets[next_seq] = packet
              emulator.transmit(sock, packet, receiver)
              sent_times[next_seq] = time.monotonic()
              retries[next_seq] = 0
              retransmitted.discard(next_seq)
              print(f"Sent packet {next_seq}")
              next_seq += 1

            # TODO 2 and 3: Receive and record an ACK.
            try:
                ack_packet, address = sock.recvfrom(2048)
                packet_type, ack_seq, payload = parse_packet(ack_packet)

                if packet_type == TYPE_ACK and address == receiver:
                  if ack_seq in packets and ack_seq not in acked:

                    if ack_seq not in retransmitted and ack_seq in sent_times:
                      sample = time.monotonic() - sent_times[ack_seq]

                      if srtt is None:
                        srtt = sample
                        rttvar = sample / 2
                      else:
                        rttvar = 0.75 * (rttvar if rttvar is not None else 0.0) + 0.25 * abs(srtt - sample)
                        srtt = 0.875 * srtt + 0.125 * sample

                      rto = max(0.1, min(60.0, srtt + max(0.001, 4 * rttvar)))
                      print(
                      f"RTT: {sample:.3f}s, "
                      f"SRTT: {srtt:.3f}s, RTO: {rto:.3f}s"
                   )

                    acked.add(ack_seq)
                    sent_times.pop(ack_seq, None)
                    print(f"Received ACK {ack_seq}")

            except socket.timeout:
                pass
            except ValueError as error:
                print("Invalid ACK packet:", error)

            # TODO 4: Advance the window.
            while base in acked:
                base += 1

            # TODO 5 and 6: Check timers and retransmit expired packets.
            current_time = time.monotonic()

            for seq in list(sent_times):
                if current_time - sent_times[seq] >= rto:
                    if retries[seq] >= MAX_RETRIES:
                        raise TimeoutError(
                            f"Packet {seq} exceeded maximum retries"
                        )
                    retransmitted.add(seq)
                    emulator.transmit(sock, packets[seq], receiver)
                    sent_times[seq] = time.monotonic()
                    retries[seq] += 1
                    print(f"Retransmitted packet {seq}")

        # TODO 7 and 8: Send END after all DATA packets are ACKed.
        print("All DATA packets acknowledged")
        end_packet = make_end(total_packets)
        end_acked = False

        for attempt in range(MAX_RETRIES + 1):
            # Use the current adaptive RTO while waiting for the END ACK.
            sock.settimeout(rto)
            emulator.transmit(sock, end_packet, receiver)
            print(f"END packet sent (attempt {attempt + 1})")

            try:
                ack_packet, address = sock.recvfrom(2048)
                packet_type, ack_seq, payload = parse_packet(ack_packet)

                if (
                    address == receiver
                    and packet_type == TYPE_ACK
                    and ack_seq == total_packets
                ):
                    end_acked = True
                    print("END acknowledged")
                    break

            except socket.timeout:
                print("Waiting for END ACK timed out")

        if not end_acked:
            raise TimeoutError("END packet was not acknowledged")

        return
       

        
        
        
def main():
    parser = argparse.ArgumentParser(
        description="Selective Repeat UDP sender"
    )
    parser.add_argument("receiver_ip")
    parser.add_argument("file")
    parser.add_argument("--port", type=int, default=9010)
    parser.add_argument("--loss", type=float, default=0.1)

    args = parser.parse_args()

    start = time.perf_counter()
    send_file(args.file, args.receiver_ip, args.port, args.loss)
    print(f"Elapsed time: {time.perf_counter() - start:.3f} seconds")


if __name__ == "__main__":
    main()
