#!/bin/sh

patch="$1"

if [ -z "$patch" ]; then
  echo "Patch filename required"
  exit 1
fi

cd ~/patch-build/
diff -urBNs a/ b/ |grep -v 'are identical' >$patch
