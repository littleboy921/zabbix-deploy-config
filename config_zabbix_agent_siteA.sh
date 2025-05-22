#!/bin/bash
# description: config zabbix-agent2,enable zabbix-agent2 service
# author: zhangchiqian@foxmail.com

# zabbix server ip address,autoregistration
server_ip=192.168.1.105
# RefreshActiveChecks interval time(seconds)
interval=30
# hostname shown on zabbix server
host_name=SiteA-$(hostname)

# install zabbix-agent2 if not installed
if ! rpm -q zabbix-agent2;then
	dnf install -y zabbix-agent2
fi

# set zabbix server
if grep -qE '^Server=\S+$' /etc/zabbix/zabbix_agent2.conf;then
	sed -ri 's@^Server=\S+@Server='${server_ip}'@' /etc/zabbix/zabbix_agent2.conf
else
	echo "Server=${server_ip}" >> /etc/zabbix/zabbix_agent2.conf
fi
if grep -qE '^ServerActive=\S+$' /etc/zabbix/zabbix_agent2.conf;then
	sed -ri 's@^ServerActive=\S+@ServerActive='${server_ip}'@' /etc/zabbix/zabbix_agent2.conf
else
	echo "ServerActive=${server_ip}" >> /etc/zabbix/zabbix_agent2.conf
fi
# set RefreshActiveChecks interval time
if grep -qE '^RefreshActiveChecks=\S+$' /etc/zabbix/zabbix_agent2.conf;then
        sed -ri 's@^RefreshActiveChecks=\S+@RefreshActiveChecks='${interval}'@' /etc/zabbix/zabbix_agent2.conf
else
        echo "RefreshActiveChecks=${interval}" >> /etc/zabbix/zabbix_agent2.conf
fi
# set hostname shown on zabbix server
if grep -qE '^Hostname=\S+.*$' /etc/zabbix/zabbix_agent2.conf;then
	sed -ri 's@^Hostname=Zabbix server$@@' /etc/zabbix/zabbix_agent2.conf
        sed -ri 's@^Hostname=\S+@Hostname='${host_name}'@' /etc/zabbix/zabbix_agent2.conf
else
        echo "Hostname=${host_name}" >> /etc/zabbix/zabbix_agent2.conf
fi
# config UserParameter
#cp -f udcp_check.conf /etc/zabbix/zabbix_agent2.d/
# set zabbix agent2 service run as root
if  ! grep -qE '^User=root' /lib/systemd/system/zabbix-agent2.service;then
	sed -ri 's@^User=\S+@User=root@' /lib/systemd/system/zabbix-agent2.service && systemctl daemon-reload
fi
#systemctl enable zabbix-agent2.service --now
sed -ri 's@=/run/zabbix@=/var/run/zabbix@g' /etc/zabbix/zabbix_agent2.conf

mkdir -p /var/run/zabbix

