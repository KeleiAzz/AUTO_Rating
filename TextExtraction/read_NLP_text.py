def read_txt_file(path):
    '''
    :param path:
    :return dic with company names as keys, lists of combinations of keyword and sentences as values:
    '''
    f = open(path, 'r')

    c = f.readlines()

    for i in range(len(c)):
        c[i] = c[i].strip().split('!@#$%^')

    previous = c[0][0]

    sentenses_by_company = {}
    sentenses_by_company[previous] = []

    for row in c:
        if row[0] == previous:
            for keyword in row[1].split('#$#'):
                sentenses_by_company[previous].append([keyword, row[2]])
        else:
            sentenses_by_company[row[0]] = []
            for keyword in row[1].split('#$#'):
                sentenses_by_company[row[0]].append([keyword, row[2]])
            previous = row[0]

    for company in sentenses_by_company.keys():
        sentenses_by_company[company] = sorted(sentenses_by_company[company], key=lambda x: x[0])

    return sentenses_by_company


s = read_txt_file('/Users/keleigong/Dropbox/Python/AUTO_Rating/TextExtraction/NLP.txt')

print(len(s.keys()))