
import copy
import grp
import os.path
import pwd
import subprocess

import org.wayround.utils.path
import org.wayround.utils.terminal

SYS_UID_MAX = 999
SYS_GID_MAX = 999


USERS = {
    #users for groups

    # logick separation (special users) 1-9
    1: 'nobody',
    2: 'nogroup',
    3: 'bin',
    4: 'ftp',
    5: 'mail',
    6: 'adm',
    7: 'systemd-journal',

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
    31: 'usbfs',
    32: 'usbdev',
    33: 'usbbus',
    34: 'usblist',
    35: 'alsa',


    # daemons 36-99
    36: 'colord',

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
    99: 'aipsetupserv'
    }


GROUPS = copy.copy(USERS)


def sysusers(base_dir='/', daemons_dir='/daemons'):

    base_dir = org.wayround.utils.path.abspath(base_dir)
    base_dir_daemons_dir = org.wayround.utils.path.abspath(
        org.wayround.utils.path.join(base_dir, daemons_dir)
        )

    chroot = ['chroot', base_dir]

    errors = 0

    print("Removing existing user records")
    for i in pwd.getpwall():
        if 0 < i.pw_uid <= SYS_UID_MAX:
            org.wayround.utils.terminal.progress_write(
                "  ({:3d}%) {}".format(
                    i.pw_uid,
                    i.pw_name
                    )
                )
            p = subprocess.Popen(
                chroot + ['userdel', i.pw_name]
                )
            p.wait()
    org.wayround.utils.terminal.progress_write_finish()

    print("Removing existing group records")
    for i in grp.getgrall():
        if 0 < i.gr_gid <= SYS_GID_MAX:
            org.wayround.utils.terminal.progress_write(
                "  ({:3d}%) {}".format(
                    i.gr_gid,
                    i.gr_name
                    )
                )
            p = subprocess.Popen(
                chroot + ['groupdel', i.gr_name]
                )
            p.wait()
    org.wayround.utils.terminal.progress_write_finish()

    print("Adding new group records")
    for i in sorted(list(GROUPS.keys())):
        name = GROUPS[i]
        org.wayround.utils.terminal.progress_write(
            "  ({:3d}%) {}".format(
                i,
                name
                )
            )
        p = subprocess.Popen(
            chroot + ['groupadd', '-r', '-o', '-g', str(i), name]
            )
        res = p.wait()
        if res != 0:
            errors += 1
    org.wayround.utils.terminal.progress_write_finish()

    print("Checking `{}' dir".format(base_dir_daemons_dir))
    if not os.path.exists(base_dir_daemons_dir):
        print("   ..creating")
        try:
            os.makedirs(base_dir_daemons_dir)
        except:
            print("Error creating dir: {}".format(base_dir_daemons_dir))

    print("Creating special user accounts")
    for i in sorted(list(USERS.keys())):
        name = USERS[i]
        home_path = org.wayround.utils.path.join(base_dir_daemons_dir, name)

        org.wayround.utils.terminal.progress_write(
            "  ({:3d}%) {}".format(
                i,
                name
                )
            )
        p = subprocess.Popen(
            chroot + ['useradd', '-r', '-g', str(i), '-G', name, '-u', str(i),
             '-d', home_path,
             '-s', '/bin/false',
             name]
            )
        res = p.wait()
        if res != 0:
            errors += 1

        p = subprocess.Popen(
            chroot + ['usermod', '-L', name]
            )
        res = p.wait()
        if res != 0:
            errors += 1

        try:
            os.makedirs(home_path)
        except:
            pass
            # print("Error creating dir: {}".format(home_path))

        p = subprocess.Popen(
            chroot + ['chown', '-R', '{}:'.format(name), home_path]
            )
        res = p.wait()
        if res != 0:
            errors += 1

        p = subprocess.Popen(
            chroot + ['chmod', '-R', '700', home_path]
            )
        res = p.wait()
        if res != 0:
            errors += 1

    org.wayround.utils.terminal.progress_write_finish()

    print("Ensuring `{}' permissions".format(base_dir_daemons_dir))
    p = subprocess.Popen(
        chroot + ['chown', 'root:root', base_dir_daemons_dir]
        )
    res = p.wait()
    if res != 0:
        errors += 1

    p = subprocess.Popen(
        chroot + ['chmode', '755', base_dir_daemons_dir]
        )
    res = p.wait()
    if res != 0:
        errors += 1

    print("Starting /etc/aipsetup.d/sysuser_local.sh")
    p = subprocess.Popen(
        chroot + ['bash', '/etc/aipsetup.d/sysuser_local.sh']
        )
    res = p.wait()
    if res != 0:
        errors += 1

    print("Ensuring `root' user existance")
    p = subprocess.Popen(
        chroot + ['useradd',
         '-r',
         '-g', '0',
         '-G', 'root',
         '-u', '0',
         '-d', '/root',
         '-s', '/bin/bash',
         'root']
        )
    p.wait()

    p = subprocess.Popen(
        chroot + ['usermod',
         '-U',
         'root']
        )
    res = p.wait()
    if res != 0:
        errors += 1

    if not os.path.exists('/root'):
        try:
            os.makedirs('/root')
        except:
            print("Error creating dir: {}".format('/root'))

    p = subprocess.Popen(
        chroot + ['chown',
         '-R',
         'root:root',
         '/root']
        )
    res = p.wait()
    if res != 0:
        errors += 1

    p = subprocess.Popen(
        chroot + ['chmod',
         '-R',
         '700',
         '/root']
        )
    res = p.wait()
    if res != 0:
        errors += 1

    print("Sorting passwd and group files")
    p = subprocess.Popen(
        chroot + ['pwck', '-s']
        )
    res = p.wait()
    if res != 0:
        errors += 1

    p = subprocess.Popen(
        chroot + ['grpck', '-s']
        )
    res = p.wait()
    if res != 0:
        errors += 1

    ret = 0
    if errors != 0:
        ret = 1

    return ret


def sysusers_sys(chroot):

    errors = 0

    sysuser_sys = org.wayround.utils.path.join(
        org.wayround.utils.path.abspath(os.path.dirname(__file__)),
        'sysuser_sys.sh'
        )
    print("Starting {}".format(sysuser_sys))
    p = subprocess.Popen(
        chroot + ['bash', sysuser_sys]
        )
    res = p.wait()
    if res != 0:
        errors += 1

    return errors
