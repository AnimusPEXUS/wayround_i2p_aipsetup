#!/bin/bash

touch /etc/passwd
touch /etc/group
touch /etc/shadow

maxsuid=100

getuserbyid_p1=
getuserbyid_ret=
getuserbyid() {
    local i=0
    for (( i=1 ; i != "$maxsuid" ; i++ ))
    do
        if [ "$getuserbyid_p1" -eq "$i" ]
        then
            local r=`cat /etc/passwd | sed -e "/.*:.*:$getuserbyid_p1:.*/{s/:.*//;p};d"`

            if [ "$r" = '' ]
            then
                getuserbyid_ret=
            else
                getuserbyid_ret="$r"
            fi
        fi
    done
}

getgroupbyid_p1=
getgroupbyid_ret=
getgroupbyid() {
    local i
    for (( i=1 ; i != "$maxsuid" ; i++ ))
    do
        if [ "$getgroupbyid_p1" -eq "$i" ]
        then
            local r=`cat /etc/group | sed -e "/.*:.*:$getgroupbyid_p1:.*/{s/:.*//;p};d"`

            if [ "$r" = '' ]
            then
                getgroupbyid_ret=
            else
                getgroupbyid_ret="$r"
            fi
        fi
    done
}


makeusers() {
    local i

    #users for groups

    # logick separation (special users) 1-9
    local u[1]=nobody
    local u[2]=nogroup
    local u[3]=bin
    local u[4]=ftp
    local u[5]=mail
    local u[6]=adm

    # terminals 10-19
    local u[10]=pts
    local u[11]=tty

    # devices 20-35
    local u[20]=disk
    local u[21]=usb
    local u[22]=flash
    local u[23]=mouse
    local u[24]=lp
    local u[25]=floppy
    local u[26]=video
    local u[27]=audio
    local u[28]=cdrom
    local u[29]=tape
    local u[30]=pulse
    local u[31]=usbfs
    local u[32]=usbdev
    local u[33]=usbbus
    local u[34]=usblist
    local u[35]=alsa


    # daemons 36-99
    local u[36]=colord

    local u[40]=messagebus
    local u[41]=sshd
    local u[42]=haldaemon
    local u[43]=clamav
    local u[44]=mysql
    local u[45]=exim
    local u[46]=postgres
    local u[47]=httpd
    local u[48]=cron
    local u[49]=mrim
    local u[50]=icq
    local u[51]=pyvkt
    local u[52]=j2j
    local u[53]=gnunet
    local u[54]=ejabberd
    local u[55]=cupsd
    local u[56]=bandersnatch
    local u[57]=torrent
    local u[58]=ssl
    local u[59]=dovecot
    local u[60]=dovenull
    local u[61]=spamassassin
    local u[62]=yacy
    local u[63]=irc
    local u[64]=hub
    local u[65]=cynin
    local u[66]=mailman
    local u[67]=asterisk
    local u[68]=bitcoin
    local u[69]=adch


    local u[70]=dialout
    local u[71]=kmem
    local u[72]=polkituser
    local u[73]=nexuiz
    local u[74]=couchdb
    local u[75]=polkitd
    local u[76]=kvm

    local u[90]=mine

    local u[91]=utmp
    local u[92]=lock
    local u[93]=avahi
    local u[94]=avahi-autoipd
    local u[95]=netdev
    local u[96]=freenet
    local u[97]=jabberd2
    local u[98]=mongodb
    local u[99]=aipsetupserv


    # delete users
    echo deleting
    for (( i=1 ; i != "$maxsuid" ; i++ ))
    do
        getuserbyid_p1="$i"
        getuserbyid
        if [ "$getuserbyid_ret" != ''  ]
        then
            echo "deleting user $getuserbyid_ret"
            userdel "$getuserbyid_ret"  > /dev/null 2>&1
        fi
    done



    # delete groups
    for (( i=1 ; i != "$maxsuid" ; i++ ))
    do
        getgroupbyid_p1="$i"
        getgroupbyid
        if [ "$getgroupbyid_ret" != ''  ]
        then
            echo "deleting group $getgroupbyid_ret"
            groupdel "$getgroupbyid_ret"  > /dev/null 2>&1
        fi
    done

    for (( i=1 ; i != "$maxsuid" ; i++ ))
    do
        if [ "${u[$i]}" != '' ]
        then
            echo "deleting group ${u[$i]}"
            groupdel "${u[$i]}"  > /dev/null 2>&1
        fi
    done



    # delete users again
    for (( i=1 ; i != "$maxsuid" ; i++ ))
    do
        if [ "${u[$i]}" != '' ]
        then
            echo "deleting user ${u[$i]}"
            userdel "${u[$i]}"  > /dev/null 2>&1
        fi
    done


    # add groups
    echo adding
    for (( i=1 ; i != "$maxsuid" ; i++ ))
    do
        if [ "${u[$i]}" != '' ]
        then
            echo "$i"
            groupadd -r -o -g "$i" "${u[$i]}"  > /dev/null
        fi
    done

    mkdir -p /daemons
    for (( i=1 ; i != "$maxsuid" ; i++ ))
    do
        if [ "${u[$i]}" != '' ]
        then
            echo "$i"
            useradd -r -g "$i" -G "${u[$i]}" -u "$i" -d /daemons/"${u[$i]}" -s /bin/false  "${u[$i]}"  > /dev/null 2>&1
            usermod -L "${u[$i]}" > /dev/null
            mkdir -p /daemons/"${u[$i]}"
            chown -R "${u[$i]}": /daemons/"${u[$i]}"
            chmod -R 700 /daemons/"${u[$i]}"
        fi
    done
    chown root: /daemons
    chmod 755 /daemons

    bash /etc/rc.d/rc.sysuser_sys
    bash /etc/rc.d/rc.sysuser_local

    useradd -r -g 0 -G root -u 0 -d /root -s /bin/bash root
    usermod -U root
    mkdir -p /root
    chown -R root: /root
    chmod -R 700 /root


    pwck -s
    grpck -s

    chmod 0744 /etc/group
    chmod 0744 /etc/passwd
}

makeusers
exit 0
