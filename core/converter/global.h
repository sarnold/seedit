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
/* $Id: global.h,v 1.15 2006/05/05 15:21:06 ynakam Exp $ */

#ifndef GLOBAL_H
#define GLOBAL_H
#include "hashtab.h"


/*max filename length*/
#define MAX_FILENAME 4048
#define MAX_TMP_FILE 1024


/**
 *  default path and keyword
 */
#define SECURITY_CONF_FILE	"/etc/selinux/seedit"
#define CRONTAB_FILE            "/etc/crontab"
#define CROND_FILE              "/etc/cron.d"
#define CRON_SPOOL_FILE         "/var/spool/cron"
#define CRONTAB_TYPE            "system_cron_spool_t"
#define DUMMY_DOMAIN_NAME	"dummy_domain_t"
#define DUMMY_ROLE_NAME	"dummy_role_r"
#define FILE_ACL_TABLE_SIZE	1024

#define INITRC_DIR              "/etc/rc.d/init.d"


/*size of general buffer*/
#define BUFSIZE				1024

/**
 *  DOMAIN structure
 */
typedef struct domain_t DOMAIN;

/**
 *  RBAC structure
 */
typedef struct rbac_domain_t RBAC;

/**
 *  this stores File Rule
 */
/*To represent state */
/*  allow <filename>*/
#define FILE_ITSELF 0x01
/*allow <dir>*     */
#define FILE_DIRECT_CHILD 0x02
/*allow <dir>**    */
#define FILE_ALL_CHILD 0x04
typedef struct file_acl_rule_t{
  DOMAIN		*domain;	/* domain                */
  char		*path;		/* path name             */
  int		allowed;	/* toggle for permission */
  int  state; /* FILE_DIRECT_CHILD   FILE_ALL_CHILD FILE_ITSELF */
} FILE_ACL_RULE; 


/**
 *  allowtmp
 */
typedef struct file_tmp_rule_t
{
	DOMAIN		*domain;	/* domain                */
	char		*path;		/* path name             */
	char		*name;		/* label		 */
} FILE_TMP_RULE;

typedef struct fs_tmp_rule_t{
  DOMAIN *domain;
  char *fs;
  char *name;
}FS_TMP_RULE;

/*allow <path> exclusive -all <permission>*/
typedef struct tmp_all_rule_t{
  DOMAIN *domain;
  char *path;
  int allowed; /*permission*/
} TMP_ALL_RULE;


#define NONE			0x00

/**
 *  network ACL
 */

/*store allownet -tcp|-udp|-raw rule*/
/* store only one rule */
typedef struct net_socket_rule_t{
  DOMAIN *domain;
  int type; /*DENY_RULE or ALLOW_RULE*/
  int protocol; /*NET_TCP,UDP,RAW*/
  int behavior; /*NET_SERVER,CLIENT,USE*/
  char **port;     /*port number array terminates by NULL*/
  char **target;  /*domain list array terminates by NULL*/
} NET_SOCKET_RULE;


typedef struct net_netif_rule_t{
  DOMAIN *domain;
  int type; /*DENY_RULE or ALLOW_RULE*/
  int protocol; /*NET_TCP,UDP,RAW*/
  int permission; /*NET_SEND,RECV*/
  char **netif; /*List of name of netif*/
}NET_NETIF_RULE;

typedef struct net_node_rule_t{
  DOMAIN *domain;
  int type; /*DENY_RULE or ALLOW_RULE*/
  int protocol; /*NET_TCP,UDP*/
  int permission; /*NET_SEND,RECV,BIND*/
  char  **ipv4addr;  /*list of <ipaddress>/<netmask> e.g: 168.0.0.1/255.255.255.0*/
}NET_NODE_RULE;


typedef struct key_rule_t{
  DOMAIN *domain;
  int type; /*DENY_RULE or ALLOW_RULE*/
  int permission; 
  char **target; /*domain list array terminated by NULL*/
} KEY_RULE;

/**
 *  IPC ACL
 */
typedef struct com_rule_t
{
	DOMAIN		*domain;
	int		flag;		/* kind of IPC ,kinds are described in #define */
	char		*domain_name;	/* the destination domain */
	int		perm;		/* allowed permission (r,w) */
} COM_ACL_RULE;


