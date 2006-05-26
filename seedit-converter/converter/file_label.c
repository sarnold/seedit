/*
Written by Yuichi Nakamura
based on Hitachi Software's code.
Some Hitachi Software's codes are used.
*/
/* All Rights Reserved (C) 2005-2006, Yuichi Nakmura ynakam@gwu.edu */
/*
 * All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include "hashtab.h"
#include "global.h"
#include "file_label.h"
#include <seedit/common.h>

/**
 ***********************************************
 *   Functions to associate label with file 
 ***********************************************
 */

/**
 *  hash table of association of label with file
 *  key:file name
 */
HASH_TABLE *file_label_table;
HASH_TABLE *dir_label_table;
HASH_TABLE *defined_label_table;

static HASH_TABLE *declared_type_table;

#define FILE_LABEL_TABLE_SIZE 1024*8


#if 0
/*
 * convert "path" to labelname.
 * return label name by malloc.
 * label is <program name>_exec_t
 */
static char *
make_exec_label(char *path)
{
	char *p;
	char *result;
	const char tail[] = "_exec_t";
	int len;
	int i;

	p = strrchr(path, '/');
	if (p == NULL)
	{
		yyerror("invalid file name\n");
		exit(1);
	}
	p = p+1;

	len = strlen(p);
	result = (char *)my_malloc(sizeof(char) * (len + sizeof(tail) + 1));

	sprintf(result, "%s%s", p, tail);

	len = strlen(result);
	for (i = 0; i < len; i++)
	{
		if (result[i] == '.')
		{
			result[i] = '_';
		}
	}

	//fprintf(stderr, "%s", result);

	return result;
}
#endif

/**
 *  @name:	add_file_label
 *  @about;	register label with FILE_LABEL.
 * 		label is generated by path in "file_acl".
 *  @args:	file_acl (void *) -> 
 *  @return:	return 0 on success
 */
static int add_file_label(FILE_ACL_RULE file_rule){
  FILE_LABEL *label;
  FILE_LABEL *tmp;
  char *s;

  /* create label buffer */
  label = (FILE_LABEL *)my_malloc(sizeof(FILE_LABEL));
  
  /* store path name and label name */
  label->filename = strdup(file_rule.path);
  label->labelname = make_label(file_rule.path);

  if (file_rule.state == FILE_ALL_CHILD){
    label->rec_flag = 1;
  }else	{
    label->rec_flag = 0;
  }

  /* search same file info */
  if ((tmp = search_element(file_label_table, label->filename)) == NULL){
    /* when filename isn't exclusive name, check label name conflict */
    if (strchr(label->filename, '/') != NULL){
      if (register_label_table(label->labelname) == -2){
	s=resolve_label_conflict(label->labelname);
	if (strcmp(label->filename, "/proc") != 0){
	  fprintf(stderr,
		  "Warning label name conflict is detected.Label for %s was %s but replaced by %s.\n",
		  label->filename, label->labelname, s);
	}
	free(label->labelname);
	label->labelname = s;
      }
    }
    
    insert_element(file_label_table, label, label->filename);
  }
  else{
    if (tmp->rec_flag != 0){
      tmp->rec_flag = label->rec_flag;
    }
  }
  
  return 0;
}


/**
 *  @name:	one_domain_file_label
 *  @about:	
 *  @args:	domain (void *) -> domain
 *  @return:	return 0 on success 
 */
static int
one_domain_file_label(void *domain)
{
	DOMAIN *d;
	FILE_ACL_RULE *file_rule_array;
	int file_rule_array_num;
	int i;
	d = domain;
	file_rule_array = d->file_rule_array;
	file_rule_array_num = d->file_rule_array_num;
	for(i=0;i<file_rule_array_num;i++){
	  add_file_label(file_rule_array[i]);
	}

	return 0;
}

/**
 *  @name:	insert_force
 *  @about:	insert "filename,labelname" in file_label hash table
 *  @args:	filename (char *) -> file name
 *  @args:	labelname (char *) -> label name
 *  @return:	none
 */
