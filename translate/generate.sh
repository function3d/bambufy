#!/bin/bash
set -e

for lang in en es fr de it pt cs ru tr ja ko zh; do
  echo "   → $lang"
  python generate.py ../bambufy.cfg $lang
done