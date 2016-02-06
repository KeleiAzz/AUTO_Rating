import sys
import getopt
import AWS as aws
import digitalocean as DO
import os
import time

def main():
    provider = 'aws'
    num = 1
    key = "private.key"
    action = 'none'
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'hn:p:k:a:', ['num=', 'provider=', 'key=', 'action='])
        # print options, remainder
        for opt, arg in options:
            if opt == '-h':
                print('Provisioning.py -n <number of instances/droplets> -p <provider:aws or DO> -k <private key file>')
            elif opt in ('-n', '--num'):
                num = int(arg)
            elif opt in ('-p', '--provider'):
                provider = arg
            elif opt in ('-k,', '--key'):
                key = arg
            elif opt in ('-a', '--action'):
                action = arg
        if action.lower() == 'start':
            aws.startAllInstances(key)
            update_proxy()
            print('All instances started, inventory file updated')
        elif action.lower() == 'stop':
            aws.stopAllInstances()
            print("All instances stopped")
        elif action.lower() == 'terminate':
            aws.terminateAllInstances()
            print("All instances terminated")
        else:
            if provider.lower() == "aws":
                instances = aws.createInstances(num, security_group='proxy')
                while not aws.checkIfAllActive(instances):
                    print("Wait for servers initialization")
                    time.sleep(5)
                print("All servers ready")
                aws.createInventory(instances, 'private.key')
            if provider.lower() in ('do', 'digitalocean'):
                token = os.environ["DO_TOKEN"]
                conn = DO.Digitalocean(token)
                for i in range(num):
                    conn.createDroplet('devops%d' % i, 'nyc3', 'ubuntu-14-04-x32')
                while not conn.checkIfAllActive():
                    print("Wait for servers initialization")
                    time.sleep(5)
                print("All servers ready")
                conn.createInventory(key)

    except getopt.GetoptError:
        print('Provisioning.py -n <number of instances/droplets> -p <provider:aws or DO>')
        sys.exit(1)

def update_proxy():
    f = open('inventory', 'r')
    text = f.read()
    f.close()
    text = text.split('\n')
    res = []
    for line in text:
        # print(line.split(' '))
        if len(line) > 2:
            ip = line.split(' ')[1]
            ip = ip.split('=')[-1]
            res.append(ip)

    f = open('proxy.txt', 'w')
    for i in res:
        f.write('socks5 ' + i + ':10080' + '\n')
    f.close()


if __name__ == "__main__":
    main()
