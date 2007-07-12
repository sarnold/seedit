%{
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

/* $Id: middle_lang.y,v 1.20 2006/05/05 14:23:24 ynakam Exp $ */
/*yacc specification for middle language*/
/*Yuichi Nakamura fix after 2004 */
#include <stdio.h>
#include <seedit/parse.h>
#include <seedit/middle_lang.h>
#include <seedit/common.h>
#define YYSTYPE char *
static char **domains_list=NULL;
static char **paths_list=NULL;
static char **idents_list=NULL;
static char **string_list=NULL;
static char **port_list=NULL;
static char *name=NULL;
static char *option=NULL;
static int protocol;
static int behavior;
static int permission;
static int ipc_flag;

extern int yylex(void);

%}

%token DOMAIN
%token ROLE
%token USER
%token ALL
%token ALLOW
%token ALLOWNET
%token ALLOWCOM
%token ALLOWADM
%token ALLOWDEV
%token ALLOWKEY
%token ALLOWFS
%token ALLOWTMP
%token ALLOWPRIV
%token DENYPRIV
%token ROOT
%token NAME
%token NET
%token RAW
%token NETLINK
%token CONNECT
%token FS
%token DIRECTORY
%token TCP
%token UDP
%token NETIFOPT
%token NODEOPT
%token PROTOCOLOPT
%token IPV4ADDRESS
%token SERVER
%token DEFAULT
%token CLIENT
%token USE
%token SEND
%token RECV
%token BIND
%token DOMAINOPT
%token ALLPORT
%token WELLKNOWN
%token UNPRIVPORT
%token UNIX
%token IPC
%token SEM
%token MSG
%token MSG
%token MSGQ
%token SHM
%token PIPE
%token SIG
%token PORT
%token SECURITY
%token SYSTEM
%token SELF
%token OTHER
%token KMSG
%token PROC
%token CREATE
%token CHANGE
%token GENERAL
%token DENY
%token DOMAIN_TRANS
%token PROGRAM
%token PATH
%token GLOBAL_DOMAIN
%token IDENTIFIER
%token FILENAME
%token NUMBER
%token EXCLUSIVE_FILE
%token TTY
%token PTS
%token ALLTERM
%token NOOWNER
%token OPEN
%token ADMIN
%token INCLUDE
%token INCLUDESTR
%%



POLICY : POLICY TE_SECTION
       |POLICY RBAC_SECTION
       |TE_SECTION
       |RBAC_SECTION
       ;

TE_SECTION  :'{' DOMAIN_DEF DOMAIN_TRANS_DEFS BODY_DEFS '}'
         |'{' DOMAIN_DEF BODY_DEFS '}'
         |'{' DOMAIN_DEF  '}'
         |'{' DOMAIN_DEF DOMAIN_TRANS_DEFS '}'
/*         |'{'   PROGRAM_AUTO_DEF BODY_DEFS '}'
         |'{' PROGRAM_AUTO_DEF '}' */
         ;


RBAC_SECTION :'{' ROLE_DEF USER_DEFS DOMAIN_TRANS_DEFS BODY_DEFS '}'
             |'{' ROLE_DEF  DOMAIN_TRANS_DEFS BODY_DEFS '}'
             |'{' ROLE_DEF   BODY_DEFS '}'
             |'{' ROLE_DEF USER_DEFS  BODY_DEFS '}'
;

ROLE_DEF: ROLE IDENTIFIER ';'{register_role($2);}
;

USER_DEFS: USER_DEFS USER_DEF
         | USER_DEF
;

USER_DEF: USER IDENTIFIER ';'{register_user($2);}
;


DOMAIN_DEF  : DOMAIN IDENTIFIER ';' {register_domain($2,0); }
;

BODY_DEFS :ALLOW_DEF|DENY_DEF|ALLOWNET_DEF|ALLOWCOM_DEF|ALLOWPRIV_DEF|ALLOWFS_DEF|ALLOWDEV_DEF|INCLUDE_DEF|ALLOWTMP_DEF|ALLOWKEY_DEF
          |BODY_DEFS ALLOW_DEF
          |BODY_DEFS DENY_DEF
          |BODY_DEFS ALLOWNET_DEF
          |BODY_DEFS ALLOWCOM_DEF
          |BODY_DEFS ALLOWPRIV_DEF
          |BODY_DEFS ALLOWFS_DEF
          |BODY_DEFS ALLOWDEV_DEF
          |BODY_DEFS INCLUDE_DEF
          |BODY_DEFS ALLOWTMP_DEF
          |BODY_DEFS ALLOWKEY_DEF
