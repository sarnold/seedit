/*
  Common functions to parse SPDL.
  All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
  (c) Yuichi Nakamura ynakam@gwu.edu */
/*Some functions are taken from action.c developed by Hitachi Software, cleand up by Yuichi Nakamura */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#include <seedit/parse.h>
#include <seedit/common.h>

/**
 *  Buffer for error message
 */
static char errmsg[1024];


/**
 *  Variable used to analyze permission
 */
static int tmp_perm = DENY_PRM;

int get_tmp_perm(){
  return tmp_perm;
}

void set_tmp_perm(int value){
  tmp_perm=value;
}

/**
 *  @name:	str_to_perm
 *  @about:	convert permission string to number
 *  @args:	s (char *) -> permission string
 *  @return:	permission number
 */
int str_to_perm(char *s){

	if (strcmp(s, READ_STR) == 0){
	  return READ_PRM;
	}else if (strcmp(s, WRITE_STR) == 0){
	  return WRITE_PRM;
	}else if (strcmp(s, EXECUTE_STR) == 0){
	  return EXECUTE_PRM;
	}else if (strcmp(s, APPEND_STR) == 0){
	  return APPEND_PRM;
	}else if (strcmp(s, SEARCH_STR) == 0){
	  return SEARCH_PRM;
	}else if (strcmp(s, OVERWRITE_STR) ==0 ){
	  return OVERWRITE_PRM;
	}else if (strcmp(s, APPEND_STR) == 0){
	  return APPEND_PRM;
	}else if (strcmp(s, ERASE_STR) == 0){
	  return ERASE_PRM;
	}else if (strcmp(s, CREATE_STR) == 0){
	  return CREATE_PRM;	
	}else if (strcmp(s, SETATTR_STR)==0){
	  return SETATTR_PRM;
	}else if (strcmp(s,DOMAIN_EXECUTE_STR)==0){
	  return DOMAIN_EXECUTE_PRM;
	}else if(strcmp(s, WILDCARD_STR) == 0){
	  return READ_PRM|WRITE_PRM|EXECUTE_PRM|APPEND_PRM|SEARCH_PRM|OVERWRITE_PRM|ERASE_PRM|CREATE_PRM|SETATTR_PRM;
	}
	return -1;
}


/**
 *  @name:	perm_to_str
 *  @about:	convert permission number to string
 *  @args:	allowed (int) -> permission number
 *  @return:	return string as static buffer
 */
char *perm_to_str(int allowed){
  static char buf[256];
  char str[] = {'-', '-', '-', '-', '-', '-','-','-','-','\0'};
  
  if (allowed & READ_PRM){
    str[0] = 'r';
  }if (allowed & WRITE_PRM){
    str[1] = 'w';
  }
  if (allowed & EXECUTE_PRM){
    str[2] = 'x';
  }

  if (allowed & SEARCH_PRM){
    str[3]='s';
  }

  if (allowed & APPEND_PRM){
    str[4]='a';
  }
  
  if(allowed & ERASE_PRM){
    str[5]='e';
  }
  if(allowed & OVERWRITE_PRM){
    str[6]='o';
  }
  if(allowed & CREATE_PRM){
    str[7]='c';
  }
  if(allowed & SETATTR_PRM){
    str[8]='t';
  }

  strcpy(buf, str);
  
  return buf;
}


/**
 *  @name:	str_to_rw_perm
 *  @about:	convert rw permission string to rw permission number
 *  @args:	s (char *) -> permission string
 *  @return:	return permisstion number on success, return -1 in failure.
 */
int
str_to_rw_perm(char *s)
{
	if (strcmp(s, READ_STR) == 0)
	{
		return READ_PRM;
	}
	else if (strcmp(s, WRITE_STR) == 0)
	{
		return WRITE_PRM;
	}
	else if(strcmp(s, WILDCARD_STR) == 0)
	{
	  return READ_PRM|WRITE_PRM;
	}
	return -1;
}

int str_to_net_perm(char *s){
  
  if(strcmp(s,NET_PERM_SEND_STR)==0){
    return  NET_PERM_SEND;
  }else if(strcmp(s,NET_PERM_RECV_STR)==0){
    return NET_PERM_RECV;
  }else if(strcmp(s,NET_PERM_BIND_STR)==0){
    return NET_PERM_BIND;
  }

  return -1;
}

/**
 *  @name:	str_to_sig_perm
 *  @about:	convert sig permission string to sig permission number
 *  @args:	s (char *) -> permission string
 *  @return:	return permisstion number on success, return -1 in failure.
 */
int str_to_sig_perm(char *s){
  
  if (strcmp(s, CHID_STR) == 0){
    return CHID_PRM;
  }else if (strcmp(s, KILL_STR) == 0) {
    return KILL_PRM;
  }else if (strcmp(s, STOP_STR) == 0) {
    return STOP_PRM;
  }else if (strcmp(s, OTHERSIG_STR) == 0){
    return OTHERSIG_PRM;
  }else if (strcmp(s, NULL_STR) == 0){
    return NULL_PRM;
  }else if(strcmp(s,"*") == 0){
    return CHID_PRM|KILL_PRM|STOP_PRM|NULL_PRM;
  }
	return -1;
}



/**
 *  @name:	add_permisstion
 *  @about:	add permittion 
 *  @args:	s (char *) -> admin permisstion string
 *  @args:	flag (int) -> 
 *  @args:	init (int) -> whether ADMIN_RULE buffer is initialized..
 *  @return:	return 0 on success.
 */
int add_permission(char *s, int flag, int init)
{
	int p = DENY_PRM;

	/* this means to start analyze permission */
	if (init == 1)
	{
		tmp_perm = DENY_PRM;
	}


	/* get permission number */
	if (flag == FILE_PERM)
	{
		p = str_to_perm(s);
	}
	if (flag == RW_PERM)
	{
		p = str_to_rw_perm(s);
	}
	if (flag == SIG_PERM)
	{
		p = str_to_sig_perm(s);
	}
	if (flag ==NET_PERM){
	  p = str_to_net_perm(s);
	}
	if (flag == ADM_PERM)
	{
	  
	        debug_print(__FILE__, __LINE__, "bug!!!");
		exit(1);
	}

	/* error check */
	if (p < 0)
	{
	        action_error(errmsg, sizeof(errmsg), "no such permission %s\n", s);
                exit(1);
	}

	/* Add permission */
	tmp_perm |= p;

	return 0;
}
/**
 *  @name:	action_error
 *  @about:	yyerror like printf
 *  @args:	fmt (char *) -> format
 *  @return:	none
 */
void
action_error(char *fmt, ...)
{
	va_list ap;
	char buf[1024];

	va_start(ap, fmt);

	vsnprintf(buf, sizeof(buf), fmt, ap);
	va_end(ap);

	yyerror(buf);
}
void
action_warn(char *fmt, ...)
{
	va_list ap;
	char buf[1024];

	va_start(ap, fmt);

	vsnprintf(buf, sizeof(buf), fmt, ap);
	va_end(ap);

	yywarn(buf);
}


int warn_tmpfs(){
  action_warn("allowtmpfs is not used. Use allowfs tmpfs instead\n");
  return 0;
}


void free_strlist(char **list){
  free_ntarray(list);
  list = NULL;
  return ;
}

char **add_strlist(char **list, char *str, int init_flag){
  if(init_flag==1){
    if(list!=NULL){
      free_strlist(list);    
      list = NULL;
    }
  }
  list = extend_ntarray(list, str);
  return list;
}

char *alloc_str(char *str, char *old){  
  if(old!=NULL)
    free(old);
  
  return strdup(str);
}
