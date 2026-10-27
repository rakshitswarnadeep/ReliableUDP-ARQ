from common import make_data


class SelectiveRepeatSender:

    def __init__(self, window_size=4, timeout=2):
        self.window_size = window_size
        self.timeout = timeout

        self.base = 0
        self.next_seq = 0

        self.acked = set()
        self.timers = {}

    def can_send(self):
        return self.next_seq < self.base + self.window_size

    def send_packet(self, data):

        if not self.can_send():
            print("Window is full")
            return None

        seq_num = self.next_seq

        packet = make_data(seq_num, data)

        self.timers[seq_num] = "started"
        self.next_seq += 1

        print(f"Sending packet {seq_num}")

        return packet

    def receive_ack(self, seq_num):

        self.acked.add(seq_num)

        if seq_num in self.timers:
            del self.timers[seq_num]

        while self.base in self.acked:
            self.base += 1

    def check_timeout(self, seq_num):

        if seq_num in self.timers:

            if seq_num not in self.acked:
                print("Timeout: retransmitting packet", seq_num)
                return True

        return False



sender = SelectiveRepeatSender(window_size=4)

sender.send_packet(b"A")
sender.send_packet(b"B")
sender.send_packet(b"C")

print("Initial base:", sender.base)

sender.receive_ack(0)

print("After ACK 0, base:", sender.base)

print("Packet 1 timeout:", sender.check_timeout(1))

sender.receive_ack(1)

print("After ACK 1, base:", sender.base)

print("Packet 1 timeout after ACK:",
      sender.check_timeout(1))