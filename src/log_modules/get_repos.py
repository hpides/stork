import json
import logging
import os
import sys
import time
from pathlib import Path

import requests
# project_folder = Path(__file__).resolve().parents[]
# sys.path.append(str(project_folder))
from log_results import createLogger

# query = "read_csv+language:python"
# query = "read_csv+language:python"
# query = "read_csv+extension%3Apy+extension%3Aipynb+language%3APython"
# languages = ["python", "Jupyter Notebook"]
# pages = range(1)
per_page = 30
storage_path = "/home/ilint/HPI/fs00/rabl/ilin.tolovski/stork/repositories-test/"
# # new token
token = "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"

# years = [2018, 2019, 2020, 2021, 2022, 2023]
# months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
# days = range(1,32)

years = [2018]
days = range(28, 29)
months = ['02']
licenses = ['mit']

# pages = range(1,101)
pages = range(1,2)
eom = False
for year in years:
    for month in months:
        for day in days:

            log = createLogger(filename=f"outputs/repo_stats/repositories-{year}-{month}-{day}.log",
                               project_name=f"repo_stats-{year}-{month}-{day}", level=logging.INFO)
            for page in pages:
                if (page > 1) and (page % 30 == 1):
                    time.sleep(60)
                else:
                    query = f"q=license:mit+created:{year}-{month}-{day}+language:Python&type=repositories"
                    url = f"https://api.github.com/search/repositories?{query}&page={page}"
                    print(url)
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github+json"
                    }
                    response = requests.request("GET", url, headers=headers)
                    json_response = response.json()
                    # print(json_response)
                    with open(f"outputs/repo_lists/repos_read_csv_{year}-{month}-{day}_page_{page}.json", mode="w") as file:
                        json.dump(json_response, file)

                    repositories = {}
                    if "items" not in json_response.keys():
                        eom = True
                        break
                    if not json_response["items"]:
                        time.sleep(60)
                        break
                    else:

                        for item in json_response["items"]:
                            repositories[item["name"]] = item["html_url"]

                        for repository in repositories:

                            print(f"Repository: {repository}, url: {repositories[repository]}")
                            log.info(f"Repository: {repository}, url: {repositories[repository]}, "
                                     f"date (yyyy-mm-dd):{year}-{month}-{day}")
                            response = requests.request("GET", repositories[repository], headers=headers)
                            os.system(f"git clone --depth 1 --single-branch --shallow-submodules {repositories[repository]} {storage_path}{repository}")

                    file.close()
            if eom:
                eom = False
                break
            log.info(f"Total count for {year}-{month}-{day}: {json_response['total_count']}")






# url = "/search/q=license:mit+created:2018-01-01..2018-01-03+language:Python&type=repositories"
#
#
# # new token
# token = "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"
#
#
# for page in pages:
#     url = f"https://api.github.com/search/code?q={query}&type=code&page={page}"
#
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Accept": "application/vnd.github+json"
#     }
#
#     response = requests.request("GET", url, headers=headers)
#     json_response = response.json()
#     print(json_response)
#     with open(f"repos_read_csv_{page}_{per_page}.json", mode="w") as file:
#         json.dump(json_response, file)
#
#     repositories = {}
#
#     for item in json_response["items"]:
#         repositories[item["repository"]["name"]] = item["repository"]["html_url"]
#
#     for repository in repositories:
#         print(f"Repository: {repository}, url: {repositories[repository]}")
#         # response = requests.request("GET", repositories[repository], headers=headers)
#         # os.system(f"git clone {repositories[repository]} github_repos_3000/{repository}")
#         # os.system(f"git clone {repositories[repository]} /home/ilint/HPI/repos/read_csv_repos_300/{repository}")
#
#     time.sleep(60)
