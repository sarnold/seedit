/*
#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura
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
#include <unistd.h>
#include <libxml/parser.h>
#include <libxml/tree.h>
#include <seedit/common.h>
#include <seedit/parse.h>

extern FILE *yyin;
extern int yyparse(void);
extern char **yycomment;
const char usage[]= "Usage :seedit-export  -i <infile> -o <output>";

xmlDocPtr gXMLdoc = NULL;       
xmlNodePtr gCurrent_domain_node = NULL;
xmlNodePtr gRoot_node=NULL;

void yycomment_free(){
  int i=0;
  for(i=0; yycomment[i]!=NULL;i++){
    free(yycomment[i]);
  }
  yycomment=NULL;
}
/*get comment string not displayed.
 comment string is reset(cleared) after this.
*/
xmlChar *get_comment_str(){
  int len=0;
  int i;
  char *result;
  int pos;
  if (yycomment==NULL)
    return NULL;
  
  for(i=0;yycomment[i]!=NULL;i++){
    len = len + strlen(yycomment[i])+2;
  }
  
  result=(char *)my_malloc(sizeof(char)*len);
  
  pos=0;
  for(i=0;yycomment[i]!=NULL;i++){
    sprintf(&(result[pos]), "%s\n", yycomment[i]);
    pos = pos+strlen(yycomment[i])+strlen("\n");
  }

  yycomment_free();
  return BAD_CAST result;
}



int register_role(char *name){
  xmlNodePtr node=NULL;
  
  node=xmlNewChild(gRoot_node, NULL, BAD_CAST "section",NULL);
  xmlNewProp(node, BAD_CAST "id", BAD_CAST name);
  xmlNewProp(node, BAD_CAST "type", BAD_CAST "role");
  xmlNewChild(node, NULL, BAD_CAST "comment",get_comment_str());

  
  gCurrent_domain_node=node;

  return 0;
}

void register_domain(char *name, int role_flag){
  xmlNodePtr node=NULL;
  node=xmlNewChild(gRoot_node, NULL, BAD_CAST "section",NULL);
  xmlNewProp(node, BAD_CAST "id", BAD_CAST name);
  xmlNewProp(node, BAD_CAST "type", BAD_CAST "domain");
  xmlNewChild(node, NULL, BAD_CAST "comment",get_comment_str());

  gCurrent_domain_node=node;
  
  return;
}


void register_program(char **path_list, int flag){
  xmlNodePtr program_node=NULL;
  xmlNodePtr node=NULL;
  int num;
  int i;

  program_node = xmlNewChild(gCurrent_domain_node, NULL, BAD_CAST "program",NULL);
  xmlNewChild(program_node, NULL, BAD_CAST "comment",get_comment_str());
  
  num = get_ntarray_num(path_list);
  
  for(i=0;i<num;i++){
    node=xmlNewChild(program_node, NULL, BAD_CAST "path",BAD_CAST path_list[i]);   
  }
  return;
}


void register_domain_trans(char **domain_list, char **path_list){
  xmlNodePtr domain_trans_node=NULL;
  xmlNodePtr node=NULL;
  int d_list_num;
  int p_list_num;
  int i;
  int j;

  d_list_num = get_ntarray_num(domain_list);
  p_list_num = get_ntarray_num(path_list);
 
  domain_trans_node=xmlNewChild(gCurrent_domain_node, NULL, BAD_CAST "domaintrans",NULL);
  xmlNewChild(domain_trans_node, NULL, BAD_CAST "comment",get_comment_str());

  
  for(i=0;i<d_list_num;i++){
    node=xmlNewChild(domain_trans_node, NULL, BAD_CAST "parentdomain",BAD_CAST domain_list[i]);
  }
  for(j=0;j<p_list_num;j++){
    node=xmlNewChild(domain_trans_node, NULL, BAD_CAST "entrypoint",BAD_CAST path_list[j]);
  }

  return;
}

void register_dev_acl(char **path_list){
  int p_list_num;
  int i;
  xmlNodePtr allowdev_node=NULL;
  p_list_num = get_ntarray_num(path_list);
  allowdev_node=xmlNewChild(gCurrent_domain_node, NULL, BAD_CAST "allowdev",NULL);  
  xmlNewProp(allowdev_node, BAD_CAST "type", BAD_CAST "allow");

  xmlNewChild(allowdev_node, NULL, BAD_CAST "comment",get_comment_str());
  xmlNewChild(allowdev_node, NULL, BAD_CAST "option",BAD_CAST "root");
  for(i=0;i<p_list_num;i++){
    xmlNewChild(allowdev_node, NULL, BAD_CAST "path",BAD_CAST path_list[i]);
  }
}



