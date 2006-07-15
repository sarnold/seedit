#! SELinux Policy Editor, a simple editor for SELinux policies
#! Copyright (C) 2006 Yuichi Nakamura

{
domain unconfined_su_t;
domain_trans unconfined_t /bin/su;

allowpriv all;
}
