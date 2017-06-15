#!/bin/sh

patch="$1"

if [ -z "$patch" ]; then
  exit 1
fi

cd ~/patch-build/
diff -urBNs a/ b/ |grep -v 'are identical' >$patch
