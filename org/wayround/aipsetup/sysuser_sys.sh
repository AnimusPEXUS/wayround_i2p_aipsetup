#!/bin/bash

usermod -G httpd,ejabberd,ssl httpd
usermod -G ejabberd,ssl ejabberd
usermod -G jabberd2,ssl jabberd2
usermod -G dovecot,ssl,mail dovecot
usermod -G exim,ssl,mail exim
usermod -G adch,ssl adch

chmod 750 /daemons/ejabberd
chmod 750 /daemons/ejabberd/var
chmod 750 /daemons/ejabberd/var/www
chmod -R 750 /daemons/ejabberd/var/www/logs

chmod -R 750 /daemons/ssl

chown root:mail /var/mail
chmod 1777 /var/mail

chgrp exim /etc/shadow
chmod g+r /etc/shadow


# polkit settings
chown root:root /etc/polkit-1/localauthority
chmod 0700 /etc/polkit-1/localauthority

chown polkitd:polkitd /etc/polkit-1/rules.d
chmod 0700 /etc/polkit-1/rules.d

chown polkitd:polkitd /usr/share/polkit-1/rules.d
chmod 0700 /usr/share/polkit-1/rules.d

chown root:root /var/lib/polkit-1
chmod 0700 /var/lib/polkit-1


chmod 4755 /usr/libexec/dbus-daemon-launch-helper
chmod 4755 /usr/lib/polkit-1/polkit-agent-helper-1
chmod 4755 /usr/bin/pkexec
chmod 4755 "`which xinit`"
chmod 4755 "`which su`"
chmod 4755 "`which sudo`"
chmod 4755 "`which mount`"
chmod 4755 "`which exim`"
