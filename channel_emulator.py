
import random
import time


class ChannelEmulator:
    def __init__(
        self,
        loss_rate=0.0,
        delay=0.1,
        duplication_rate=0.05,
        corruption_rate=0.02,
        reorder_rate=0.05,
        seed=None,
    ):
        self.loss_rate = loss_rate
        self.delay = delay
        self.duplication_rate = duplication_rate
        self.corruption_rate = corruption_rate
        self.reorder_rate = reorder_rate

        # A fixed seed makes experiments repeatable.
        self.rng = random.Random(seed)

    def transmit(self, sock, packet, address):
        if self.rng.random() < self.loss_rate:
            print("Packet dropped")
            return

        time.sleep(self.rng.uniform(0, self.delay))

        if self.rng.random() < self.corruption_rate and packet:
            packet = bytearray(packet)
            index = self.rng.randrange(len(packet))
            packet[index] ^= 1
            packet = bytes(packet)
            print("Packet corrupted")

        if self.rng.random() < self.reorder_rate:
            time.sleep(self.delay)
            print("Packet reordered (delayed)")

        sock.sendto(packet, address)
        print("Packet transmitted")

        if self.rng.random() < self.duplication_rate:
            time.sleep(0.01)
            sock.sendto(packet, address)
            print("Packet duplicated")


if __name__ == "__main__":
    emulator = ChannelEmulator(seed=42)

    print("Channel Emulator")
    print("Loss rate:", emulator.loss_rate)
    print("Delay:", emulator.delay)
    print("Duplication rate:", emulator.duplication_rate)
    print("Corruption rate:", emulator.corruption_rate)
    print("Reorder rate:", emulator.reorder_rate)
    print("Random seed: 42")
