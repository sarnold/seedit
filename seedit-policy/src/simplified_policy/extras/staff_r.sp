
{
role staff_r;
user root;
user ynakam;

include user_common.sp;
include common-relaxed.sp;

allow /root/** r,s;
allow ~/** r,w,s;

}
