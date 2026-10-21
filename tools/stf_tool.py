#!/usr/bin/env python3
"""Read, dump and extend SWG localized string tables (.stf).

Binary layout (little endian), per
src/external/ours/library/localization/src/shared/LocalizedStringTable.cpp:

    u32 magic (0xabcd), u8 version (1), u32 nextUniqueId, u32 numEntries
    numEntries x { u32 id, u32 crc, u32 charCount, UTF-16LE chars }
    numEntries x { u32 id, u32 nameLen, ASCII name }

A duplicate id makes the loader reject the WHOLE table (see PROGRESS.md P9.3), so
`add` refuses duplicate keys, assigns fresh ids from nextUniqueId, and verifies that
the untouched table re-serialises byte-for-byte before anything is written.

Usage:
    stf_tool.py dump FILE.stf
    stf_tool.py add  FILE.stf OUT.stf KEY=TEXT [KEY=TEXT ...]
"""
import struct
import sys

MAGIC = 0xABCD


def parse(data):
    magic, version, next_id, count = struct.unpack_from('<IBII', data, 0)
    if magic != MAGIC or version != 1:
        raise ValueError('not a version 1 stf (magic=%#x version=%d)' % (magic, version))
    pos = 13
    entries = []  # [id, crc, text]
    for _ in range(count):
        sid, crc, n = struct.unpack_from('<III', data, pos)
        pos += 12
        text = data[pos:pos + n * 2].decode('utf-16-le')
        pos += n * 2
        entries.append([sid, crc, text])
    names = []  # [id, name]
    for _ in range(count):
        sid, n = struct.unpack_from('<II', data, pos)
        pos += 8
        name = data[pos:pos + n].decode('ascii')
        pos += n
        names.append([sid, name])
    if pos != len(data):
        raise ValueError('%d trailing bytes after name table' % (len(data) - pos))
    return version, next_id, entries, names


def build(version, next_id, entries, names):
    out = bytearray(struct.pack('<IBII', MAGIC, version, next_id, len(entries)))
    for sid, crc, text in entries:
        out += struct.pack('<III', sid, crc, len(text))
        out += text.encode('utf-16-le')
    for sid, name in names:
        raw = name.encode('ascii')
        out += struct.pack('<II', sid, len(raw))
        out += raw
    return bytes(out)


def main(argv):
    if len(argv) >= 3 and argv[1] == 'dump':
        _, _, entries_, names_ = parse(open(argv[2], 'rb').read())
        by_id = {e[0]: e for e in entries_}
        for sid, name in names_:
            print('%5d  %-40s %s' % (sid, name, by_id[sid][2].replace('\n', '\\n')))
        return 0
    if len(argv) >= 5 and argv[1] == 'add':
        src, dst = argv[2], argv[3]
        data = open(src, 'rb').read()
        version, next_id, entries, names = parse(data)
        if build(version, next_id, entries, names) != data:
            print('refusing: table does not round-trip byte-for-byte', file=sys.stderr)
            return 1
        existing = {n for _, n in names}
        ids = {e[0] for e in entries}
        for pair in argv[4:]:
            key, _, text = pair.partition('=')
            if not key or key in existing:
                print('skip/duplicate key: %r' % key, file=sys.stderr)
                return 1
            new_id = max(next_id, max(ids) + 1)
            ids.add(new_id)
            next_id = new_id + 1
            # crc column: reuse the convention of the table (all entries share it or are 0)
            entries.append([new_id, 0xFFFFFFFF if all(e[1] == 0xFFFFFFFF for e in entries) else 0, text])
            names.append([new_id, key])
            existing.add(key)
        entries.sort(key=lambda e: e[0])
        names.sort(key=lambda n: n[1])
        out = build(version, next_id, entries, names)
        parse(out)  # must parse again
        open(dst, 'wb').write(out)
        print('wrote %s (%d entries)' % (dst, len(entries)))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
