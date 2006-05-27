/* Written by Yuichi Nakamura based on Hitachi Software's code.
   Some Hitachi Software's codes are used.
*/
/* All Rights Reserved (C) 2005-2006, Yuichi Nakmura ynakam@gwu.edu */
/*
 * All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/types.h>
#include "file_label.h"
#include "global.h"
#include "action.h"
#include "hashtab.h"
#include "convert.h"
#include "out_file_acl.h"
#include "initial_policy.h"
#include <seedit/common.h>
#include <seedit/parse.h>
#include "security_class.h"

static void modify_rules();
static void make_dir_list();
static void out_allow(FILE *,FILE *);
static void out_domain_trans(FILE *);
//static void out_dummy_user_conf(FILE *);
static void out_net_type(FILE *);
static void out_rbac(FILE *);


void out_customizable_types(FILE *fp){
  HASH_NODE **array;
  int i;
  int num;
  char *label;
  array= create_hash_array(tmp_label_table);
  num = tmp_label_table->element_num;

  for(i=0;i<num;i++){
    label = (char *)array[i]->key;    
    fprintf(fp,"%s\n",label);
  }
  
}

FILE *openfile(char *outdir, char *filename){
  FILE *fp;
  char *fullpath;
  char *tmp;
  tmp = joint_str(outdir,"/");
  fullpath = joint_str(tmp,filename);
  if ((fp = fopen(fullpath, "w")) == NULL){
    perror(fullpath);
    exit(1);
  }
  free(tmp);
  free(fullpath);
  return fp;
}


/**
 *  @name:	convert
 *  @about:	Major process of converter
 *  @args:	policy_fp (FILE *) -> FILE pointer to print SELinux configuration.
 *  @args:	file_context_fp (FILE *) -> :FILE pointer to print file_contexts.
 *  @return:	none
 */
void convert(char *outdir){
  FILE *policy_fp=stdout;
  FILE *file_context_fp=stdout;
  FILE *unconfined_fp=stdout;
  FILE *customizable_types_fp=stdout;
  FILE *homedir_template_fp=stdout;

  if(outdir!=NULL){
    policy_fp= openfile(outdir,"generated.conf");
    file_context_fp = openfile(outdir,"file_contexts");
    unconfined_fp = openfile(outdir,"unconfined_domains");
    customizable_types_fp=openfile(outdir,"customizable_types");
  }  

 /* print default files */
  include_file(get_base_policy_files()->security_class, policy_fp);
  include_file(get_base_policy_files()->initial_sids, policy_fp);
  include_file(get_base_policy_files()->access_vectors, policy_fp);
  /* print default all attribute */
  declare_attributes(policy_fp);
  /* print initial types */
  declare_initial_types(policy_fp);
  /* print "allow" at least necessary to configuration */
  /* print "socket allow"				     */
  default_allow(policy_fp);


  /*used to sort file_context*/
  TMP_fp = tmpfile();
  if (TMP_fp == NULL){
    fprintf(stderr,"Error opening tmpfile\n");
    exit(1);
  }

  if (domain_hash_table == NULL){
    fprintf(stderr, "bug? domain table is not initialized.\n");
    exit(1);
  }

  /* calculate relationship between file and label. */
  create_file_label_table(domain_hash_table);	
#ifdef DIRSEARCH
	create_dir_label_table(); 
	//	print_dir_label_tab();
#endif


	//	print_file_label_tab();

	modify_rules();

#ifdef DIRSEARCH
	make_dir_list();
#endif

	/* print "type .." of label on files */
	out_file_type(policy_fp);
	out_net_type(policy_fp);

	/* print "allow ..." */
	out_allow(policy_fp,unconfined_fp);

	/* print "domain_auto_trans or domain_trans " */
	out_domain_trans(policy_fp);

	/* print rbac configuration */
 	out_rbac(policy_fp);
	/* print constraints */
	declare_initial_constrains(policy_fp);
	
	/* declare default contexts */
	include_file(get_base_policy_files()->initial_sid_context, policy_fp);
	
	/* include fs_use, genfs_conf */
	include_file(get_base_policy_files()->fs_use, policy_fp);
	include_file(get_base_policy_files()->genfs_context, policy_fp);

	/* print portcon rules */
	out_netcontext(policy_fp);

	/* print file_contexts */
	out_file_contexts_config(file_context_fp);

	/*print customizable_types*/
	out_customizable_types(customizable_types_fp);

#ifdef DEBUG
	//print_user();
#endif
	if(policy_fp!=NULL)
	  fclose(policy_fp);
	if(file_context_fp != NULL)
	  fclose(file_context_fp);
	if(unconfined_fp!=NULL)
	  fclose(unconfined_fp);
	if(customizable_types_fp!=NULL)
	  fclose(customizable_types_fp);
	if(homedir_template_fp!= NULL)
	  fclose(homedir_template_fp);
}

/**
 *  @name:	out_net_type
 *  @about:	print labels of port numbers
 *  @args:	outfp (FILE *) -> output file descripter
 *  @return:	none
 *  @notes:	used_tcp_ports and used_udp_ports is global variable
 */
static void out_port_type(int protocol,FILE *outfp){
  HASH_TABLE *table;
  int num;
  int i;
  char *type;
  HASH_NODE **port_array;
  int portnum;

  if(protocol==NET_TCP){
    table = tcp_port_label_table;
  }else if(protocol == NET_UDP){
    table = udp_port_label_table;
  }else{
    return;
  }

  if(table == NULL)
    return;
  
  port_array= create_hash_array(table);
  num = table->element_num;
  for(i=0;i<num;i++){
    type = port_array[i]->data;
    portnum = atoi(port_array[i]->key);
    if(portnum<1024){
      fprintf(outfp, "type %s ,port_type;\n", type);
    }else{
      fprintf(outfp, "type %s ,port_type,unpriv_port_type;\n", type);
    }
  }
  free(port_array);

}

static void out_node_type(FILE *outfp){
  HASH_TABLE *table;
  int num;
  int i;
  char *type;
  HASH_NODE **node_array;
  table = node_label_table;
  fprintf(outfp,"###Begin of node type declare\n");
  if(table == NULL){
    fprintf(outfp,"###End of node type declare\n");
    return;
  }

  node_array = create_hash_array(table);
  num = table->element_num;
  for(i=0;i<num;i++){
    type = node_array[i]->data;
    fprintf(outfp, "type %s node_type;\n", type);
  }  
  fprintf(outfp,"###End of node type declare\n");


  free(node_array);

}

static void out_net_type(FILE *outfp){
  
  out_port_type(NET_TCP,outfp);
  out_port_type(NET_UDP,outfp);
  out_node_type(outfp);
}


#define MAX_NETLINK_CLASS 256
#define NETLINK_PREFIX "netlink"
void allow_netlink_classes(char *domain,  FILE *outfp){
  char *netlink_class[MAX_NETLINK_CLASS];
  int netlink_class_num = 0; 
  char buf[BUFSIZE];
  char *work;
  FILE *fp;
  char *class = NULL;
  int i;
 
  /*creates lists of classes related to netlink socket*/
  if ((fp=fopen(get_base_policy_files()->security_class,"r")) == NULL)
    {
      fprintf(stderr, "security_classes file open error %s\n", get_base_policy_files()->security_class );
      exit(1);
    }
  
  while (fgets(buf, sizeof(buf), fp) != NULL)
    {
      chop_nl(buf);

      /*syntax of class is "class <class name>"*/
      work = strdup(buf);
      char *classtok = get_nth_tok(work," \t", 1);
      if(classtok == NULL)
	continue;
      if(strcmp(classtok, "class")!=0)
	continue;
      free(work);
      
      class = get_nth_tok(buf," \t", 2);
      if(class == NULL)
	continue;
      
      if(strncmp(class,NETLINK_PREFIX, strlen(NETLINK_PREFIX))==0)
	{
	  if(netlink_class_num>=MAX_NETLINK_CLASS)
	    {
	      fprintf(stderr, "Error: too many classes are declared in security_classes file. modify MAX_NETLINK_CLASS and recompile.\n");
	      exit(1);
	    }
	  /*class is related to netlink*/
	  netlink_class[netlink_class_num] = strdup(class);
	  netlink_class_num ++;
	}
    }    
 
  if(netlink_class_num == 0)
    return;
  
  for(i = 0;i<netlink_class_num;i++){
    fprintf(outfp,"allow %s self:%s *;\n", domain, netlink_class[i]);
    free(netlink_class[i]);
  }
    
  fclose(fp);
  
}

