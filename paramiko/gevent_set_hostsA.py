from gevent import monkey
monkey.patch_all()  
import gevent
import paramiko
import os

hostfile='SiteA.txt'
cmd_list=['dnf install zabbix-agent2;systemctl restart zabbix-agent2']
local_file = 'zabbix-agent2/user_check.conf'
remote_dir = '/etc/zabbix/zabbix_agent2.d/'

# define a generator
def g_readfile(filename):
    with open(filename,"r",encoding='utf-8') as file:
        for line in file:
            arg_list=line.split()
            # 跳过空行
            if len(arg_list) == 0:
                continue
            # 跳过以#开头的行
            if arg_list[0].startswith('#'):
                continue
            yield arg_list

def execute_command(address,username,password):
    transport = paramiko.Transport((address, 22))
    transport.connect(username=username, password=password)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh._transport = transport
    
    # 将本地文件上传至服务器
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(local_file, os.path.join(remote_dir,os.path.basename(local_file)))
    
    # 执行命令
    for cmd_line in cmd_list:
        stdin, stdout, stderr = ssh.exec_command(cmd_line)
        return_code = stdout.channel.recv_exit_status()
        output_str=stdout.read().decode("utf-8")
        print(f'CMD: {cmd_line}')
        print(output_str)
        if return_code != 0:
            err_str=stderr.read().decode("utf-8")
            if len(err_str.strip()) == 0:
                continue
            print(f'ERROR: {err_str}')
            print('Stop Job!')
            break
    transport.close()
    ssh.close()

jobs = [gevent.spawn(execute_command,arg_list[0],arg_list[1],arg_list[2]) for arg_list in g_readfile(hostfile)]
gevent.wait(jobs)
