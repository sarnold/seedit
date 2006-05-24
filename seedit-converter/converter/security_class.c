/*
 * All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
 */
/* $Id: security_class.c,v 1.1.1.1 2006/02/23 22:04:56 ynakam Exp $ */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <seedit/common.h>
#include "security_class.h"
#include "initial_policy.h"

/**
 *  Global variable
 */
static char security_classes[MAX_CLASS_NUM][CLASS_LENGTH];
static int class_num;

/**
 *  name:	get_class_num
 *  about:	get a number of class 
 *  args:	none
 *  return:	number of class
 */
int
get_class_num()
{
	return class_num;
}

/**
 *  name:	get_security_class
 *  about:	get security class with target id
 *  args:	number of target class
 *  return:	string of class name
 */
char *
get_security_class(int i)
{
	return security_classes[i];
}

/**
 *  name:	print_classes
 *  about:	print all classes
 *  args:	none
 *  return:	none
 */
void
print_classes()
{
	int i;
	for (i = 0; i < class_num; i++)
		printf("%s\n", security_classes[i]);

	return;
}

/**
 *  name:	init_classes
 *  about:      open security_classes file and read class information.
 *         	all class informations is written into security_classes array.
 *  args: 	security_class_file (char *) -> path name of security_class	
 *  return:	return 0
 */
int
init_classes(char *security_class_file)
{
	FILE *fd;
	char buf[CLASS_FILE_LINE_MAX];
	int i=0;
	char *p;

	if ((fd = fopen(security_class_file, "r")) == NULL)
	{
		perror(security_class_file);
		exit(1);
	}

	while (fgets(buf, sizeof(buf), fd) != NULL)
	{
		/* skip comments */
		if (buf[0] == '#')
			continue;

		chop_nl(buf);

		if ((p = strtok(buf, " ")) == NULL)
		{
			continue;
		}
		else
		{
			p = strtok(NULL, " ");
		}

		if (p == NULL)
		{
			continue;
		}
		strncpy(security_classes[i], p, CLASS_LENGTH);
		i++;
	}
	class_num = i;

	fclose(fd);
	return 0;
}