/*Check whether domain |name| exists*/
int check_domainname(char *name){
  char *domain;
  if(strcmp(name,"domain")==0 || strcmp(name,"self")==0){
    return 0;
  }
  domain = make_role_to_domain(name);
  if((DOMAIN *)search_element(domain_hash_table, domain)!=NULL){
    return 0;
  }  
  return -1;
}

static void out_socket_core_rule_one(FILE *outfp, char *protocol_name, DOMAIN *domain, char *target){
  char *name;
  name = domain->name;
  if(check_domainname(target)==0){
    fprintf(outfp,"allow_network_%s_use(%s,%s)\n",protocol_name, name,target);
  }else{
    fprintf(stderr,"Warning. Domain %s does not exist skipped.\n", target);
  }
}

static void out_socket_core_rule(FILE *outfp, NET_SOCKET_RULE rule){
  int num;
  int i;
  char *target;
  DOMAIN *domain ;
  char *name;
  char * protocol_name;
  num = get_ntarray_num(rule.target);
  domain = rule.domain;
  name = rule.domain->name;

  for(i = 0;i<num ;i++){
    target = rule.target[i];
    if(rule.protocol & NET_TCP){
      protocol_name = "tcp";
      out_socket_core_rule_one(outfp, protocol_name, domain,target);
    }
    if(rule.protocol & NET_UDP){
      protocol_name ="udp";
      out_socket_core_rule_one(outfp, protocol_name, domain,target);
    }
    if(rule.protocol & NET_RAW){
      protocol_name = "raw";
      out_socket_core_rule_one(outfp, protocol_name, domain,target);
    }
  }
}



static void out_port_rule_one(FILE *outfp, int protocol, char *domain_name, char *type,int permission){
  if(permission & NET_SERVER && protocol & NET_TCP  ){
    fprintf(outfp,"allow_network_tcp_server(%s,%s)\n",domain_name,type);
  }
  if(permission & NET_SERVER && protocol & NET_UDP  ){
    fprintf(outfp,"allow_network_udp_server(%s,%s)\n",domain_name,type);
  }
  if(permission & NET_CLIENT && protocol & NET_TCP){
    fprintf(outfp,"allow_network_tcp_client(%s,%s)\n",domain_name,type);
  }
  if(permission & NET_CLIENT && protocol & NET_UDP){
    fprintf(outfp,"allow_network_udp_client(%s,%s)\n",domain_name,type);
  }
}


/*find type label for |port| for protocol |protocol|*/
char *get_port_type(char *port, int protocol){
  char *type = NULL;
  HASH_TABLE *label_table =NULL;

  if(strcmp(port, PORT_ALL)==0){
    type ="port_type";
  }else if(strcmp(port, PORT_WELLKNOWN)==0){
    if(protocol==NET_TCP){
      type = "wellknown_tcp_port_t";
    }else{
      type = "wellknown_udp_port_t";
    }
  }else if(strcmp(port, PORT_UNPRIV)==0){
    if(protocol==NET_TCP){
      type = "unpriv_tcp_port_t";
    }else{
      type = "unpriv_udp_port_t";
    }
  }else{
    if(protocol == NET_TCP){
      label_table = tcp_port_label_table;
    }else if(protocol & NET_UDP){
      label_table = udp_port_label_table;
    }
    type = search_element(label_table, port);
    if(type == NULL){
      error_print(__FILE__, __LINE__, "Type for port %s is not found. must be bug\n", port);
      exit(1);
    }
  }
  return type;
}

static void out_port_rule(FILE *outfp, NET_SOCKET_RULE rule){
  int num;
  int j;
  char *port;
  char *type;
  char *domain;
  domain = rule.domain->name;

  if(rule.protocol & NET_TCP || rule.protocol & NET_UDP){/*allownet -tcp|-udp*/
    num = get_ntarray_num(rule.port);
    for(j=0;j<num;j++){
      port = rule.port[j];
      /*obtain type*/
      if(rule.protocol & NET_TCP){
	type = get_port_type(port, NET_TCP);
	out_port_rule_one(outfp, NET_TCP, domain, type,rule.behavior);

      }
      if(rule.protocol & NET_UDP){
	type = get_port_type(port, NET_UDP);
	out_port_rule_one(outfp, NET_UDP, domain, type,rule.behavior);
      }
    }
  }

}

static void out_raw_socket_rule(FILE *outfp, NET_SOCKET_RULE rule){
  char *domain;
  domain = rule.domain->name;
  if(rule.protocol & NET_RAW){
    if(rule.behavior & NET_SERVER){
      fprintf(outfp,"allow_network_raw_server(%s,null)\n",domain);
    }
    if(rule.behavior & NET_CLIENT){
      fprintf(outfp,"allow_network_raw_client(%s,null)\n",domain);
    }
    if(rule.behavior & NET_USE){
      fprintf(outfp,"allow_network_raw_use(%s,domain)\n",domain);
    }
  }
}

/*generate policy for allownet -tcp|-udp|-raw -port rule*/
static void out_net_socket_acl(FILE *outfp, DOMAIN *d){
  NET_SOCKET_RULE rule;
  int i;

  for (i=0; i< d->net_socket_rule_array_num; i++){
    rule = d->net_socket_rule_array[i];
    out_socket_core_rule(outfp,rule);
    out_port_rule(outfp, rule);
    out_raw_socket_rule(outfp,rule);
  }
}

static void out_node_macro(FILE *outfp,NET_NODE_RULE rule, char *type){
  int protocol;
  int permission;
  char *domain;
  protocol = rule.protocol;
  permission = rule.permission;
  domain = rule.domain->name;
  if(rule.type != ALLOW_RULE){
    return;
  }
  
  if(protocol & NET_TCP && permission & NET_SEND)
    fprintf(outfp, "allow_network_node_tcp_send(%s,%s)\n",domain,type);
  if(protocol & NET_TCP && permission & NET_RECV)
    fprintf(outfp, "allow_network_node_tcp_recv(%s,%s)\n",domain,type);
  if(protocol & NET_TCP && permission & NET_BIND)
    fprintf(outfp, "allow_network_node_tcp_bind(%s,%s)\n",domain,type);
  
  if(protocol & NET_UDP && permission & NET_SEND)
    fprintf(outfp, "allow_network_node_udp_send(%s,%s)\n",domain,type);
  if(protocol & NET_UDP && permission & NET_RECV)
    fprintf(outfp, "allow_network_node_udp_recv(%s,%s)\n",domain,type);
  if(protocol & NET_UDP && permission & NET_BIND)
    fprintf(outfp, "allow_network_node_udp_bind(%s,%s)\n",domain,type);
  
  if(protocol & NET_RAW && permission & NET_SEND)
    fprintf(outfp, "allow_network_node_rawip_send(%s,%s)\n",domain,type);
  if(protocol & NET_RAW && permission & NET_RECV)
    fprintf(outfp, "allow_network_node_rawip_recv(%s,%s)\n",domain,type);
  if(protocol & NET_RAW && permission & NET_BIND)
    fprintf(outfp, "allow_network_node_rawip_bind(%s,%s)\n",domain,type);
  
}

static void out_net_node_acl(FILE *outfp, DOMAIN *d){
  NET_NODE_RULE *array;
  NET_NODE_RULE rule;
  int array_num;
  char *type;
  int i;
  int j;

  array = d->net_node_rule_array;
  if(array == NULL){
    return;
  }
  array_num = d->net_node_rule_array_num;

  for(i=0;i<array_num;i++){
    rule = array[i];
    for(j=0;rule.ipv4addr[j]!=NULL ;j++){
      if(strcmp(rule.ipv4addr[j],"*")==0){
	type = "node_type";
      }else{
	type = (char *)search_element(node_label_table, rule.ipv4addr[j]);
      }
      if(type == NULL){
	error_print(__FILE__, __LINE__, "Must be bug.aborted.");
	exit(1);
      }
      out_node_macro(outfp,rule,type);
    }
  }

}

