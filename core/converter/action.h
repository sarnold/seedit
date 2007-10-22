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
char *get_filename(char *path, int state);
int get_file_state(char *path);

#define CAT_ALLOW 0
#define CAT_ALLOWFS 1
#endif
