#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys

from rsc import RSC
from tools import err

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('rsc', help='*.rsc file')
    parser.add_argument('--output-objects', dest='obj_file', default='obj.yaml', help='*.yaml file')
    parser.add_argument('--output-semantics', dest='sem_file', default='sem.yaml', help='*.yaml file')
    parser.add_argument('--output-parameters', dest='par_file', default='par.yaml', help='*.yaml file')

    args = parser.parse_args()

    with open(args.rsc, 'rb') as f:
        err(
            'File: %s, Output: %s, %s, %s' % (
                args.rsc,
                args.obj_file,
                args.sem_file,
                args.par_file,
            )
        )

        rsc = RSC.parse(f)
        rsc.args = args
        rsc.info()
        rsc.dump()
