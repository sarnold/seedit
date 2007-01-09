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
/* $Id: security_class.h,v 1.1.1.1 2006/02/23 22:04:56 ynakam Exp $ */

#ifndef SECURITY_CLASS_H
#define SECURITY_CLASS_H


#define MAX_CLASS_NUM			256
#define CLASS_LENGTH			64
#define CLASS_FILE_LINE_MAX		1024 

int init_classes(char *);
void print_classes();
int get_class_num();
char *get_security_class(int);

#endif