static void
insert_force(char *filename, char *labelname)
{
	FILE_LABEL *l;

	if ((l = search_element(file_label_table, filename)) == NULL)
	{
		l = (FILE_LABEL *)my_malloc(sizeof(FILE_LABEL));
		l->filename = strdup(filename);
		l->labelname = strdup(labelname);
		l->rec_flag = 1;
		insert_element(file_label_table, l, l->filename);
	}
	else
	{
		free(l->labelname);
		l->labelname = strdup(labelname);
	}
}

/**
 *  @name:	set_domain_trans_label
 *  @about:	register label named by domain_trans
 *  @args:	none
 *  @return:	none
 */
static void set_domain_trans_label(){
  int i;
  TRANS_RULE t;
  FILE_LABEL *label;
  FILE_LABEL *tmp;
  int st;
  char *s;

  for (i = 0; i < domain_trans_rule_num; i++){
    t = rulebuf[i];
    label = (FILE_LABEL *)my_malloc(sizeof(FILE_LABEL));

    if(t.path == NULL)
      continue;
    label->filename = strdup(t.path);
    label->labelname = make_label(t.path);
    
    tmp = search_element(file_label_table, label->filename);
    if (tmp == NULL) {
      if (register_label_table(label->labelname) == -2)	{
	s=resolve_label_conflict(label->labelname);
	free(label->labelname);
	label->labelname = s;
	fprintf(stderr,
		"Warning label name conflict is detected.Label for %s was %s but replaced by %s.\n",
		label->filename, label->labelname, s);
      }
      st = insert_element(file_label_table, label, label->filename);
    } else {
      tmp->rec_flag=0;	//???OK?      
    }
  }
  
  return;
}

/**
 *  @name:	create_file_label_table
 *  @about:	major function to label files
 *  @args:	domaintab (HASH_TABLE *) -> hash table
 *  @return:	return 0 on success
 */
int
create_file_label_table(HASH_TABLE *domaintab){
  int i;
  FORCE_LABEL *fl;
  /* create file hash table */
  file_label_table = create_hash_table(FILE_LABEL_TABLE_SIZE);
  
  /* store handler function to the domain table */
  handle_all_element(domaintab, one_domain_file_label);

  /*label files in force_label_list*/
  for(i=0; converter_conf.force_label_list[i]!=NULL; i++ ){
    fl = converter_conf.force_label_list[i];
    insert_force(fl->filename, fl->type);
  }
  set_domain_trans_label();

  return 0;
}

int create_dir_label_table(HASH_TABLE *domaintab){
  HASH_NODE **array;
  int num;
  int i;
  char *name;
  FILE_LABEL *label;
  FILE_LABEL *tmp;
  char prefix[]="dir_";
  char *s;
  
  dir_label_table = create_hash_table(FILE_LABEL_TABLE_SIZE);  
  array = create_hash_array(all_dirs_table);
  if(array==NULL)
    return 0;
  num = all_dirs_table->element_num;
  
  for (i=0; i<num; i++){
    name = array[i]->key;
    label = (FILE_LABEL *)my_malloc(sizeof(FILE_LABEL));
    label->filename = strdup(name);
    label->labelname = joint_str(prefix,make_label(name));
    
    if ((tmp = search_element(dir_label_table, label->filename)) == NULL){ 
      if (register_label_table(label->labelname) == -2){
	s = resolve_label_conflict(label->labelname);
	if (strcmp(label->filename, "/proc") != 0){
	  fprintf(stderr,
		  "Warning label name conflict is detected.Label for %s was %s but replaced by %s.\n",
			label->filename, label->labelname, s);
	}
	free(label->labelname);
	label->labelname = s;
      }
    }
    insert_element(dir_label_table, label, label->filename);
  }
  
  free(array);

  

  return 0;
}




/**
 *  @name:	print_file_label
 *  @about:	print file label
 *  @args:	n (void *) -> file data
 *  @retrun:	return 0
 */
static int
print_file_label(void *n)
{
	FILE_LABEL *l;

	l = n;
	printf("%s,%s\n", l->filename, l->labelname);

	return 0;
}
 
/**
 *  @name:	print_file_label_tab
 *  @about:	print file label table
 *  @args:	none
 *  @return:	none
 */
void
print_file_label_tab()
{
	handle_all_element(file_label_table, print_file_label);
}

