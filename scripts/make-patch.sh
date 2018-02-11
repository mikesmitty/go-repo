#!/bin/sh

patch="$1"

if [ -z "$patch" ]; then
  echo "Patch filename required"
  exit 1
fi

cd ~/patch-build/
diff -urBN a/ b/ >$patch