xmlNodePtr create_permission_tag(int perm, xmlNodePtr parent){
  char *buf;
  int i;  
  char c[2]="";
  xmlNodePtr node =NULL;
  
  buf = perm_to_str(perm);
  for(i=0; i<strlen(buf);i++){
    if (buf[i]=='-')
      continue;
    c[0] = buf[i];    
    c[1] = '\0';
    node = xmlNewChild(parent,NULL,BAD_CAST "permission",BAD_CAST c);
  }

  return node;
}

#define DIR 1
#define FS 2
void register_tmp_rule_common(int dir_or_fs, char *dir_fs_name, char *label, int perm_flag){
  xmlNodePtr allowtmp_node = NULL;
  xmlNodePtr node = NULL;
  int perm;

  allowtmp_node = xmlNewChild(gCurrent_domain_node, NULL, BAD_CAST "allowtmp",NULL);
  xmlNewChild(allowtmp_node, NULL, BAD_CAST "comment",get_comment_str());
  xmlNewProp(allowtmp_node, BAD_CAST "type", BAD_CAST "allow");

  if(dir_or_fs == DIR){
    node = xmlNewChild(allowtmp_node,NULL,BAD_CAST "dir",BAD_CAST dir_fs_name);    
  }else{
    node = xmlNewChild(allowtmp_node,NULL,BAD_CAST "fs",BAD_CAST dir_fs_name);
  }

  node = xmlNewChild(allowtmp_node,NULL,BAD_CAST "name",BAD_CAST label);
  
  if(perm_flag){
    perm = get_tmp_perm();
    create_permission_tag(perm, allowtmp_node);
  }
}

int register_tmp_file_acl(char *path, char *label, int perm_flag){
  register_tmp_rule_common(DIR,path,label,perm_flag);
  return 0;
}

int register_tmp_fs_acl(char *path, char *label, int perm_flag){
  register_tmp_rule_common(FS,path,label,perm_flag);
  return 0;
}

int register_file_acl_core(char *name, int deny_flag){
  xmlNodePtr allowfile_node = NULL;
  xmlNodePtr node = NULL;
  int perm;

  allowfile_node = xmlNewChild(gCurrent_domain_node, NULL, BAD_CAST "allowfile",NULL);
  xmlNewChild(allowfile_node, NULL, BAD_CAST "comment",get_comment_str());

  if(deny_flag){
    xmlNewProp(allowfile_node, BAD_CAST "type", BAD_CAST "deny");
  }else{
    xmlNewProp(allowfile_node, BAD_CAST "type", BAD_CAST "allow");
  }
  node = xmlNewChild(allowfile_node,NULL,BAD_CAST "path",BAD_CAST name);
  if(! deny_flag){
    perm = get_tmp_perm();
    create_permission_tag(perm, allowfile_node);
  } 
  return 0;
}


int register_file_rule(char *name){
  register_file_acl_core(name,0);
  return 0;
}


int register_file_deny(char *name){
  register_file_acl_core(name,1);
  return 0;
}


int register_user(char *name){    
  xmlNodePtr user_node = NULL;
  user_node = xmlNewChild(gCurrent_domain_node, NULL, BAD_CAST "user",NULL);
  xmlNewChild(user_node, NULL, BAD_CAST "comment",get_comment_str());
  xmlNewChild(user_node, NULL, BAD_CAST "uname", BAD_CAST name);

  return 0;
}


