/*
 * All Rights Reserved, Copyright (C) 2003, Hitachi Software Engineering Co., Ltd.
 */
/* $Id: initial_policy.h,v 1.1.1.1 2006/02/23 22:04:56 ynakam Exp $ */

#ifndef INITIAL_POLICY_H
#define INITIAL_POLICY_H


#define SECURITY_CLASS_FILE		"security_classes"
#define INITIAL_SIDS_FILE		"initial_sids"
#define INITIAL_SID_CONTEXT_FILE	        "initial_sid_contexts"
#define FS_USE_FILE			"fs_use"
#define GENFS_CONTEXT_FILE		"genfs_contexts"
#define ACCESS_VECTORS_FILE		"access_vectors"
#define DEFAULT_TE_FILE                 "default.te"
#define TYPES_FILE                      "types.te"
#define ATTRIBUTE_FILE                   "attribute.te"
#define CONVERTER_CONF_FILE                   "converter.conf"
#define DEFAULT_BASE_POLICY_DIR          "base_policy"
#define UNSUPPORTED_TE_FILE                   "unsupported.te"


/*struct to store full path file name for base policy files*/
typedef struct basepolicy_t{
  char * security_class;
  char * initial_sids;
  char * initial_sid_context;
  char * fs_use;
  char * genfs_context;
  char * access_vectors;
  char * default_te;
  char * unsupported_te;
  char * types_te;
  char * attribute_te;
  char * converter_conf;
} BASEPOLICY;



#define CONTEXT_LEN			64
#define USER_LEN			64
#define ROLE_LEN			64
#define TYPE_LEN			64

/**
 *  structure for containing sid contexts
 */
typedef struct context_t
{
	char		context[CONTEXT_LEN];
	char		user[USER_LEN];
	char		role[ROLE_LEN];
	char		type[TYPE_LEN];
}	CONTEXT;

int include_file(char *f, FILE *);
void declare_initial_types(FILE *);
void declare_initial_roles(FILE *);
void declare_initial_users(FILE *);
void declare_initial_constrains(FILE *);
void declare_attributes(FILE *);
void test_allow(FILE *);
void default_allow(FILE *);
void register_initial_types();
void parse_genfscon(char *);
void set_base_policy_files(char *);
BASEPOLICY *get_base_policy_files();
void free_base_policy_files();
void parse_converter_conf();
char **get_rulename_list();
#endif
