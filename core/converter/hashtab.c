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
/* $Id: hashtab.c,v 1.1.1.1 2006/02/23 22:04:56 ynakam Exp $ */

/**
 * Functions to handle hash table
 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "hashtab.h"

/**
 *  @name:	hash_func
 *  @about:	very simple hash function
 *  @args:	key (char *) -> hash key
 *  @args:	max (int) -> max hash table size
 *  @return:	hash value
 */
static int
hash_func(char *key, int max)
{
	int i;
	int len;
	int t = 0;

	len = strlen(key);

	for (i = 0; i < len; i++)
	{
		t += key[i];
	}

	return t%max;
}

/**
 *  @name:	create_hash_table
 *  @about:	create hash table of "size" bytes
 *  @args:	size (int) -> hash table initial size
 *  @return:	error:return NULL
 */
HASH_TABLE *
create_hash_table(int size)
{
	HASH_NODE *head;		/* the head of table	*/
	HASH_TABLE *t;			/* return value		*/

	t = (HASH_TABLE *)malloc(sizeof(HASH_TABLE));
	head = (HASH_NODE *)malloc(size*(sizeof(HASH_NODE)));

	if (t == NULL || head == NULL)
	{
		perror("malloc");
		return NULL;
	}

	memset(head, 0, size*(sizeof(HASH_NODE)));	/* clear table	*/

	t->buf = head;
	t->tab_size = size;
	t->element_num = 0;

	return t;
}

/**
 *  @name:	delete_hash_table
 *  @about:	free the frame of hash table.
 * 		This doesn't free the "body" of hash table.
 *  @args:	t (HASH_TABLE *) -> hash table
 *  @return:	return 0 on success
 */
int
delete_hash_table(HASH_TABLE *t)
{
	HASH_NODE *p;
	HASH_NODE *q;
	int i;

	for (i = 0; i < t->tab_size; i++)
	{
		p = &(t->buf[i]);
		q = p->next;
		if (q != NULL)
		{
			while (q != NULL)
			{
				p = q->next;
				free(q);
				q = p;
			}
		}
	}

	free(t->buf);
	free(t);

	return 0;
}

/**
 *  @name:	insert_element
 *  @about:	insert new element in hash table
 *  @args:	t (HASH_TABLE *) -> hash table
 *  @args:	e (void *) -> element
 *  @args:	key (char *) -> key
 *  @return:	return value
 * 		-1:memory allocation error
 * 		-2:the key already exists
 */
int
insert_element(HASH_TABLE *t, void *e, char *key)
{
	int i;
	HASH_NODE *tab;
	HASH_NODE *newnode;
	HASH_NODE *q;
	HASH_NODE *p;

	if (t == NULL)
	{
		fprintf(stderr, "Useage error hashtab doesn't exist");
		exit(1);
	}

	if (e == NULL)
	{
		fprintf(stderr, "outof memory\n");
		return -1;
	}

	/* calculate hash value */
	i = hash_func(key, t->tab_size);
	tab = t->buf;

	/* search target element */
	if (search_element(t, key) != NULL)
	{
		return -2;
	}

	/* insert element at first */
	if (tab[i].data == NULL)
	{
		memset(&tab[i], 0, sizeof(HASH_NODE));
		tab[i].key = strdup(key);
		tab[i].data = e;
		tab[i].next = NULL;
	}
	else
	{
		/* search end element */
		q = &tab[i];
		p = tab[i].next;

		while(p != NULL)
		{
			q = p;
			p = p->next;
		}

		/* create new node */
		newnode = (HASH_NODE *)malloc(sizeof(HASH_NODE));
		if (newnode == NULL)
		{
			perror("malloc");
			return -1;
		}
		memset(newnode, 0, sizeof(HASH_NODE));

		q->next = newnode;

		/* insert element */
		newnode->key = strdup(key);
		newnode->data = e;
		newnode->next = NULL;
	}
	t->element_num += 1;

	return 0;
}


/**
 *  @name:	delete_element
 *  @about:	if element related to key doesn't exist,return -1
 *  @args:	t (HASH_TABLE *) -> hash table
 *  @args:	key (char *) -> hash key
 *  @return: 	return 0 on success, return -1 in failure	
 */
