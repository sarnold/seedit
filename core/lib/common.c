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
/* $Id: common.c,v 1.4 2006/04/21 00:07:32 ynakam Exp $ */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>
#include <seedit/common.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/types.h>
#include <dirent.h>
/**
 *  @name:	chop_nl
 *  @about:	chop \n
 *  @args:	buf (char *) -> target data
 *  @return:	none
 */
void
chop_nl(char *buf)
{
	int len;

	len = strlen(buf);

	if (buf[len - 1] == '\n')
		buf[len - 1] = '\0';

	return ;
}

/*delete char c at the end of buf*/
/*if deleted return 1, else 0*/
int chop_char(char *buf, char c){
  int len;
  
  len = strlen(buf);
  
  if (buf[len - 1] == c){
    buf[len - 1] = '\0';
    return 1;
  }
  return 0;
}

void chop_str(char *buf, char *del){
   int len;
  int i=0;
  int flag =1;
  int deleted=0 ;
  len = strlen(del);
  
  while(flag){
    while(del[i]!='\0'){
      deleted = chop_char(buf,del[i]);
      if(deleted)
	continue;
      i++;
    }    
    if(deleted == 0)
      flag = 0;
  }  
}

/**
 *  @name:	get_nth_tok
 *  @about:	get n th token of str.
 *  @args:	str (char *) -> target string
 *  @args:	delm (char *) -> delimitor
 *  @args:	n (int) -> target number
 *  @attention:	str is destroyed.
 */
char *
get_nth_tok(char *str, char *delm, int n)
{
	char *p;
	int i = 0;
	char *result = NULL;

	p = strtok(str, delm);
	if (p == NULL)
	{
		return NULL;
	}

	i = 0;
	while (p != NULL)
	{
		i++;
		if (i == n)
		{
			result = p;
		}
		p = strtok(NULL, delm);
	}

	return result;
}

/*BY Y.N*/
/*return result is stored in malloced region*/
char *get_nth_tok_alloc(char *str, char *delm, int n){
  char *buf;

  buf = strdup(str);
  return get_nth_tok(buf, delm, n);

}
/**
 *  @name:	extend_array
 *  @about:	extends dynamic array.
 *  @args:	array (void *) -> pointer to dynamic array.
 *  @args:	array_num (int) -> number of elements
 *  @args:	size (size_t) -> size of each element
 *  @return:	pointer to extended array 
 */
void *extend_array(void *array, int *array_num, size_t size){
  void *tmp;
  
  if (array == NULL){
    *array_num = 0;
    
    if ((tmp = (void *)malloc(size)) == NULL){
      perror("malloc");
      exit(1);
    }
  }else{
    if ((tmp = (void *)realloc(array, size*(*array_num + 1))) == NULL){
      perror("realloc");
      exit(1);
    }
  }
  array = tmp;
  (*array_num)++;
  

  return tmp;
}


int get_ntarray_num(char **array){
  int i;
  int num =0;
  if(array==NULL)
    return 0;
  for(i = 0; array[i]!=NULL;i++){
    num ++;
  }
  return num;
}

/*check whether str exists in array*/
int ntarray_check_exist(char **array,char *str){
  int i;

  if(array==NULL)
    return 0;
  for(i = 0; array[i]!=NULL;i++){
    if(strcmp(array[i],str)==0)
      return 1;
  }
  return 0;  
}

void free_ntarray(char **array){
  int i;
  if(array==NULL){
    return;
  }
  for(i = 0;array[i]!=NULL;i++)
    free(array[i]);
  free(array);
}

/*dynamic null terminated char array*/
/* array: array, 
   str:string set at the end of the array, strduped inside*/
char **extend_ntarray(char **array,char *str){
  char **tmp;
  int array_num = 0;

  if (array == NULL){
    tmp = (char **)malloc(sizeof(char *)*2);
  }else{
    array_num = get_ntarray_num(array);
    tmp = (char **)my_realloc(array, sizeof(char *)*(array_num + 2));
  }
  array = tmp;
  array[ array_num ] = strdup(str);
  array[ array_num +1 ] = NULL;
  return tmp;
}

char **joint_ntarray(char **a1, char **a2){
  int num;
  int num_a1;
  int num_a2;
  char **result;
  int i;
  num_a1 = get_ntarray_num(a1);
  num_a2 = get_ntarray_num(a2);
  num = num_a1 + num_a2;
  
  result = (char **)my_malloc(sizeof(char *)*(num + 2));
  for(i=0;i<num_a1;i++){
    result[i] = a1[i];
  }
  for(i=0;i<num_a2;i++){
    result[i+ num_a1] = a2[i];
  }

  result[num ] =NULL;

  return result;
}

