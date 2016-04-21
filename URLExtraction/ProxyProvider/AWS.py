__author__ = 'keleigong'
import os
import time
import boto3

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

def createInstances(num, key='scrc_server', security_group='proxy'):
    instances = ec2.create_instances(
        ImageId='ami-d05e75b8',
        MinCount=num,
        MaxCount=num,
        SecurityGroups=[security_group],
        InstanceType='t2.micro',
        KeyName=key
    )
    ids = [ins.id for ins in instances]
    print("Instances created, IDs: ", ids)
    time.sleep(3)
    ips = []
    for id in ids:
        ips.append(ec2.Instance(id).public_ip_address)
    while(True):
        if all(ips):
            print("Get IPs: ", ips)
            break
        else:
            print("Waiting for IP address")
            time.sleep(5)
            ips = []
            for id in ids:
                ips.append(ec2.Instance(id).public_ip_address)
    return instances

def createKeyPairs(name, public_key_file):
    f = open(public_key_file, 'r')
    key = f.read()
    f.close()
    key_pair = ec2.import_key_pair(
        KeyName=name,
        PublicKeyMaterial=key
    )
    return key_pair

def createSecurityGroup(name, description):
    sg = ec2.create_security_group(
        GroupName=name,
        Description=description
    )
    sg.authorize_ingress(
        IpProtocol='-1',
        CidrIp='0.0.0.0/0'
    )

def updateSecurityGroup():
    sg = ec2.SecurityGroup('sg-e888718e')
    local_IP = getLocalIP()
    try:
        sg.authorize_ingress(
            IpProtocol='-1',
            CidrIp=local_IP + '/32'
        )
        print('Authorize inbound IP success')
    except:
        pass
        # print('Already exists')


def createInventory(instances, key_file):
    key_file_path = os.path.abspath(key_file)
    user = 'ubuntu'
    ids = [ins.id for ins in instances]
    ips = []
    for id in ids:
        ips.append(ec2.Instance(id).public_ip_address)
    f = open('inventory', 'w')
    print("Writing to inventory")
    for i in range(len(ips)):
        s = '%s ansible_ssh_host=%s ansible_ssh_user=%s ansible_ssh_private_key_file=%s' % (ids[i], ips[i], 'ubuntu', key_file_path,)
        print(s)
        # print(s, file=f)
        f.write(s + '\n')
    f.close()

def checkIfAllActive(instances):
    ids = [ins.id for ins in instances]
    status = client.describe_instance_status(InstanceIds=ids)['InstanceStatuses']
    # if all([s['InstanceStatus']['Details'][0]['Status'] == 'passed' and s['SystemStatus']['Details'][0]['Status'] == 'passed' for s in status]):
    if all([s['InstanceState']['Name'] == 'running' for s in status]):
        return True
    else:
        return False

def startAllInstances(key_file):
    key_file_path = os.path.abspath(key_file)
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
    )
    instances.start()
    print("Wait for instances to start")
    time.sleep(5)
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'pending']}]
    )
    ids = [ins.id for ins in instances]
    print("Instances started, IDs: ", ids)
    ips = []
    for id in ids:
        ips.append(ec2.Instance(id).public_ip_address)
    local_IP = getLocalIP()

    while(True):
        if all(ips):
            print("Get IPs: ", ips)
            break
        else:
            print("Waiting for IP address")
            time.sleep(5)
            ips = []
            for id in ids:
                ips.append(ec2.Instance(id).public_ip_address)
    f = open('inventory', 'w')
    for i in range(len(ids)):
        s = '%s ansible_ssh_host=%s ansible_ssh_user=%s ansible_ssh_private_key_file=%s' % (ids[i], ips[i], 'ubuntu', key_file_path,)
        f.write(s + '\n')
    f.close()
    sg = ec2.SecurityGroup('sg-e888718e')
    try:
        sg.authorize_ingress(
            IpProtocol='-1',
            CidrIp=local_IP + '/32'
        )
        print('Authorize inbound IP success')
    except:
        print('Already exists')


def stopAllInstances():
    ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    ).stop()

def terminateAllInstances():
    ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped', 'stopping']}]
    ).terminate()

def getLocalIP():
    try:
        import urllib2
    except:
        import urllib.request as urllib2
    import json
    import codecs
    reader = codecs.getreader('utf-8')
    response = urllib2.urlopen('http://ipinfo.io/json')
    data = json.load(reader(response))
    return str(data['ip'])

if __name__ == "__main__":
    # createKeyPairs("scrc_server", "public.key")
    createSecurityGroup("proxy", "proxy server")