int register_net_node_acl(int rule_type, int protocol, char **node_list, int permission){
  xmlNodePtr allownet_node=NULL;
  xmlNodePtr node=NULL;
  int len;
  int i;
  char *addr;
  
  allownet_node = xmlNewChild(gCurrent_domain_node, NULL,  BAD_CAST "allownet", NULL);
  xmlNewProp(allownet_node, BAD_CAST "type", BAD_CAST "allow");
  xmlNewChild(allownet_node, NULL,  BAD_CAST "comment", get_comment_str());

  if (protocol & NET_TCP)
    node = xmlNewChild(allownet_node,NULL,BAD_CAST "protocol",BAD_CAST "tcp");
  if(protocol & NET_UDP)
    node = xmlNewChild(allownet_node,NULL,BAD_CAST "protocol",BAD_CAST "udp");
  if(protocol & NET_RAW)
    node = xmlNewChild(allownet_node,NULL,BAD_CAST "protocol",BAD_CAST "raw");

  if(node_list != NULL){
    len = get_ntarray_num(node_list);
    for(i=0;i<len;i++){
      addr =  node_list[i];
      node = xmlNewChild(allownet_node,NULL,BAD_CAST "node",BAD_CAST addr);
    }
  }
  
  if(permission & NET_SEND){
    node = xmlNewChild(allownet_node, NULL ,BAD_CAST "permission", BAD_CAST "send");    
  }
  if(permission & NET_RECV){
    node = xmlNewChild(allownet_node, NULL ,BAD_CAST "permission", BAD_CAST "recv");    
  }  
  if(permission & NET_BIND){
    node = xmlNewChild(allownet_node, NULL ,BAD_CAST "permission", BAD_CAST "bind");    
  }

  return 0;
}


int  register_net_netif_acl(int rule_type, int protocol, char **netif_list, int permission){
  xmlNodePtr allownet_node=NULL;
  xmlNodePtr node=NULL;
  int len;
  int i;
  char *netif;
  
  allownet_node = xmlNewChild(gCurrent_domain_node, NULL,  BAD_CAST "allownet", NULL);
  xmlNewProp(allownet_node, BAD_CAST "type", BAD_CAST "allow");
  xmlNewChild(allownet_node, NULL,  BAD_CAST "comment", get_comment_str());


  if (protocol & NET_TCP)
    node = xmlNewChild(allownet_node,NULL,BAD_CAST "protocol",BAD_CAST "tcp");
  if(protocol & NET_UDP)
    node = xmlNewChild(allownet_node,NULL,BAD_CAST "protocol",BAD_CAST "udp");
  if(protocol & NET_RAW)
    node = xmlNewChild(allownet_node,NULL,BAD_CAST "protocol",BAD_CAST "raw");

  if(netif_list != NULL){
    len = get_ntarray_num(netif_list);
    for(i=0;i<len;i++){
      netif =  netif_list[i];
      node = xmlNewChild(allownet_node,NULL,BAD_CAST "netif",BAD_CAST netif);
    }
  }
  
  if(permission & NET_SEND){
    node = xmlNewChild(allownet_node, NULL ,BAD_CAST "permission", BAD_CAST "send");    
  }
  if(permission & NET_RECV){
    node = xmlNewChild(allownet_node, NULL ,BAD_CAST "permission", BAD_CAST "recv");    
  }  

  return 0;
}


int register_net_sock_acl(int rule_type,int protocol, int permission, char **port_list, char **domain_list){

  xmlNodePtr allownet_node=NULL;
  xmlNodePtr node=NULL;
  int len;
  int i;
  char *port;
  char *domain;

  allownet_node = xmlNewChild(gCurrent_domain_node, NULL,  BAD_CAST "allownet", NULL);
  xmlNewProp(allownet_node, BAD_CAST "type", BAD_CAST "allow");
  xmlNewChild(allownet_node, NULL,  BAD_CAST "comment", get_comment_str());

  /*make <protocol> tag*/
  if (protocol & NET_TCP)
    node = xmlNewChild(allownet_node,NULL,BAD_CAST "protocol",BAD_CAST "tcp");
  if(protocol & NET_UDP)
    node = xmlNewChild(allownet_node,NULL,BAD_CAST "protocol",BAD_CAST "udp");
  if(protocol & NET_RAW)
    node = xmlNewChild(allownet_node,NULL,BAD_CAST "protocol",BAD_CAST "raw");
      
  if(port_list != NULL){
    len = get_ntarray_num(port_list);
    for(i=0;i<len;i++){
      port =  port_list[i];
      node = xmlNewChild(allownet_node,NULL,BAD_CAST "port",BAD_CAST port);
    }
  }
   
  if (domain_list !=NULL){
    len = get_ntarray_num(domain_list);
    for(i = 0;i<len;i++){
      domain = domain_list[i];
      if(strcmp(domain,"domain")!=0)
	node = xmlNewChild(allownet_node, NULL ,BAD_CAST "domain", BAD_CAST domain);    
    }
  }
   
  if(permission & NET_SERVER){
    node = xmlNewChild(allownet_node, NULL ,BAD_CAST "permission", BAD_CAST "server");    
  }
  if(permission & NET_CLIENT){
    node = xmlNewChild(allownet_node, NULL ,BAD_CAST "permission", BAD_CAST "client");    
  }
  if(permission & NET_USE){
    node = xmlNewChild(allownet_node, NULL ,BAD_CAST "permission", BAD_CAST "use");    
  }  
  
  return 0;
}

