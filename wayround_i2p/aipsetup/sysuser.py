
import copy
import os.path
import subprocess
import pwd
import spwd
import grp

import wayround_org.utils.path
import wayround_org.utils.terminal

# TODO: consider moving to system.py


SYS_UID_MAX = 999


USERS = {
    # users for groups

    # logick separation (special users) 1-9
    1: 'nobody',
    2: 'nogroup',
    3: 'bin',
    4: 'ftp',
    5: 'mail',
    6: 'adm',
    7: 'gdm',
    8: 'wheel',

    # terminals 10-19
    10: 'pts',
    11: 'tty',

    # devices 20-35
    20: 'disk',
    21: 'usb',
    22: 'flash',
    23: 'mouse',
    24: 'lp',
    25: 'floppy',
    26: 'video',
    27: 'audio',
    28: 'cdrom',
    29: 'tape',
    30: 'pulse',
    31: 'pulse-access',
    32: 'usbfs',
    33: 'usbdev',
    34: 'usbbus',
    35: 'usblist',
    36: 'alsa',


    # daemons 39-99
    39: 'colord',

    40: 'messagebus',
    41: 'sshd',
    42: 'haldaemon',
    43: 'clamav',
    44: 'mysql',
    45: 'exim',
    46: 'postgres',
    47: 'httpd',
    48: 'cron',
    49: 'mrim',
    50: 'icq',
    51: 'pyvkt',
    52: 'j2j',
    53: 'gnunet',
    54: 'ejabberd',
    55: 'cupsd',
    56: 'bandersnatch',
    57: 'torrent',
    58: 'ssl',
    59: 'dovecot',
    60: 'dovenull',
    61: 'spamassassin',
    62: 'yacy',
    63: 'irc',
    64: 'hub',
    65: 'cynin',
    66: 'mailman',
    67: 'asterisk',
    68: 'bitcoin',
    69: 'adch',


    70: 'dialout',
    71: 'kmem',
    72: 'polkituser',
    73: 'nexuiz',
    74: 'couchdb',
    75: 'polkitd',
    76: 'kvm',

    90: 'mine',

    91: 'utmp',
    92: 'lock',
    93: 'avahi',
    94: 'avahi-autoipd',
    95: 'netdev',
    96: 'freenet',
    97: 'jabberd2',
    98: 'mongodb',
    99: 'aipsetupserv',

    100: 'systemd-bus-proxy',
    101: 'systemd-network',
    102: 'systemd-resolve',
    103: 'systemd-timesync',
    104: 'systemd-journal',
    105: 'systemd-journal-gateway',
    106: 'systemd-journal-remote',
    107: 'systemd-journal-upload',

    200: 'tor',
    201: 'shinken'
    }


# GROUPS = copy.copy(USERS)


def calc_daemon_home_dir(base_dir, daemons_dir_no_base, user_name):
    ret = wayround_org.utils.path.join(
        base_dir,
        daemons_dir_no_base,
        user_name
        )
    return ret


def calc_user_home_dir(base_dir, user_name):
    if user_name == 'root':

        ret = wayround_org.utils.path.join(
            base_dir,
            'root'
            )

    else:

        ret = wayround_org.utils.path.join(
            base_dir,
            'home',
            user_name
            )

    return ret


def personalize_home(home_dir, user, user_id):

    ret = 0

    os.makedirs(home_dir, exist_ok=True)

    if user_id < 1000:

        p = subprocess.Popen(
            [
                'chown',
                '-R',
                '{0}:{0}'.format(user),
                home_dir
            ]
            )
        ret += int(p.wait() != 0)

        p = subprocess.Popen(
            [
                'chmod',
                '-R',
                '700',
                home_dir
            ]
            )
        ret += int(p.wait() != 0)

    return ret