;

ALLOW_DEF  : ALLOW PATH  PERMISSIONS ';' {register_file_rule($2);}
           |ALLOW IDENTIFIER  PERMISSIONS ';' {register_file_rule($2);}
;

ALLOWTMP_DEF : ALLOWTMP DIRECTORY PATH NAME IDENTIFIER ';' {register_tmp_file_acl($3,$5,0);}
| ALLOWTMP DIRECTORY PATH NAME IDENTIFIER PERMISSIONS ';' { register_tmp_file_acl($3,$5,1);}            
| ALLOWTMP DIRECTORY PATH NAME  ASTERISK PERMISSIONS ';' {  register_tmp_file_acl($3,$5,1); }
| ALLOWTMP FS IDENTIFIER NAME IDENTIFIER ';' { register_tmp_fs_acl($3,$5,0);}
| ALLOWTMP FS IDENTIFIER NAME IDENTIFIER PERMISSIONS ';' { register_tmp_fs_acl($3,$5,1);}
| ALLOWTMP FS PATH NAME  ASTERISK PERMISSIONS ';' {  register_tmp_file_acl($3,$5,1); }
;


ASTERISK		: '*'
;

PERMISSIONS : PERMISSIONS ',' IDENTIFIER {add_permission($3,FILE_PERM,0);}
            |IDENTIFIER { add_permission($1,FILE_PERM,1); }
            |ASTERISK { add_permission($1,FILE_PERM,1);}
;





DENY_DEF :DENY PATH ';'{register_file_deny($2);}
;



DOMAIN_TRANS_DEFS:DOMAIN_TRANS_DEF
                 |DOMAIN_TRANS_DEFS DOMAIN_TRANS_DEF
                 |PROGRAM_DEF
;

DOMAIN_TRANS_DEF:DOMAIN_TRANS DOMAINS_DEF PATHS_DEF ';' {register_domain_trans(domains_list,paths_list);}
                |DOMAIN_TRANS DOMAINS_DEF ';' {register_domain_trans(domains_list,NULL);}

;

PROGRAM_DEF:PROGRAM PATHS_DEF ';' {register_program(paths_list,0);}
;

/*domain name is automatically defined*/
/*PROGRAM_AUTO_DEF: PROGRAM PATHS_DEF ';' {register_program(paths_list,1); }
*/

PATHS_DEF : PATHS_DEF ',' PATH { paths_list = add_strlist(paths_list,$3,0); }
          |PATH { paths_list = add_strlist(paths_list,$1,1); }             
               
;

IDENTIFIER_PATHS_DEF : IDENTIFIER_PATHS_DEF ','  IDENTIFIER { idents_list = add_strlist(idents_list,$3,0); }
                     |IDENTIFIER_PATHS_DEF ','  PATH { idents_list = add_strlist(idents_list,$3,0); }
                     |IDENTIFIER { idents_list = add_strlist(idents_list,$1,1); }                      
                     |PATH { idents_list = add_strlist(idents_list,$1,1); }                       
;




DOMAINS_DEF : DOMAINS_DEF ',' IDENTIFIER { domains_list = add_strlist(domains_list,$3,0);}
|IDENTIFIER { domains_list = add_strlist(domains_list,$1,1); }                           
;

/*allownet rule*/
ALLOWNET_DEF:
/*allownet -protocol tcp,udp,raw -domain <domain>|global use*/
ALLOWNET PROTOCOLOPT TCPUDP_DEF DOMAINOPT DOMAINS_DEF USE ';' {register_net_sock_acl(ALLOW_RULE, protocol,NET_USE, NULL,domains_list);}
/*allownet -protocol tcp|udp -port <portnumber> client,server;*/
|ALLOWNET PROTOCOLOPT TCPUDP_DEF PORT PORT_DEF  PORT_PERM_DEF ';' {register_net_sock_acl(ALLOW_RULE, protocol,behavior,port_list,NULL);}
/*allownet -protocol raw use*/
|ALLOWNET PROTOCOLOPT RAW USE ';' { 
domains_list = add_strlist(domains_list,"domain",1);  
register_net_sock_acl(ALLOW_RULE, NET_RAW,NET_USE,NULL, domains_list);  
}

