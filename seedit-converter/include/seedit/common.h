/*
 * All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
 */
/* $Id: common.h,v 1.3 2006/04/10 20:20:07 ynakam Exp $ */

#ifndef COMMON_H
#define COMMON_H
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
void strip_slash(char *s);
char **get_dir_list(char *path);
int ntarray_check_exist(char **array,char *str);
char *make_label(char *name);
int chk_child_dir(char *s, char *t);
int chk_child_file(char *old_s, char *t);

#define ROOT_LABEL		"rootdir_t"


#endif
