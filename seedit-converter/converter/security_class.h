/*
 * All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
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
