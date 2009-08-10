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

#ifndef PARSE_H
#define PARSE_H
int str_to_perm(char *);
int str_to_key_perm(char *);
char *perm_to_str(int allowed);
int get_tmp_perm();
void set_tmp_perm(int value);
void action_error(char *fmt, ...);
void action_warn(char *fmt, ...);
int warn_tmpfs();
char **add_strlist(char **list, char *str, int init_flag);
int add_permission(char *s, int flag, int init);
char *alloc_str(char *,char*);

/*Functions which must be implemented by each programs that uses parser(middle_lang.y middle_lang.l)*/
int register_comment(char *);
int register_role(char *);
int register_user(char *);
void register_domain(char *, int);
void register_type(char *);
void register_program(char **paths_list, int create_domain_name_flag);
void register_class(char *class);
void register_program_entry_force(char **paths_list);
int register_file_rule(char *);
int register_file_deny(char *);
int register_tmp_file_acl(char *,char *,int);
int register_tmp_fs_acl(char *,char *,int);
int register_net_acl(int, int);
int register_key_acl(char **);
int register_net_sock_acl(int,int ,int,char**,char **);
int register_net_netif_acl(int,int,char **,int);
int register_net_node_acl(int,int,char **,int);
int register_com_acl(int, char *);
int register_tty_acl(char *, int);
int register_pts_acl(char *, int);
int register_fs_acl(char *);
int register_admin_other_acl(char *,int);
void register_domain_trans(char **, char **);
void register_dev_acl(char **);
void register_terminal_acl(char *,char *, int);
void include_rule(char *);

char *get_sourcefile();

/*** Constants used for parser***/
#define ALLOW_RULE 1
#define DENY_RULE 0

#define FILE_PERM		0
#define IPC_PERM		1
#define SIG_PERM		2
#define ADM_PERM		3
#define RW_PERM			4
#define NET_PERM                5
#define KEY_PERM                6

#define TCP_ACL		0x01		/* TCP socket		*/
#define UDP_ACL		0x02		/* UDP socket		*/
#define UNIX_ACL	0x04		/* UNIX domain socket	*/
#define SEM_ACL		0x08		/* semaphore		*/
#define MSG_ACL		0x10		/* message		*/
#define MSGQ_ACL	0x20		/* message queue	*/
#define SHM_ACL		0x40		/*pshared memory	*/
#define PIPE_ACL	0x80		/* pipe			*/
#define SIG_ACL		0x100		/* signal		*/
#define TMPFS_ACL	10		/* tmpfs		*/

#define PROC_SELF	1
#define PROC_OTHER	2
#define PROC_SYSTEM	3
#define PROC_KMSG	4
#define PROC_PROC	5

/*used in allownet*/
#define NET_TCP 0x01
#define NET_UDP 0x02
#define NET_RAW 0x04

#define NET_DENY 0
#define NET_SERVER 0x01
#define NET_CLIENT 0x02
#define NET_USE 0x04
#define NET_SEND 0x08
#define NET_RECV 0x10
#define NET_BIND 0x20

#define NET_PORT_WELLKNOWN 6
#define NET_PORT_UNPRIV 7
#define NET_PORT_ALL 8
#define NET_PERM_SEND 0x01
#define NET_PERM_RECV 0x02
#define NET_PERM_BIND 0x04

#define NET_PERM_SEND_STR "send"
#define NET_PERM_RECV_STR "recv"
#define NET_PERM_BIND_STR "bind"

#define PORT_WELLKNOWN "wellknown"
#define PORT_ALL "allport"
#define PORT_UNPRIV "unprivport"


/**
 *  permissions used for file/key
 */
#define DENY_PRM		0x00
#define READ_PRM		0x01
#define WRITE_PRM		0x02
#define EXECUTE_PRM		0x04
#define APPEND_PRM		0x08
#define SEARCH_PRM		0x10
#define CHANGE_PRM		0x20
#define OVERWRITE_PRM           0x40
#define ERASE_PRM               0x80
#define CREATE_PRM              0x100
#define SETATTR_PRM             0x200
#define DOMAIN_EXECUTE_PRM      0x400
#define VIEW_PRM                0x800
#define LINK_PRM                0x1000
#define EXECMOD_PRM             0x2000

#define READ_STR		"r"
#define WRITE_STR		"w"
#define EXECUTE_STR		"x"
#define APPEND_STR		"a"
#define SEARCH_STR		"s"
#define OVERWRITE_STR           "o"
#define ERASE_STR               "e"
#define CREATE_STR              "c"
#define SETATTR_STR             "t"
#define DOMAIN_EXECUTE_STR      "dx"
#define VIEW_STR                "v"
#define LINK_STR                "l"
#define EXECMOD_STR             "m"

/**
 *  permission of SIGNAL
 */
#define CHID_PRM		0x01
#define KILL_PRM		0x02
#define STOP_PRM		0x04
#define OTHERSIG_PRM		0x08
#define NULL_PRM               0x10

#define CHID_STR		"c"
#define KILL_STR		"k"
#define STOP_STR		"s"
#define NULL_STR                "n"
#define OTHERSIG_STR		"o"

/**
 * permission of allowadm
 */
#define RELABEL_STR		"relabel"	
#define GETSECURITY_STR		"getsecurity" // replace "chsid" to "compute_relabel"
#define SETENFORCE_STR		"setenforce"  // replace "av_toggle" to "setenforce" 
#define LOAD_POLICY_STR		"load_policy"
#define NET_STR			"net"
#define BOOT_STR		"boot"
#define INSMOD_STR		"insmod"
#define QUOTAON_STR		"quotaon"
#define SWAPON_STR		"swapon"
#define MOUNT_STR		"mount"
#define RAW_IO_STR		"raw_io"
#define PTRACE_STR		"ptrace"
#define CHROOT_STR		"chroot"
#define SEARCH_ALL_STR		"search"
#define UNLABEL_STR		"unlabel"
#define READ_ALL_STR		"read"
#define WRITE_ALL_STR		"write"
#define PART_RELABEL_STR	"part_relabel"
#define ALL_STR                 "all"
#define WILDCARD_STR            "*"

int yyerror(char *);
int yywarn(char *);

#endif
