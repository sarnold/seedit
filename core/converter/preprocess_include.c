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
/*
Preprocess "include" element
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "preprocess_include.h"
#include <seedit/common.h>

static char source_file[255];
int source_lineno;


/*if include is found , return included str*/
char *check_include(char *line){
  char *p;
  char *tmp;
  tmp = strdup(line);
  chop_nl(tmp);
  p = strtok(tmp, " ");
  if(p != NULL){
    if(strcmp(p, "include")==0){
	p = strtok(NULL ," ");
	free(tmp);
	return strdup(p);
    }
  }
  free(tmp);
  return NULL;
}

void do_include(FILE *output, char *incstr, char *include_dir, int lineno,int nest){
  char *filename;
  char *tmp;
  FILE *fp;
  char buf[INPUTBUF];
  char *p;
  int inc_lineno=0;

  if(incstr == NULL){
    fprintf(stderr, "In line:%d, Syntax Error.\n", lineno);
    exit(1);
  }
  
  chop_nl(incstr);
  chop_char(incstr, ';');

  tmp = joint_str(include_dir,"/");
  filename = joint_str(tmp, incstr);

  free(tmp);


  if ((fp=fopen(filename,"r")) == NULL){
    fprintf(stderr, "Error: Include file open error %s, LINE %d\n", filename,lineno);
    exit(1);
  }


  fprintf(output, "#line 1 \"%s\"\n",filename);

  while (fgets(buf, sizeof(buf), fp) != NULL){
    inc_lineno++;
    if((p = check_include(buf))!=NULL){
      nest ++;
      do_include(output,p,include_dir,lineno,nest);
      fprintf(output, "#line 1 \"%s\"\n",filename);
      fprintf(output, "#line %d\n",inc_lineno+2);
    }else{
      fprintf(output, "%s", buf);
    }
  }

  if(nest==0){
    if(source_file){
      fprintf(output, "#line 1 \"%s\"\n",source_file);
      fprintf(output, "#line %d\n",source_lineno);
    }
  }

  fclose(fp);
}

void preprocess_include(FILE *input, FILE *output,char *include_dir){
  int lineno = 0;
  int len;
  char buf[INPUTBUF];
  char *p;
  char lineno_str[]="#line 1 ";
  int lineno_str_len ;


  lineno_str_len = strlen(lineno_str);

  if (include_dir == NULL){
    include_dir = ".";
  }

  while (fgets(buf, sizeof(buf), input)!=NULL){
    if(strncmp(buf,lineno_str,lineno_str_len)==0){
      source_lineno=1;
      strncpy(source_file, buf+9, 255); 
      source_file[strlen(source_file)-1] = '\0';
    }

    len = strlen(buf);
    if(strchr(buf,'\n')){
      lineno ++;
      source_lineno++;
    }

    if (len == sizeof(buf)-1){
      if(buf[len -1]!='\n'){
	fprintf(stderr, "In line %d:Line is too long %s\n",lineno,buf);
	exit(1);
      }
    }

    if((p = check_include(buf))!=NULL){
      do_include(output,p,include_dir,lineno,0);
    }else{
      fprintf(output,"%s",buf);
    }
  
    
  }
}

