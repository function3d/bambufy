#!/bin/sh

CONF=/opt/config/printer.base.cfg
awk '
  /^\[stepper_z\]/ {
    in_z = 1
    print
    next
  }
  /^\[/ {
    in_z = 0
    print
    next
  }
  in_z && /^[[:space:]]*position_endstop[[:space:]]*:/ && !/^[[:space:]]*;/ {
    print ";" $0
    next
  }
  { print }
' ${CONF} > /tmp/tmp && mv /tmp/tmp $CONF