/*generate policy for allownet -tcp|-udp|-raw -netif rule*/
static void out_net_netif_acl(FILE *outfp, DOMAIN *d){
  NET_NETIF_RULE rule;
  int i;
  char *type;
  int j;
  int num;

  for (i=0; i< d->net_netif_rule_array_num; i++){
    rule = d->net_netif_rule_array[i];
    if(rule.type == ALLOW_RULE){
      num = get_ntarray_num(rule.netif);
      for(j=0;j<num;j++){
	if(strcmp(rule.netif[j],"*")==0){
	  type = strdup("netif_type");
	}else{
	  type = joint_str(rule.netif[j],"_t");
	}
	if(rule.permission & NET_SEND && rule.protocol & NET_TCP){
	  fprintf(outfp,"allow_network_netif_tcp_send(%s,%s)\n",d->name, type);
	}
	if(rule.permission & NET_RECV && rule.protocol & NET_TCP){
	  fprintf(outfp,"allow_network_netif_tcp_recv(%s,%s)\n",d->name, type);
	}
	if(rule.permission & NET_SEND && rule.protocol & NET_UDP){
	  fprintf(outfp,"allow_network_netif_udp_send(%s,%s)\n",d->name, type);
	}
	if(rule.permission & NET_RECV && rule.protocol & NET_UDP){
	  fprintf(outfp,"allow_network_netif_udp_recv(%s,%s)\n",d->name, type);
	}
	if(rule.permission & NET_SEND && rule.protocol & NET_RAW){
	  fprintf(outfp,"allow_network_netif_rawip_send(%s,%s)\n",d->name, type);
	}
	if(rule.permission & NET_RECV && rule.protocol & NET_RAW){
	  fprintf(outfp,"allow_network_netif_rawip_recv(%s,%s)\n",d->name, type);
	}
	free(type);
      }
    }
    
  }
}



void out_portcon(FILE *outfp, int protocol){
  HASH_NODE **port_array;
  HASH_TABLE *table;
  int num;
  int i;
  char *type;
  char *number;
  char *protostr=NULL;

  if(protocol==NET_TCP){
    table = tcp_port_label_table;
    protostr = "tcp";
  }else if(protocol == NET_UDP){
    table = udp_port_label_table;
    protostr = "udp";
  }else{
    return;
  }
  if(table == NULL)
    return;
  port_array= create_hash_array(table);
  num = table->element_num;
  for(i=0;i<num;i++){
    type = port_array[i]->data;
    number = port_array[i]->key;
    fprintf(outfp, "portcon %s %s system_u:object_r:%s\n",protostr,number,type);
  }
  free(port_array);

}

void out_netifcon(FILE *outfp){
  char **netif_list;
  char *type;
  int i;
  netif_list = converter_conf.netif_name_list;
  fprintf(outfp, "#Type for NIC\n"); 
  if(netif_list == NULL){
    /* dummy labels: to satisfy syntax  */
    fprintf(outfp, "netifcon lo system_u:object_r:netif_t system_u:object_r:unlabeled_t\n");
    return;
  }
  for(i=0; netif_list[i]!=NULL;i++){
    type = joint_str(netif_list[i],"_t");
    fprintf(outfp, "netifcon %s system_u:object_r:%s system_u:object_r:unlabeled_t\n",netif_list[i],type);
  }  
}

void out_nodecon(FILE *outfp){
  HASH_TABLE *table;
  int num;
  char *type;
  int i;
  char *addr;
  char *netmask;
  char *s;
  char *p;
  HASH_NODE **node_array;

  fprintf(outfp, "#Type for node\n"); 
  if(node_label_table == NULL||node_label_table->element_num==0){
    /* dummy labels: to satisfy syntax  */
    fprintf(outfp, "nodecon 127.0.0.1 255.255.255.255 system_u:object_r:node_t\n");
    return;
  }
  table = node_label_table;
  node_array = create_hash_array(table);
  num = table->element_num;
  for(i=0;i<num;i++){
    type = node_array[i]->data;
    s = strdup(node_array[i]->key);
    p = strchr(s, '/');
    if(p==NULL){
      error_print(__FILE__, __LINE__, "Must be bug.aborted.%s",s);
      exit(1);
    }
    *p ='\0';
    addr = s;
    netmask = p+1;
    fprintf(outfp, "nodecon %s %s system_u:object_r:%s;\n",addr,netmask, type);
    free(s);
  }  

}

/**
 *  @name:	out_netcontext
 *  @about:	print labels about network
 *  @args:	outfp (FILE *) -> output file descripter
 *  @return:	none
 */
void out_netcontext(FILE *outfp){
  
  fprintf(outfp, "####net_contexts\n"); 
	
  out_portcon(outfp,NET_TCP);
  out_portcon(outfp,NET_UDP);
  
  fprintf(outfp,"#Default port number\n");
  fprintf(outfp,"portcon tcp 1-1023 system_u:object_r:wellknown_tcp_port_t\n");
  fprintf(outfp,"portcon udp 1-1023 system_u:object_r:wellknown_udp_port_t\n");
  fprintf(outfp,"portcon tcp 1024-65535 system_u:object_r:unpriv_tcp_port_t\n");
  fprintf(outfp,"portcon udp 1024-65535 system_u:object_r:unpriv_udp_port_t\n");
  out_netifcon(outfp);

  out_nodecon(outfp);
}


/**
 *  @name:	out_one_com_acl
 *  @about:	print "allow" that means "domain_name" is allowed to use "acl"
 *  @args:	outfp (FILE *) -> output file descripter
 *  @args:	domain_name (char *) -> domain name
 *  @args:	acl (COM_ACL_RULE *) -> communication acl rule data
 *  @return:	none
 */
