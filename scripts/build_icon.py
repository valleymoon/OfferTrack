"""一次性脚本：把源 PNG 转成多分辨率 Windows ICO。

用法：
    python scripts/build_icon.py <源 PNG 路径> [<输出 ICO 路径>]

默认输出到 assets/app.ico。需要 Pillow，可用项目 venv 里临时装：
    backend/.venv/Scripts/pip.exe install pillow

注意：手工构造 ICO 文件，规则：
- 16/32/48/64/128 用 32-bit BMP（BITMAPINFOHEADER + BGRA + AND mask）
- 256×256 用 PNG 压缩
原因：Pillow 12.x 默认把所有子图都写成 PNG entries，Windows Explorer
解析小尺寸 PNG ICO 子图时偶发失败，桌面快捷方式会回退到默认图标。
"""

from __future__ import annotations

import io
import struct
import sys
from pathlib import Path

from PIL import Image

ICO_SIZES = [16, 32, 48, 64, 128, 256]
PNG_THRESHOLD = 256  # >= 这个尺寸用 PNG，其余用 BMP


def _build_dib(im: Image.Image) -> bytes:
    """RGBA PIL Image -> ICO 内嵌 DIB（BITMAPINFOHEADER + 像素 + AND mask）。

    像素：32-bit BGRA，自下而上。AND mask 全 0（透明完全靠 alpha）。
    biHeight 是实际高度的 2 倍（Win ICO 格式约定，含 AND mask 区）。
    """
    w, h = im.size
    # tobytes("raw", "BGRA")：BGRA、top-down
    bgra_top_down = im.tobytes("raw", "BGRA")
    row_bytes = w * 4
    # 翻成 bottom-up
    rows = [bgra_top_down[i * row_bytes:(i + 1) * row_bytes] for i in range(h)]
    pixel_data = b"".join(reversed(rows))

    # AND mask: 1 bit/pixel，每行 4 字节对齐，全 0
    mask_row_bytes = ((w + 31) // 32) * 4
    and_mask = b"\x00" * (mask_row_bytes * h)

    bih = struct.pack(
        "<IiiHHIIiiII",
        40,         # biSize
        w,          # biWidth
        h * 2,      # biHeight (XOR + AND)
        1,          # biPlanes
        32,         # biBitCount
        0,          # biCompression (BI_RGB)
        0,          # biSizeImage
        0,          # biXPelsPerMeter
        0,          # biYPelsPerMeter
        0,          # biClrUsed
        0,          # biClrImportant
    )
    return bih + pixel_data + and_mask


def _build_png(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def build_ico(src_png: Path, out_ico: Path, sizes: list[int]) -> None:
    src = Image.open(src_png).convert("RGBA")
    blobs: list[tuple[int, bytes]] = []
    for sz in sizes:
        im = src.resize((sz, sz), Image.LANCZOS)
        if sz >= PNG_THRESHOLD:
            blobs.append((sz, _build_png(im)))
        else:
            blobs.append((sz, _build_dib(im)))

    n = len(blobs)
    header = struct.pack("<HHH", 0, 1, n)  # ICONDIR: reserved, type=1(ICO), count
    # 数据起点 = ICONDIR(6) + n × ICONDIRENTRY(16)
    offset = 6 + n * 16
    entries = bytearray()
    for sz, data in blobs:
        # 256 在 ICONDIRENTRY.bWidth/bHeight 字段必须存 0
        w_byte = 0 if sz >= 256 else sz
        h_byte = 0 if sz >= 256 else sz
        entries += struct.pack(
            "<BBBBHHII",
            w_byte,     # bWidth
            h_byte,     # bHeight
            0,          # bColorCount (32bpp 时填 0)
            0,          # bReserved
            1,          # wPlanes
            32,         # wBitCount
            len(data),  # dwBytesInRes
            offset,     # dwImageOffset
        )
        offset += len(data)

    body = b"".join(d for _, d in blobs)
    out_ico.write_bytes(header + bytes(entries) + body)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    src = Path(sys.argv[1]).resolve()
    if not src.exists():
        print(f"[X] 源文件不存在：{src}")
        sys.exit(1)

    project_root = Path(__file__).resolve().parent.parent
    default_out = project_root / "assets" / "app.ico"
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else default_out
    out.parent.mkdir(parents=True, exist_ok=True)

    build_ico(src, out, ICO_SIZES)
    sizes_str = ", ".join(f"{s}x{s}" for s in ICO_SIZES)
    fmt = ", ".join(("PNG" if s >= PNG_THRESHOLD else "BMP") for s in ICO_SIZES)
    print(f"[OK] 已写入：{out}（{sizes_str}）")
    print(f"     格式：{fmt}")


if __name__ == "__main__":
    main()