/**
 *  TTY ACL
 */
typedef struct allow_tty_t
{
	DOMAIN		*domain;
	//  RBAC	*role;
	char		*rolename;	/* destination */
	int		perm;		/* allowed permission (r,w,CHANGE) */
} TTY_RULE;

/**
 *  PTS ACL
 *  access rights of domain to pts of "domainname"
 */
typedef struct allow_pts_t
{
	DOMAIN		*domain;
	char		*domain_name;	/* destination */
	// char		*change_name;
	int		perm;		/* allowed permission(r,w,CHANGE) */
} PTS_RULE;



typedef struct allow_fs_rule_t {
  DOMAIN		*domain;	/* domain                */
  char		*fs;		/* file system name. what can be used as fs is listed in supported_fs section in converter.conf*/
  int             allowed;		/* permission, the same as file */
} FS_RULE;


/*for  allowpriv*/
typedef struct allow_admin_priv_rule_t{
  DOMAIN *domain;
  char *rule;
  int deny_flag; /*if 1, denypriv*/
} ADMIN_OTHER_RULE;


/**
 *  The main structure.
 *  Information about domain.
 */
struct domain_t {
  char		*name;			/* name of domain		*/
  int		roleflag;		/* if "name" is role,then 1	*/
  int           program_flag;            /* if domain transition is described by "program" statement, then 1 else 0  */

  
  /* File */
  FILE_ACL_RULE *file_rule_array;
  int file_rule_array_num;
  HASH_TABLE	*appeared_file_name;   /*key:file name that appeared in allow/deny, value:1*/

  char **user; /*user statement, NULL terminated array*/

  FILE_TMP_RULE	*tmp_rule_array;	/* "allowtmp"	*/  
  int		tmp_rule_array_num;
  TMP_ALL_RULE    *tmp_all_array;     /*allowtmp <path> -name -all <permissions>*/
  int tmp_all_array_num;
  
  /* net, ipc */
  COM_ACL_RULE	*com_acl_array;		/* IPC				*/
  int		com_acl_array_num;


  /* allowdev*/
  char **dev_root_array; /*allowdev -root <directory>;*/
  int   dev_root_array_num;

  /** allowdev -pts/-tty*/
  /* -tty */
  char		tty_create_flag;	/* allow -tty open */
  TTY_RULE	*tty_acl_array;
  int		tty_acl_array_num;
  /* -pts */
  char		pts_create_flag; 
  PTS_RULE	*pts_acl_array;
  int		pts_acl_array_num;
  //  char *pts_change_name;
  
  FS_RULE    *fs_rule_array;     /*allowfs*/
  int fs_rule_array_num;  
  FS_TMP_RULE *fs_tmp_rule_array; /*allowfs exclusive*/
  int fs_tmp_rule_array_num;

  /*allownet*/
  NET_SOCKET_RULE *net_socket_rule_array;
  int              net_socket_rule_array_num; 
  NET_NETIF_RULE *net_netif_rule_array;
  int             net_netif_rule_array_num;
  NET_NODE_RULE *net_node_rule_array;
  int           net_node_rule_array_num;

  /*allowkey*/
  KEY_RULE *key_rule_array;
  int key_rule_array_num;

  /*allowpriv*/
  ADMIN_OTHER_RULE *admin_rule_array;
  int               admin_rule_array_num;

  HASH_TABLE	*dir_list;   /*Key:Directories that appeared in allow rules. Value:1*/
};

/**
 *  domain transition 
 */
typedef struct trans_rule_t
{
	char		*parent;
	char		*path;
  int state; /*state of path : FILE_DIRECT_CHILD   FILE_ALL_CHILD FILE_ITSELF */
	char		*child;
	int		auto_flag;	/* if the transition is "domain_auto_trans",then 1 */

} TRANS_RULE;

/**
 *  association of file with label
 */
typedef struct file_label_t
{
	char		*filename;
	char		*labelname;
	char		rec_flag;	/* if the label is inherited by child directory, this is 1,else 0 */
} FILE_LABEL;


typedef struct force_label_t{
  char *filename;
  char *type;
}FORCE_LABEL;


/**
 *     rbac     
 */

/**
 *  relationship between  role and domain
 */
