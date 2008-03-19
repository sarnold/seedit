/*
#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2003 Hitachi Software Engineering Co., Ltd.
#! Copyright (C) 2005 - 2007 Yuichi Nakamura
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
/*the action of yacc*/
/*build DOMAIN structure(domain_hash_table)*/

/*Add allow <dir> exclusive -all <permissions>;
 allowfs support, many fixes after 2005 Jan
 By Yuichi Nakamura*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <ctype.h>
#include <stdarg.h>
#include "global.h"
#include <seedit/parse.h>
#include "action.h"
#include <seedit/common.h>
#include "file_label.h"
#include "hashtab.h"
#include "initial_policy.h"
#include <sys/stat.h>

/**
 *  Buffer for error message
 */
static char errmsg[1024];

/**
 *  the name of domain currently handled
 */
static char *current_domain = NULL;

/**
 *  Dummy domain used to enforce file labeing.
 */
static DOMAIN dummy_domain;

char **g_file_user_list = NULL;


HASH_TABLE * tmp_label_table = NULL;
HASH_TABLE * all_dirs_table=NULL;
HASH_TABLE  *tcp_port_label_table = NULL;
HASH_TABLE  *udp_port_label_table = NULL;
HASH_TABLE *node_label_table =NULL;

ENTRY_POINT *g_entry_point_array =NULL;
int g_entry_point_array_num = 0;

char *make_role_to_domain(char *name);
void label_parent_dir(char **dir_list, char *filename, int state);
int add_filerule_to_domain(char *domain_name, char *filename, int perm, int state);


/**
 *  @name:	init_dummy_domain
 *  @about:	initialize dummy domain
 *  @args:	none
 *  @return:	none
 */
static void
init_dummy_domain()
{
	static int init = 0;

	if (init == 0)
	{
		memset(&dummy_domain, 0, sizeof(DOMAIN));
		dummy_domain.name = strdup(DUMMY_DOMAIN_NAME);
		init=1;
	}
}



/**
 *  @name:	check_domain_name
 *  @about:	chech whether domain name is valid.
 *  @args:	name (char *) -> domain name
 *  @return: 	return 1 if domain name is valid.	
 */
int
check_domain_name(char *name)
{
	int len;
	char *tmp;
	len = strlen(name);

	tmp = strdup(name);

	/**
         *  domain format have to be formed xxxxx_t
	 */
	if (len < 2 || !(tmp[len-2] == '_' && tmp[len-1] == 't')){
	  action_error("Invalid domain name:%s\n", name);
	  exit(1);
	}
	free(tmp);

	return 1;
}

/*
checks whether sourcefile is <domainname>_t.sp
*/
int check_sourcefile_name(char *sourcefile, char *domain){
  
  char *correct_name;
  char *name;
  char *s;
  correct_name = joint_str(domain,".sp");
  s = strrchr(sourcefile, '/');
  if(s==NULL){
    name = sourcefile;
  }else{
    name = s+1;
  }
  if(strcmp(name, correct_name)==0){
    free(correct_name);
    return 0;
  }else{
    free(correct_name);
    return -1;
  }
  
  return -1;
}

/**
 *  @name:	register_domain
 *  @about:	register domain name
 *  @args:	dname (char *) -> domain name
 *  @args:      role_flags (int) -> If role_flag=1 "name" is a domain which belong to a role.
 *  @return:	none
 */ 
void
register_domain(char *dname, int role_flag)
{
	DOMAIN *d;
	char *name = dname;
	char *tmp = NULL;
	char *sourcefile;
	char *rname;

	sourcefile= get_sourcefile();

	if(sourcefile!=NULL){
	  if(!role_flag){

	    if(check_sourcefile_name(sourcefile,dname)==-1){
	      action_error("Source filename error. Source file name must be %s.sp\n",dname);
	      exit(1);
	    }
	  }else{
	    rname = make_domain_to_role(dname);
	    if(check_sourcefile_name(sourcefile,rname)==-1){
	      action_error("Source filename error. Source file name must be %s.sp\n",dname);
	      exit(1);
	    }
	    free(rname);
	  }
	}

	check_domain_name(name);
	if(search_domain_hash(name)){
	  action_error("Domain name conflicts!! Multiple definition of domain %s\n", name);
	  exit(1);
	}

	if (register_label_table(name) == -2)
	{
		tmp = resolve_label_conflict(name);
		fprintf(stderr,
			"Warning! Domain %s conflicts label reserved by system. Domain name %s is used instead.\n",
			name, tmp);
		name = tmp;
	}

	if (insert_domain_hash_by_name(name) == -2)
	{
		action_error("Domain name conflicts!! Multiple definition of domain %s\n", name);
		exit(1);
	}

	if (current_domain != NULL)
	{
		free(current_domain);
	}
	current_domain = strdup(name);

	if (current_domain == NULL)
	{
		action_error(errmsg, sizeof(errmsg), "Too long domain name:%s", name);
		exit(1);
	}

	if (role_flag == 1)
	{
		d = search_domain_hash(name);
		d->roleflag = 1;
		insert_element(domain_hash_table, d, name);
	}

	if (tmp != NULL)
	{
		free(tmp);
	}

	return;
}


/*register deny file rule*/
int register_file_deny(char *path){
  set_tmp_perm(DENY_PRM);
  if(is_home_dir(path, converter_conf.homedir_list)){	
    snprintf(errmsg, sizeof(errmsg), "deny %s; deny for user home directory does not work, neglected.\n", path);
    yywarn(errmsg);
    return 0;
  }
  register_file_rule(path);
  return 0;
}

void label_parent_dir(char **dir_list, char *filename, int state){
	int i;
	int s;

	if (all_dirs_table == NULL){
		all_dirs_table = create_hash_table(FILE_RULE_TABLE_SIZE);
		if (all_dirs_table == NULL){
			yyerror("memory shortage\n");
			exit(1);
		}
	}
	for(i=0;dir_list[i]!=NULL;i++){		
		if(strcmp(filename, dir_list[i])==0){
			if (state == FILE_FILE) {
				continue;
			}
		}
		s = insert_element(all_dirs_table, "1", dir_list[i]);
		if(s==-2) {
			;
		} else if (s<0) {
			bug_and_die("");
		}
		add_filerule_to_domain(DUMMY_DOMAIN_NAME, dir_list[i], READ_PRM, FILE_ALL_CHILD);

	}
	return;
}


/**
 *  @name:	label_child_dir	
 *  @about:	To label child directory of "path",
 *              this function registers ACL in dummy domain.
 *  @args:	path (char *) -> full path name 
 *  @return:	none
 */