static void
out_one_com_acl(FILE *outfp, DOMAIN *d, COM_ACL_RULE *acl)
{
	int flag;
	char *to_domain = NULL;
	char *prefix = NULL;
	char *domain_name = d->name;
	flag = acl->flag;

	//  to_domain=acl->domain_name;
	if (strcmp(acl->domain_name, "self") == 0){
	  prefix = strdup("dummy");
	  to_domain = strdup(acl->domain_name);
	}else if(strcmp(acl->domain_name,"*")==0){
	  prefix = strdup("dummy");
	  to_domain = strdup("domain");
	}else{
	  prefix = get_prefix(acl->domain_name);
	  to_domain = malloc(strlen(prefix) + 3);
	  sprintf(to_domain, "%s_t", prefix);
	}

	if(check_domainname(to_domain)!=0){
	  fprintf(stderr,"Warning: Target domain %s does not exist for allowcom rule. Skipped.\n", to_domain);
	  return;
	}


	if(flag & UNIX_ACL){
	  fprintf(outfp, "\n#%s and  %s can communicate unix domain \n", domain_name, to_domain);
	  fprintf(outfp, "allow_ipc_unix_common(%s,%s)\n", domain_name, to_domain);
	  if (acl->perm & READ_PRM) {
	    fprintf(outfp, "\n#unix read\n");
	    fprintf(outfp, "allow_ipc_unix_r(%s,%s)\n", domain_name, to_domain);
	  }
	  if(acl->perm & WRITE_PRM){
	    fprintf(outfp, "\n#unix write\n");
	    fprintf(outfp, "allow_ipc_unix_w(%s,%s)\n", domain_name, to_domain);
	  }
	}

	
        if(flag & SEM_ACL){
	  if (acl->perm & READ_PRM){
	    fprintf(outfp, "\n#sem read\n");
	    fprintf(outfp, "allow_ipc_sem_r(%s,%s)\n", domain_name, to_domain);
	  }
	  if(acl->perm & WRITE_PRM){
	    fprintf(outfp, "\n#sem write\n");
	    fprintf(outfp, "allow_ipc_sem_w(%s,%s)\n", domain_name, to_domain);
	  }
	}
		
	if(flag & MSG_ACL){
	  if (acl->perm & READ_PRM){
	    fprintf(outfp, "\n#msg read\n");
	    fprintf(outfp, "allow_ipc_msg_r(%s,%s)\n", domain_name, to_domain);
	  }
	  if (acl->perm & WRITE_PRM){
	    fprintf(outfp, "\n#msg write\n");
	    fprintf(outfp, "allow_ipc_msg_w(%s,%s)\n", domain_name, to_domain);
	  }
	}

	if(flag&MSGQ_ACL){
	  if (acl->perm & READ_PRM){
	    fprintf(outfp, "\n#msgq read\n");
	    fprintf(outfp, "allow_ipc_msgq_r(%s,%s)\n", domain_name, to_domain);
	  }
	  if(acl->perm & WRITE_PRM){
	    fprintf(outfp, "\n#msgq write\n");
	    fprintf(outfp, "allow_ipc_msgq_w(%s,%s)\n",
		    domain_name, to_domain);
	  }
	}

	if(flag& SHM_ACL){
	  if (acl->perm & READ_PRM){
	    fprintf(outfp, "\n#shm read\n");
	    fprintf(outfp, "allow_ipc_shm_r(%s,%s)\n", domain_name, to_domain);
	  }
	  if(acl->perm & WRITE_PRM){
	    fprintf(outfp, "\n#shm write\n");
	    fprintf(outfp, "allow_ipc_shm_w(%s,%s)\n",
		    domain_name, to_domain);
	  }
	}
	
	if(flag&PIPE_ACL){
	  if (acl->perm & READ_PRM){
	    fprintf(outfp, "\n#pipe read\n");
	    fprintf(outfp, "allow_ipc_pipe_r(%s,%s)\n", domain_name, to_domain);
	  }
	  if(acl->perm & WRITE_PRM){
	    fprintf(outfp, "\n#pipe write\n");
	    fprintf(outfp, "allow_ipc_pipe_w(%s,%s)\n", domain_name, to_domain);
	  }
	}


        if(flag== SIG_ACL){
	
	  if(acl->perm & CHID_PRM){
	    fprintf(outfp, "\n#sigchid\n");
	    fprintf(outfp, "allow_signal_sigchld(%s,%s)\n", domain_name, to_domain);
	  }
	  if(acl->perm & KILL_PRM){
	    fprintf(outfp, "\n#sigkill\n");
	    fprintf(outfp, "allow_signal_sigkill(%s,%s)\n", domain_name, to_domain);
	  }
	  if(acl->perm & STOP_PRM) {
	    fprintf(outfp, "\n#sigstop\n");
	    fprintf(outfp, "allow_signal_sigstop(%s,%s)\n", domain_name, to_domain);	
	  }
	  if(acl->perm & NULL_PRM) {
	    fprintf(outfp, "\n#signull\n");
	    fprintf(outfp, "allow_signal_signull(%s,%s)\n", domain_name, to_domain);	
	  }
	  if(acl->perm & OTHERSIG_PRM){
	    fprintf(outfp, "\n#other signals\n");
	    fprintf(outfp, "allow_signal_sigother(%s,%s)\n", domain_name, to_domain);
	  }
	}

	free(prefix);
	free(to_domain);
}

/**
 *  @name:	out_com_acl
 *  @about:	print "allow" from acl_array in DOMAIN structure.
 *  @args:	outfp (FILE *) -> output file descripter
 *  @args:	d (DOMAIN *) -> domain data
 *  @return:	none
 */
static void
out_com_acl(FILE *outfp, DOMAIN *d)
{
	int i;
	COM_ACL_RULE *acl;

	for (i = 0; i < d->com_acl_array_num; i++)
	{
		acl = &(d->com_acl_array[i]);
		out_one_com_acl(outfp, d, acl);
	}
}


/**
 *  @name:	role_to_termlabel
 *  @about:	Convert role name to tty's label name.
 * 		return tty's label by malloc.
 *  @args:	role (char *) -> role name
 *  @return:	terminal role
*/
char *
role_to_termlabel(char *role)
{
	char *tmp;
	char *result;
	int len;
	char tail[] = "_tty_device_t";

	tmp = strdup(role);
	len = strlen(tmp);
	if (len < 2)
	{
		fprintf(stderr, "Invalid rolename %s\n", role);
		exit(1);
	}

	/*chop "_r"*/
	tmp[len-2] = '\0';

	result = (char *)malloc(sizeof(char)*(len+strlen(tail)+1));
	sprintf(result, "%s%s", tmp, tail);

	free(tmp);

	return result;
}

char *
role_to_ptylabel(char *role)
{
	char *tmp;
	char *result;
	int len;
	char tail[] = "_devpts_t";

	tmp = strdup(role);
	len = strlen(tmp);
	if (len < 2)
	{
		fprintf(stderr, "Invalid rolename %s\n", role);
		exit(1);
	}

	/*chop "_r"*/
	tmp[len-2] = '\0';

	result = (char *)malloc(sizeof(char)*(len+strlen(tail)+1));
	sprintf(result, "%s%s", tmp, tail);

	free(tmp);

	return result;
}
/**
 *  @name:	role_to_pts_termlabel
 *  @about:	Convert role name to pty's label name.
 * 		return tty's label by malloc.
 *  @args:	role (char *) -> role name
 *  @return:	role name
 */
char *
role_to_pts_termlabel(char *role)
{
	char *tmp;
	char *result;
	int len;
	char tail[] = "_devpts_t";

	tmp = strdup(role);
	len = strlen(tmp);
	if (len < 2)
	{
		fprintf(stderr, "Invalid rolename %s\n", role);
		exit(1);
	}

	/*chop "_r"*/
	tmp[len-2] = '\0';

	result = (char *)malloc(sizeof(char)*(len+strlen(tail)+1));
	sprintf(result, "%s%s", tmp, tail);

	free(tmp);
	return result;
}

/**
 *  ALLOWTTY ACL
 */
/**
 *  @name:	out_tty_acl
 *  @about:	output tty acl rule
 *  @args:	outfp (FILE *) -> output file descripter
 *  @args:	domain (DOMAIN *) -> domain name
 *  @return	none
 */
static void
out_tty_acl(FILE *outfp, DOMAIN *domain){
  TTY_RULE *t;
  int i;
  char *tty_type = NULL;
  char general_type[] = "{ devtty_t tty_device_t }";
  char global_type[] = "ttyfile";
  char vcs_type[] = "vcs_device_t";

  fprintf(outfp,"\n##TTY configurations \n");
  if (domain->tty_create_flag == 1) {
    /*allowtty -create*/
    fprintf(outfp, "#%s can create its own terminal \n", domain->name);
    fprintf(outfp, "type %s,file_type,ttyfile;\n", role_to_termlabel(domain->name));	
		fprintf(outfp, "allow_tty_create(%s,%s)\n", domain->name, role_to_termlabel(domain->name));	
  }
  
  
  for(i = 0; i < domain->tty_acl_array_num; i++){
    t = &(domain->tty_acl_array)[i];
    
    if (strcmp(t->rolename, "all") == 0){
      /*allowtty global*/
      tty_type=global_type;;
    }else if (strcmp(t->rolename, "general") == 0){
      /*allowtty general*/
      tty_type = general_type;
    }else if(strcmp(t->rolename, "vcs") == 0){
      tty_type = vcs_type;
    }else{
      tty_type = role_to_termlabel(t->rolename);
    }
    
    if (t->perm & READ_PRM) {
      fprintf(outfp, "allow_tty_r(%s, %s)\n", domain->name, tty_type);
    }
    if (t->perm & WRITE_PRM) {
      fprintf(outfp, "allow_tty_w(%s, %s)\n", domain->name, tty_type);
    }
    if (t->perm & CHANGE_PRM) {      
      fprintf(outfp, "allow_tty_change(%s, %s)\n", domain->name, tty_type);
    }
  
  }
}



/**
 *  allowpts
 */
/**
 *  @name:	out_pts_acl
 *  @about:	output pts acl
 *  @args:	outfp (FILE *) -> output file descripter
 *  @args:	domain (DOMAIN *) -> domain data
 *  @return:	none
 */