int register_com_acl(int flag, char *to_domain){
  xmlNodePtr allowcom_node=NULL;
  xmlNodePtr node=NULL;
  char *option=NULL;
  int perm=0;
  char *permstr=NULL;

  allowcom_node = xmlNewChild(gCurrent_domain_node, NULL,  BAD_CAST "allowcom", NULL);
  xmlNewProp(allowcom_node, BAD_CAST "type", BAD_CAST "allow");
  xmlNewChild(allowcom_node, NULL,  BAD_CAST "comment", get_comment_str());
  
  switch(flag){
  case UNIX_ACL|SEM_ACL|MSG_ACL| MSGQ_ACL|SHM_ACL| PIPE_ACL:
    option ="ipc";
    break;
  case UNIX_ACL:
    option="unix";
    break;
  case SEM_ACL:
    option="sem";
    break;
  case MSG_ACL:
    option="msg";
    break;
  case MSGQ_ACL:
    option="msgq";
    break;
  case SHM_ACL:
    option="shm";
    break;
  case PIPE_ACL:
    option="pipe";
    break;
  case SIG_ACL:
    option="sig";
    break;
  default:
    action_error("allowcom rule error can not be exported to XML\n");
    exit(1);
    break;  
  }



  node = xmlNewChild(allowcom_node,NULL,BAD_CAST "option",BAD_CAST option);

  if(to_domain!=NULL){
    node = xmlNewChild(allowcom_node,NULL,BAD_CAST "domain",BAD_CAST to_domain);
  }
  
  if (flag == SIG_ACL){
    perm = get_tmp_perm();
    if(perm & CHID_PRM){
      permstr=CHID_STR;
      node = xmlNewChild(allowcom_node,NULL,BAD_CAST "permission",BAD_CAST permstr);
    }
    if(perm & KILL_PRM){
      permstr=KILL_STR;
      node = xmlNewChild(allowcom_node,NULL,BAD_CAST "permission",BAD_CAST permstr);
    }
    if(perm & STOP_PRM){
      permstr=STOP_STR;
      node = xmlNewChild(allowcom_node,NULL,BAD_CAST "permission",BAD_CAST permstr);
    }
    if(perm & NULL_PRM){
      permstr=NULL_STR;
      node = xmlNewChild(allowcom_node,NULL,BAD_CAST "permission",BAD_CAST permstr);
    }
    if(perm & OTHERSIG_PRM){
      permstr = OTHERSIG_STR;
      node = xmlNewChild(allowcom_node,NULL,BAD_CAST "permission",BAD_CAST permstr);
    }    

  }else{
    create_permission_tag(get_tmp_perm(),allowcom_node);
  }

  return 0;
}

#define ALLOWTTY 0
#define ALLOWPTS 1

void register_terminal_acl(char *option, char *name, int flag){
  xmlNodePtr allow_node=NULL;
  xmlNodePtr node=NULL;
  char *o;
  allow_node = xmlNewChild(gCurrent_domain_node, NULL,  BAD_CAST "allowdev", NULL);
  xmlNewProp(allow_node, BAD_CAST "type", BAD_CAST "allow");
  xmlNewChild(allow_node, NULL,  BAD_CAST "comment", get_comment_str());

  if(option[0]=='-'){
    o = option+1;/*remove "-"*/
  }else{
    o = option;
  }
  node = xmlNewChild(allow_node,NULL,BAD_CAST "option", BAD_CAST o);
  
  if(name!=NULL){
    node = xmlNewChild(allow_node,NULL,BAD_CAST "role", BAD_CAST name);
  }
  
  if(flag == 0){
    node = xmlNewChild(allow_node,NULL,BAD_CAST "permission", BAD_CAST "open");
  }
   
  if(flag == 1){
    node = xmlNewChild(allow_node,NULL,BAD_CAST "permission", BAD_CAST "admin");
  }

  if(flag==2){
    create_permission_tag(get_tmp_perm(),allow_node);
  }

  return;
}

