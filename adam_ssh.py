import paramiko


def SSH_test(ip):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print ("Checking SSH Connection to " + ip)
        ssh.connect(ip, username='zero', password='00friday13th00')
        ssh.exec_command("uptime")
        ssh.close()
        return True
    except paramiko.ssh_exception.AuthenticationException:
        print ("Authentication error via SSH on " + ip)
        return False