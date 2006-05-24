/*
 * All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
 */
/* $Id: out_file_acl.h,v 1.1.1.1 2006/02/23 22:04:56 ynakam Exp $ */

#ifndef OUT_FILE_ACL_H
#define OUT_FILE_ACL_H

void out_file_acl(FILE *, DOMAIN *);
int chk_child_dir(char *, char *);
int chk_child_file(char *, char *);
void print_file_allow(DOMAIN *,char*,int,int, FILE*);
int check_dev_flag(DOMAIN *domain, char *filename);

#endif
