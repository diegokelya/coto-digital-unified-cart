#!/usr/bin/env python3
"""Generate Home Assistant brand icon sizes from the 512px logo."""

from __future__ import annotations

import binascii
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "logo.png"
BRAND_DIR = ROOT / "custom_components" / "coto_digital" / "brand"


def read_rgba_png(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Source is not a PNG")

    position = 8
    compressed = bytearray()
    width = height = 0
    while position < len(data):
        length = struct.unpack(">I", data[position : position + 4])[0]
        chunk_type = data[position + 4 : position + 8]
        chunk_data = data[position + 8 : position + 8 + length]
        position += length + 12
        if chunk_type == b"IHDR":
            width, height, depth, color_type, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
            if (depth, color_type, compression, filtering, interlace) != (8, 6, 0, 0, 0):
                raise ValueError("Expected a non-interlaced 8-bit RGBA PNG")
        elif chunk_type == b"IDAT":
            compressed.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    raw = zlib.decompress(compressed)
    stride = width * 4
    rows = []
    previous = bytearray(stride)
    offset = 0

    for _ in range(height):
        filter_type = raw[offset]
        scanline = bytearray(raw[offset + 1 : offset + 1 + stride])
        offset += stride + 1
        reconstructed = bytearray(stride)
        for index, value in enumerate(scanline):
            left = reconstructed[index - 4] if index >= 4 else 0
            above = previous[index]
            upper_left = previous[index - 4] if index >= 4 else 0
            if filter_type == 0:
                result = value
            elif filter_type == 1:
                result = (value + left) & 0xFF
            elif filter_type == 2:
                result = (value + above) & 0xFF
            elif filter_type == 3:
                result = (value + ((left + above) // 2)) & 0xFF
            elif filter_type == 4:
                estimate = left + above - upper_left
                pa = abs(estimate - left)
                pb = abs(estimate - above)
                pc = abs(estimate - upper_left)
                predictor = left if pa <= pb and pa <= pc else above if pb <= pc else upper_left
                result = (value + predictor) & 0xFF
            else:
                raise ValueError(f"Unsupported PNG filter: {filter_type}")
            reconstructed[index] = result
        rows.append(reconstructed)
        previous = reconstructed

    return width, height, b"".join(rows)


def resize_half_rgba(pixels: bytes, width: int, height: int) -> bytes:
    if width % 2 or height % 2:
        raise ValueError("Dimensions must be even")
    output = bytearray((width // 2) * (height // 2) * 4)
    output_width = width // 2
    for y in range(output_width):
        for x in range(output_width):
            for channel in range(4):
                indexes = (
                    ((2 * y) * width + 2 * x) * 4 + channel,
                    ((2 * y) * width + 2 * x + 1) * 4 + channel,
                    (((2 * y + 1) * width + 2 * x) * 4 + channel),
                    (((2 * y + 1) * width + 2 * x + 1) * 4 + channel),
                )
                output[(y * output_width + x) * 4 + channel] = sum(pixels[i] for i in indexes) // 4
    return bytes(output)


def chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_rgba_png(path: Path, width: int, height: int, pixels: bytes) -> None:
    stride = width * 4
    raw = b"".join(b"\x00" + pixels[y * stride : (y + 1) * stride] for y in range(height))
    payload = b"\x89PNG\r\n\x1a\n"
    payload += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    payload += chunk(b"IDAT", zlib.compress(raw, 9))
    payload += chunk(b"IEND", b"")
    path.write_bytes(payload)


def main() -> None:
    width, height, pixels = read_rgba_png(SOURCE)
    if (width, height) != (512, 512):
        raise ValueError(f"Expected 512x512 source, got {width}x{height}")

    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    (BRAND_DIR / "icon@2x.png").write_bytes(SOURCE.read_bytes())
    write_rgba_png(BRAND_DIR / "icon.png", 256, 256, resize_half_rgba(pixels, width, height))
    print(f"Generated {BRAND_DIR / 'icon.png'} (256x256)")
    print(f"Generated {BRAND_DIR / 'icon@2x.png'} (512x512)")


if __name__ == "__main__":
    main()