/*allownet -netif <nic name> send|recv*/
|ALLOWNET PROTOCOLOPT PROTOCOL_DEF NETIFOPT IDENTIFIER_LIST_DEF SEND_RECV_PERM_DEF';' {register_net_netif_acl(ALLOW_RULE, protocol,string_list,permission);}
/*allownet -node <nodename> send|recv|bind*/
|ALLOWNET PROTOCOLOPT PROTOCOL_DEF NODEOPT IPV4ADDRESS_LIST_DEF SEND_RECV_BIND_PERM_DEF ';'{register_net_node_acl(ALLOW_RULE, protocol,string_list,permission);}
;

IDENTIFIER_LIST_DEF : IDENTIFIER_LIST_DEF ',' IDENTIFIER { string_list = add_strlist(string_list,$3,0);}
|IDENTIFIER { string_list = add_strlist(string_list,$1,1); } 
|ASTERISK { string_list = add_strlist(string_list,"*",1); } 
;

IPV4ADDRESS_LIST_DEF : IPV4ADDRESS_LIST_DEF ',' IPV4ADDRESS {string_list = add_strlist(string_list, $3,0);}
| IPV4ADDRESS_LIST_DEF ',' DEFAULT {string_list = add_strlist(string_list, $3,0);}
|IPV4ADDRESS {string_list = add_strlist(string_list,$1,1);}
|ASTERISK {string_list = add_strlist(string_list, "*" ,1);}
;

PROTOCOL_DEF:PROTOCOL_DEF ',' TCP {protocol|=NET_TCP;}
            | PROTOCOL_DEF ',' UDP {protocol|=NET_UDP;}
            | PROTOCOL_DEF ',' RAW {protocol|=NET_RAW;}
            | TCP {protocol=NET_TCP;}
            | UDP {protocol=NET_UDP;}
            | RAW {protocol=NET_RAW;}          
            |ASTERISK {protocol = NET_TCP|NET_UDP|NET_RAW;}
;

TCPUDP_DEF:PROTOCOL_DEF ',' TCP {protocol|=NET_TCP;}
            | PROTOCOL_DEF ',' UDP {protocol|=NET_UDP;}
            | TCP {protocol=NET_TCP;}
            | UDP {protocol=NET_UDP;}
            |ASTERISK {protocol = NET_TCP|NET_UDP;}
;


PORT_PERM_DEF: PORT_PERM_DEF ',' SERVER {behavior|=NET_SERVER;}
             |PORT_PERM_DEF ',' CLIENT {behavior|=NET_CLIENT;}
             |SERVER {behavior=NET_SERVER;}
             |CLIENT {behavior=NET_CLIENT;}
             |ASTERISK {behavior = NET_SERVER|NET_CLIENT;}
	     ;



SEND_RECV_PERM_DEF: SEND_RECV_PERM_DEF ',' SEND {permission|=NET_SEND;}
| SEND_RECV_PERM_DEF ',' RECV {permission |=NET_RECV;}
| SEND {permission =NET_SEND;}
|RECV  {permission =NET_RECV;}
;

SEND_RECV_BIND_PERM_DEF: SEND_RECV_PERM_DEF ',' SEND {permission|=NET_SEND;}
| SEND_RECV_PERM_DEF ',' RECV {permission |=NET_RECV;}
| SEND_RECV_PERM_DEF ',' BIND {permission |=NET_BIND;}
| SEND {permission =NET_SEND;}
| RECV  {permission =NET_RECV;}
| BIND  {permission =NET_BIND;}
;
/*NET_PERMISSIONS: NET_PERMISSIONS ',' IDENTIFIER {add_permission($3,NET_PERM,0);}
               |IDENTIFIER { add_permission($1,NET_PERM,1); }
	       ;*/
 
