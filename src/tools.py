# -*- coding: utf-8 -*-

import sys


def msg(message):
    sys.stderr.write('%s\n' % message)


def err(message):
    sys.stdout.write('%s\n' % message)


def split_bits(data, mask):
    result = []
    for i in mask:
        m = '%s%s' % ('0' * (8 - i), '1' * i)
        b = data & int(m, 2)
        result.append(b)
        data = data >> i
    return result


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def print_hex(data, chunk_size=8):
    for i in chunks(data, chunk_size):
        ha = [format(ord(p), '02x') for p in i]
        aa = [p if ord(p) > 32 and ord(p) < 255 else '.' for p in i]

        if len(ha) < chunk_size:
            ha.extend(['__'] * (chunk_size - len(ha)))
            aa.extend(['.'] * (chunk_size - len(ha)))
        h = ' '.join(ha)
        a = ''.join(aa)

        err('%s | %s\n' % (h, a))


def strip_0(data):
    idx = data.find('\0')
    if idx != -1 and idx < len(data):
        data = data[:idx]
    return data.strip()
