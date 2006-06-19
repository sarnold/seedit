/*(c)2006 Yuichi Nakamura
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