void label_child_dir(char *path) {
	char *fullname;
	strip_slash(path);
	int s;
	
	if(strcmp(path, "/") == 0 ){
		fullname = joint_str(path, DUMMY_FILE_NAME);	
	} else {
		fullname = joint_3_str(path, "/", DUMMY_FILE_NAME);	
	}
	if(gDir_search) {
		s = insert_element(all_dirs_table, "1", fullname);
		if(s==-2) {
			;
		} else if (s<0) {
			bug_and_die("");
		}
	}
	add_filerule_to_domain(DUMMY_DOMAIN_NAME, fullname, READ_PRM, FILE_ALL_CHILD);	

	return;
}

int register_tmp_all(char *path){
  DOMAIN *domain;
  TMP_ALL_RULE *tmp;
  TMP_ALL_RULE work;

  domain = search_domain_hash(current_domain);
  work.domain = domain;
  work.path = strdup(path);
  work.allowed = get_tmp_perm();

  tmp = (TMP_ALL_RULE *)extend_array(domain->tmp_all_array, &(domain->tmp_all_array_num),sizeof(TMP_ALL_RULE));
  tmp[domain->tmp_all_array_num-1] = work;
  domain->tmp_all_array = tmp;  
  
  return 0;
}


int get_file_state(char *path) {
	int len;
	int state;
	len = strlen(path);
  
	if(path[len-3]=='/' && path[len-2]=='*' && path[len-1]=='*'){
		state = FILE_ALL_CHILD;
	}else if(path[len-2]=='/' && path[len-1]=='*'){
		state = FILE_DIRECT_CHILD;
	} else {
		if (path[len -1]=='/') {
			state = FILE_DIR;
		} else {
			state = FILE_FILE ;
		}
	}
	return state;
}

/*strip **,*,/ */
char *get_filename(char *path, int state){
  char *buf;
  int len;
  buf = strdup(path);
  len = strlen(buf);
 
  if(state == FILE_ALL_CHILD){
    if(strcmp(path,"/**")==0||strcmp(path,"~/**")==0){
      buf[len-2]='\0';
    }else{
      buf[len-3]='\0';
    }
  }else if(state == FILE_DIRECT_CHILD){

    if(strcmp(path,"/*")==0||strcmp(path,"~/*")==0){
      buf[len-1]='\0';
    }else{
      buf[len-2]='\0';
    }
  }else{
    if(strcmp(path,"/")==0||strcmp(path,"~/")==0){
      ;
    }else{
      if(buf[len-1]=='/'){
	buf[len-1]='\0';
      }
    }
  }
  return buf;
}

int overwrite_file_rule(FILE_RULE *array, int array_num, FILE_RULE rule) {
	int i;
	FILE_RULE value;
	int overwritten = 0;
	int s;
	for(i = 0; i<array_num;i++) {
		value = array[i];

		/*deny cancels allow rule for child dir*/
		if(rule.allowed == DENY_PRM) {
			if(rule.state == FILE_ALL_CHILD) {
				if(chk_child_dir(rule.path,value.path) == 1) {
					array[i] = rule;
					overwritten = 1;
				}
			}
			if(rule.state == FILE_DIRECT_CHILD) {
				if(value.state == FILE_FILE) {
					s = 1;
				} else {
					s = 0;
				}
				if(chk_child_file(rule.path,value.path, s) == 1) {
					array[i] = rule;
					overwritten = 1;
				}
			}
			if(rule.state == FILE_FILE) {
				if(strcmp(value.path,rule.path) == 0) {
					array[i] = rule;
					overwritten = 1;
				}	 
			}
			continue;
		}
		    
		if(strcmp(value.path,rule.path) == 0){
			if(value.state == rule.state) {
				/*Only deny /foo-> allow /foo, it is overwritten*/
				if(value.allowed == DENY_PRM && rule.allowed!=DENY_PRM){
					array[i] = rule; /*over written*/
					overwritten = 1;
				} else {
					array[i].allowed = value.allowed | rule.allowed; /*OR operation*/
					overwritten = 1;
				}
			}
		}
	}
	return overwritten;
}

int add_filerule_to_domain(char *domain_name, char *filename, int perm, int state){
  DOMAIN *domain;
  HASH_TABLE *table;
  FILE_RULE work;
  FILE_RULE *tmp;
  int overwritten=0;
  struct stat buf;
  int r;

  if (gMoreWarning) {
	  memset(&buf,0,sizeof(buf));
	  r = stat(filename, &buf);
	  if (r == 0) {
		  if (state != FILE_FILE) {
			  if (!S_ISDIR(buf.st_mode)) {
				  snprintf(errmsg, sizeof(errmsg), 
					   "File name %s is not directory, but it is configured as directory", filename);
				  yywarn(errmsg);
			  }
		  } else {
			  if(S_ISDIR(buf.st_mode)) {
				   snprintf(errmsg, sizeof(errmsg), 
					   "File name %s is directory, but it is configured as normal file", filename);
				  yywarn(errmsg);
			  }
		  }
	  }
  }
  

  strip_slash(filename); 

  /* register new acl with domain's file_acl */
  domain = search_domain_hash(domain_name);
  if (domain == NULL){
    action_error("Must be bug. Domain %s isn't defined\n", domain_name);
    exit(1);
  }
  
  work.domain = domain;
  work.path = strdup(filename);
 
  work.allowed = perm;
  work.state = state;


  if(domain->file_rule_array !=NULL){
    overwritten = overwrite_file_rule(domain->file_rule_array, domain->file_rule_array_num, work);
   
    if(!overwritten){/*append*/
      tmp = (FILE_RULE *)extend_array(domain->file_rule_array, &(domain->file_rule_array_num),sizeof(FILE_RULE));
      tmp[domain->file_rule_array_num -1 ] = work;
      domain ->file_rule_array = tmp;
    }
  }else{/*initialize*/
    tmp = (FILE_RULE *)extend_array(domain->file_rule_array, &(domain->file_rule_array_num),sizeof(FILE_RULE));
    tmp[domain->file_rule_array_num -1 ] = work;
    domain ->file_rule_array = tmp;      

  }

  /* create hash table for acl */
  table = domain->appeared_file_name;
  if (table == NULL){
    table = create_hash_table(FILE_RULE_TABLE_SIZE);
    if (table == NULL){
      yyerror("memory shortage\n");
      exit(1);
    }
    domain->appeared_file_name = table;
  }

  insert_element(table, "1", strdup(filename));

  return 0;
}

