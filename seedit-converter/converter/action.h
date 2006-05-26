/*
 * All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
 */
/* $Id: action.h,v 1.1.1.1 2006/02/23 22:04:56 ynakam Exp $ */

#ifndef ACTION_H
#define ACTION_H
#include <stdio.h>
#include "global.h"
/**
 *  handle hash table about domain
 */
DOMAIN *search_domain_hash(char *);
int insert_domain_hash(DOMAIN *);/*not used*/
int insert_domain_hash_by_name(char *);

void print_all_domain();
void free_domain_tab();

void free_rbac_hash_table();
void free_user_hash_table();
void print_domain_info(DOMAIN);

void print_domain_trans();
void free_domain_trans();
void register_dummy_home_rule();
int append_file_rule(char *domain_name, char *filename, int perm, int state);

#define CAT_ALLOW 0
#define CAT_ALLOWFS 1
#endif
