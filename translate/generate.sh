#!/bin/bash
set -e

for lang in es fr de it pt cs ru tr; do
  echo "   → $lang"
  python generate.py ../en/bambufy.cfg $lang
done