static void out_pts_acl(FILE *outfp, DOMAIN *domain){
  char *pts_type = NULL;
  char general_type[] = "{ devpts_t ptmx_t }";
  char global_type[] = "ptyfile";
  int i;
  PTS_RULE *p;

  fprintf(outfp, "\n##PTS configurations \n");
  
  /* allowpts -create */
  if (domain->pts_create_flag == 1){
    pts_type = role_to_ptylabel(domain->name);
    fprintf(outfp, "#%s can create its own terminal \n", domain->name);
    fprintf(outfp, "type %s ,file_type,ptyfile;\n", pts_type);
    fprintf(outfp, "allow_pts_create(%s,%s)\n", domain->name, pts_type); 
  }
  
  for(i = 0; i < domain->pts_acl_array_num; i++){
    p = &(domain->pts_acl_array)[i];
    if (strcmp(p->domain_name, "all") == 0){
      /*allowpts global*/
      pts_type=global_type;;
    }else if (strcmp(p->domain_name, "general") == 0){
      /*allowpts general*/
      pts_type = general_type;		  
    }else{
      pts_type = role_to_termlabel(p->domain_name);
    }
    if (p->perm & READ_PRM) {
      fprintf(outfp, "allow_pts_r(%s, %s)\n", domain->name, pts_type);
    }
    if (p->perm & WRITE_PRM) {
      fprintf(outfp, "allow_pts_w(%s, %s)\n", domain->name, pts_type);
    }
    if (p->perm & CHANGE_PRM) {
      fprintf(outfp, "allow_pts_change(%s, %s)\n", domain->name, pts_type);
    }	  
  }
	
}


/*outputs tty_type_change between role/domains */
void out_tty_type_change(FILE *outfp, DOMAIN *domain) {
  HASH_NODE **domain_array;
  int i;
  DOMAIN *d;
  domain_array = create_hash_array(domain_hash_table);
  
  fprintf(outfp, "###allows change tty/pts label\n");
  if (domain->tty_create_flag == 1){
    for (i = 0; i < domain_hash_table->element_num; i++){
      d = (DOMAIN *)domain_array[i]->data;
	if (d->tty_create_flag == 1){
	  fprintf(outfp, "type_change %s %s:chr_file %s;\n", domain->name, role_to_termlabel(d->name), role_to_termlabel(domain->name));
	}
    }
  }

  if (domain->pts_create_flag == 1){
    for (i = 0; i < domain_hash_table->element_num; i++){
      d = (DOMAIN *)domain_array[i]->data;
      if (d->pts_create_flag == 1){
	fprintf(outfp, "type_change %s %s:chr_file %s;\n", domain->name, role_to_pts_termlabel(d->name), role_to_pts_termlabel(domain->name));
	}
    }
  }
}

/*Output implicit dir:search rules*/
/*domain can dir:search for dirs that domain uses(including parent dirs)*/
void out_dir_search(FILE* outfp, DOMAIN *domain){
  HASH_NODE **dir_list_array;
  int num;
  int i;
  char *name;
  FILE_LABEL *label;

  fprintf(outfp,"##Begin of implicit dir:search\n");
  if(domain->dir_list==NULL)
    return;
  
  dir_list_array = create_hash_array(domain->dir_list);
  num = domain->dir_list->element_num;
  
  for(i=0;i<num;i++){
    name = dir_list_array[i]->key;
    label = (FILE_LABEL *)search_element(dir_label_table, name);
    if(label==NULL){		
      error_print(__FILE__, __LINE__, "Must be bug. name:%s\n", name);
      exit(1);
    }
    fprintf(outfp,"allow %s %s:dir search;\n", domain->name, label->labelname);
  }
  fprintf(outfp,"##End of implicit dir:search\n");
}


/*return labels related to path*/
char *tmp_all_types(char *path){
  HASH_NODE **tmp_label_table_array;
  int num;
  char *data;
  char *label;
  int i;
  char *result = NULL;
  char *tmp = NULL;
  int size;

  tmp_label_table_array = create_hash_array(tmp_label_table);
  num = tmp_label_table -> element_num;
  
  for(i=0;i<num;i++){
    label = tmp_label_table_array[i]->key;
    data = tmp_label_table_array[i]->data;
    if(strcmp(data,path) == 0){
      if(result == NULL){
	result = strdup(label);
      }else{
	size = strlen(label)+strlen(result)+2;
	tmp = strdup(result);
	result = (char *)my_realloc(result, size*sizeof(char));
	snprintf(result, size, "%s %s", tmp, label);
	free(tmp);
      }
    }
  }
  
  if(result !=NULL){
    size = strlen(result)+strlen("{ }");
    tmp = strdup(result);
    result = (char *)my_realloc(result, size*sizeof(char));
    snprintf(result, size, "{%s}",tmp);
    free(tmp);
  }

  free(tmp_label_table_array);
  return result;
}

/*output rules for allow <path> exclusive -all <permissions>;*/
void out_tmp_all(FILE *fp, DOMAIN *domain){
  int i;
  TMP_ALL_RULE rule;
  char *types = NULL;
  int devflag;
  for(i=0; i<domain->tmp_all_array_num;i++){
    rule = domain->tmp_all_array[i];
    types = tmp_all_types(rule.path);    
    if(types != NULL){
      fprintf(fp, "#####allow %s exclusive -all\n",rule.path);
      devflag= check_dev_flag(domain, rule.path);
      print_file_allow(domain, types, devflag, rule.allowed, fp);
      free(types);
    }
  } 

  return;
}

/*output rules related to allowfs <fs> <permissions>;*/
void out_fs_acl(FILE *fp, DOMAIN *domain){
  int i;
  FS_RULE rule;
  char *type = NULL;
  char suffix[] = "_t";
  int len;
  int devflag=0;
  fprintf(fp, "##allowfs rule\n");
  for(i = 0; i<domain->fs_rule_array_num; i++){
    rule = domain->fs_rule_array[i];
    len = strlen(rule.fs) + strlen(suffix);

    if(strcmp(rule.fs,"proc_pid_self")==0){
      type = strdup("self");
      fprintf(fp, "#Can access /proc/pid/self\n");
    }else if(strcmp(rule.fs,"proc_pid_other")==0){
      type =strdup("global");
      fprintf(fp, "#Can access /proc/pid/<other processes>\n");
    }else{
      type =(char *) my_malloc(len + 1);
      snprintf(type, len + 1 ,"%s%s",rule.fs,suffix);
      fprintf(fp, "#Can access %s filesystem.\n", rule.fs);
    }
    devflag = check_dev_flag(domain, rule.fs);
    //    printf("#??%s,%d\n", rule.fs, devflag);
    print_file_allow(domain, type, devflag, rule.allowed, fp);    
    free(type);
  }

  fprintf(fp, "##end of allowfs rule\n");
}

/*output rules related to allowfs exclusive*/
void out_fs_trans_acl(FILE *fp, DOMAIN *domain){
  int i;
  FS_TMP_RULE rule;
  char *domain_name;
  char *entrypoint;
  domain_name = domain->name;
  
  
  fprintf(fp, "##allowfs exclusive rule\n");
  for(i = 0; i<domain->fs_tmp_rule_array_num; i++){
    rule = domain->fs_tmp_rule_array[i];
    fprintf(fp,"#file type trans in %s filesystem\n",rule.fs);
    entrypoint = joint_str(rule.fs, "_t");
    fprintf(fp, "file_type_auto_trans(%s, %s, %s)\n", domain_name, entrypoint, rule.name);
    free(entrypoint);
  }
  fprintf(fp, "##end of allowfs exclusive rule\n");
}




/*output rules related to allowkernel,allowpriv,allowsepol*/
void out_adm_other_acl(FILE *fp, DOMAIN *domain){
  int i;
  ADMIN_OTHER_RULE rule;
  
  fprintf(fp, "##allowpriv rule\n");
  for(i = 0; i<domain->admin_rule_array_num; i++){
    rule = domain->admin_rule_array[i];
    if(rule.deny_flag==1){
      continue;
    }
    fprintf(fp, "allow_admin_%s(%s)\n", rule.rule, domain->name);
    
  }
  fprintf(fp, "##end of allowpriv rule\n");
  /*allowpriv part_relabel is in out_file_acl.c*/
  

}


