#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys

from rsc import RSC
from sxf import SXF

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('files', nargs='+', help='*.sfx files')
    parser.add_argument('--rsc', dest='rsc', help='classifier')

    args = parser.parse_args()

    if args.rsc:
        with open(args.rsc, 'rb') as f:
            rsc = RSC.parse(f)
            rsc.info()

    for i, filename in enumerate(args.files, start=1):
        sys.err.write('%s %s' % i, filename)

        with open(filename, 'rb') as f:
            sxf = SXF.parse(f)
            sxf.info()
