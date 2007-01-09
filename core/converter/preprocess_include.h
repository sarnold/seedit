/*
#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura
*/

#ifndef PREPROCESS_INCLUDE_H
#define PREPROCESS_INCLUDE_H
#define INPUTBUF 8196
void preprocess_include(FILE *input, FILE *output,char *include_dir);
#endif
