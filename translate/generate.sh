#!/bin/bash
set -e

for lang in en es fr de it pt cs ru tr ja ko zh; do
  python3 generate.py ../bambufy.cfg $lang
done