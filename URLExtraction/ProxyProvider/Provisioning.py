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
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'hn:p:k:', ['num=', 'provider=', 'key='])
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




if __name__ == "__main__":
    main()