/**
 *  @name:	out_acls
 *  @about:	print all "allow"
 *  @args:	outfp (FILE *) -> output file descripter
 *  @args:	domain (DOMAIN*) -> domain data
 *  @return:	none
 */
static void
out_acls(FILE *outfp, DOMAIN *domain)
{

        out_file_acl(outfp, domain);
#ifdef DIRSEARCH
	out_dir_search(outfp,domain);
#endif
	out_tmp_all(outfp,domain);
	out_net_socket_acl(outfp,domain);
	out_net_netif_acl(outfp,domain);
	out_net_node_acl(outfp,domain);
	out_com_acl(outfp, domain);
	out_tty_acl(outfp, domain);
	out_pts_acl(outfp, domain);
	out_tty_type_change(outfp, domain);
	out_fs_acl(outfp, domain);
	out_fs_trans_acl(outfp, domain);
	out_adm_other_acl(outfp, domain);
	
}

/**
 *  @name:	out_one_role
  *		print "type" based on USER_ROLE structure
 *  @return:	none
 */
static int
out_one_role_types(FILE *rbac_out, RBAC *rbac,char *domain)
{

	HASH_NODE **rbac_array;
	RBAC *element;
	char *rname;
	char *dname;
	int num;
	int i;
	char *ng_domain[MAX_ROLE];
	int ng_domain_num = 0;
	for(i=0;i<MAX_ROLE;i++)
	  ng_domain[i] = NULL;
	
	rbac_array = create_hash_array(rbac_hash_table);
	num = rbac_hash_table->element_num;


	/* this prohibit login with unrelated type */
	for (i = 0; i <num; i++)
	{
		element = (RBAC *)rbac_array[i]->data;
		rname = element->rolename;
		dname = element->default_domain->name;

		if (strcmp(rbac->rolename, rname) == 0)
		{
			continue;
		}
		ng_domain[ng_domain_num] = dname;
		ng_domain_num ++;
		if(ng_domain_num == MAX_ROLE){
		  fprintf(stderr, "too many roles modify MAX_ROLE and recompile\n");
		  exit(1);
		}
	}
	

	/* if(domain is not other roles's domain), output role types*/
	for(i=0;i<ng_domain_num;i++){
	  if(strcmp(ng_domain[i], domain) == 0){
	    free(rbac_array);
	    return 0;
	  }
	}
	
	fprintf(rbac_out, "role %s types %s;\n", rbac->rolename, domain);
	
	free(rbac_array);
	
	return 0;
}


static int
out_sysadm_r_types(FILE *rbac_out, char *domain)
{

	HASH_NODE **rbac_array;
	RBAC *element;
	char *rname;
	char *dname;
	int num;
	int i;
	char *ng_domain[MAX_ROLE];
	int ng_domain_num = 0;
	for(i=0;i<MAX_ROLE;i++)
	  ng_domain[i] = NULL;
	
	rbac_array = create_hash_array(rbac_hash_table);
	num = rbac_hash_table->element_num;


	/* this prohibit login with unrelated type */
	for (i = 0; i <num; i++)
	{
		element = (RBAC *)rbac_array[i]->data;
		rname = element->rolename;
		dname = element->default_domain->name;
		ng_domain[ng_domain_num] = dname;
		ng_domain_num ++;
		if(ng_domain_num == MAX_ROLE){
		  fprintf(stderr, "too many roles modify MAX_ROLE and recompile\n");
		  exit(1);
		}
	}
	

	/* if(domain is not other roles's domain), output role types*/
	for(i=0;i<ng_domain_num;i++){
	  if(strcmp(ng_domain[i], domain) == 0){
	    free(rbac_array);
	    return 0;
	  }
	}
	
	
	free(rbac_array);
	
	return 0;
}

int is_role_domain(char *domain){
  char *role;
  int i;

  int num; 
  HASH_NODE **rbac_array;
  if(rbac_hash_table == NULL)
    return 0;
  role = make_domain_to_role(domain);
  rbac_array = create_hash_array(rbac_hash_table);
  if(rbac_array == NULL)
    return 0;
  num = rbac_hash_table->element_num;
  for (i = 0; i <num; i++){
    if(strcmp(role, ((RBAC *)rbac_array[i]->data)->rolename)==0)
      return 1;
  }
  free(rbac_array);
  free(role);
  return 0;
}


void out_role_types(FILE *fp, char *domain){
  HASH_NODE **rbac_array;
  int num;
  int i;
  if (is_role_domain(domain)){
    ;
  }else{
    fprintf(fp, "role system_r types %s;\n",  domain);
  }
  if(rbac_hash_table == NULL)
    return;
  rbac_array = create_hash_array(rbac_hash_table);
  if(rbac_array == NULL)
    return;
  num = rbac_hash_table->element_num;
  for (i = 0; i <num; i++){
    out_one_role_types(fp, (RBAC *)rbac_array[i]->data, domain);
  }
  out_sysadm_r_types(fp, domain);

  free(rbac_array);
}

/*If domain is unconfined domain return 1*/
int check_unconfined(DOMAIN *domain){
  ADMIN_OTHER_RULE *array;
  int array_num;
  int i;
  array = domain->admin_rule_array;
  array_num = domain->admin_rule_array_num;

  for(i=0;i<array_num;i++){
    if(array[i].deny_flag==0 && strcmp(array[i].rule,"all")==0){
      return 1;
    }
  }
  return 0;
}

/**
 *  @name:	out_allow
 *  @about:	print "allow"
 *  @args:	outfp (FILE *) -> output file descripter
 *  @return:	none
 */

void
out_allow(FILE *outfp,FILE *unconfined_fp)
{
	HASH_NODE **domain_array;
	DOMAIN *domain;
	int i;
	char *prefix=NULL;

	domain_array = create_hash_array(domain_hash_table);

	/****************"allow" of normal domain***************************/

	for (i = 0; i < domain_hash_table->element_num; i++)
	{
		domain = (DOMAIN *)domain_array[i]->data;

		/* Don't print dummy domain */
		if (strcmp(domain->name, DUMMY_DOMAIN_NAME) == 0)
			continue;

		fprintf(outfp, "###########################\n");
		fprintf(outfp, "############## %s domain\n", domain->name);

		/* declaration of domain */
		if(check_unconfined(domain)){
		  fprintf(unconfined_fp,"%s\n",domain->name);
		  if(check_exist_in_list(domain->name,converter_conf.authentication_domain)){
		    fprintf(outfp, "type %s,domain;\n", domain->name);
		    
		  }else{
		    fprintf(outfp, "type %s,domain,unconfined_domain;\n", domain->name);
		  }
		}else{
		  fprintf(outfp, "type %s,domain;\n", domain->name);
		}

		if(domain->program_flag){
		  prefix = get_prefix(domain->name);
		  fprintf(outfp,"bool %s_disable_trans false;\n",prefix);
		  free(prefix);
		}
		
		/* print "role x types domain->name" */
		out_role_types(outfp, domain->name);

		/* print acl */
		out_acls(outfp, domain);

		fprintf(outfp, "\n##### endof %s domain\n\n\n", domain->name);

	}
	free(domain_array);
}

/**
 *  @name:	free_all_objets
 *  @about:	free all (domain file-label domain trans) objects
 *  @args:	none
 *  @return:	none
 */
void
free_all_objects()
{
	free_rbac_hash_table();
	free_user_hash_table();
	free_domain_tab();
	delete_file_label_tab();
	free_domain_trans();
}


