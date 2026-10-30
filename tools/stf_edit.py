#!/usr/bin/env python3
"""Read and edit SWG binary .stf string tables (version 1 layout).

Layout: u32 magic 0xABCD, u8 version, u32 nextUniqueId, u32 numStrings,
  numStrings x (u32 id, u32 sourceCrc, u32 charCount, UTF-16LE chars),
  then name entries (u32 id, u32 byteLen, ascii name) until end of file (no count).
Names must stay sorted (the engine binary-searches them) and ids unique (P9, P11).

Usage:
  stf_edit.py check FILE                      parse + verify round trip is byte-identical
  stf_edit.py dump FILE [substring]           list name -> text
  stf_edit.py set FILE KEY TEXT [KEY TEXT..]  add or replace entries, write back in place
"""
import struct, sys

MAGIC = 0xABCD

def parse(data):
    magic, ver, nxt, n = struct.unpack_from('<IBII', data, 0)
    assert magic == MAGIC, hex(magic)
    off = 13
    strings = []
    for _ in range(n):
        i, crc, cc = struct.unpack_from('<III', data, off); off += 12
        txt = data[off:off + cc * 2].decode('utf-16-le'); off += cc * 2
        strings.append([i, crc, txt])
    names = []
    while off < len(data):
        i, ln = struct.unpack_from('<II', data, off); off += 8
        names.append([i, data[off:off + ln].decode('ascii')]); off += ln
    assert off == len(data), (off, len(data))
    return ver, nxt, strings, names

def crc_of(txt):
    # source crc is not validated by the loader for display; keep 0 for new entries
    return 0xFFFFFFFF  # existing entries use 0xFFFFFFFF

def build(ver, nxt, strings, names):
    out = bytearray(struct.pack('<IBII', MAGIC, ver, nxt, len(strings)))
    for i, crc, txt in strings:
        out += struct.pack('<III', i, crc, len(txt)) + txt.encode('utf-16-le')
    for i, nm in names:
        b = nm.encode('ascii')
        out += struct.pack('<II', i, len(b)) + b
    return bytes(out)

def main():
    cmd, path = sys.argv[1], sys.argv[2]
    data = open(path, 'rb').read()
    ver, nxt, strings, names = parse(data)
    if cmd == 'check':
        same = build(ver, nxt, strings, names) == data
        ids = [s[0] for s in strings]
        print(f"{path}: version={ver} nextId={nxt} strings={len(strings)} names={len(names)} "
              f"unique_ids={len(set(ids)) == len(ids)} sorted_names={[n[1] for n in names] == sorted(n[1] for n in names)} "
              f"roundtrip_identical={same}")
    elif cmd == 'dump':
        sub = sys.argv[3] if len(sys.argv) > 3 else ''
        text = {i: t for i, _, t in strings}
        for i, nm in names:
            if sub in nm:
                print(f"{i}\t{nm}\t{text.get(i, '')!r}")
    elif cmd == 'set':
        kv = sys.argv[3:]
        assert len(kv) % 2 == 0
        by_name = {nm: i for i, nm in names}
        text_idx = {s[0]: s for s in strings}
        for k, v in zip(kv[::2], kv[1::2]):
            if k in by_name:
                text_idx[by_name[k]][2] = v
            else:
                new_id = nxt; nxt += 1
                strings.append([new_id, crc_of(v), v])
                names.append([new_id, k])
                by_name[k] = new_id
        names.sort(key=lambda n: n[1])
        open(path, 'wb').write(build(ver, nxt, strings, names))
        print(f"wrote {path}: {len(strings)} strings")

main()
