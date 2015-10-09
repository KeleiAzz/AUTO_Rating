__author__ = 'keleigong'

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