/*By Yuichi Nakamura*/
/*make fullpath from dir and file. fullpath=<dir>/<file>*/
char *mk_fullpath(char *dir, char *file){
  char *fullname;
  int fullnamelen = strlen(dir) + strlen(file);
  
  fullname = (char *)malloc(sizeof(char)*(2+fullnamelen));
  if(fullname == NULL)
    return NULL;
  
  if (strcmp(dir, "/") == 0)
    {
    sprintf(fullname, "%s%s", dir, file);
    }
  else
    {
      sprintf(fullname, "%s/%s", dir, file);
    }  
  
  return fullname;
}



/**
 *  @name:	error_print
 *  @about:	call yyerror like printf
 *  @args:	file (char *) -> file name
 *  @args:	lineno (int) -> line nuber
 *  @args:	fmt (char *) -> print format
 *  @return:	none
 */
void
error_print(char *file, int lineno, char *fmt,...)
{
	va_list ap;
	char buf[1024];

	va_start(ap, fmt);

	vsnprintf(buf, sizeof(buf), fmt, ap);
	va_end(ap);

	fprintf(stderr, "ERROR:In file %s:%d:[%s]\n", file, lineno, buf);
}


/*By Y.N*/
void * my_malloc(size_t size){
  void *p;  
  p = malloc(size);
  if (p ==NULL){    
    perror("malloc");
    exit(1);
  }
  return p;
}
void * my_realloc(void *p, size_t size){
  p = (char *)realloc(p, size);
  if(p == NULL){
    perror("realloc");
    exit(1);
  }
  return p;
}

/*joint str a and b, 
allocates and returns jointed str*/
char *joint_str(char *a, char *b){
  int len;
  char *result;
  len = strlen(a) + strlen(b);
  result = (char *)my_malloc((len+1)*(sizeof(char)));
  snprintf(result, len+1, "%s%s",a,b);
  return result;
}

char *joint_3_str(char *a, char *b, char *c){
  char *tmp;
  char *result;
  tmp = joint_str(a,b);
  
  result = joint_str(tmp, c);
  free(tmp);
  return result;
}


/*checks whether name exists in list(NULL terminated).*/
int check_exist_in_list(char *name, char **list){
  int exist = 0;
  int i = 0;
  if (list == NULL)
    return 0;
  while(list[i] != NULL ){
    if(strcmp(name, list[i]) == 0){
      exist = 1;
      break;
    }
    i++;
  }
  return exist;
}

/*split by delm and set value in list. list max length is max*/
/*success: return 0
exceed max return -1
*/
int split_and_set_list(char *buf, char *delm, char **list, int max){
  char *p;
  char *work;
  work = strdup(buf);
  int i = 0;
  
  p = strtok(buf, delm);
  if (p == NULL){
    list[0]=NULL;
    return 0;
  }
  
  while (p != NULL){    
    p = strtok(NULL, delm);
    
    if(p != NULL)
      list[i] = strdup(p);
    i++;    

    if(i>=max){
      return -1;
    }
    list[i] = NULL;
  }  
  free(work);

  return 0;
}


/**
 *  @name:	get_prefix
 *  @about:	chop "_t" or "_r" and return it(by malloc)
 *  @args:	p (char *) -> path name
 *  @return:	prefix
 */
char *get_prefix(char *p){
  int len;
  char *result;
  len = strlen(p);
     
  if (len < 3) {
    fprintf(stderr, "invalid domain %s\n", p);
    exit(1);
  }
  
  result = (char *)my_malloc(sizeof(char) * (len+1));
  strcpy(result, p);  
  result[len-2] = '\0';
  
  return result; 
}


/*if type ends with _t return 1, else 0*/
int check_type_suffix(char *type){
  int len;  
  len = strlen(type);
  if (len < 2 || !(type[len-2] == '_' && type[len-1] == 't')){
    return 0;
  }
  return 1;
}


/**
 *  @name:	debug_print
 *  @about:	call yyerror like printf
 *  @args:	file (char *) -> file name
 *  @args:	lineno (int) -> line nuber
 *  @args:	fmt (char *) -> print format
 *  @return:	none
 */
void
debug_print(char *file, int lineno, char *fmt,...)
{
#ifdef DEBUG
	va_list ap;
	char buf[1024];

	va_start(ap, fmt);

	vsnprintf(buf, sizeof(buf), fmt, ap);
	va_end(ap);

	fprintf(stderr, "DEBUG:In file %s:%d:[%s]\n", file, lineno, buf);
#endif
}


/**
 *  @name:	make_role_to_domain
 *  @about:	This generates domain name by malloc from rolename.
 * 		domain name is <role name prefix>_t
 *  @args:	name (char *) -> role
 *  @return:	return domain name exchanged role name
 */