void
print_dir_label_tab()
{
	handle_all_element(dir_label_table, print_file_label);
}



/**
 *  @name:	free_file_label
 *  @about:	free file label buffer
 *  @args:	l (void *) -> label buffer
 *  @return:	return 0
 */
static int
free_file_label(void *l)
{
	FILE_LABEL *n;

	n = l;
	free(n->filename);
	free(n->labelname);
	free(n);

	return 0;
}

/**
 *  @name:	delete_file_label_tab
 *  @about:	delete file label table
 *  @args:	none
 *  @return:	none
 */
void
delete_file_label_tab()
{
	handle_all_element(file_label_table, free_file_label);
	delete_hash_table(file_label_table);
}

/**
 *  output file pointer (static)
 */
static FILE *out_fp;

/**
 *  @name:	print_type
 *  @about:	print file type
 *  @args:	n (void *) -> FILE_LABEL pointer 
 *  @return:	return 0 on success
 */	

static int print_type(void *n){
  FILE_LABEL *l;
  FILE_LABEL *t;  
  l = n;
  t = (FILE_LABEL *)search_element(declared_type_table, l->labelname);
  if(t == NULL){
    fprintf(out_fp, "type %s,file_type;\n", l->labelname);
    fprintf(out_fp, "#%s\n", l->filename);	  
    insert_element(declared_type_table, l, l->labelname);
  }
  
  return 0;
}

/**
 *  @name:	out_file_type
 *  @about:	output file type
 *  @args:	out (FILE *) -> output file descripter
 *  @return:	none
 */

void out_file_type(FILE *out){	
  out_fp = out;
  declared_type_table = create_hash_table(FILE_LABEL_TABLE_SIZE);	
  handle_all_element(file_label_table, print_type);
#ifdef DIRSEARCH
  handle_all_element(dir_label_table, print_type);
#endif
}

/**
 *  Functions related to file_context
 */
static char **file_name_buf;
//static FILE *context_out_fp;

/**
 *  @name:	set_buf
 *  @about:	to set value in array to  sort
 * 		This function is supposed to be called only once because of "static"
 *  @args:	e (void *) -> file label
 *  @return:	return 0 on success
 */
static int
set_buf(void *e)
{
	static int i=0;
	FILE_LABEL *l;
	l = e;
	file_name_buf[i] = l->filename;
	i++;

	return 0;
}

/**
 *  @name:	compar
 *  @about:	compare strings
 *  @args:	a (void *) -> first target
 *  @args:	b (void *) -> second target
 *  @return:	return 0 if a < b, otherwise return 1
 */
static int
compar(const void *a, const void *b)
{
	return strcmp(*(char **)a, *(char **)b);
}

static int
rev_compar(const void *a, const void *b)
{
	return strcmp(*(char **)b, *(char **)a);
}


int not_generate_condition_normal_file(char *filename){

  /*does not output for proc mount point*/
  if(check_exist_in_list(filename, converter_conf.proc_mount_point_list)){
    return 1;
  }
  /*not filename, ~/ */
  if(filename[0]!='/'){
    return 1;
  }
  /*/home is outputted in different place*/
  if(is_home_dir(filename, converter_conf.homedir_list))
    return 1;

  return 0;

}

