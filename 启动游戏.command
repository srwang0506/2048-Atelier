#!/bin/zsh
cd -- "${0:A:h}"
if [[ ! -x .venv/bin/python ]]; then
  echo '正在准备 2048 的独立 Python 环境…'
  python3 -m venv .venv || exit 1
fi
if ! .venv/bin/python -c 'import pygame, numpy, numba, PIL' >/dev/null 2>&1; then
  .venv/bin/python -m pip install -r requirements.txt || exit 1
fi
exec .venv/bin/python game.py
