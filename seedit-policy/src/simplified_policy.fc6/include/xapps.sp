# SELinux Policy Editor, a simple editor for SELinux policies
# Copyright (C) 2006 Yuichi Nakamura

allow /usr/share/X11/** r,s;
allow /etc/X11  s;


allow /etc/scim/** r,s;
allow ~/.scim  s,r;
allow /usr/share/scim/** r,s;

allow /etc/fonts/** s,r;
allow /usr/share/fonts/** r,s;
allow /var/cache/fontconfig/**  r,s;
allow ~/.rh-fontconfig/** r,s;

allow ~/.gnome2/**  s,r;
allow ~/.local/**  s,r;
allow xauthority_t  r,s;


allow /dev/dsp  r,s,o;
allow /dev/mixer r,s,o;

allow /usr/share/gimp/** r,s;
allow /usr/share/applications/** r,s;
allow /usr/share/mime/** r,s;
allow /etc/mime.types  r,s;
allow /usr/share/desktop-menu-patches/** r,s;
allow /etc/pango/** s,r;
allow /usr/share/icons/** r,s;
allow /etc/gtk-2.0/** r,s;
allow /etc/gnome-vfs-2.0/** r,s;
allow /usr/share/X11/locale/** r,s;
allow /usr/share/themes/** r,s;

allowcom -ipc unconfined_t w,r;
allowcom -ipc xserver_t r,w;
