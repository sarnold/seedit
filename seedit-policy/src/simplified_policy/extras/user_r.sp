{
role user_r;
user user_u;

include user_common.sp;
include common-relaxed.sp

allow ~/** r,w,s;
}