int register_proc_acl(int flag){
  xmlNodePtr allowproc_node=NULL;
  xmlNodePtr node=NULL;  
  char *option=NULL;

  allowproc_node=xmlNewChild(gCurrent_domain_node, NULL, BAD_CAST "allowproc",NULL);
  xmlNewProp(allowproc_node, BAD_CAST "type", BAD_CAST "allow");
  xmlNewChild(allowproc_node, NULL, BAD_CAST "comment",get_comment_str());


  switch(flag){
  case PROC_SELF:
    option="self";
    break;
  case PROC_OTHER:
    option="other";
    break;
  default:
    action_error("allowproc rule error can not be exported to XML\n");
    break;    
  }  
  node = xmlNewChild(allowproc_node,NULL,BAD_CAST "option", BAD_CAST option);

  create_permission_tag(get_tmp_perm(),allowproc_node);

  return 0;
}

int register_fs_acl(char *fs){
  xmlNodePtr allowfs_node=NULL;
  xmlNodePtr node=NULL;  
  
  allowfs_node=xmlNewChild(gCurrent_domain_node, NULL, BAD_CAST "allowfs",NULL);
  xmlNewProp(allowfs_node, BAD_CAST "type", BAD_CAST "allow");
  xmlNewChild(allowfs_node, NULL, BAD_CAST "comment",get_comment_str());

  node = xmlNewChild(allowfs_node,NULL,BAD_CAST "fs", BAD_CAST fs);
  
  create_permission_tag(get_tmp_perm(),allowfs_node);
  

  return 0;
}


int register_admin_other_acl(char *rule,int deny_flag){
  xmlNodePtr allowadm_node=NULL;
  xmlNodePtr node=NULL;  
  char *rulename; 

  rulename="allowpriv";
  allowadm_node=xmlNewChild(gCurrent_domain_node, NULL, BAD_CAST rulename,NULL);  
 
  xmlNewChild(allowadm_node, NULL, BAD_CAST "comment",get_comment_str());

  if(deny_flag==1){
    xmlNewProp(allowadm_node, BAD_CAST "type", BAD_CAST "deny");
  }else{
    xmlNewProp(allowadm_node, BAD_CAST "type", BAD_CAST "allow");
  }
  
  node = xmlNewChild(allowadm_node,NULL,BAD_CAST "option", BAD_CAST rule);

  return 0;
}

int main(int argc, char **argv){

  char *output_xml=NULL;
  int ch;  
  xmlNodePtr root_node = NULL;
  xmlDtdPtr dtd = NULL;     
  if (argc == 1)
    {
      fprintf(stderr, "%s\n", usage);
      exit(1);
    }
  
  while ((ch = getopt(argc, argv, "o:i:")) != EOF){
    switch (ch){
    case 'o':
      output_xml=strdup(optarg);
      break;
    case 'i':
      if ((yyin = fopen(optarg, "r")) == NULL){
	perror(optarg);
	exit(1);
      }
      break;
      
    default:
      fprintf(stderr, "%s\n", usage);
      exit(1);
      break;
    }
  }


  /*Init XML*/
  LIBXML_TEST_VERSION;
  gXMLdoc = xmlNewDoc(BAD_CAST "1.0");
  root_node = xmlNewNode(NULL, BAD_CAST "policy");
  xmlDocSetRootElement(gXMLdoc, root_node);
  dtd = xmlCreateIntSubset(gXMLdoc, BAD_CAST "policy", NULL, BAD_CAST "simplified_policy.dtd");

  gRoot_node=root_node;

  if (yyparse() != 0)
    exit(1);

  xmlSaveFormatFileEnc(output_xml==NULL ? "-" : output_xml , gXMLdoc, "UTF-8", 1);
  xmlFreeDoc(gXMLdoc);
  xmlCleanupParser();  
  xmlMemoryDump();
  return 0;
}

void include_rule(char *str){
  xmlNodePtr include_node=NULL;
  
  include_node = xmlNewChild(gCurrent_domain_node, NULL,  BAD_CAST "include", NULL);
  xmlNewChild(include_node, NULL,  BAD_CAST "comment", get_comment_str());

  xmlNewChild(include_node, NULL, BAD_CAST "path", BAD_CAST str);

  return;

}

