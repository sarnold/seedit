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

/* $Id: middle_lang.l,v 1.15 2006/05/05 14:23:24 ynakam Exp $ */

/* lex definition for middle language */
/*refered checkpolicy's source to output error.*/

%option nounput

%{
#include <stdio.h>
#include <string.h>
#include "y.tab.h"
#include <seedit/common.h>

#ifndef YYSTYPE
#define YYSTYPE char *
#endif

extern YYSTYPE yylval;
/*To handle comment*/
char **yycomment = NULL; /*NULL terminated array that stores comments*/
static int yycomment_num =0;

unsigned int policydb_lineno = 1;

unsigned int policydb_errors = 0;
char source_file[255];
unsigned long source_lineno = 1;


%}
%array
letter  [A-Za-z]
digit   [0-9]
%%
domain {return(DOMAIN);}
role   {return(ROLE);}
user   {return(USER);}
type   {return(TYPE);}
allow {return(ALLOW);}
allowtmp {return(ALLOWTMP);}
allownet {return(ALLOWNET);}
allowcom {return(ALLOWCOM);}
allowkey {return(ALLOWKEY);}
allowdev {return(ALLOWDEV);}
allowfs {return(ALLOWFS);}
allowpriv {return(ALLOWPRIV);}
denypriv {return(DENYPRIV);}
-net {return(NET);}
raw {return(RAW);}
-connect {return(CONNECT);}
-netlink {return(NETLINK);}
tcp {return(TCP);}
udp {return(UDP);}
-netif {return(NETIFOPT);}
-node {return(NODEOPT);}
default {return(DEFAULT);}
server {return(SERVER);}
client {return(CLIENT);}
use {return(USE);}
send {return(SEND);}
recv {return(RECV);}
bind {return(BIND);}
allport {return(ALLPORT);}
wellknown {return(WELLKNOWN);}
\<1024 {return(WELLKNOWN);}
=<1023 {return(WELLKNOWN);}
-1023 {return(WELLKNOWN);}
-domain {return(DOMAINOPT);}
-protocol {return(PROTOCOLOPT);}
unprivport {return(UNPRIVPORT);}
>=1024 {return(UNPRIVPORT);}
>1023 {return(UNPRIVPORT);}
1024- {return(UNPRIVPORT);}
-dir {return(DIRECTORY);}
-fs {return(FS);}
-name {return(NAME);}
-unix {return(UNIX);}
-sem {return(SEM);}
-msg {return(MSG);}
-msgq {return(MSGQ);}
-shm {return(SHM);}
-pipe {return(PIPE);}
-ipc {return(IPC);}
-sig {return(SIG);}
-port {return(PORT);}
-security {return(SECURITY);}
-system {return(SYSTEM);}
-create {return(CREATE);}
-change {return(CHANGE);}
-self   {return(SELF);}
-other  {return(OTHER);}
-kmsg   {return(KMSG);}
-proc   {return(PROC);}
-all    {return(ALL);}
-root   {return(ROOT);}
-tty   {yylval=strdup("-tty"); return(TTY);}
-pts   {yylval=strdup("-pts"); return(PTS);}
-allterm {yylval=strdup("-allterm");return(ALLTERM);}
open { return(OPEN); }
admin { return(ADMIN);}
global {yylval=strdup("global"); return(GLOBAL_DOMAIN);}
general {yylval=strdup("general");return(GENERAL);}
deny {return(DENY);}
program {return(PROGRAM);}
domain_trans {return(DOMAIN_TRANS);}
exclusive {return(EXCLUSIVE_FILE);}
include {return(INCLUDE);}
("~/"|"/")({letter}|{digit}|"."|_|-|"/")*("/*"|"/**")?	{ yylval=strdup(yytext);return(PATH); }
("~/*"|"/*"|"~/**"|"/**") {yylval = strdup(yytext); return(PATH);}
({letter}({letter}|{digit}|_|-|".")*"/")+({letter}({letter}|{digit}|_|-|".")*)	{ yylval=strdup(yytext);return(INCLUDESTR); }
{letter}({letter}|{digit}|_|-)*	{ yylval=strdup(yytext);return(IDENTIFIER); }
{letter}({letter}|{digit}|_|-|".")*	{ yylval=strdup(yytext);return(FILENAME); }
{digit}* {yylval=strdup(yytext); return(NUMBER);}
({digit}+)"."({digit}+)"."({digit}+)"."({digit}+)"/"({digit}+)"."({digit}+)"."({digit}+)"."({digit}+) {yylval=strdup(yytext);return(IPV4ADDRESS);}
#line[ ]1[ ]\"[^\n]*\"          { source_lineno = 1; strncpy(source_file, yytext+9, 255); source_file[strlen(source_file)-1] = '\0'; }
#line[ ]{digit}{digit}*         { source_lineno = atoi(yytext+6)-1; }
#[^\n]*                         { 
if(yycomment==NULL){
  yycomment = (char **)my_malloc(2*sizeof(char *));
  yycomment[0]=NULL;
  yycomment[1]=NULL;
  yycomment_num=0;
}else{
  yycomment = (char **)my_realloc(yycomment, (yycomment_num+2)*sizeof(char *));
}
yycomment[yycomment_num]=strdup(yytext);
yycomment[yycomment_num+1]=NULL;
yycomment_num++;
}
[ \t\f]+			{ /* delete whitespace */ }
\n				{ /* delete whitespace */ policydb_lineno++; source_lineno++; }
"," |
"<" |
">" |
":" |
";" |
"(" |
")" |
"{" |
"}" |
"[" |
"-" |
"." |
"]" |
"~" |
"*"				{ yylval=strdup(yytext);return(yytext[0]); }
%%

int yyerror(char *msg){
        if(source_file[0])
            fprintf(stderr, "seedit-converter:Error:%s:line %ld:", source_file,source_lineno -1 );
        else
            fprintf(stderr,"(unknown source):line %d:",policydb_lineno);

	fprintf(stderr, "Error (token '%s'): %s\n\n", yytext, msg);
	policydb_errors++;
	return -1;
}

int
yywarn(char *msg)
{   

        if(source_file[0])
            fprintf(stderr, "%s:%ld:", source_file,source_lineno -1 );
        else
            fprintf(stderr,"(unknown source):line %d:",policydb_lineno);
        
	fprintf(stderr, ":Warning (token '%s'): %s\n\n", yytext, msg);
	return 0;
}

char *get_sourcefile(){
 if(source_file[0])
   return source_file;
 else
   return NULL;
}