void register_dummy_home_rule(){
  char *p_current_domain;
  p_current_domain = current_domain;
  current_domain = DUMMY_DOMAIN_NAME;
  register_file_rule("~/**");

  current_domain = p_current_domain;
}



/*
  extract user name from homedirectory 
  and add to g_user_file_list.
  Example;
  path : /home/ynakam/himainu
  -> ynakam is added
*/
void add_file_user_list(char *path){
  char **homedir;
  char *user;
  homedir = converter_conf.homedir_list;
  
  user = get_user_from_path(path, homedir);
  if(user !=NULL){
    if(!check_exist_in_list(user, g_file_user_list))
      g_file_user_list = extend_ntarray(g_file_user_list,user);
    free(user);
  }

}

/*replace '//' with '/' */
char *remove_slash(char *path) {
	char *buf;
	char *result;
	int len;
	int i;
	int j;
	result = strdup(path);	
	len = strlen(path);
	buf = (char *)my_malloc(sizeof(char) * (len + 1));
	memset(buf, 0, sizeof(char) * (len + 1));

	j = 0;
	for (i=0; i < len; i++) {
		if(path[i] == '/') {
			if (i > 0 && path[i-1] == '/'){
				/*do nothing*/
			} else {
				buf[j] = path[i];
				j++;
			}			
		} else {
			buf[j] = path[i];
			j++;
		}
	}
	memcpy(result,buf,len+1);
	free(buf);
	return result;
}

int register_file_rule(char *path){
  char **dir_list;
  char *filename;  
  int state;
  path = remove_slash(path);
  state = get_file_state(path); 
  filename = get_filename(path, state);  
  add_file_user_list(filename);

  if (get_tmp_perm() == DENY_PRM) {
	  if (state == FILE_DIR) {
		  action_error("Directory can not be specified for deny rule\n");
		  exit(1);
	  }
  }

  if(gDir_search) {
	  dir_list = get_dir_list(filename,  converter_conf.homedir_list, 1);
	  if(dir_list!=NULL){
		  /*label all parent directory*/
		  label_parent_dir(dir_list, filename, state);
		  free_ntarray(dir_list);
	  }  
  }

  add_filerule_to_domain(current_domain, filename, get_tmp_perm(), state);
  
  if (state == FILE_DIRECT_CHILD){
    /* when allow <dir>* is described, add dummy permission to dummy domain. */
    label_child_dir(filename);
  }

  free(path);
  return 0;

}





/*if tmp_name is already used for other type.
create replace tmp_name.
result is malloced and returned.
*/
char *check_tmp_name(char *tmp_name){
  char *tmpname;
  char *result = NULL;
  result = strdup(tmp_name);
  
  if (register_label_table(tmp_name) == -2){
    if (search_element(tmp_label_table, tmp_name) == NULL){
      tmpname = resolve_label_conflict(tmp_name);
      fprintf(stderr,
	      "Warning! Exclusive label %s conflicts label reserved by system. Domain name %s is used instead.\n",
	      tmp_name, tmpname);
      free(result);
      result = strdup(tmpname);
    }
  }  
  return result;
}

/*
label should be <domain_prefix>_<filesystem>_t

*/
int check_fs_tmp_name(char *domain, char *fs,  char *label){
  char *d_prefix;
  char *must_name;
  int len;

  d_prefix = get_prefix(domain);
  len = strlen(d_prefix) + strlen(fs) + strlen("__t");
  must_name = (char *)my_malloc((len + 1)*(sizeof(char)));
  snprintf(must_name, len+1, "%s_%s_t", d_prefix, fs); 
  
  if(strcmp(must_name, label) !=0){
    action_error("In allowfs exclusive, label name must be <domain or role prefix>_<filesystem>_t\n");
    exit(1);
  }

  free(d_prefix);
  free(must_name);
  return 0;
}

int register_tmp_fs_acl(char *fs, char *e_name, int permission_flag){
  DOMAIN *domain;
  FS_TMP_RULE work;
  FS_TMP_RULE *tmp;
  char *s1;
  char *s2;
  char *s3;
  char *new_name;

  char *tmp_name;
  if(check_exist_in_list(fs, converter_conf.file_type_trans_fs_list)==0){
    action_error("allowfs exclusive is not supported for %s file system.\n",fs);
    exit(1);
  }
  
  /*e_name is automatically generated from domain and fs*/
  if(strcmp(e_name, "auto")==0){
    s1 = get_prefix(current_domain);
    s2 = joint_str(s1,"_");
    s3 = joint_str(fs, "_t");
    new_name = joint_str(s2, s3);
    free(s1);
    free(s2);
    free(s3);
    e_name = new_name;
  }

  /* check label name conflict */
  tmp_name = check_tmp_name(e_name);  
  
  /*allowtmp all rule*/
  if (strcmp(e_name, "*")==0 || strcmp(e_name, "all")==0){
    register_tmp_all(fs);
    return 0;
  }
 
  /* set tmp_name in tmp_label_table */
  if (tmp_label_table == NULL){
    tmp_label_table = create_hash_table(LABEL_LIST_SIZE / 2);
  }  
  insert_element(tmp_label_table, strdup(fs), tmp_name);  

  /*
   * register P_DENY with dummy domain's File ACL
   * by this, tmp_name is registered to file_label_table
   */
  add_filerule_to_domain(DUMMY_DOMAIN_NAME, tmp_name, DENY_PRM,  FILE_FILE);
  
  domain = search_domain_hash(current_domain);
  work.domain = domain;
  work.fs = strdup(fs);  
  work.name = tmp_name;

 
  check_fs_tmp_name(domain->name, fs,  tmp_name);

  tmp = (FS_TMP_RULE *)extend_array(domain->fs_tmp_rule_array,
				      &(domain->fs_tmp_rule_array_num),
				      sizeof(FS_TMP_RULE));
  tmp[domain->fs_tmp_rule_array_num-1] = work;
  domain->fs_tmp_rule_array = tmp;

  if(permission_flag){
    register_file_rule(e_name);
  }

  return 0;
}

void register_type(char *label) {
    char path[] = "DUMMY_FILE_NAME";
    if (tmp_label_table == NULL)
        tmp_label_table = create_hash_table(LABEL_LIST_SIZE / 2);
    insert_element(tmp_label_table, strdup(path), label);
    return;
}
/*
register allowtmp
if permission_flag is true, 
register permission for e_name.
 */