/*
Output file contexts for files
that does not matche condition by not_generate_condition(filename)
*/
void out_file_contexts_general(FILE *file_contexts, int (*not_generate_condition)(char *)){
  int i;
  FILE_LABEL *fl;
  struct stat buf;
  char fc_str[MAX_FILENAME]="";
  char prev_fc_str[MAX_FILENAME]="";//to eleminate multiple same specification
  char *tmp_file_table[MAX_TMP_FILE];
  int tmp_file_table_size = 0;
#ifdef DIRSEARCH
  HASH_NODE **dir_label_array ;
#endif
  char *filename=NULL;
  int r;
  FILE *file_tmp_fp; /*output fc for normal files temporally*/
  FILE *outfp;
  
  file_tmp_fp = tmpfile();
   
  
  for (i = 0; i < file_label_table->element_num; i++){
    fl = (FILE_LABEL *)search_element(file_label_table, file_name_buf[i]);
    if (fl == NULL){
      fprintf(stderr, "bug???error\n");
      exit(1);
    }
    memset(&buf,0,sizeof(buf));
    filename = file_name_buf[i];
    /*if file doesn't exist or dir, output file_contexts as dir*/
    if (stat(filename, &buf) == -1 ||S_ISDIR(buf.st_mode) ) {
      
      outfp = file_contexts;
      if(not_generate_condition(filename))
	continue;

      filename = file_name_buf[i];
      
      if (fl->rec_flag == 1){
	snprintf(fc_str, sizeof(fc_str), "%s(|/.*)\tsystem_u:object_r:%s\n", filename, fl->labelname);
      }else{
	if (strcmp(filename, "/") == 0){
	  snprintf(fc_str, sizeof(fc_str), "%s(|[^/]*) \t system_u:object_r:%s\n", filename, fl->labelname);
	}else{
	  snprintf(fc_str, sizeof(fc_str), "%s(|/[^/]*) \t system_u:object_r:%s\n", filename, fl->labelname);
	}
      }
    }else{  
      if(not_generate_condition(filename))
	continue;
      outfp = file_tmp_fp;
      snprintf(fc_str, sizeof(fc_str), "%s\tsystem_u:object_r:%s\n", filename, fl->labelname);
    }
    /*to eleminate same line*/
    if(strcmp(fc_str, prev_fc_str) != 0){
      fprintf(outfp,"%s",fc_str);
    }
    strncpy(prev_fc_str, fc_str, sizeof(fc_str));
  }

  /*output fc for normal files*/
  rewind(file_tmp_fp);
  tmp_file_table_size = 0;
  while (fgets(fc_str, sizeof(fc_str), file_tmp_fp) != NULL){
    tmp_file_table[tmp_file_table_size] = strdup(fc_str);
    tmp_file_table_size ++;
    if(tmp_file_table_size == MAX_TMP_FILE){
      fprintf(stderr, "Error: Too big TMP_FILE. Modify MAX_TMP_FILE and recompile\n");
      exit(1);
    }
  }
  qsort(tmp_file_table, tmp_file_table_size, sizeof(char *), rev_compar);
  /*eleminate same line and output contents of TMP_FILE to file_contexts*/
  fprintf(file_contexts, "#Normal files\n");
  for(i = 0;i < tmp_file_table_size; i++){
    strncpy(fc_str, tmp_file_table[i], sizeof(fc_str));
    fprintf(file_contexts,"%s",fc_str);
    free(tmp_file_table[i]);
  }
  fclose(file_tmp_fp);

#ifdef DIRSEARCH
  fprintf(file_contexts, "#These labels are to support dir:search permission\n");
  dir_label_array = create_hash_array(dir_label_table);
  for (i = 0; i<dir_label_table->element_num; i++){
    fl =dir_label_array[i]->data;
    if(not_generate_condition(fl->filename))
      continue;
    
    r = lstat(fl->filename, &buf);
    if ( r==0 && S_ISLNK(buf.st_mode))/*Skip symbolic link*/
      continue;
   
    fprintf(file_contexts, "%s\tsystem_u:object_r:%s\n", fl->filename, fl->labelname);
    
  }
  fprintf(file_contexts, "#End of dir:search\n");
#endif
  
  return;  
}

void out_file_contexts_normal_file(FILE *out){
  out_file_contexts_general(out, not_generate_condition_normal_file);
  
}

void out_file_contexts_special_file(FILE *file_contexts){
  char **proc_mount_point_list;
  int i;

  fprintf(file_contexts, "####Begin of special files\n");

  proc_mount_point_list =  converter_conf.proc_mount_point_list;

  fprintf(file_contexts, "#These labels are to protect Terminal\n");
  fprintf(file_contexts, "/dev/[^/]*tty[^/]* \tsystem_u:object_r:tty_device_t\n");
  fprintf(file_contexts, "/dev/[^/]*pty[^/]* \tsystem_u:object_r:tty_device_t\n");
  fprintf(file_contexts, "/dev/pts\tsystem_u:object_r:devpts_t\n");
  fprintf(file_contexts, "/dev/pts(/.*)?	<<none>>\n");
  fprintf(file_contexts, "/dev/vcs[^/]*\tsystem_u:object_r:vcs_device_t\n");
  fprintf(file_contexts, "/dev/tty\tsystem_u:object_r:devtty_t\n");
  fprintf(file_contexts, "/dev/ptmx\tsystem_u:object_r:ptmx_t\n");
  fprintf(file_contexts, "#Ignore proc\n");
  for(i=0; proc_mount_point_list[i]!=NULL ;i++){
    fprintf(file_contexts, "%s(/.*)?             <<none>>\n",proc_mount_point_list[i]);
  }
  fprintf(file_contexts, "####End of special files\n");

}

