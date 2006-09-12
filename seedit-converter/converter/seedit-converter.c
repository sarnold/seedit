/*
#! SELinux Policy Editor, a simple editor for SELinux policies
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
#include <unistd.h>
#include "action.h"
#include "convert.h"
#include "initial_policy.h"
#include "security_class.h"
#include "preprocess_include.h"

extern FILE *yyin;
extern int yyparse(void);

#define DEFAULT_INFILE		"test.conf"
#define DEFAULT_POLICY		"policy.conf"
#define DEFAULT_FILE_CONTEXT	"file_context"

const char usage[]= "Usage : seedit-converter -i <infile> -b <base policy dir> -o <output dir> \n";


int main(int argc, char **argv){
  char *outdir=NULL;
  char *basedir = NULL;
  char *include_dir =NULL;
  int ch;
  FILE *tmp;
  FILE *input=stdin;

  if (argc == 1)	{
    fprintf(stderr, "%s\n", usage);
    exit(1);
  }

  while ((ch = getopt(argc, argv, "po:i:b:I:")) != EOF){
    switch (ch){
    case 'o':
      outdir = strdup(optarg);
      break;

    case 'i':
      if ((input = fopen(optarg, "r")) == NULL){
	perror(optarg);
	exit(1);
      }	
      break;
			

    case 'b':		  
      if (optarg == NULL){
	basedir = DEFAULT_BASE_POLICY_DIR;
      }else{
	basedir = optarg;
      }
      set_base_policy_files(basedir);
      break; 

    case 'I':
      include_dir = strdup(optarg);
      break;


    default:
      fprintf(stderr, "%s\n", usage);
      exit(1);
      break;
    }
  }
  if(basedir == NULL){ 
    basedir = DEFAULT_BASE_POLICY_DIR;
    set_base_policy_files(basedir);	  
  }
  
  tmp = tmpfile();
  if (!tmp) {
    fprintf(stderr,"Error opening tmpfile\n");
    exit(1);
  }
  
  /*do preprocess */
  preprocess_include(input, tmp,include_dir);
  rewind(tmp);
  yyin = tmp;

  /* create hash table for label table */
  defined_label_table = create_hash_table(LABEL_LIST_SIZE);
  
  /* initialize default class arrray */
  init_classes(get_base_policy_files()->security_class);
  
  parse_converter_conf();
  
  if (yyparse() != 0)
    exit(1);
 
  register_dummy_home_rule();
  append_homedir_rule();
  
  /* convert SPDL to SELinux configuration language */
  convert(outdir);
  

#if 0
  free_all_objects();
#endif
  fclose(tmp);
  return 0;
}
