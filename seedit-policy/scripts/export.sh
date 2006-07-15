#!/bin/sh

#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

EXPORTDIR=$1
DEFINE=$2

FILES=`/bin/ls simplified_policy`

mkdir -p $EXPORTDIR

for FILE in $FILES
do
  if [ -d ./simplified_policy/$FILE ]
      then 
      continue
  fi 
  m4  ./macros/template_macros.te $DEFINE "./simplified_policy/$FILE"> "$EXPORTDIR/$FILE"
done