PORT_DEF:PORT_DEF ',' NUMBER {port_list = add_strlist(port_list,$3,0);}
        |NUMBER { port_list = add_strlist(port_list,$1,1);}
        |ALLPORT_DEF { port_list = add_strlist(port_list,PORT_ALL,1);}
        |WELLKNOWN { port_list = add_strlist(port_list,PORT_WELLKNOWN,1);}
        |UNPRIVPORT { port_list = add_strlist(port_list,PORT_UNPRIV,1);}
;

ALLPORT_DEF: ALLPORT {;}
           |ASTERISK {;}
;



ALLOWCOM_DEF:ALLOWCOM IPC_OPT IDENTIFIER READ_WRITE_PERMISSIONS';' {register_com_acl(ipc_flag,$3);}
            |ALLOWCOM IPC_OPT ASTERISK READ_WRITE_PERMISSIONS';' {register_com_acl(ipc_flag,$3);}
            |ALLOWCOM SIG IDENTIFIER SIG_PERMISSIONS';' {register_com_acl(SIG_ACL,$3);}
            |ALLOWCOM SIG ASTERISK SIG_PERMISSIONS ';' {register_com_acl(SIG_ACL,$3);}
;

IPC_OPT : UNIX {ipc_flag = UNIX_ACL;}
        | SEM {ipc_flag = SEM_ACL;}
        | MSG {ipc_flag = MSG_ACL;}
        | MSGQ {ipc_flag = MSGQ_ACL;}
        | SHM {ipc_flag = SHM_ACL;}
        |PIPE {ipc_flag = PIPE_ACL;}
        | IPC {ipc_flag = UNIX_ACL|SEM_ACL|MSG_ACL|MSGQ_ACL|SHM_ACL|PIPE_ACL;}
;

SIG_PERMISSIONS : SIG_PERMISSIONS ',' IDENTIFIER {add_permission($3,SIG_PERM,0);}
                |IDENTIFIER { add_permission($1,SIG_PERM,1); }             
                |ASTERISK { add_permission($1, SIG_PERM, 1); }
;


ALLOWKEY_DEF:ALLOWKEY DOMAINS_DEF KEY_PERMISSIONS ';' {register_key_acl(domains_list);}
;

KEY_PERMISSIONS : KEY_PERMISSIONS ',' IDENTIFIER {add_permission($3,KEY_PERM,0);}
                |IDENTIFIER { add_permission($1,KEY_PERM,1); }             
                |ASTERISK { add_permission($1, KEY_PERM, 1); }
;



ALLOWPRIV_DEF:ALLOWPRIV   IDENTIFIER ';' {register_admin_other_acl($2,0);}
             |DENYPRIV    IDENTIFIER ';'  {register_admin_other_acl($2,1);}
;


ALLOWDEV_DEF: ALLOWDEV ROOT IDENTIFIER_PATHS_DEF ';' {register_dev_acl(idents_list);}
|ALLOWDEV DEVOPT_DEF NAME_DEF READ_WRITE_PERMISSIONS ';' {register_terminal_acl(option,name,2);}
|ALLOWDEV DEVOPT_DEF OPEN ';' {register_terminal_acl(option,NULL,0);}
|ALLOWDEV DEVOPT_DEF NAME_DEF ADMIN ';' {register_terminal_acl(option,name,1);}
;

DEVOPT_DEF: TTY { option = alloc_str($1,option);}
          |PTS  { option = alloc_str($1,option); }
          |ALLTERM { option = alloc_str($1,option);}
;
NAME_DEF: IDENTIFIER {  name = alloc_str($1,name);}
          |GLOBAL_DOMAIN { name = alloc_str($1,name);}
          |GENERAL { name = alloc_str($1,name);}
;


ALLOWFS_DEF: ALLOWFS IDENTIFIER PERMISSIONS';'{register_fs_acl($2);}
;


READ_WRITE_PERMISSIONS: READ_WRITE_PERMISSIONS',' IDENTIFIER {add_permission($3,RW_PERM,0);}
                    |IDENTIFIER { add_permission($1,RW_PERM,1); }
                    |ASTERISK { add_permission($1, RW_PERM,1);}
;

INCLUDE_DEF: INCLUDE  INCLUDESTR ';' {include_rule($2);}
| INCLUDE  IDENTIFIER ';'  {include_rule($2);}
| INCLUDE FILENAME ';' {include_rule($2);}

;


%%

