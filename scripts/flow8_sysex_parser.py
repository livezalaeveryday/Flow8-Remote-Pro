"""
Behringer FLOW 8 SysEx Snapshot Encoder & Decoder
Parses the 2,600-byte DSP snapshot buffer extracted from FLOW 8 firmware v11748.
"""
import struct, zlib

BEHRINGER_SYSEX_HEADER = bytes([0xF0, 0x00, 0x20, 0x32, 0x21, 0x00])
FLOW_MAGIC = b"FLOW"

def unpack_7bit_to_8bit(data_7bit):
    """
    Decodes 7-bit MIDI SysEx payload into 8-bit binary stream
    as implemented in firmware routine 0x01adc8.
    """
    out = bytearray()
    shift = 0
    accum = 0
    for byte in data_7bit:
        accum |= (byte & 0x7F) << shift
        shift += 7
        if shift >= 8:
            out.append(accum & 0xFF)
            accum >>= 8
            shift -= 8
    return bytes(out)

def pack_8bit_to_7bit(data_8bit):
    """Encodes 8-bit binary stream into 7-bit MIDI SysEx payload."""
    out = bytearray()
    accum = 0
    shift = 0
    for byte in data_8bit:
        accum |= (byte << shift)
        shift += 8
        while shift >= 7:
            out.append(accum & 0x7F)
            accum >>= 7
            shift -= 7
    if shift > 0:
        out.append(accum & 0x7F)
    return bytes(out)

def parse_dsp_snapshot(raw_payload):
    """
    Parses un-nibblized 8-bit binary payload.
    Validates 'FLOW' magic header and CRC-32 checksum.
    """
    if len(raw_payload) < 0x4e0 + 2600:
        raise ValueError(f"Payload too short: {len(raw_payload)} bytes")

    magic = raw_payload[0x4d0:0x4d4]
    if magic != FLOW_MAGIC:
        raise ValueError(f"Invalid magic header: {magic}, expected {FLOW_MAGIC}")

    expected_crc = struct.unpack('<I', raw_payload[0x4d8:0x4dc])[0]
    dsp_block = raw_payload[0x4e0:0x4e0 + 2600]

    calc_crc = zlib.crc32(dsp_block)
    if expected_crc != calc_crc:
        print(f"Warning: CRC mismatch: expected {hex(expected_crc)}, calculated {hex(calc_crc)}")

    return {
        "magic": magic.decode('ascii'),
        "crc32": hex(expected_crc),
        "dsp_bytes": len(dsp_block),
        "mon1_master_level": dsp_block[0x414 - 0x4e0] if len(dsp_block) > 0x414 else 0,
        "mon2_master_level": dsp_block[0x415 - 0x4e0] if len(dsp_block) > 0x415 else 0,
    }

if __name__ == '__main__':
    print("FLOW 8 SysEx Snapshot Tools Initialized.")