struct rbac_domain_t {
	char *rolename;
	DOMAIN *default_domain;
	//DOMAIN **domain_array;
	//int domain_array_num;
};

/**
 *  relation between user and role
 */
typedef struct user_role_t
{
	char *username;
	char **role_name_array;
	int role_name_array_num;
} USER_ROLE;

typedef struct entry_point_table_t{
  char *filename; /*wildcard is not permitted*/
  int state; /*state of filename */ /* FILE_DIRECT_CHILD   FILE_ALL_CHILD FILE_ITSELF */
  char *to_domain;/*to domain*/
} ENTRY_POINT;


/**
 *  global value 
 */
#define DEFAULT_HASH_TABLE_SIZE 1000
extern HASH_TABLE *domain_hash_table;		/* Hash table of DOMAIN structure
						   the body is in action.c			*/
extern HASH_TABLE *file_label_table;		/* relationship between file and label,
						   the body is in file_label.c			*/
extern HASH_TABLE *dir_label_table;             /*Relationship between dir and label. This is to used to allow dir:search access to parent dirs*/

extern HASH_TABLE *defined_label_table;		/* registers defined label lists
						   key:labelname,value:1(int)			*/
extern HASH_TABLE *tmp_label_table;		/* registers defined allow exclusive labels
						   key:labelname,value:path(int)			*/

extern HASH_TABLE * all_dirs_table;/*All dirs used in allow/deny rules*/

/*to store reserved port*/
/*key: string of <port number> value:type for port*/
extern HASH_TABLE *tcp_port_label_table;
extern HASH_TABLE *udp_port_label_table;
/*key <ipaddress>/<netmask> value: type for node*/
extern HASH_TABLE *node_label_table;


/*To store all entry points*/
extern ENTRY_POINT *g_entry_point_array;
extern int g_entry_point_array_num;

#define LABEL_LIST_SIZE 10000

/**
 *  domain transition
 */
extern TRANS_RULE *rulebuf;			/* the body is in action.c			*/
extern int domain_trans_rule_num;

/**
 *  relationship between user adn role
 */
extern HASH_TABLE *user_hash_table;		/* element is USER_ROLE structure		*/
extern HASH_TABLE *rbac_hash_table;		/* element is RBAC structure			*/

/**
 *  allownet
 */
extern char used_tcp_ports[1024+1];		/* body is in action.c				*/
extern char used_udp_ports[1024+1];		/* body is in action.c				*/


/*list to store attribute*/
/*End of list is NULL*/
#define MAX_ATTR 1024
extern char *attribute_list[MAX_ATTR];

/* NULL terminated arraylist to store users that appeared in filename */
extern char **g_file_user_list;

/*struct and global value to store elements configurable in converter.conf*/
#define MAX_FORCE 1024
#define MAX_FS 1024 
#define MAX_CLASS 1024
#define MAX_NETIF 16
#define MAX_PROC_MOUNT 16
#define MAX_HOME 16
#define MAX_ENTRY 256
typedef struct converter_conf_t{
  /*list to store files that are labeled in configuration in conveter.conf*/
  /*End of list is NULL*/
  FORCE_LABEL *force_label_list[MAX_FORCE];/*force_label*/
  char *supported_fs_list[MAX_FS];/*supported_fs section end of list is null*/
  char *file_type_trans_fs_list[MAX_FS];/*for file_type_trans_fs section, NULL terminated*/
  char *allowpriv_class_list[MAX_CLASS];  
  char *netif_name_list[MAX_NETIF];
  char *proc_mount_point_list[MAX_PROC_MOUNT];
  char *authentication_domain[MAX_CLASS];
  char *homedir_list[MAX_HOME]; /*path to home directory, no slash at the end : i.e /home*/
  char *mcs_range_trans_entry[MAX_ENTRY]; /*Entrypoint of range_trans, like: 
                                        range_transition getty_t login_exec_t s0 - s0:c0.c1023;
                                       */
}CONVERTER_CONF;

extern CONVERTER_CONF converter_conf;


#define MAX_ROLE 1024

/**
 *  this stores labels named by "file_type_auto_trans",because these labels are overwritten by "setfiles".
 */
FILE *TMP_fp;


#define MAX_COMMENT 256

#endif
