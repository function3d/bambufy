#!/bin/bash
set -e

for lang in es fr de it pt cs ru tr ja ko zh; do
  echo "   → $lang"
  python generate.py ../en/bambufy.cfg $lang
done