char *make_role_to_domain(char *name){
  int len;
  char *domain_name;
  
  len = strlen(name);
  if ((domain_name = (char *)malloc(len+1)) == NULL){
    perror("malloc");
    exit(1);
  }
  
  strcpy(domain_name,name);
  domain_name[len-1] = 't';
  
  return domain_name;
}

char *make_domain_to_role(char *name){
  int len;
  char *role_name;
  
  len = strlen(name);
  if ((role_name = (char *)malloc(len+1)) == NULL){
    perror("malloc");
    exit(1);
  }
  
  strcpy(role_name,name);
  role_name[len-1] = 'r';
  
  return role_name;

}


/**
 *  @name:	strip_slash
 *  @about:	Remove "/" at the end of "s".
 *              But when s is "/",this function does nothing.
 *  @args:	s (char *) -> target data
 *  @return:	none
 */
void strip_slash(char *s){
  int len;
  
  len = strlen(s);
  if(strcmp(s,"~/")==0)
    return;

  if (s[len-1] == '/' && len > 1){
    s[len-1] = '\0';
  }
}

/*
get NULL terminated array, that contains parent dir and |path| it self for |path|.
*/
char **get_dir_list(char *path,char **homedir_list){
  char **list=NULL;
  char **tmp_list;
  char *p;
  char *prev;
  char *current;
  int len;
  int i;
  char *work;
  char delm[]="/";

  if(path[0]!='/' && path[0]!='~'){
    return NULL;
  }
  
  if(path[0]=='~'){
    list = get_dir_list(path+1, homedir_list);
    for(i=0; list[i]!=NULL;i++){
      work = strdup(list[i]);
      list[i]=joint_str("~",work);
      free(work);
    }
    for(i=0;homedir_list[i]!=NULL;i++){
      tmp_list  = get_dir_list(homedir_list[i], homedir_list);
      list = joint_ntarray(list, tmp_list);
    } 
    
    return list;
  }

  work = strdup(path);
  strip_slash(work);
  list = extend_ntarray(list,"/");    
  p = strtok(work, delm); 
  if (p == NULL){
    return list;
  }

  len = strlen(p);
  current = (char *)my_malloc((len+3)*sizeof(char));
  snprintf(current, len+2, "/%s",p);
  list = extend_ntarray(list,current);    

  while (p != NULL){
    p = strtok(NULL, delm);
    if(p!=NULL){
      len = strlen(current)+2+strlen(p);
      prev = strdup(current);
      free(current);
      current = (char *)my_malloc((len+3)*sizeof(char));
      snprintf(current, len+2, "%s/%s", prev,p);
      free(prev);
      list = extend_ntarray(list,current);    
    }
  }
  if(is_home_dir(path, homedir_list)){
    list = extend_ntarray(list,"~/");
  }

  free(current);
  free(work);
  return list;
}


/**
 *  @name:	make_label
 *  @about:	make label name from filename.
 *  @args:	name (char *) -> label name
 *  @return:	returns label name by malloc.
 *  @notes:	!!Warning!! Conflict of label name isn't considered
 */
char *make_label(char *name)
{
	char *head = NULL;
	char *label;
	int len;
	int i;
	char *filename;
	char *suffix;
	char *home_prefix = "homedir_";
	
	if(name == NULL)
	    return NULL;

	filename = strdup(name);

	/*home directory*/
	if (filename[0] == '~'){
	  suffix = make_label(filename + 1);
	  label = joint_str(home_prefix,suffix);
	  return label;
	}

	if (filename[0] != '/' )
	{
		/**
		 * if the top of filename isn't "/",
		 * filename is "allow exclusive"
		 */
		label = strdup(name);
		return label;
	}

	/* the label of root directory */
	if (strcmp(name, "/") == 0)
	{
		label = strdup(ROOT_LABEL);
		return label;
	}

	/* chop "/" at the top of filename,at the end of filename */
	if (filename[0] == '/')
		head = filename+1;

	len = strlen(head);

	if (head[len-1] == '/')
	{
		head[len-1]='\0';
	}

	/* convert "/" to "_","." to "d" */
	for (i = 0; i < len; i++)
	{
		if (head[i] == '/')
		{
			head[i]='_';
		}
		if(head[i] == '.')
		{
			head[i]='d';
		}
		if (head[i] == '+')
		{
			head[i] = 'p';
		}
		if (head[i] == '-')
		{
			head[i] = 'm';
		}

		if (head[i] == ':')
		{
			head[i] = 's';
		}
	}

	label = (char *)my_malloc(sizeof(char)*(len+3));

	sprintf(label, "%s_t", head);
	free(filename);

	return label;
}

