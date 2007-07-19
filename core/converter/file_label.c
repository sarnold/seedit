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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include "hashtab.h"
#include "global.h"
#include "file_label.h"
#include "action.h"
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

/*allocate label buffer and set value*/
FILE_LABEL *init_file_label(char *path, int state) {
	FILE_LABEL *label;
	label = (FILE_LABEL *)my_malloc(sizeof(FILE_LABEL));
	if (label == NULL) {
		return NULL;
	}
	label->filename = strdup(path);
	label->labelname = make_label(path);

	label->label_child_dir = 0;
	if (state == FILE_DIRECT_CHILD){
		label->label_child_dir = 1;
	} 
	if (state == FILE_FILE) {
		label->dir_flag = 0;
	} else {	
		label->dir_flag = 1;
	}
	//	printf("Debug: %s %s %d\n", label->filename, label->labelname, label->label_child_dir);
	return label;
}

/*
  Add label to file_label_table.
*/
static void register_file_label_table(FILE_LABEL *label) {
	FILE_LABEL *tmp;
	char *s;

	if ((tmp = search_element(file_label_table, label->filename)) == NULL){
		/* when filename isn't file_type_auto_trans name, check label name conflict */
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
	} else {  
		/*label is already stored*/
		/*Overwrite dir_flag and label_child_dir*/
		if (label->dir_flag == 1){
			tmp->dir_flag = 1;
		}
		if (label->label_child_dir == 1){
			tmp->label_child_dir =1;
		}
		
	}
}

/**
 *  @name:	add_file_label
 *  @about;	register label with FILE_LABEL.
 * 		label is generated by path in "file_acl".
 *  @args:	file_acl (void *) -> 
 *  @return:	return 0 on success
 */
