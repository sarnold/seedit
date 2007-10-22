#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/types.h>
#include "global.h"
#include "hashtab.h"
#include <seedit/common.h>


/*key:name of defined attribute, value:how many times attribute appeared*/
/*This is used for profile*/
static HASH_TABLE *attribute_table = NULL; 

/*key: name of attribute to be used instead of macro, value:1*/
static HASH_TABLE *tobe_used_attribute_table = NULL;

static char *make_attribute(char *macro, char *doamin, char *type) {
	char *attribute;
	char *tmp;
	
	if (type == NULL) {
		tmp = joint_str(macro,"");
	} else {
		tmp = joint_str(joint_str(macro,"_"),type);
	}
	attribute = joint_str(tmp,"_attr");

	return attribute;
}

static void do_out_macro(FILE *fp, char *macro, char *domain, char *type){
	if(type == NULL) {
		fprintf(fp,"%s(%s)\n", macro, domain);
	} else {
		fprintf(fp,"%s(%s,%s)\n", macro, domain, type);
	}
}

/*output macro with size optimization*/
/*!! FIXME It is a stub, under development, 
  does not do not optimization in fact for now.*/
int out_optimized_macro(FILE *fp, char *macro, char *domain, char *type) {
	do_out_macro(fp, macro, domain, type);
	return 0;	
}


void print_profile(FILE *fp) {
	int num;
	int i;
	HASH_NODE **attribute_array;
	if (!gProfile || attribute_table == NULL)
		return;
	
	attribute_array = create_hash_array(attribute_table);
	num = attribute_table -> element_num;
	for (i = 0; i < num; i++ ){
		int count = atoi((char *)attribute_array[i]->data);
		fprintf(fp, "%s %d\n", attribute_array[i]->key, count);
	}
}

/*Read result of profile, and make optimize_macro_table
*/
void init_tobe_used_attribute_table(FILE *attribute_profile){  
	char buf[BUFSIZE];
	char *attribute;
	char *count;
	int th = OPTIMIZE_THRESHOLD;

	tobe_used_attribute_table = create_hash_table(FILE_ACL_TABLE_SIZE);
	
	while(fgets(buf, sizeof(buf), attribute_profile)){
		attribute = get_nth_tok_alloc(buf, " \t", 1);
		count = get_nth_tok_alloc(buf, " \t", 2);
		if (atoi(count) >= th)
			insert_element(tobe_used_attribute_table, "1", attribute);
	}

}
