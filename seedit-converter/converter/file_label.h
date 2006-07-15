/*
#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2003 Hitachi Software Engineering Co., Ltd.
#! Copyright (C) 2005, 2006 Yuichi Nakamura
#! 
#! This program is free software; you can redistribute it and/or modify
#! it under the terms of the GNU General Public License as published by
#! the Free Software Foundation; either version 2 of the License, or
#! (at your option) any later version.
#! 
#! This program is distributed in the hope that it will be useful,
#! but WITHOUT ANY WARRANTY; without even the implied warranty of
#! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#! GNU General Public License for more details.
#! 
#! You should have received a copy of the GNU General Public License
#! along with this program; if not, write to the Free Software
#! Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
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