int register_tmp_file_acl(char *path, char *e_name, int permission_flag){
  DOMAIN *domain;
  FILE_TMP_RULE work;
  FILE_TMP_RULE *tmp;
  char *tmp_name;
  char *s;
  char *s1;
  char *s2;
  char *new_name;


  /*allowtmp all rule*/
  if (strcmp(e_name, "*")==0 || strcmp(e_name, "all")==0){
    register_tmp_all(path);
    return 0;
  }

  /*e_name is automatically generated from domain and path*/
  if(strcmp(e_name, "auto")==0){
    s = make_label(path);
    s1 = get_prefix(current_domain);
    s2 = joint_str(s1,"_");
    new_name = joint_str(s2, s);
    free(s);
    free(s1);
    free(s2);
    e_name = new_name;
  }

  if(check_type_suffix(e_name) == 0){
    action_error("label must end with _t for allowtmp\n");
    exit(1);
  }

  strip_slash(path);

  tmp_name = check_tmp_name(e_name);

  /* set tmp_name in tmp_label_table */
  if (tmp_label_table == NULL)    {
    tmp_label_table = create_hash_table(LABEL_LIST_SIZE / 2);
  }  
  insert_element(tmp_label_table, strdup(path), tmp_name);

  /*
   * register P_DENY with dummy domain's File ACL
   * by this, tmp_name is registered to label_table
   */
  add_filerule_to_domain(DUMMY_DOMAIN_NAME, tmp_name, DENY_PRM, FILE_FILE);

  /*
   * This solves bug which happens when "allow exclusive" is described
   * to unlabeled directory. To enforce labeling ,this registers dummy acl
   */
  add_filerule_to_domain(dummy_domain.name, path, READ_PRM, FILE_ALL_CHILD);

  /* add to tmp_rule_array */
  domain = search_domain_hash(current_domain);
  work.domain = domain;
  work.path = strdup(path);
  work.name = tmp_name;
  
  tmp = (FILE_TMP_RULE *)extend_array(domain->tmp_rule_array,
				      &(domain->tmp_rule_array_num),
				      sizeof(FILE_TMP_RULE));
  tmp[domain->tmp_rule_array_num-1] = work;
  domain->tmp_rule_array = tmp;

  if(permission_flag){
    register_file_rule(e_name);
  }
  return 0;
}

/**
 *  Information of domain is registerd.
 *  This is very important.
 */
#define DOMAIN_HASH_TABLE_SIZE 1024
HASH_TABLE *domain_hash_table = NULL; 

/**
 *  @name:	insert_domain_hash_by_name
 *  @about:	register new domain named "name" with hash table
 *  @args:	name (char *) -> domain name
 *  @return:	none
 */
int
insert_domain_hash_by_name(char *name)
{

	DOMAIN *newdomain;

	if (domain_hash_table == NULL)
	{
		domain_hash_table = create_hash_table(DOMAIN_HASH_TABLE_SIZE);
		if (domain_hash_table == NULL)
		{
			perror("malloc");
			exit(1);
			return -1;
		}
		/* dummy domain is created */
		init_dummy_domain();
		insert_element(domain_hash_table, &dummy_domain, dummy_domain.name);

	}

	if ((newdomain = (DOMAIN *)malloc(sizeof(DOMAIN))) == NULL)
	{
		perror("malloc");
		exit(1);
	}

	memset(newdomain, 0, sizeof(DOMAIN));

	newdomain->name = strdup(name);
	newdomain->roleflag = 0;
	newdomain->user = NULL;
	newdomain->program_flag = 0;
	newdomain->appeared_file_name = NULL;
	newdomain->file_rule_array = NULL;
	newdomain->file_rule_array_num = 0;
	newdomain->tmp_rule_array = NULL;
	newdomain->com_acl_array = NULL;
	newdomain->tty_create_flag = 0;
	newdomain->tty_acl_array = NULL;
	newdomain->tty_acl_array_num = 0;
	newdomain->pts_create_flag = 0;
	//  newdomain->pts_change_name = NULL;
	newdomain->pts_acl_array = NULL;
	newdomain->pts_acl_array_num = 0;
	newdomain->net_socket_rule_array=NULL;
	newdomain->net_socket_rule_array_num=0;
	newdomain->net_netif_rule_array =NULL;
	newdomain->net_netif_rule_array_num = 0;
	newdomain->key_rule_array = NULL;
	newdomain->key_rule_array_num = 0;

	return insert_element(domain_hash_table, newdomain, newdomain->name);
}

/**
 *  @name:	search_domain_hash
 *  @about:	return pointer to domain named "key".
 *  @args:	key (char *) -> hash key
 *  @return:	domain data on success, return NULL in failure
 */
DOMAIN *
search_domain_hash(char *key)
{
	if (domain_hash_table == NULL)
	{
	  return NULL;
	}
	return (DOMAIN *)search_element(domain_hash_table, key);
}



/**
 *  @name:	free_file_exc
 *  @about:	free tmp_array in DOMAIN structure
 *  @args:	tmp_array (FILE_TMP_RULE *) -> file sec rule
 *  @args:	array_num (int) -> a number of elements of array 
 */
static void
free_file_exc(FILE_TMP_RULE *tmp_array, int array_num)
{
	int i;
	FILE_TMP_RULE tmp;

	for (i = 0; i < array_num; i++)
	{
		tmp = tmp_array[i];
		free(tmp.path);
		free(tmp.name);
	}
	free(tmp_array);
}

static void free_pts_acl(DOMAIN *d);
static void free_tty_acl(DOMAIN *d);
static void free_com_acl(COM_ACL_RULE *com_array, int array_num);

/**
 *  @name:	free_domain
 *  @about:	free DOMAIN structure
 *  @args:	domain (void *) -> domain data
 *  @return:	return 0
 */
int
free_domain(void *domain)
{
	DOMAIN *d;
	d = domain;

	free_file_exc(d->tmp_rule_array, d->tmp_rule_array_num);
	free_com_acl(d->com_acl_array, d->com_acl_array_num);


	free_tty_acl(domain);
	free_pts_acl(domain);

	return 0;
}



/**
 *  @name:	free_domain_tab
 *  @about:	free "domain_hash_table"
 *  @args:	none
 *  @return:	none
 */
void
free_domain_tab()
{
	handle_all_element(domain_hash_table, free_domain);
	delete_hash_table(domain_hash_table);
}

/**
 *  Functions related to domain transition
 */
TRANS_RULE *gDomain_trans_rules=NULL;
int gDomain_trans_rule_num=0;

/**
 *  @name:	print_domain_trans
 *  @about:	print domai trans rule
 *  @args:	none
 *  @return:	none
 */
void
print_domain_trans()
{
	int i;
	TRANS_RULE t;

	for (i = 0; i < gDomain_trans_rule_num; i++)
	{
		t = gDomain_trans_rules[i];
		printf("trans:%s %s %s\n", t.parent,t.path, t.child);
	}
}