void out_file_contexts_file_type_trans(FILE *file_contexts){
  char fc_str[MAX_FILENAME]="";
  char prev_fc_str[MAX_FILENAME]="";//to eleminate multiple same specification
  char *tmp_file_table[MAX_TMP_FILE];
  int tmp_file_table_size = 0;
  int i;
 /*sort tmpfile opened by tmpfile() */
  rewind(TMP_fp);

  tmp_file_table_size = 0;
  while (fgets(fc_str, sizeof(fc_str), TMP_fp) != NULL){
    tmp_file_table[tmp_file_table_size] = strdup(fc_str);
    tmp_file_table_size ++;
    if(tmp_file_table_size == MAX_TMP_FILE){
      fprintf(stderr, "Error: Too big TMP_FILE. Modify MAX_TMP_FILE and recompile\n");
      exit(1);
    }
  }
  qsort(tmp_file_table, tmp_file_table_size, sizeof(char *), compar);
       
  /*eleminate same line and output contents of TMP_FILE to file_contexts*/
  fprintf(file_contexts, "#These files are labeled by file_type_auto_trans\n");
  for(i = 0;i < tmp_file_table_size; i++){
    strncpy(fc_str, tmp_file_table[i], sizeof(fc_str));
    if(strcmp(fc_str, prev_fc_str) != 0){
      fprintf(file_contexts,"%s",fc_str);
    }
    free(tmp_file_table[i]);
    strncpy(prev_fc_str, fc_str, sizeof(fc_str));
  }

  fclose(TMP_fp);
}

int not_generate_condition_user_home_dir(char *path){  
  if(is_home_dir(path, converter_conf.homedir_list))
    return 0;
  return 1;

}

/*out file contexts for /home/<username>  */
void out_file_contexts_user_home_dir(FILE *out){
  fprintf(out,"##### Individual user home\n");
  out_file_contexts_general(out,not_generate_condition_user_home_dir);
  fprintf(out,"##### End of individual user home\n");
}


