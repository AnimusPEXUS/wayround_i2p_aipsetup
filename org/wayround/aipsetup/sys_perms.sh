#!/bin/bash

chmod 1777 /tmp

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

chown root:root /var/lib/polkit-1
chmod 0700 /var/lib/polkit-1

# systemd services
chmod 0644 /usr/lib/systemd/system
find /usr/lib/systemd/system/ -type d -exec chmod 744 '{}' ';'


chmod 4755 /usr/libexec/dbus-daemon-launch-helper
chmod 4755 /usr/lib/polkit-1/polkit-agent-helper-1
chmod 4755 /usr/bin/pkexec
chmod 4755 "`which xinit`"
chmod 4755 "`which su`"
chmod 4755 "`which sudo`"
chmod 4755 "`which mount`"
chmod 4755 "`which exim`"
chmod 4755 "`which weston-launch`"
#chmod 4755 /usr/lib/virtualbox/bin/VirtualBox


exit 0