void register_one_domain_trans(char *from_domain, char *path){
  TRANS_RULE *tmp;
  TRANS_RULE work;
  DOMAIN *d;
  char *filename = NULL;
  int state=0;
  ENTRY_POINT entry;
  ENTRY_POINT *entry_tmp;
  char **dir_list;

  if (path != NULL){
    state = get_file_state(path);
    filename = get_filename(path, state);  
    add_file_user_list(filename);
  }
  if (state == FILE_DIR) {
	  action_error("entry point can not be directory in domain_trans\n");
	  exit(1);
  }

  if(gDir_search){
	  dir_list = get_dir_list(filename, converter_conf.homedir_list, 1);
	  if(dir_list!=NULL){
		  /*label all parent directory*/
		  label_parent_dir(dir_list, filename, state);
		  free_ntarray(dir_list);
	  } 
  }

  d = search_domain_hash(current_domain);

  work.parent = strdup(from_domain);
  if(path != NULL){
    work.path = strdup(filename);
  }else{
    work.path = NULL;
  }
  work.child = strdup(current_domain);
  work.state = state;
  
  if (d->roleflag == 1){
    /*domain_trans or domain_auto_trans*/
    work.auto_flag = 0;
  }
  else{
    work.auto_flag = 1;
  }
  
  tmp = (TRANS_RULE *)extend_array(gDomain_trans_rules, &(gDomain_trans_rule_num), sizeof(TRANS_RULE));
  
  tmp[gDomain_trans_rule_num-1] = work;
  
  gDomain_trans_rules = tmp;  

  if (state == FILE_DIRECT_CHILD){
    /* when allow <dir>* is described, add dummy permission to dummy domain. */
    label_child_dir(filename);
  }

  if(filename!=NULL){
    entry.filename = strdup(filename);
    entry.state = state;
    entry.to_domain=strdup(current_domain);
    entry_tmp = (ENTRY_POINT *)extend_array(g_entry_point_array, &(g_entry_point_array_num),sizeof(ENTRY_POINT));
    entry_tmp[g_entry_point_array_num -1]=entry;
    g_entry_point_array = entry_tmp;
  }

  return;
}

char *resolve_domain_conflict(char *path){
  char *new_domain;
  int i;
  char *tmp;
  char *s;
  int len;

  tmp = strdup(path);
  len = strlen(tmp);
  for(i=0;i<len;i++){
    if(!isalnum(tmp[i]))
      tmp[i]='_';
  }
  s = joint_str("domain", tmp);
  new_domain = joint_str(s,"_t");
  free(s);
  free(tmp);
  return new_domain;
}

void register_program(char **paths_list, int create_domain_name_flag){
  char **list=NULL;
  char *domain="unconfined_domain";
  char *new_domain=NULL;
  char *tmp=NULL;
  char *s0;
  char *s;
  int len;
  int i;
  DOMAIN *current;
  
  if(create_domain_name_flag==1){
    tmp = strdup(paths_list[0]);
    len = strlen(tmp);
    if(tmp[len-1]=='/')
      tmp[len-1]='\0';
    s0 = strrchr(tmp,'/');
    s0 =s0+1;
    s = joint_str(s0,"_t");
        
    new_domain = strdup(s);
    free(tmp);
    len = strlen(new_domain);
    for(i=0;i<len;i++){
      if(!isalnum(new_domain[i])){
	new_domain[i]='_';
      }
    }
    if(search_domain_hash(new_domain)){
      new_domain = resolve_domain_conflict(paths_list[0]);
      action_warn("Domain name conflicted, domain name %s is generated\n", new_domain);
    }
    register_domain(new_domain,0);
    free(new_domain);
  }

  current =  search_domain_hash(current_domain);
  current -> program_flag = 1;

  list=add_strlist(list, domain,1); 
  register_domain_trans(list ,paths_list);
 
}

/**
 *  @name:	register_domain_trans
 *  @about:	When yacc finds "domain_trans",register information about domain transition
 */

void register_domain_trans(char **domain_list, char **path_list){
  int d_list_num;
  int p_list_num;
  int i;
  int j;
  d_list_num = get_ntarray_num(domain_list);
  p_list_num = get_ntarray_num(path_list);


  if(path_list == NULL){
    for(i =0 ;i<d_list_num;i++)
      register_one_domain_trans(domain_list[i],NULL);
  }else{
    for(i=0;i<d_list_num;i++){
      for(j=0;j<p_list_num;j++){
	register_one_domain_trans(domain_list[i],path_list[j]);
      }
    }
  }
}


void register_dev_acl(char **path_list){
  int p_list_num;
  int i;
  char **tmp;  
  DOMAIN *domain;

  p_list_num = get_ntarray_num(path_list);

  for(i=0 ; i<p_list_num; i++){
    domain = search_domain_hash(current_domain);
    tmp = (char **)extend_array(domain->dev_root_array,&(domain->dev_root_array_num),sizeof(char *)) ;
    tmp[domain->dev_root_array_num -1] = strdup(path_list[i]);
    domain->dev_root_array = tmp;
  }

}


void register_terminal_acl(char *option, char *name, int flag){
  
  //  fprintf(stderr,"####opt%s name %s",option,name);
  /*Internally uses old allowtty/pts data structure*/
  if(strcmp(option,"-tty")==0){
    register_tty_acl(name,flag);
  }else if(strcmp(option,"-pts")==0){
    register_pts_acl(name,flag);
  }else if(strcmp(option,"-allterm")==0){
    register_tty_acl(name,flag);
    register_pts_acl(name,flag);    
  }else{
    action_error("option %s isn't defined\n", option);
    exit(1);
  }

}

/**
 *  @name:	free_domain_trans
 *  @about:	free TRANS_RULE
 *  @args:	none
 *  @return:	none
 */
void
free_domain_trans()
{
	int i;
	TRANS_RULE t;

	for (i = 0; i < gDomain_trans_rule_num; i++)
	{
		t = gDomain_trans_rules[i];
		free(t.parent);
		free(t.path);
		free(t.child);
	}
	free(gDomain_trans_rules);
	gDomain_trans_rule_num = 0;
}

/**
 *  register network ACL
 */