/*delete admin_rule_array from global and add individual domains*/
void modify_priv_rule(){
  DOMAIN *domain;
  HASH_NODE **domain_array;
  int i;
  int j;
  ADMIN_OTHER_RULE work;
  char **denied_rule=NULL;

  domain_array = create_hash_array(domain_hash_table);
  for (i = 0; i < domain_hash_table->element_num; i++){
    domain = (DOMAIN *)domain_array[i]->data;
    /*get denied rule*/
    for(j =0; j<domain->admin_rule_array_num; j++){
      work = domain->admin_rule_array[j];
      if(work.deny_flag==1){
	denied_rule = extend_ntarray(denied_rule,work.rule);
      }
    }
    /*if denypriv is described, set deny_flag*/
    for(j =0; j<domain->admin_rule_array_num; j++){
      work = domain->admin_rule_array[j];
      if(ntarray_check_exist(denied_rule, work.rule)==1){
	work.deny_flag=1;
	domain->admin_rule_array[j]=work;
      }	
    }
    free_ntarray(denied_rule);
    denied_rule=NULL;
  }
}


/*
If |user| roles role other  than |role|
return 1
*/
int user_roles_other_role(char *user, char *role){
  USER_ROLE *user_role;
  char **role_array;
  int array_num;
  int i;
  user_role = (USER_ROLE *)search_element(user_hash_table, user);

  if(user_role == NULL)
    return 0;
  
  role_array = user_role->role_name_array;
  array_num = user_role->role_name_array_num;
  
  for(i=0;i<array_num;i++){
    if(strcmp(role, role_array[i])!=0)
      return 1;
  }
  return 0;
}

void append_homedir_rule_to_domain(DOMAIN *domain, FILE_ACL_RULE rule, char **home_prefix_list){
  
  char *path;
  int i;
  char *user;
  char *role;
  if(home_prefix_list==NULL||rule.path[0]!='~')
    return;
  
  for(i=0; home_prefix_list[i]!=NULL;i++){
    if(domain->roleflag == 0){/*Normal domain*/
      path = joint_str(home_prefix_list[i],rule.path+1);
      append_file_rule(domain->name, path, rule.allowed, rule.state);   
      free(path);
    }else{/*Role */
      path = joint_str(home_prefix_list[i],rule.path+1);
      user = get_user_from_path(path,converter_conf.homedir_list);
      if(user == NULL){
	free(path);
	continue;
      }
      role = make_domain_to_role(domain->name);
      if(user_roles_other_role(user, role)){
	;
      }else{
	append_file_rule(domain->name, path, rule.allowed, rule.state);
      }
      /*
	if domain->roleflag == 1
	user = get user from path(path)
	user_role = (USER_ROLE *)search_element(user_hash_table, user);
	check whether user is used in other role
	If used in other role
	do nothing
	else
	append_file_rule
      */   
      free(path);
      free(user);
      free(role);
    }
    

   }
  
}

/*
if rules that begin from ~/<path>, 
add /home/username/<path> rules.
*/
void append_homedir_rule(){
  char **homedir_list;
  char **user_list;
  char **home_prefix_list = NULL;/*list of str(homedir_list + user_list)*/
  char *prefix;
  int i,j;
  DOMAIN *domain;
  HASH_NODE **domain_array;
  FILE_ACL_RULE rule;
  int rule_num_orig;

  homedir_list = converter_conf.homedir_list;
  user_list = g_file_user_list;
  if(homedir_list == NULL || user_list == NULL)
    return;

  /*make home_prefix_list  */
  for(i=0 ; homedir_list[i]!=NULL ;i++){
    for(j=0; user_list[j]!=NULL;j++){
      prefix = joint_3_str(homedir_list[i],"/", user_list[j]);
      home_prefix_list = extend_ntarray(home_prefix_list,prefix);
      free(prefix);
    }
  }
  
 
  domain_array = create_hash_array(domain_hash_table);

  for (i = 0; i < domain_hash_table->element_num; i++){
    domain = (DOMAIN *)domain_array[i]->data;
    rule_num_orig = domain->file_rule_array_num;
    for(j=0; j<rule_num_orig; j++){
      rule = domain->file_rule_array[j];
      if(rule.path[0]=='~'){
	append_homedir_rule_to_domain(domain, rule, home_prefix_list);
      }
    }
  }
}

/*
remove rules from global domain and add individual domains
It is neccesary to resolve "deny" rules
*/
void modify_rules(){
  	/**
	 *  find "access right to some file of global">"access right to some file of domain"
	 *  and convert such access rights to "access right to some file of global"<"access
	 *  right to some file of domain"
	 */
	modify_priv_rule();

}

void register_dirs(DOMAIN *domain, char **dir_list){
  HASH_TABLE *dirshash;
  int i;
  int s;
  int r;
  struct stat buf;
  dirshash = domain->dir_list;  
  if (dirshash ==NULL){
    dirshash = create_hash_table(FILE_ACL_TABLE_SIZE);
    if (dirshash == NULL){
      yyerror("memory shortage\n");
      exit(1);
    }
  }
  domain -> dir_list = dirshash;
  for(i=0;dir_list[i]!=NULL;i++){
    memset(&buf,0,sizeof(buf));
    r=stat(dir_list[i],&buf);
    if(r==0 && S_ISDIR(buf.st_mode)){
      s = insert_element(dirshash, "1", dir_list[i]);  
      if(s==-2){
	;
      }else if(s<0){
	fprintf(stderr, "system error in line %d\n", __LINE__);
	exit(1);
      }
    }
  }  
}

/*for each domain, make dir_list hash table*/
void make_dir_list(){
  HASH_NODE **domain_array;
  FILE_ACL_RULE *acl_array;
  int i;
  FILE_ACL_RULE acl;
  int j;
  char **dir_list;
  DOMAIN *domain;

  domain_array = create_hash_array(domain_hash_table);
  for (i = 0; i < domain_hash_table->element_num; i++){
    domain = (DOMAIN *)domain_array[i]->data;
    if(domain->file_rule_array == NULL)
      continue;
    acl_array = domain->file_rule_array;
    for(j = 0; j<domain->file_rule_array_num;j++){
      acl = acl_array[j];
     
      if(acl.allowed!=DENY_PRM){
	dir_list = get_dir_list(acl.path, converter_conf.homedir_list);
	if(dir_list!=NULL){
	  register_dirs(domain, dir_list);
	}
      }
    }
  }
}

char *get_disable_trans_boolean_name(char *domain){
  char *prefix;
  char *result;
  prefix = get_prefix(domain);
  result= joint_str(prefix,"_disable_trans");
  return result;
}

int check_disable_trans_boolean_defined(char *to_domain){
  DOMAIN *d;
  d =  (DOMAIN *)search_element(domain_hash_table, to_domain);
  if(d==NULL){
    error_print(__FILE__, __LINE__, "Must be bug\n");
    exit(1);
  }
  if(d->program_flag)
    return 1;

  return 0;
}

void out_domain_trans_child_dir(FILE *, TRANS_RULE *, char *);

/**
 *  @name:	out_domain_trans
 *  @about:	print domain_trans by using rulebuf
 *  @args:	outfp (FILE *) -> output file descripter
 *  @return:	none
 *  @notes:	rulebuf is global variable
 */