int
delete_element(HASH_TABLE *t, char *key)
{
	int i;
	HASH_NODE *buf = NULL;
	HASH_NODE *p = NULL;
	HASH_NODE *prev = NULL;

	if (t == NULL || key == NULL)
		return -1;

	/* calculate hash value */
	i = hash_func(key,t->tab_size);
	buf = t->buf;

	/* element is not stored */
	if (buf[i].data == NULL)
		return -1;

	/* delete element */
	if (strcmp(buf[i].key, key) == 0)
	{
		free(buf[i].key);
		buf[i].key=NULL;
		buf[i].data=NULL;

		if (buf[i].next != NULL)
		{
			buf[i].key  = buf[i].next->key;
			buf[i].data = buf[i].next->data;
			buf[i].next = buf[i].next->next;
		}
		t->element_num -= 1;

		return 0;
	}
	else
	{
		p = buf[i].next;
		if (p == NULL)
			return -1;
		do {
			if (strcmp(p->key, key) == 0)
			{
				free(p->key);
				prev->next = p->next;
				free(p);
				t->element_num -= 1;
				return 1;
			}
			else
			{
				prev = p;
				p = p->next;
			}
		} while (p != NULL);
	}

	return -1;
}

/**
 *  @name:	search_element
 *  @about:	can't find "key":return NULL
 *  @args:	t (HASH_TABLE *) -> hash table
 *  @args:	key (char *) -> hash key
 *  @return:	return value on success, return NULL in failure
 */
void *
search_element(HASH_TABLE *t, char *key)
{
	int i;
	HASH_NODE *buf;
	HASH_NODE *p;

	if(t == NULL || key == NULL)
		return NULL;

	/* calclate hash value */
	i = hash_func(key, t->tab_size);
	buf = t->buf;

	/* element is not stored */
	if (buf[i].data == NULL)
		return NULL;

	/* return data mutched specified key */
	if (strcmp(buf[i].key, key) == 0)
	{
		return buf[i].data;
	}
	else
	{
		p = buf[i].next;
		if (p == NULL)
			return NULL;

		do {
			if (strcmp(p->key, key) == 0)
			{
				return p->data;
			}
			else
			{
				p = p->next;
			}
		} while (p != NULL);
	}

	return NULL;
}

/**
 *  @name:	update_element
 *  @about:	can't find "key":return -1
 *  @args:	t (HASH_TABLE *) -> hash table
 *  @args:	key (char *) -> hash key
 *  @args:	data: update data
 *  @return:	return value on success, return NULL in failure
 */
int update_element(HASH_TABLE *t, void *data, char *key) {
	int i;
	HASH_NODE *buf;
	HASH_NODE *p;

	if(t == NULL || key == NULL)
		return -1;

	/* calclate hash value */
	i = hash_func(key, t->tab_size);
	buf = t->buf;

	/* element is not stored */
	if (buf[i].data == NULL)
		return -1;

	/* return data mutched specified key */
	if (strcmp(buf[i].key, key) == 0) {
		buf[i].data = data;
		return 0;
	} else {
		p = buf[i].next;
		if (p == NULL)
			return -1;
		
		do {
			if (strcmp(p->key, key) == 0) {
				p->data = data;
				return 0;
			} else {
				p = p->next;
			}
		} while (p != NULL);
	}

	return -1;
}
/**
 *  @name:	handle_all_element
 *  @about:	execute "func(element)" to all elements in hash table.
 *  @args:	t (HASH_TABLE *) -> hash table
 *  @args:	func (int (*)(void *) ) -> function
 *  @return:	none
 */
void
handle_all_element(HASH_TABLE *t, int (*func)(void *))
{
	HASH_NODE *n;
	int i;

	if (t == NULL)
	{
		//    fprintf(stderr, "Warning:hash table is null\n");
		return ;
	}

	for (i = 0; i < t->tab_size; i++)
	{
		if (t->buf[i].key == NULL)
			continue;
		//printf("%s\n", t->buf[i].key);
		func(t->buf[i].data);

		n = t->buf[i].next;
		while (n != NULL)
		{
			//  printf("%s\n", n->key);
			func(n->data);
			n = n->next;
		}
	}

	return;
}

/**
 *  @name:	create_hash_array
 *  @about:	convert hash table to array by malloc
 *  @args:	t (HASH_TABLE *) -> hash table
 *  @return:	return hash table array
 */
HASH_NODE **
create_hash_array(HASH_TABLE *t)
{
	HASH_NODE **array;
	HASH_NODE *n;
	int i;
	int index = 0;

	if ((array = (HASH_NODE **)malloc(t->element_num * sizeof(HASH_NODE *))) == NULL)
	{
		perror("malloc");
		return NULL;
	}

	for (i = 0; i < t->tab_size; i++)
	{
		if (t->buf[i].key == NULL)
			continue;

		array[index] = &(t->buf[i]);
		index++;

		n = t->buf[i].next;

		while (n != NULL)
		{
			array[index] = n;
			index++;
			n = n->next;
		}
	}

	return array;
}
