import re
import paramiko
import time
import os

txt_file_path = '/home/data/paramiko/SiteA.txt'
cmd_list=['dnf install zabbix-agent2;systemctl restart zabbix-agent2']
local_file = 'zabbix-agent2/udcp_check.conf'
remote_dir = '/etc/zabbix/zabbix_agent2.d/'

def parse_txt(txt_file):
    # 读取txt中的数据
    try:
        with open(txt_file,"r",encoding='utf-8') as file:
            for line in file:
                arg_list=line.split()
                print(f'address: {arg_list[0]}')
                # 如果有#注释则跳过
                if arg_list[0].startswith('#'):
                    continue
                else:
                    #print(f'user: {arg_list[1]}')
                    #print(f'password: {arg_list[2]}')
                    ssh_remote_operate(arg_list[0],arg_list[1],arg_list[2])

    except FileNotFoundError:
        print(f'Cannot find file {txt_file}')
    except Exception as e:
        print(f'Error reading file: {str(e)}')

def ssh_remote_operate(address,username,password):
    print(f'ssh to {address}')
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
    
    # 将远端文件下载到本地
    # stdin, stdout, stderr = ssh.exec_command('ls /root/checkout_*.txt')
    # output_str=stdout.read().decode("utf-8")
    # result = re.split("\n", output_str)
    # for remote_file in result:
    #     # 如果是空行则跳过此次循环
    #     if len(remote_file.strip()) == 0:
    #         continue
    #     sftp.get(remote_file, '/home/zhangchiqian/Desktop/nw_results/'+os.path.basename(remote_file))

    transport.close()
    ssh.close()
# 从txt批量读取ip进行操作
parse_txt(txt_file_path)
# 单独对某台机器进行操作
#ssh_remote_operate('192.168.1.11')