void out_domain_trans(FILE *outfp){
  int i;
  TRANS_RULE t;
  FILE_LABEL *label;
  char *name;/*domain name*/
  int len;
  int disable_trans_defined=0;
  char *boolean_name=NULL;
  /* print domain_auto_trans */
  for (i = 0; i < domain_trans_rule_num; i++){
    /* search target path's file label */
    t = rulebuf[i];
    disable_trans_defined = check_disable_trans_boolean_defined(t.child);
    if(disable_trans_defined){
      boolean_name = get_disable_trans_boolean_name(t.child);
      fprintf(outfp,"if(%s){}else{\n",boolean_name);
      free(boolean_name);
    }


    name = strdup(t.parent);
    len = strlen(name);	
    /* convert "_r" to "_t" */
    if(strcmp(name,"unconfined_domain")!=0){
      if (len < 2){
	fprintf(stderr, "bug line %d\n", __LINE__);
      }
      name[len-1] = 't';
    }
       
    if(strcmp(name,"unconfined_domain")==0){
      ;
    }else if(search_element(domain_hash_table, name) == NULL){
      fprintf(stderr, "Warning: domain %s does not exists for \"domain_trans %s %s\" rule. Skipped.\n", name, t.parent,t.path);
      continue;
    }else if(search_element(domain_hash_table, t.child) == NULL){
      error_print(__FILE__, __LINE__, "bug! Aborted");
      exit(1);
    }

    if(t.path == NULL){
      /*dynamic transition rule*/
      fprintf(outfp, "domain_dyn_trans(%s,%s)\n", name, t.child);
      continue;
    }

    label = search_element(file_label_table, t.path);
    if (label == NULL){
      fprintf(stderr, "bug line %d\n", __LINE__);
      exit(1);
    }
    if (t.auto_flag == 1){
      fprintf(outfp, "domain_auto_trans(%s,%s,%s)\n", name,label->labelname, t.child);
      label = search_element(dir_label_table, t.path);
      if(label)
	fprintf(outfp, "domain_auto_trans(%s,%s,%s)\n", name,label->labelname, t.child);


    } else {
      fprintf(outfp, "domain_trans(%s,%s,%s)\n", name, label->labelname, t.child);
      label = search_element(dir_label_table, t.path);
      if(label)
	fprintf(outfp, "domain_trans(%s,%s,%s)\n", name, label->labelname, t.child);
    }
    
    
    /*
     * when entry point is directory(<dir>/ * or <dir>/ **) and a file under the directory is labeled,
     * then output domain_auto_trans for label of the file.
     */ 
    out_domain_trans_child_dir(outfp, &t,name);

    free(name);
    if(disable_trans_defined){
      /*close if(_disable_trans){}else{q*/
      fprintf(outfp,"}\n");
    }


  }
}

/**
 *  @name:	out_domain_trans_child_dir
 *  @about:	print domain_trans by using rulebuf
 * 		attention:wildcard isn't supported,the program of the same name isn't supported.
 *  @args:	outfp (FILE *) -> output file descripter
 *  @return:	none
 *  @notes:	rulebuf is global variable
 */
void out_domain_trans_child_dir(FILE *outfp, TRANS_RULE *t, char *domain_name){
	FILE_LABEL *label;
	HASH_NODE **file_label_array;	
	HASH_NODE **dir_label_array;

	int i;
	if(t->state ==  FILE_ITSELF){
	  return;
	}
	file_label_array = create_hash_array(file_label_table);

	for (i = 0; i < file_label_table->element_num; i++){
	  label = (FILE_LABEL *)file_label_array[i]->data;
	  if(t->state == FILE_DIRECT_CHILD){
	    if (chk_child_file(t->path, label->filename) == 1){
	      fprintf(outfp, "domain_auto_trans(%s,%s,%s)\n", domain_name, label->labelname, t->child);
	    }
	  }
	  if(t->state == FILE_ALL_CHILD){
	    if(chk_child_dir(t->path,label->filename)==1){
	      fprintf(outfp, "domain_auto_trans(%s,%s,%s)\n", domain_name, label->labelname, t->child);
	    }
	  }
	}
	dir_label_array = create_hash_array(dir_label_table);
	
	for (i = 0; i < dir_label_table->element_num; i++){
	  label = (FILE_LABEL *)dir_label_array[i]->data;
	  if(t->state == FILE_DIRECT_CHILD){
	    if (chk_child_file(t->path, label->filename) == 1){
	      fprintf(outfp, "domain_auto_trans(%s,%s,%s)\n", domain_name, label->labelname, t->child);
	    }
	  }
	  if(t->state == FILE_ALL_CHILD){
	    if(chk_child_dir(t->path,label->filename)==1){
	      fprintf(outfp, "domain_auto_trans(%s,%s,%s)\n", domain_name, label->labelname, t->child);
	    }
	  }
	}
	

	free(file_label_array);
}

/**
 *  Global variable
 */
static FILE *rbac_out;

/**
 *  @name:	out_one_user_role
 *  @about:	print "user" based on USER_ROLE structure
 *  @args:	u (void *) -> user data
 *  @return:	none
 */
static int
out_one_user_role(void *u)
{
	USER_ROLE *ur;
	int i;
	int max;
	char **str_a;

	ur = (USER_ROLE*)u;
	max = ur->role_name_array_num;
	str_a = ur->role_name_array;

	fprintf(rbac_out, "user %s roles {", ur->username);

	for (i = 0; i < max; i++)
	{
		fprintf(rbac_out, " %s ", str_a[i]);
	}
	
	fprintf(rbac_out,"system_r };\n");

	return 0;
}

/**
 *  @name:	out_role_allow
 *  @about:	print role allow
 *  @args:	u (void *) -> user data
 *  @return:	none
 */
static int
out_role_allow(void *u)
{
	RBAC *rbac;
	HASH_NODE **rbac_array;
	RBAC *element;
	char *rname;
	int num;
	int i;

	rbac = u;
	rbac_array = create_hash_array(rbac_hash_table);
	num = rbac_hash_table->element_num;

	for (i = 0; i < num; i++)
	{
		element = (RBAC *)rbac_array[i]->data;
		rname = element->rolename;
		fprintf(rbac_out, "allow %s %s;\n", rbac->rolename, rname);
	}

	free(rbac_array);

	return 0;
}




/*outputs role system_r types ~{<domains related to other roles>}*/
void out_system_r_rbac(HASH_TABLE *t)
{
  HASH_NODE **rbac_array;
  int num;
  rbac_array = create_hash_array(t);
  num = t->element_num;
  char *rname;
  char *dname;
  int i;
  RBAC *element;

  /* this prohibit login to display selection of system_r */
  fprintf(rbac_out, "role system_r types ~{");
  for (i = 0; i <num; i++)
    {
      element = (RBAC *)rbac_array[i]->data;
      rname = element->rolename;
      dname = element->default_domain->name;
      fprintf(rbac_out," %s ", dname);
    }
  fprintf(rbac_out,"};\n");
  free(rbac_array);
}

/**
 *  @name:	out_one_role
 *  @about:	called by handle_all_element
 *		print role transition
 *  @args:	u (void *) -> user data
 *  @return:	none
 */
static int
out_one_role(void *u)
{
	RBAC *rbac;
	char *tmp;
	int len;
	FILE_LABEL *label;

	rbac = u;

	tmp = strdup(rbac->rolename);
	/* allow role transition */
	fprintf(rbac_out, "allow system_r %s;\n", rbac->rolename);
	fprintf(rbac_out, "allow %s system_r;\n", rbac->rolename);
	/* allow role transition at /etc/init.d */
	label = search_element(file_label_table, INITRC_DIR);
	if (label == NULL)
	{
	    fprintf(stderr, "Warning: no label found for /etc/rc.d/init.d\n");
	}else
	{
	   // fprintf(rbac_out, "role_transition %s %s system_r;\n", rbac->rolename, label->labelname);
	  //  fprintf(rbac_out, "role_transition %s bin_su_t system_r;\n", rbac->rolename);

	}
	
	/* chop "_r" */
	len = strlen(tmp);
	if ( len < 2)
	{
		fprintf(stderr, "Invalid rolename %s\n", tmp);
		exit(1);
	}
	tmp[len-2] = '\0';
	//  fprintf(rbac_out, "user_tty_domain(%s)\n", tmp);

	free(tmp);

	return 0;
}

/**
 *  @name:	out_rbac
 *  @about:	print rbac rule
 *  @args:	outfp (FILE *) -> output file descripter
 *  @return:	none
 */
static void
out_rbac(FILE *outfp)
{
	rbac_out = outfp;

	fprintf(rbac_out, "\n#RBAC related configration\n");


	if (rbac_hash_table == NULL){
	  fprintf(rbac_out, "user system_u roles system_r;\n");
	  fprintf(rbac_out, "user user_u roles { system_r };\n");
	  return;
	}
	/*print role system_r ..*/
	//out_system_r_rbac(rbac_hash_table);

	/* print "role transition" */
	handle_all_element(rbac_hash_table, out_one_role);
	
	/* print allow <role> <role>; */
	 handle_all_element(rbac_hash_table, out_role_allow);

	/* print "user" */
	fprintf(rbac_out, "user system_u roles system_r;\n");
	fprintf(rbac_out, "user user_u roles { system_r };\n");
	handle_all_element(user_hash_table, out_one_user_role);


	
}


