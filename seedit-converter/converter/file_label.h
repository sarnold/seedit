/*
 * All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
 */
/* $Id: file_label.h,v 1.2 2006/04/21 00:07:30 ynakam Exp $ */

#ifndef FILE_LABEL_H
#define FILE_LABEL_H

#include <stdio.h>
#include "hashtab.h"

int create_file_label_table(HASH_TABLE *);
int create_dir_label_table();

void print_file_label_tab();
void delete_file_label_tab();
void out_file_type(FILE *);
void out_file_contexts_config(FILE *file_contexts);

int register_label_table(char *);
char *resolve_label_conflict(char *);

#endif
