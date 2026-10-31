#!/usr/bin/env python3
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# Ensure the root package is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mscli.cli import main

if __name__ == '__main__':
    main()