/*out file contexts for ~/ */
void out_file_contexts_home_dir(FILE *outfp){
#ifdef DIRSEARCH
  HASH_NODE **dir_label_array ;
#endif
  int i;
  int j;
  FILE_LABEL *fl;

  char fc_str[MAX_FILENAME]="";
  char prev_fc_str[MAX_FILENAME]="";//to eleminate multiple same specification
  char *filename=NULL;
  char *homedir;

  fprintf(outfp,"##### Home directories\n");
  for (i = 0; i < file_label_table->element_num; i++){
    fl = (FILE_LABEL *)search_element(file_label_table, file_name_buf[i]);

    if (fl == NULL){
      fprintf(stderr, "bug???error\n");
      exit(1);
    }
    filename = file_name_buf[i];
    if(filename[0]=='~'){
      filename = filename+1;
      if (fl->rec_flag == 1){
	if (strcmp(filename,"/")==0){
	  for(j=0; converter_conf.homedir_list[j]!=NULL ;j++){
	    homedir = converter_conf.homedir_list[j];
	    snprintf(fc_str, sizeof(fc_str), "%s/[^/]*/(|.*)\tsystem_u:object_r:%s\n", homedir, fl->labelname);
	  }	
	}else{
	  for(j=0; converter_conf.homedir_list[j]!=NULL ;j++){
	    homedir = converter_conf.homedir_list[j];
	    snprintf(fc_str, sizeof(fc_str), "%s/[^/]*%s(|/.*)\tsystem_u:object_r:%s\n", homedir,filename, fl->labelname);	
	  }
	}
      }else{
	if (strcmp(filename, "/") == 0){
	  for(j=0; converter_conf.homedir_list[j]!=NULL ;j++){
	    homedir = converter_conf.homedir_list[j];
	    snprintf(fc_str, sizeof(fc_str), "%s/[^/]*%s(|[^/]*) \t system_u:object_r:%s\n", homedir,filename, fl->labelname);
	  }
	}else{
	  for(j=0; converter_conf.homedir_list[j]!=NULL ;j++){
	    homedir = converter_conf.homedir_list[j];
	    snprintf(fc_str, sizeof(fc_str), "%s/[^/]*%s(|/[^/]*) \t system_u:object_r:%s\n", homedir,filename, fl->labelname);
	    
	  }
	}
      }
    }
    /*to eleminate same line*/
    if(strcmp(fc_str, prev_fc_str) != 0){
      fprintf(outfp,"%s",fc_str);
    }    
    strncpy(prev_fc_str, fc_str, sizeof(fc_str));
  }
  
  /*out file contexts for individual user home*/


  
#ifdef DIRSEARCH
  fprintf(outfp, "#These labels are to support dir:search permission\n");
  dir_label_array = create_hash_array(dir_label_table);
  for (i = 0; i<dir_label_table->element_num; i++){
    fl =dir_label_array[i]->data;
    if(fl->filename[0]!='~')
      continue;
    if(strcmp((fl->filename)+1,"/")==0){
      for(j=0; converter_conf.homedir_list[j]!=NULL ;j++){
	homedir = converter_conf.homedir_list[j];
	fprintf(outfp, "%s\tsystem_u:object_r:%s\n",homedir,  fl->labelname);
      }
    }else{
      for(j=0; converter_conf.homedir_list[j]!=NULL ;j++){
	homedir = converter_conf.homedir_list[j];
	fprintf(outfp, "%s/[^/]*%s\tsystem_u:object_r:%s\n",homedir, (fl->filename)+1, fl->labelname);
      }
    }
  }
  fprintf(outfp, "#End of dir:search\n");
#endif
  fprintf(outfp,"##### End of Home directories\n");

}




void out_file_contexts_config(FILE *file_contexts, FILE *homedir_template){
  file_name_buf = (char **)my_malloc(sizeof(char *)*(file_label_table->element_num));
  
  handle_all_element(file_label_table, set_buf); 
  qsort(file_name_buf, file_label_table->element_num, sizeof(char *), compar);

  out_file_contexts_normal_file(file_contexts);
  out_file_contexts_home_dir(file_contexts);
  out_file_contexts_user_home_dir(file_contexts);
  out_file_contexts_special_file(file_contexts);
  out_file_contexts_file_type_trans(file_contexts);
  
  free(file_name_buf);
}

/**
 *  @name:	registar_label_table
 *  @about;	register "name" with defined_label_table.and return -2
 * 		if "name" already exists
 *  @args:	name (char *) -> label name
 *  @return:	return 0 on success, return -2 if label already exists
 */
int
register_label_table(char *name)
{
	int *v;
	v=(int *)my_malloc(sizeof(int));
	*v=1;

	return insert_element(defined_label_table, v, name);
}

/**
 *  @name:	print_label_table
 *  @about:	print label table
 *  @args:	none
 *  @return:	none
 */
void
print_label_table()
{
	int num,i;
	HASH_NODE **n;

	n = create_hash_array(defined_label_table);
	num = defined_label_table->element_num;

	for (i = 0; i < num; i++)
	{
		printf("%s\n", (char *)(n[i]->key));
	}
}

/**
 *  @name:	resovle_label_conflict
 *  @about:	resolve label name conflict and returns new label
 * 		new label name is automatically registered.
 *  @args:	name (char *) -> label name
 *  @return:	??
 */
char *
resolve_label_conflict(char *name)
{
	char *tmp;
	char *tmp2;
	static char foot[] = "_t";

	tmp = strdup(name);

	do {
		tmp2 = (char *)my_malloc(sizeof(char)*(strlen(tmp)+sizeof(foot)));
		sprintf(tmp2, "%s%s", tmp, foot);
		free(tmp);
		tmp=tmp2;
	} while(register_label_table(tmp2) == -2);

	return tmp2;
}