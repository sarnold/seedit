{
domain unconfined_restorecon_t;
program /sbin/restorecon;
include common-relaxed.sp;

allowpriv all;
}
