#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys


def install(module):
    subprocess.check_call([sys.executable, "-m", "pip", "install", module])


def main():
    with open("requirements.txt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                install(line)


if __name__ == "__main__":
    main()
