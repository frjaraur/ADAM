import paramiko


def SSH_test(ip):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print ("Checking SSH Connection to " + ip)
        ssh.connect(ip, username='username', password='password')
        stdin, stdout, stderr = ssh.exec_command("uptime")
        #print (stdout.readlines())
        ssh.close()
        return True
    except paramiko.ssh_exception.AuthenticationException:
        print ("Authentication error via SSH on " + ip)
        return False