/**
 *  @name:	chk_child_dir
 *  @about:	check wether target path includes parent path 
 *  @args:	s (char *) -> parent path
 *  @args:	t (char *) -> child path
 *  @return:	if t is the child directory of s,then return 1
 *		s must not end with "/"
 */
int chk_child_dir(char *s, char *t){
	int len_s;
	int len_t;

	if (strcmp(s, "/") == 0)
	{
		return 1;
	}

	len_s = strlen(s);
	len_t = strlen(t);

	if (len_s >= len_t)
		return 0;

	if (strncmp(s, t, len_s) != 0)
		return 0;

	if (t[len_s] == '/')
		return 1;

	return 0;
}


/**
 *  @name:	chop_slash	
 *  @about:	chop slash from target string 
 *  @args:	s (char *) -> target string
 *  @return:	none
 */
void
chop_slash(char *s)
{
	int len;

	if (strcmp(s, "/") == 0)
	{
		return ;
	}

	len = strlen(s);

	if (s[len-1] == '/')
	{
		s[len-1] = '\0';
	}
}

/*
  If t is directly under dir s then return 1
  "root" is path to root file system for cross development
  if not cross development, root will be NULL
*/
int chk_child_file(char *s, char *t, char *root){
	char *s2;
	char *name;
	int len_s;
	int len_t;
	struct stat buf;

	len_t = strlen(t);

	s2 = strdup(s);
	chop_slash(s2);

	len_s = strlen(s2);

	if (len_s >= len_t) {
		goto notchild;
	}

	if (t[len_t - 1] == '/')
		goto notchild;
	root_stat(t, &buf, root, stat);
	if (S_ISDIR(buf.st_mode)) {		
		goto notchild;
	}

	if (strncmp(s2, t, len_s) != 0)
		goto notchild;
	
	if (strcmp(s2,"/") == 0){
		name = &t[len_s];
	} else {
		name = &t[len_s + 1];
	}

	if (strchr(name, '/'))
		goto notchild;
	
	free(s2);
	return 1;
	
 notchild:
	free(s2);
	return 0;
}

/*
if path is homedir, 
return homedir name, with slash, 
return value is malloced, must free.
For example, assume /home is included in homedir_list,
path: /home/ynakam/hoge
->  return /home/
path: /usr/bin/
-> return NULL
path: /home/
-> return NULL
*/
char *match_home_dir(char *path, char **homedir_list){
  int i;
  char *home;
  char *s;
  for(i =0 ; homedir_list[i]!=NULL ;i++){
    home = joint_str(homedir_list[i],"/");   
    if(strcmp(home, path)==0)
      continue;
    s = strstr(path, home);
    if(s == path){
      return strdup(homedir_list[i]);
    }else{
      free(home);
    }
  }
  return NULL;
}

int is_home_dir(char *path, char **homedir_list){
  if (match_home_dir(path, homedir_list)==NULL)
    return 0;
  
  return 1;
}


char *get_user_from_path(char *path, char **homedir_list){
  char *home;
  char *user;
  char *result;
  char *work;
  char *s;
  int l;
  home = match_home_dir(path, homedir_list); 

  if(home == NULL)
    return NULL;
  
  l = strlen(home);
  work = strdup(path);
  user = work + l +1;

  s = strchr(user, '/');
  if(s!=NULL)
    *s = '\0';
  
  free(home);

  result = strdup(user);
  free(work);
  return result;
}

/*get type from security context
  result: type,allocated by malloc, when error, NULL returned
*/
char *get_type_from_context(security_context_t context){
  char *type;
  char *work;
  char *work2;
  work = strdup(context);
  work2 = get_nth_tok(work, ":", 3);
  type = strdup(work2);
  free(work);
  return type;
}


char *get_name_from_path(char *path) {
	char *s;
	s = strrchr(path, '/');
	if (!s)
		return NULL;
	if (*(s+1) != '\0') {
		s++;
		return strdup(s);
	}
	return NULL;
}

/*do stat() to root+path */
int root_stat(char *path, struct stat *buf, char *root, int (*statfunc)(const char *p, struct stat *b)) {
	char *realpath;
	int rc;
	if(root) {
		realpath = joint_str(root, path);
		rc = statfunc(realpath,buf);	
		free(realpath);
	} else {
		return statfunc(path, buf);
	}

	return rc;
} 

DIR *root_opendir(const char *name, char *root) {
	DIR *d;
	char *realpath;
	if(root) {
		realpath = joint_str(root, (char *)name);
	} else {
		realpath = strdup(name);
	}
       
	d = opendir(realpath);
	free(realpath);
	return d;
}

