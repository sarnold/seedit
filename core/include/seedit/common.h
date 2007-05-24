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
/* $Id: common.h,v 1.3 2006/04/10 20:20:07 ynakam Exp $ */

#ifndef COMMON_H
#define COMMON_H
#include <selinux/selinux.h>

void chop_nl(char *);
char *get_nth_tok(char *, char *, int);
char *get_nth_tok_alloc(char *, char *, int);
void *extend_array(void *, int *, size_t);
char *mk_fullpath(char *, char *);
void chop_str(char *, char *);
int chop_char(char *, char );
void * my_malloc(size_t);
void *my_realloc(void *, size_t);
char *joint_str(char *, char *);
char *joint_3_str(char *a, char *b, char *c);
void error_print(char *, int, char *, ...);
int check_exist_in_list(char *, char **);
int split_and_set_list(char *buf, char *delm, char **list, int max);
char *get_prefix(char *);
int check_type_suffix(char *type);
int get_ntarray_num(char **);
char **extend_ntarray(char **, char *);
void free_ntarray(char **array);
void debug_print(char *, int, char *, ...);
char *make_role_to_domain(char *name);
char *make_domain_to_role(char *name);

void strip_slash(char *s);
char **get_dir_list(char *path,char **homedir_list);
int ntarray_check_exist(char **array,char *str);
char *make_label(char *name);
int chk_child_dir(char *s, char *t);
int chk_child_file(char *old_s, char *t);

int is_home_dir(char *path, char **homedir_list);
char *match_home_dir(char *path, char **homedir_list);
char *get_user_from_path(char *path, char **homedir_list);
char **joint_ntarray(char **a1, char **a2);
char *get_type_from_context(security_context_t context);
char *get_name_from_path(char *path);

#define ROOT_LABEL		"rootdir_t"


#endif