int register_port_label_table(int protocol, char *port){
  char *type;
  char *key;
  char *protstr;
  char suffix[]="_port_t";
  int len;
  HASH_TABLE *table;
  if(protocol == NET_TCP){
    table = tcp_port_label_table;
    protstr = "tcp";
  }else if(protocol == NET_UDP){
    table = udp_port_label_table;
    protstr ="udp";
  }else{
    return -1;
  }
  key = port;
  len = strlen(protstr)+strlen(port)+strlen(suffix);
  type = (char *)my_malloc((len+2)*sizeof(char));
  snprintf(type, len+1, "%s%s%s",protstr,port,suffix);

  if(search_element(table,key)==NULL){
    insert_element(table , type, key);
    register_label_table(type);
  }   

  return 0;
}

int register_net_node_acl(int rule_type, int protocol, char **node_list, int permission){
  NET_NODE_RULE rule;
  NET_NODE_RULE *tmp;
  DOMAIN *domain;
  char **node = NULL;
  char *type;
  char *s;
  int len;
  int table_size;
  char nodenum[16];
  char node_prefix[]="node_";
  int i;
  if(node_label_table == NULL){
    node_label_table = create_hash_table(DEFAULT_HASH_TABLE_SIZE);
  }
  domain = search_domain_hash(current_domain);
  rule.type = rule_type;
  rule.domain = domain;
  rule.protocol = protocol;
  rule.permission = permission;
  
  len = get_ntarray_num(node_list);
  for(i=0;i<len;i++){
    node = extend_ntarray(node, node_list[i]);
    if(strcmp(node_list[i],"*") == 0)
       continue;

    if(search_element(node_label_table, node_list[i])==NULL){
      table_size = node_label_table->element_num;
      snprintf(nodenum,sizeof(nodenum),"%d",table_size);
      s = joint_str(node_prefix,  nodenum);
      type = joint_str(s, "_t");
      free(s);
      insert_element(node_label_table, type, node_list[i]);
      register_label_table(type);      
    }
  }
  rule.ipv4addr = node;
  
  tmp = (NET_NODE_RULE *)extend_array(domain->net_node_rule_array, &(domain->net_node_rule_array_num), sizeof(NET_NODE_RULE));
  tmp[domain->net_node_rule_array_num -1]=rule;
  domain->net_node_rule_array = tmp;
  
  return 0;
}

int register_net_netif_acl(int rule_type, int protocol, char **netif_list, int permission){
  
  NET_NETIF_RULE rule;
  NET_NETIF_RULE *tmp;
  DOMAIN *domain;
  char **netif = NULL;
  int len;
  int i;

  domain = search_domain_hash(current_domain);
  rule.type = rule_type;
  rule.domain = domain;
  rule.protocol = protocol;
  rule.permission = permission;
  
  len = get_ntarray_num(netif_list);
  for(i=0;i<len;i++){

    if(strcmp(netif_list[i],"*")==0||check_exist_in_list(netif_list[i], converter_conf.netif_name_list)==1){      
      netif = extend_ntarray(netif, netif_list[i]);

    }else{    
      action_warn("Warning: NIC %s does not exist, skipped\n",netif_list[i]);
    }
  }
  rule.netif = netif;
  
  tmp = (NET_NETIF_RULE *)extend_array(domain->net_netif_rule_array, &(domain->net_netif_rule_array_num), sizeof(NET_NETIF_RULE));
  tmp[domain->net_netif_rule_array_num -1]=rule;
  domain->net_netif_rule_array = tmp;
  
  return 0;
}


int register_net_sock_acl(int rule_type,int protocol, int behavior, char **port_list, char **domain_list){
  int i;
  int len;
  char **port=NULL;
  char **target=NULL;
  DOMAIN *domain;
  NET_SOCKET_RULE rule;
  NET_SOCKET_RULE *tmp;

  if(tcp_port_label_table == NULL){
    tcp_port_label_table = create_hash_table(DEFAULT_HASH_TABLE_SIZE);
  }
  if(udp_port_label_table == NULL){
    udp_port_label_table = create_hash_table(DEFAULT_HASH_TABLE_SIZE);
  }

  domain = search_domain_hash(current_domain);
  rule.type = rule_type;
  rule.domain = domain;
  rule.protocol = protocol;
  rule.behavior = behavior;
  
  len = get_ntarray_num(port_list);
  for(i=0;i<len;i++){
    port = extend_ntarray(port, port_list[i]);
    if (strcmp(port_list[i],PORT_ALL)==0){
      ;
    }else if (strcmp(port_list[i],PORT_WELLKNOWN)==0){
      ;
    }else if (strcmp(port_list[i],PORT_UNPRIV)==0){
      ;
    }else{
      if(rule_type == ALLOW_RULE){
	if(protocol & NET_TCP){
	  register_port_label_table(NET_TCP, port_list[i]);
	}
	if(protocol & NET_UDP){
	  register_port_label_table(NET_UDP, port_list[i]);
	}
      }
    }
  }
  rule.port = port;

  len = get_ntarray_num(domain_list);  
  for(i=0;i<len;i++){
    target = extend_ntarray(target, domain_list[i]);
  }
  rule.target= target;

  tmp = (NET_SOCKET_RULE *)extend_array(domain->net_socket_rule_array, &(domain->net_socket_rule_array_num), sizeof(NET_SOCKET_RULE));
  tmp[domain->net_socket_rule_array_num -1]=rule;
  domain->net_socket_rule_array = tmp;
  
  return 0;
}


/**
 *  register IPC ACL
 */

/**
 *  @name:	register_com_acl
 *  @about:	register communication acl
 *  @args:	flag (int) ->
 *  @args:	to_domain (char *) ->
 *  @return:	return 0 on success
 */
int
register_com_acl(int flag, char *to_domain)
{
	DOMAIN *domain;
	COM_ACL_RULE *tmp;
	COM_ACL_RULE work;

	domain = search_domain_hash(current_domain);
	work.domain = domain;
	work.flag = flag;
	work.domain_name = strdup(to_domain);
	work.perm = get_tmp_perm();


	tmp = (COM_ACL_RULE *)extend_array(domain->com_acl_array, &(domain->com_acl_array_num),
					   sizeof(COM_ACL_RULE));
	tmp[domain->com_acl_array_num-1] = work;
	domain->com_acl_array = tmp;

	return 0;
}

/**
 *  @name:	free_com_acl
 *  @about:	free communication acl
 *  @args:	com_array (COM_ACL_RULE *) -> array of rule
 *  @args:	array_num (int) -> number of elements
 *  @return:	none
 */
static void
free_com_acl(COM_ACL_RULE *com_array, int array_num)
{
	int i;

	COM_ACL_RULE tmp;
	for (i = 0; i < array_num; i++)
	{
		tmp = com_array[i];
		free(tmp.domain_name);
	}
	free(com_array);
}

