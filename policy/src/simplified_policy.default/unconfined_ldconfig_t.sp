{
# This domain is necessary to label ld.so.cache correctly.
domain unconfined_ldconfig_t;
program /sbin/ldconfig;
include common-relaxed.sp;

allowpriv all;
allowtmp -dir /etc -name ldconfig_cache_t r,w,s;
}
