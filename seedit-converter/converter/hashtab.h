/*
 * All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
 */
/* $Id: hashtab.h,v 1.1.1.1 2006/02/23 22:04:56 ynakam Exp $ */

#ifndef HASH_TAB_H
#define HASH_TAB_H

/**
 *  data structure for hash table
 */
typedef struct hash_node_t HASH_NODE;

/**
 *  hash node structure
 */
struct hash_node_t
{
	char		*key;		/* hash key     */
	void		*data;		/* hash data    */
	HASH_NODE	*next;		/* next pointer */
};

/**
 *  hash table structure 
 */
typedef struct hash_table_t
{
	HASH_NODE	*buf;		/* the body of hash table			*/
	int		tab_size;	/* the size of hash table			*/
	int		element_num;	/* the number of elements in the hash table	*/
} HASH_TABLE;

/**
 *  functions to handle hash functions
 */
HASH_TABLE *create_hash_table(int);
int delete_hash_table(HASH_TABLE *);	/* not implemented	*/
int insert_element(HASH_TABLE *, void *, char *);
int delete_element(HASH_TABLE *, char *);
void *search_element(HASH_TABLE *, char *);
void handle_all_element(HASH_TABLE *,int (*)(void *));
HASH_NODE **create_hash_array(HASH_TABLE *);

#endif
 