/**
 *  @name:	register_adm_acl
 *  @about:	register Administration ACL
 *  @args:	flag (int) ->
 *  @return:	return 0 on success
 */
int register_adm_acl(int flag){
  action_warn("allowadm is no longer supported. Use allowkernel,allowpriv,allowseop instead.Skipped. \n");  
  return 0;
}

/**
 *  tty ACL
 */

/**
 *  @name:	register_tty_acl
 *  @about:	role=NULL only tty_create_flag is set.
 * 		flag=0:-create,flag=1:-change,flag=2:r,w
 *  @arsg:	role (char *) -> role name
 *  @args:	flag (int) ->
 :  @return:	return 0 on success 
 */
int
register_tty_acl(char *role, int flag)
{
	DOMAIN *d;
	TTY_RULE *tmp_tty_rule;
	TTY_RULE work;
	memset(&work, 0, sizeof(TTY_RULE));

	d = search_domain_hash(current_domain);

	if (flag == 0)
	{
		d->tty_create_flag = 1;
		return 0;
	}

	if (flag == 1)
	{
		work.domain = d;
		work.rolename = strdup(role);
		work.perm = CHANGE_PRM;
	}

	if (flag == 2)
	{
		work.domain = d;
		work.rolename = strdup(role);
		work.perm = get_tmp_perm();
	}

	/* update */
	tmp_tty_rule = (TTY_RULE *)extend_array(d->tty_acl_array,&(d->tty_acl_array_num),
						sizeof(TTY_RULE));
	tmp_tty_rule[d->tty_acl_array_num - 1] = work;
	d->tty_acl_array = tmp_tty_rule;

	return 0;
}

/**
 *  @name:	free_tty_acl
 *  @about:	free tty acl
 *  @args:	d (DOMAIN *) -> domain data
 *  @return:	none
 */
static void
free_tty_acl(DOMAIN *d)
{
	int i;

	if (d->tty_acl_array == NULL)
		return ;

	for (i = 0; i < d->tty_acl_array_num; i++)
	{
		if (d->tty_acl_array[i].rolename != NULL)
			free(d->tty_acl_array[i].rolename);
	}
	free(d->tty_acl_array);
}

/**
 *  PTS ACL
 */

/**
 *  @name:	register_pts_acl
 *  @about:	register pts acl
 *  @args:	domain (char *) -> domain name
 *  @args:	flag (int) ->
 *  @return:	return 0 on success
 */
int
register_pts_acl(char *domain, int flag)
{
	DOMAIN *d;
	PTS_RULE *tmp;
	PTS_RULE work;

	d = search_domain_hash(current_domain);
	work.domain = d;
	work.domain_name = NULL;
	work.perm = 0;
	
	if(domain!=NULL){
	  if(strcmp(domain,"vcs")==0){
	    action_error("vcs is not supported for -pts,-allterm\n");
	    exit(1);
	  }
	}

	if (flag == 0)
	{
		d->pts_create_flag = 1;
		return 0;
	}

	if (flag == 1)
	{
		work.domain_name = strdup(domain);
		work.perm = CHANGE_PRM;
	}

	if (flag == 2)
	{
		work.domain_name = strdup(domain);
		work.perm = get_tmp_perm();
	}
	/*update*/
	tmp = (PTS_RULE *)extend_array(d->pts_acl_array, &(d->pts_acl_array_num),
				       sizeof(PTS_RULE));
	tmp[d->pts_acl_array_num - 1] = work;

	d->pts_acl_array = tmp;

	return 0;
}

/**
 *  @name:	free_pts_acl
 *  @about:	free pts acl
 *  @args:	d (DOMAIN *) -> domain data
 *  @return:	none
 */
static void
free_pts_acl(DOMAIN *d)
{
	int i;
	char *p;

	if (d->pts_acl_array == NULL)
		return;

	for (i = 0; i < d->pts_acl_array_num; i++)
	{
		p = d->pts_acl_array[i].domain_name;
		if (p != NULL)
			free(p);
	}

	/*  if (d->pts_change_name != NULL)
	    {
	    free(d->pts_change_name);
	    }*/
	free(d->pts_acl_array);
}


/**
 *  RBAC
 */

/**
 *  This points to rolename currently handled.
 *  This is initialized by register_role.
 *  This is used by register_user.
 */
static char *tmp_role_name=NULL;

/**
 *  user-role
 */
HASH_TABLE *user_hash_table=NULL;

/**
 *  rbac information
 */
HASH_TABLE *rbac_hash_table=NULL;
#define USER_HASH_TABLE_SIZE 1024
#define RBAC_HASH_TABLE_SIZE 1024

/**
 *  @name:	register_role
 *  @about:	register new role with role_hash_table
 *  @args:	name (char *) -> role name
 *  @return:	nreturn 0 on success
 */
int
register_role(char *name)
{
	char *domain_name;
	DOMAIN *default_domain;
	RBAC *rbac;
	int len;

	len = strlen(name);
	if (len < 2 || !(name[len - 2] == '_' && name[len - 1] == 'r'))
	{
		snprintf(errmsg,sizeof(errmsg),
			 "role name %s is invalid. role name must be *_r\n",name);
		yyerror(errmsg);

		exit(1);
	}

	if (tmp_role_name != NULL)
	{
		free(tmp_role_name);
	}

	tmp_role_name = strdup(name);

	/* first call */
	if (rbac_hash_table == NULL)
	{
		rbac_hash_table = create_hash_table(RBAC_HASH_TABLE_SIZE);
		if (rbac_hash_table == NULL)
		{
			perror("malloc");
			exit(1);
		}
	}

	/* role name to <rolename prefix>_t */
	domain_name=make_role_to_domain(name);

	if ((rbac = (RBAC *)malloc(sizeof(RBAC))) == NULL)
	{
		perror("malloc");
		exit(1);
	}

	/*  */
	register_domain(domain_name, 1);

	/* set rbac */
	rbac->rolename = strdup(name);
	default_domain = search_domain_hash(domain_name);
	rbac->default_domain = default_domain;

	if (insert_element(rbac_hash_table, rbac, name) == -2)
	{
		snprintf(errmsg, sizeof(errmsg), "multiple definition of role %s\n", name);
		yyerror(errmsg);
		exit(1);
	}

	free(domain_name);
	return 0;
}


/*
Give label to  
/home/|user| mandatoray
*/
void label_user_homedir(char *user){
  char **homedir_list;
  char *path;
  int i;
  if(strcmp(user, "user_u")==0 || strcmp(user, "root")==0){
    return;
  }
  homedir_list = converter_conf.homedir_list;
  for(i=0; homedir_list[i]!=NULL ;i++){
    path = joint_3_str(homedir_list[i],"/", user);
    add_filerule_to_domain(DUMMY_DOMAIN_NAME, path, READ_PRM, FILE_ALL_CHILD);
    add_file_user_list(path);
    free(path);
  }
  
}

