import struct

from common import (
    MAX_PAYLOAD,
    TYPE_ACK,
    TYPE_DATA,
    TYPE_END,
    make_ack,
    make_data,
    make_end,
    make_packet,
    parse_packet,
)


def main():
    payload = b"Hello reliable UDP"
    packet = make_data(7, payload)

    packet_type, seq, received_payload = parse_packet(packet)

    assert packet_type == TYPE_DATA
    assert seq == 7
    assert received_payload == payload
    print("PASS: DATA packet creation/parsing")

    ack = make_ack(12)
    packet_type, seq, received_payload = parse_packet(ack)
    assert packet_type == TYPE_ACK
    assert seq == 12
    assert received_payload == b""
    print("PASS: ACK packet creation/parsing")

    end = make_end(13)
    packet_type, seq, received_payload = parse_packet(end)
    assert packet_type == TYPE_END
    assert seq == 13
    assert received_payload == b""
    print("PASS: END packet creation/parsing")

    corrupted = bytearray(packet)
    corrupted[-1] ^= 0xFF

    try:
        parse_packet(bytes(corrupted))
        raise AssertionError("Corruption was not detected")
    except ValueError:
        print("PASS: checksum detects corruption")

    try:
        parse_packet(packet[:-1])
        raise AssertionError("Truncated packet was not detected")
    except ValueError:
        print("PASS: truncated packet is rejected")

    try:
        make_data(0, b"x" * (MAX_PAYLOAD + 1))
        raise AssertionError("Oversized payload was not rejected")
    except ValueError:
        print("PASS: oversized payload is rejected")

    # Packet type is encoded as an unsigned byte, so values above 255 are
    # invalid at the packet-construction layer.
    try:
        make_packet(256, 0)
        raise AssertionError("Out-of-range packet type was not rejected")
    except (ValueError, struct.error):
        print("PASS: out-of-range packet type is rejected")


if __name__ == "__main__":
    main()
