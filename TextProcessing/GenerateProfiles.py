__author__ = 'keleigong'

from TextProcessing.PreProcess import ReadDownloadedContent
import csv
import os

def generate_profiles(path, year, out_path=None):
    all_content = ReadDownloadedContent(path, output=None, process=False, stem=False)
    # for content in all_content:
    #     content.content = content.content.replace(' ', ',')
    if out_path:
        try:
            os.makedirs(out_path)
        except:
            print("Dir already exist")
        company_content = {}
        for content in all_content:
            if content.company in company_content.keys():
                company_content[content.company] += content.content
            else:
                company_content[content.company] = content.content
        rows = []
        for company, contents in company_content.items():
            rows.append([company, contents])
        with open(out_path + str(year) + '.csv', 'w', newline='') as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows(rows)
        print("CSV file created")
    return all_content

def generate_profiles_per_company(path, year, out_path=None):
    all_content = ReadDownloadedContent(path, output=None, process=False, stem=False)
    # for content in all_content:
    #     content.content = content.content.replace(' ', ',')
    if out_path:
        try:
            os.makedirs(out_path)
        except:
            print("Dir already exist")
        company_content = {}
        for content in all_content:
            if content.company in company_content.keys():
                company_content[content.company].append(content.content)
            else:
                company_content[content.company] = [content.content]
        # rows = []
        for company, contents in company_content.items():
            rows = []
            for content in contents:
                rows.append([company, content])
            with open(out_path + str(year) + "_" + company + '.csv', 'w', newline='') as fp:
                a = csv.writer(fp, delimiter=',')
                a.writerows(rows)
            print("CSV file created")
    return all_content


if __name__ == "__main__":
    for category in ["SM", "SS", "CM", "SRM", "LHR", "ES"]:
        all = generate_profiles_per_company(
            "/Users/keleigong/Google Drive/SCRC 2015 work/auto-rating/6th/full_text/%s/2015/" % category,
            2015,
            out_path="/Users/keleigong/Google Drive/SCRC 2015 work/auto-rating/6th/full_text/%s/profiles_per_company/" % category,
        )