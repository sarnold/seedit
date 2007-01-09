




{
# domain for cron scripts
domain system_crond_t;
domain_trans crond_t /bin/bash;
domain_trans crond_t /etc/crontab;
domain_trans crond_t /etc/cron.d;
domain_trans crond_t /var/spool/cron;
domain_trans initrc_t /usr/sbin/anacron;
include common-relaxed.sp;
include daemon.sp;

# Cron scripts can do everything!!!
allowpriv all;
}