static int add_file_label(FILE_RULE file_rule) {
	FILE_LABEL *label;

	label = init_file_label(file_rule.path, file_rule.state);
	register_file_label_table(label);

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
	FILE_RULE *file_rule_array;
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
insert_force(char *path, char *labelname)
{
	FILE_LABEL *l;
	char *filename;
	int state;
	state = get_file_state(path); 
	filename = get_filename(path, state);

	if ((l = search_element(file_label_table, filename)) == NULL)
	{
		l = (FILE_LABEL *)my_malloc(sizeof(FILE_LABEL));
		l->filename = strdup(filename);
		l->labelname = strdup(labelname);
		l->label_child_dir = 1;
		l->dir_flag = 1;
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
static void set_domain_trans_label() {
	int i;
	TRANS_RULE t;
	FILE_LABEL *label;
	
	for (i = 0; i < gDomain_trans_rule_num; i++){
		t = gDomain_trans_rules[i];

		if(t.path == NULL)
			continue;
		label = init_file_label(t.path, t.state);
		register_file_label_table(label);
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
    if (strstr(l->filename, DUMMY_FILE_NAME)) {
	    fprintf(out_fp, "#label for child dirs\n");	  
    } else {
	    fprintf(out_fp, "#%s\n", l->filename);	  
    }
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
  if(gDir_search) {
	  handle_all_element(dir_label_table, print_type);
  }
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


int not_generate_condition_normal_file(char *filename) {
	/* it is outputted in different place*/
	if (strstr(filename, DUMMY_FILE_NAME))
		return 1;
	
	/*does not output for proc mount point*/
	if (check_exist_in_list(filename, converter_conf.proc_mount_point_list)){
		return 1;
	}
	/*not filename, ~/ */
	if (filename[0] != '/') {
		return 1;
	}
	/*/home/<username> is outputted in different place*/
	if (is_home_dir(filename, converter_conf.homedir_list))
		return 1;
	
	/*/home it self is outputted in different place*/
	if (check_exist_in_list(filename, converter_conf.homedir_list))
		return 1;
	
	return 0;
}


void out_file_contexts_child_dir(char *buf, int bufsize, char *filename) {
	FILE_LABEL *fl;
	char *dummy_child_filename;
	char *file_label_name;
	char *dir_label_name;
	int is_root = 0;

	buf[0]='\0';
	if (strcmp(filename, "/") == 0)
		is_root = 1;
	
	if (is_root) {
		dummy_child_filename = joint_str("/", DUMMY_FILE_NAME);
	} else {
		dummy_child_filename = joint_3_str(filename, "/", DUMMY_FILE_NAME);
	}
	
	fl = (FILE_LABEL *)search_element(file_label_table, dummy_child_filename);
	if(fl == NULL) {
		bug_and_die("");
	}
	file_label_name = fl->labelname;
	
	fl = (FILE_LABEL *)search_element(dir_label_table, dummy_child_filename);
	if(fl == NULL) {
		bug_and_die("");
	}
	dir_label_name = fl->labelname;	

	if (is_root) {		
		snprintf(buf, bufsize, 
			 "/[^/]+/.+ \t gen_context(system_u:object_r:%s,s0)\n" \
			 "/[^/]+ -d  gen_context(system_u:object_r:%s,s0)\n", 
			 file_label_name, dir_label_name);	
	} else {	
		snprintf(buf, bufsize, 
			 "%s/[^/]*/.+ \t gen_context(system_u:object_r:%s,s0)\n" \
			 "%s/[^/]* -d  gen_context(system_u:object_r:%s,s0)\n", 
			 filename, file_label_name, filename, dir_label_name);
	}
	free(dummy_child_filename);
}

/*
Output file contexts for files
that does not matche condition by not_generate_condition(filename)
*/
void out_file_contexts_general(FILE *file_contexts, int (*not_generate_condition)(char *)) {
	int i;
	FILE_LABEL *fl;
	char fc_str[MAX_FILENAME] = "";
	char fc_child_str[MAX_FILENAME*2] = "";
	char prev_fc_str[MAX_FILENAME] = "";//to eleminate multiple same specification
	char *tmp_file_table[MAX_TMP_FILE];
	int tmp_file_table_size = 0;
	HASH_NODE **dir_label_array ;
	char *filename = NULL;
	FILE *file_tmp_fp; /*output fc for normal files temporally*/
	FILE *outfp;
	
	file_tmp_fp = tmpfile();
     
	for (i = 0; i < file_label_table->element_num; i++) {
		fc_child_str[0] = '\0';
		fl = (FILE_LABEL *)search_element(file_label_table, file_name_buf[i]);
		if (fl == NULL) {
			bug_and_die("");
		}
		filename = file_name_buf[i];
		if (not_generate_condition(filename))
			continue;

		if (fl->dir_flag) {      
			outfp = file_contexts;
			if (fl->label_child_dir == 0){
				snprintf(fc_str, sizeof(fc_str), 
					 "%s(|/.*)\tgen_context(system_u:object_r:%s,s0)\n", 
					 filename, fl->labelname);
				
			} else { 
				if (strcmp(filename, "/") == 0) {				
					snprintf(fc_str, sizeof(fc_str), 
						 "%s(|[^/]*) \t gen_context(system_u:object_r:%s,s0)\n", 
						 filename, fl->labelname);										
				} else {
					snprintf(fc_str, sizeof(fc_str), 
						 "%s(|/[^/]*) \t gen_context(system_u:object_r:%s,s0)\n",
						 filename, fl->labelname);
				}
				out_file_contexts_child_dir(fc_child_str, sizeof(fc_child_str), filename);
			}
		} else { 			
			if (search_element(all_dirs_table, filename)) /*filename is directory*/
				continue;
			outfp = file_tmp_fp;
			snprintf(fc_str, sizeof(fc_str), 
				 "%s\tgen_context(system_u:object_r:%s,s0)\n", 
				 filename, fl->labelname);
		}
		

		if(strcmp(fc_str, prev_fc_str) != 0) { /*to eleminate same line*/
			fprintf(outfp,"%s",fc_str);
			fprintf(outfp,"%s",fc_child_str);
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
	
	if(gDir_search) {
		fprintf(file_contexts, "#These labels are to support dir:search permission\n");
		dir_label_array = create_hash_array(dir_label_table);
		for (i = 0; i<dir_label_table->element_num; i++){
			fl =dir_label_array[i]->data;
			if(not_generate_condition(fl->filename))
				continue;
			fprintf(file_contexts, "%s\t-d\tgen_context(system_u:object_r:%s,s0)\n", 
				fl->filename, fl->labelname);
		}
		fprintf(file_contexts, "#End of dir:search\n");
	}
	
	return;  
}

void out_file_contexts_normal_file(FILE *out){  
  fprintf(out, "#This file is generated by seedit-converter\n");
  fprintf(out, "######Begin of normal files/dirs\n");

  fprintf(out, "/(|.*)\t gen_context(system_u:object_r:default_t,s0)\n");
  out_file_contexts_general(out, not_generate_condition_normal_file);
  fprintf(out, "######End of normal files/dirs\n");  
}

void out_file_contexts_special_file(FILE *file_contexts){
  char **proc_mount_point_list;
  int i;

  fprintf(file_contexts, "####Begin of special files\n");

  proc_mount_point_list =  converter_conf.proc_mount_point_list;

  fprintf(file_contexts, "#These labels are to protect Terminal\n");
  fprintf(file_contexts, "/dev/[^/]*tty[^/]* \tgen_context(system_u:object_r:tty_device_t,s0)\n");
  fprintf(file_contexts, "/dev/[^/]*pty[^/]* \tgen_context(system_u:object_r:tty_device_t,s0)\n");
  fprintf(file_contexts, "/dev/pts\tgen_context(system_u:object_r:devpts_t)\n");
  fprintf(file_contexts, "/dev/pts(/.*)?	<<none>>\n");
  fprintf(file_contexts, "/dev/vcs[^/]*\tgen_context(system_u:object_r:vcs_device_t,s0)\n");
  fprintf(file_contexts, "/dev/tty\tgen_context(system_u:object_r:devtty_t,s0)\n");
  fprintf(file_contexts, "/dev/ptmx\tgen_context(system_u:object_r:ptmx_t,s0)\n");
  fprintf(file_contexts, "#Ignore proc\n");
  for(i=0; proc_mount_point_list[i]!=NULL ;i++){
    fprintf(file_contexts, "%s(/.*)?             <<none>>\n",proc_mount_point_list[i]);
  }
  fprintf(file_contexts, "####End of special files\n");
  fprintf(file_contexts, "####Start of dummy files for MCS, modular policy\n");
  fprintf(file_contexts, "\n");
  fprintf(file_contexts," ifdef(`enable_mcs', `\n");
  fprintf(file_contexts, "HOME_ROOT/dummy -b <<none>>\n");
  fprintf(file_contexts, "HOME_DIR/dummy -b  <<none>>\n");
  fprintf(file_contexts,"')\n");
  fprintf(file_contexts, "####End of dummy files\n");
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

int not_generate_condition_user_home_dir(char *path) {  
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


void out_file_contexts_child_dir_home(char *buf, int bufsize, char *filename, char *homedir) {
	FILE_LABEL *fl;
	char *dummy_child_filename;
	char *tmp;
	int is_root = 0;
	char *file_label_name;
	char *dir_label_name;
	buf[0]='\0';

	if (strcmp(filename, "/") == 0) {
		is_root = 1;
	}

	if (is_root) {
		dummy_child_filename = joint_str("~/", DUMMY_FILE_NAME);
	
	} else {
		dummy_child_filename = joint_3_str(filename, "/", DUMMY_FILE_NAME);
		tmp = dummy_child_filename;
		dummy_child_filename = joint_str("~", tmp);
		free(tmp);
	}

	fl = (FILE_LABEL *)search_element(file_label_table, dummy_child_filename);
	if(fl == NULL) {
		bug_and_die("");
	}
	file_label_name = fl->labelname;
	fl = (FILE_LABEL *)search_element(dir_label_table, dummy_child_filename);
	if(fl == NULL) {
		bug_and_die("");
	}
	dir_label_name = fl->labelname;
	
	if (is_root) {	
		snprintf(buf, bufsize, 
			 "%s/[^/]+/.+ \t gen_context(system_u:object_r:%s,s0)\n" \
			 "%s/[^/]+ -d  gen_context(system_u:object_r:%s,s0)\n", 
			 homedir, file_label_name, homedir, dir_label_name);	
	} else {	
		snprintf(buf, bufsize, 
			 "%s%s/[^/]*/.+ \t gen_context(system_u:object_r:%s,s0)\n" \
			 "%s%s/[^/]* -d  gen_context(system_u:object_r:%s,s0)\n", 
			 homedir, filename, file_label_name, homedir, filename, dir_label_name);
	}
	free(dummy_child_filename);
}


/*out file contexts for ~/ */
void out_file_contexts_home_dir(FILE *outfp) {
	HASH_NODE **dir_label_array ;
	int i;
	FILE_LABEL *fl;	
	char fc_str[MAX_FILENAME] = "";
	char fc_child_str[MAX_FILENAME * 2] = "";
	char prev_fc_str[MAX_FILENAME] = "";//to eleminate multiple same specification
	char *filename = NULL;
	char *homedir;
	homedir = converter_conf.homedir_list[0];
	if (converter_conf.homedir_list[1] != NULL){
		fprintf(stderr, "converter.conf:Sorry, only one home dir is supported for homedir_list.\n");
		fprintf(stderr, "               Other entries are skipped.\n");
	}
	fprintf(outfp,"##### Home directories\n");
	for (i = 0; i < file_label_table->element_num; i++) {
		fc_child_str[0] = '\0';
		fl = (FILE_LABEL *)search_element(file_label_table, file_name_buf[i]);
		if (fl == NULL){
			bug_and_die("");
		}
		filename = file_name_buf[i];

		if(filename[0]!='~')
			continue;
		if(strstr(filename, DUMMY_FILE_NAME))
			continue;
		filename = filename+1;
		if (fl->dir_flag) {      
			if (fl->label_child_dir == 0){
				if (strcmp(filename,"/")==0){
					snprintf(fc_str, sizeof(fc_str), 
						 "%s/(|.*)\tgen_context(system_u:object_r:%s,s0)\n", 
						 homedir, fl->labelname);
				} else {
					snprintf(fc_str, sizeof(fc_str), 
						 "%s/[^/]*%s(|/.*)\tgen_context(system_u:object_r:%s,s0)\n", 
						 homedir,filename, fl->labelname);	
					
				}
			} else {
				if (strcmp(filename, "/") == 0){
					snprintf(fc_str, sizeof(fc_str), 
						 "%s/[^/]*%s(|[^/]*) \t gen_context(system_u:object_r:%s,s0)\n", 
						 homedir,filename, fl->labelname);
					
				} else {
					snprintf(fc_str, sizeof(fc_str),
						 "%s/[^/]*%s(|/[^/]*) \t gen_context(system_u:object_r:%s,s0)\n", 
						 homedir,filename, fl->labelname);
				}
				out_file_contexts_child_dir_home(fc_child_str, sizeof(fc_child_str), filename ,homedir);
			}
		} else {
			snprintf(fc_str, sizeof(fc_str),
				 "%s%s \t gen_context(system_u:object_r:%s,s0)\n", 
				 homedir, filename, fl->labelname);
		}
		
		/*to eleminate same line*/
		if(strcmp(fc_str, prev_fc_str) != 0){
			fprintf(outfp,"%s",fc_str);
			fprintf(outfp,"%s",fc_child_str);
		}    
		strncpy(prev_fc_str, fc_str, sizeof(fc_str));
	}
  
	/*out file contexts for individual user home*/
	if (gDir_search) {
		fprintf(outfp, "#These labels are to support dir:search permission\n");
		dir_label_array = create_hash_array(dir_label_table);
		for (i = 0; i<dir_label_table->element_num; i++) {
			fl = dir_label_array[i]->data;
			if(fl->filename[0] != '~')
				continue;
			if (strstr(fl->filename, DUMMY_FILE_NAME))
				continue;
			if(strcmp((fl->filename)+1, "/") == 0){
				fprintf(outfp, "%s\tgen_context(system_u:object_r:%s,s0)\n",homedir,  fl->labelname);
				fprintf(outfp, "%s/[^/]+\tgen_context(system_u:object_r:%s,s0)\n",homedir,  fl->labelname);
			} else {
				  fprintf(outfp, "%s/[^/]*%s\tgen_context(system_u:object_r:%s,s0)\n",homedir, (fl->filename)+1, fl->labelname);
			}
		}
		fprintf(outfp, "#End of dir:search\n");
	}
	fprintf(outfp,"##### End of Home directories\n");
}




void out_file_contexts_config(FILE *file_contexts){
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
