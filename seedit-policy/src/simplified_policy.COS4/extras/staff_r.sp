
{
role staff_r;
user root;

include user_common.sp;
include common-relaxed.sp;

allow /root/** r,w,s;
allow ~/** r,w,s;

}