/**
 *  @name:	register_user
 *  @about:	register new name with user_hash_table
 *  @args:	name (char *) -> user name
 *  @return:	nreturn 0 on success
 */
int
register_user(char *name)
{
	int n;
	USER_ROLE *u;
	//RBAC *r;
	char **new_array;
	DOMAIN *domain;

	label_user_homedir(name);
	domain = search_domain_hash(current_domain);
	domain -> user = extend_ntarray(domain->user, name);
	
	/* first call */
	if (user_hash_table == NULL)
	{
		user_hash_table = create_hash_table(USER_HASH_TABLE_SIZE);
		if (user_hash_table == NULL)
		{
			perror("malloc");
			exit(1);
		}
	}

	u = (USER_ROLE *)search_element(user_hash_table, name);
	if (u == NULL)
	{
		if ((u = (USER_ROLE *)malloc(sizeof(USER_ROLE))) == NULL)
		{
			perror("malloc");
			exit(1);
		}
		u->username = strdup(name);

		if ((new_array = (char **)malloc(sizeof(char *))) == NULL)
		{
			perror("malloc");
			exit(1);
		}
		new_array[0] = strdup(tmp_role_name);

		u->role_name_array = new_array;

		u->role_name_array_num = 1;
		insert_element(user_hash_table, u, u->username);

		return 0;
	}
	else
	{
		/* update rbac_array */
		n = u->role_name_array_num;
		new_array = (char **)realloc(u->role_name_array, sizeof(char *)*(n+1));
		if (new_array == NULL)
		{
			perror("realloc");
			exit(1);
		}
		u->role_name_array_num++;

		new_array[u->role_name_array_num - 1] = strdup(tmp_role_name);

		u->role_name_array = new_array;

		return 0;
	}

	return 0;
}

/**
 *  @name:	free_rbac
 *  @about:	free rbac data
 *  @args:	v (void *) -> rbac data
 *  @return:	return 0 on success
 */
static int
free_rbac(void *v)
{
	RBAC *r;
	r = v;
	free(r->rolename);

	return 0;
}

/**
 *  @name:	free_user_role
 *  @about:	free user role data
 *  @args:	v (void *) -> user role data
 *  @return:	return 0 on success
 */
static int
free_user_role(void *v)
{
	int i;
	USER_ROLE *r;

	r = v;

	free(r->username);

	for (i = 0; i < r->role_name_array_num; i++)
	{
		free((r->role_name_array)[i]);
	}

	free(r->role_name_array);

	return 0;
}

/**
 *  @name:	free_rback_hash_table
 *  @about:	free rbac_hash_table
 *  @args:	none
 *  @return:	none
 */
void
free_rbac_hash_table()
{
	if (rbac_hash_table == NULL)
		return;

	handle_all_element(rbac_hash_table, free_rbac);
	delete_hash_table(rbac_hash_table);
}

/**
 *  @name:	free_user_hash_table
 *  @about:	free user hash table
 *  @args:	none
 *  @return:	none
 */
void
free_user_hash_table()
{
	if (user_hash_table == NULL)
		return ;
	handle_all_element(user_hash_table, free_user_role);

	delete_hash_table(user_hash_table);
}


int register_admin_other_acl(char *rule, int deny_flag){
  DOMAIN *domain;
  char **rulename_list;
  ADMIN_OTHER_RULE *tmp;
  ADMIN_OTHER_RULE work;
  
  domain = search_domain_hash(current_domain);
  work.domain = domain;
  work.rule = strdup(rule);
  work.deny_flag=deny_flag;

  rulename_list = get_rulename_list();
  if(check_exist_in_list(rule, rulename_list) != 1){
    action_error("Error: unsupoprted rule: %s\n",rule);
    exit(1);
  }
  
  tmp = (ADMIN_OTHER_RULE *)extend_array(domain->admin_rule_array, &(domain->admin_rule_array_num),sizeof(ADMIN_OTHER_RULE));
  tmp[domain->admin_rule_array_num -1 ] = work;
  domain->admin_rule_array = tmp;

  return 0; 
}

int register_fs_acl(char *fs){

  DOMAIN *domain;
  FS_RULE *tmp;
  FS_RULE work;

  domain = search_domain_hash(current_domain);
  work.domain = domain;
  work.fs = strdup(fs);
  work.allowed = get_tmp_perm();
  
  tmp = (FS_RULE *)extend_array(domain->fs_rule_array, &(domain->fs_rule_array_num),sizeof(FS_RULE));
  tmp[domain->fs_rule_array_num -1 ] = work;
  domain->fs_rule_array = tmp;

  /* if fs is not in converter.conf 
     exit(1)*/
  if(check_exist_in_list(fs, converter_conf.supported_fs_list) != 1){
    action_error("Error: allowfs: unsupoprted fs: %s\n",fs);
    exit(1);
  } 

  return 0;
}

void include_rule(char *str){
  return;
}

/*intended to be used from other file*/
int append_file_rule(char *domain_name, char *filename, int perm, int state){
  char **dir_list;

  if(gDir_search) {
	  dir_list = get_dir_list(filename, converter_conf.homedir_list, 1);
	  if(dir_list!=NULL){
		  /*label all parent directory*/
		  label_parent_dir(dir_list, filename, state);
		  free_ntarray(dir_list);
	  }  
  }
  
  add_filerule_to_domain(domain_name, filename, perm, state);
  
  if (state == FILE_DIRECT_CHILD){
    /* when allow <dir>* is described, add dummy permission to dummy domain. */
    label_child_dir(filename);
  }
  return 0;
}


int register_key_acl(char **domain_list){

  DOMAIN *domain;
  KEY_RULE *tmp;
  KEY_RULE work;
  int len;
  int i;
  char **target=NULL;

  domain = search_domain_hash(current_domain);
  work.domain = domain;
  work.permission = get_tmp_perm();
  work.type = ALLOW_RULE;

  len = get_ntarray_num(domain_list);  
  for(i=0;i<len;i++){
    target = extend_ntarray(target, domain_list[i]);
  }
  work.target= target;
  tmp = (KEY_RULE *)extend_array(domain->key_rule_array, &(domain->key_rule_array_num), sizeof(KEY_RULE));
  tmp[domain->key_rule_array_num -1]=work;
  domain->key_rule_array = tmp;
  return 0;
}
