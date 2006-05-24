{
domain gdm_t;
domain_trans init_t /usr/bin/gdm-binary,/usr/sbin/gdm-binary;
domain_trans init_t /usr/bin/gdmgreeter,/usr/sbin/gdmgreeter;
domain_trans init_t /usr/bin/kdm,/usr/bin/kdm_greet;
include common-relaxed.sp;

allow /usr/bin/Xorg r,dx;
allowpriv all;
}