def sys_users(base_dir='/', daemons_dir_no_base='/daemons'):

    pwall = pwd.getpwall()
    spall = spwd.getspall()
    grall = grp.getgrall()

    pwall.sort(key=lambda x: x[2])
    grall.sort(key=lambda x: x[2])
    spall.sort(key=lambda x: x[0])

    pw_file_name = wayround_org.utils.path.join(base_dir, 'etc', 'passwd')
    gr_file_name = wayround_org.utils.path.join(base_dir, 'etc', 'group')
    sp_file_name = wayround_org.utils.path.join(base_dir, 'etc', 'shadow')

    pw_file = open(pw_file_name, 'w')
    gr_file = open(gr_file_name, 'w')
    sp_file = open(sp_file_name, 'w')

    spall_dict = {}
    for i in spall:
        spall_dict[i[0]] = i

    ids = {}

    for i in pwall:
        ids[i[2]] = i

    user_ids = {}

    for i in sorted(list(ids.keys())):
        if i == 0 or i >= 1000:
            user_ids[i] = ids[i]

    print("Writing system users")
    for i in sorted(list(USERS.keys())):
        user_name = USERS[i]

        home_dir = calc_daemon_home_dir(
            base_dir,
            daemons_dir_no_base,
            user_name
            )

        pw_file.write(
            '{}:{}:{}:{}:{}:{}:{}\n'.format(
                user_name,
                'x',
                i,
                i,
                user_name,
                home_dir,
                '/bin/false'
                )
            )

        gr_file.write(
            '{}:{}:{}:{}\n'.format(
                user_name,
                'x',
                i,
                user_name
                )
            )

        sp_file.write(
            '{}:{}:::::::\n'.format(
                user_name,
                '!'
                )
            )

    print("Writing root and normal users:")
    for i in sorted(list(user_ids.keys())):

        user_name = user_ids[i][0]
        home_dir = calc_user_home_dir(base_dir, user_name)

        print("    {}".format(user_name))

        pw_file.write(
            '{}:{}:{}:{}:{}:{}:{}\n'.format(
                user_name,
                'x',
                i,
                i,
                user_name,
                home_dir,
                user_ids[i][-1]
                )
            )

        gr_file.write(
            '{}:{}:{}:{}\n'.format(
                user_name,
                'x',
                i,
                user_name
                )
            )

        if user_name in spall_dict:
            sp_file.write(
                '{}:{}:{}:{}:{}:{}:{}:{}:{}\n'.format(
                    *spall_dict[user_name]
                    )
                )

    pw_file.close()
    gr_file.close()
    sp_file.close()

    for i in sorted(list(USERS.keys())):
        user_name = USERS[i]
        home_dir = calc_daemon_home_dir(
            base_dir,
            daemons_dir_no_base,
            user_name
            )
        personalize_home(home_dir, user_name, i)

    for i in sorted(list(user_ids.keys())):
        user_name = user_ids[i][0]
        home_dir = calc_user_home_dir(base_dir, user_name)
        personalize_home(home_dir, user_name, i)

    return 0


def get_sys_perms_shell_script():
    ret = """\


chown root: /
chmod 755 /

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


chown -R root:exim /var/spool/exim
chmod -R 770 /var/spool/exim

chown -R root:mail /var/log/dovecot
chmod -R 770 /var/log/dovecot

# polkit settings
chown root:root /etc/polkit-1/localauthority
chmod 0700 /etc/polkit-1/localauthority

#chown root:root /var/lib/polkit-1
#chmod 0700 /var/lib/polkit-1
chown root:root /etc/pam.d/polkit-1
chmod 0700 /etc/pam.d/polkit-1

# systemd service files

for i in \
    '/usr/lib/systemd/system' \
    '/usr/lib/systemd/user' \
    '/etc/systemd/system' \
    '/etc/systemd/user'
do

    chmod 0755 "$i"
    find "$i" -type d -exec chmod 755 '{}' ';'
    find "$i" -type f -exec chmod 644 '{}' ';'

done


chmod 4755 /usr/libexec/dbus-daemon-launch-helper
chmod 4755 /usr/lib/polkit-1/polkit-agent-helper-1
chmod 4755 /usr/bin/pkexec

# NOTE: starting from 1.16 xorg-server chmod is not needed and device
#       handlers retrived from systemd
# chmod 4755 "`which xinit`"

chmod 4755 "`which su`"
chmod 4755 "`which sudo`"
# chmod 4755 "`which mount`"
chmod 4755 "`which exim`"
# chmod 4755 "`which weston-launch`"
#chmod 4755 /usr/lib/virtualbox/bin/VirtualBox


exit 0
"""
    return ret


def sys_perms(chroot):

    errors = 0

    p = subprocess.Popen(
        chroot + [
            'bash', '-c', get_sys_perms_shell_script()
            ]
        )
    res = p.wait()
    if res != 0:
        errors += 1

    # fix simple user groups

    pwall = pwd.getpwall()
    pwall.sort(key=lambda x: x[2])

    spall_dict = {}
    for i in spall_dict:
        spall_dict[i[0]] = i

    ids = {}

    for i in pwall:
        ids[i[2]] = i

    user_ids = {}

    for i in sorted(list(ids.keys())):
        if i >= 1000:
            user_ids[i] = ids[i]

    for i in sorted(list(user_ids.keys())):
        p = subprocess.Popen(
            [
                'usermod',
                '-G',
                '{},pts,tty,pulse-access,audio,kvm,video'.format(
                    user_ids[i][0]
                    ),
                user_ids[i][0]
                ]
            )

    return errors
