"""
Common packet definitions for the Reliable Data Transfer over UDP project.
Used by Stop-and-Wait, Go-Back-N, and Selective Repeat.
"""

import struct
import zlib

MAGIC = b"RDT1"

TYPE_DATA = 1
TYPE_ACK = 2
TYPE_END = 3

# Header = MAGIC(4) + TYPE(1) + SEQ(4) + PAYLOAD LENGTH(4) + CHECKSUM(4)
# ! = network byte order (big-endian)
HEADER = struct.Struct("!4sBIII")

# Same header, without the checksum, used to calculate the checksum.
HEADER_NO_CHECKSUM = struct.Struct("!4sBII")

MAX_PAYLOAD = 1024


def checksum(data: bytes) -> int:
    """Return a 32-bit CRC checksum."""
    return zlib.crc32(data) & 0xFFFFFFFF


def make_packet(packet_type: int, seq: int, payload: bytes = b"") -> bytes:
    """Create a complete protocol packet."""
    if len(payload) > MAX_PAYLOAD:
        raise ValueError("Payload is larger than MAX_PAYLOAD")

    header_without_checksum = HEADER_NO_CHECKSUM.pack(
        MAGIC,
        packet_type,
        seq,
        len(payload),
    )

    crc = checksum(header_without_checksum + payload)

    header = HEADER.pack(
        MAGIC,
        packet_type,
        seq,
        len(payload),
        crc,
    )

    return header + payload


def parse_packet(packet: bytes):
    """Validate a packet and return (packet_type, seq, payload)."""
    if len(packet) < HEADER.size:
        raise ValueError("Packet too small")

    header_bytes = packet[:HEADER.size]
    payload = packet[HEADER.size:]

    magic, packet_type, seq, length, received_crc = HEADER.unpack(
        header_bytes
    )

    if magic != MAGIC:
        raise ValueError("Invalid magic")

    if length != len(payload):
        raise ValueError("Invalid payload length")

    header_without_checksum = HEADER_NO_CHECKSUM.pack(
        magic,
        packet_type,
        seq,
        length,
    )

    calculated_crc = checksum(header_without_checksum + payload)

    if calculated_crc != received_crc:
        raise ValueError("Checksum mismatch")

    return packet_type, seq, payload


def make_ack(seq: int) -> bytes:
    """Create an ACK packet."""
    return make_packet(TYPE_ACK, seq)


def make_data(seq: int, payload: bytes) -> bytes:
    """Create a DATA packet."""
    return make_packet(TYPE_DATA, seq, payload)


def make_end(seq: int) -> bytes:
    """Create an END packet."""
    return make_packet(TYPE_END, seq)
