{
#comment: This domain is domain for scripts that run from rpm. rpm enforces to give script different domain, so this domain is necessary.
domain rpm_script_t;
domain_trans rpm_t /bin/bash;
include common-relaxed.sp;

allowpriv all;
}
