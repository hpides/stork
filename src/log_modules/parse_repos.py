import logging
import os
import argparse
import multiprocessing

from multiprocessing import Process

from log_results import createLoggerPlain


def collect_repos(repos_path):
    years = [f.name for f in os.scandir(repos_path) if f.is_dir()]
    month_count = 0
    day_count = 0
    page_count = 0
    repo_count = 0
    print(years)
    all_repos = []
    for year in years:
        months = [f.path for f in os.scandir(f"{repos_path}{year}") if f.is_dir()]
        month_count += len(months)
        for month in months:
            days = [f.path for f in os.scandir(f"{month}") if f.is_dir()]
            day_count += len(days)
            for day in days:
                pages = [f.path for f in os.scandir(f"{day}") if f.is_dir()]
                page_count += len(pages)
                for page in pages:
                    repos = [f.path for f in os.scandir(f"{page}") if f.is_file()]
                    repo_count += len(repos)
                    all_repos.extend(repos)

    # print(day_count)
    print(repo_count)
    return all_repos


def unzip(repo_path):
    parent_dir = os.path.dirname(repo_path)
    repo_name = os.path.basename(repo_path).split(".")[0]
    os.makedirs(f"{parent_dir}/{repo_name}", exist_ok=True)
    os.system(f"unzip -u {repo_path} -d {parent_dir}/{repo_name} "
              f"-x 'bin/*' 'etc/*' 'include/*' 'lib/*' 'lib64/*' '.venv/*' '*/venv/*'")

    return parent_dir, repo_name


def getYearMonthDayPage(repo_path):
    temp = repo_path.split("/")
    year, month, day, page = temp[len(temp) - 4:len(temp)]

    print(f"{temp[len(temp) - 4:len(temp)]}")

    return year, month, day, page


def generate_requirements(repo_path, repo_name, packages_path):
    year, month, day, page = getYearMonthDayPage(repo_path)
    os.makedirs(f"{packages_path}{year}/{month}/{day}/{page}", exist_ok=True)
    sys_return = os.system(f"python3 -m pipreqs.pipreqs {repo_path}/{repo_name} "
                           f"--ignore bin,etc,include,lib,lib64,.venv --encoding=utf-8 "
                           f"--savepath {packages_path}{year}/{month}/{day}/{page}/{repo_name}")
    print(sys_return)
    if sys_return != 0:
        if os.path.exists(f"{repo_path}{repo_name}/requirements.txt"):
            os.system(
                f"cp {repo_path}{repo_name}/requirements.txt {packages_path}{year}/{month}/{day}/{page}{repo_name}")
            print(
                f"Found requirements file for repository {repo_name}. "
                f"The file is copied to {packages_path}{year}/{month}/{day}/{page}{repo_name}")
            return 0
        else:
            print(
                f"No requirements file found or generated for repository: {repo_name}. "
                f"Perform manual inspection.")
            return 1
    return 0


def delete_repo(repo_path):
    os.system(f"rm -r {repo_path}")


def parse_repo(repos_list, repo_count, packages_path, num_threads, thread_id,
               missing_repositories, repo_totals):
    missing_repo_count = 0
    repos_per_thread = repo_count // num_threads
    start_index = thread_id * repos_per_thread
    end_index = start_index + repos_per_thread
    generated_packages_count = 0
    parsed_repos = []

    if (thread_id == num_threads - 1):
        end_index = len(repos_list) - 1

    for i in range(start_index, end_index):
        parsed_repos.append(repos_list[i])
        directory, name = unzip(repos_list[i])
        success = generate_requirements(repo_path=directory, repo_name=name, packages_path=packages_path)
        if success == 0:
            generated_packages_count += 1
        else:
            missing_repositories.info(msg=f"{directory}/{name}")
            missing_repo_count += 1

        delete_repo(f"{directory}/{name}")
    repo_totals.info(f"repos_count_thread\t{end_index - start_index}")
    repo_totals.info(f"repo_percentage_processed_by_thread\t{(end_index - start_index) / repo_count}")
    repo_totals.info(f"packages_generated\t{generated_packages_count}")
    repo_totals.info(f"packages_generated_ratio\t{generated_packages_count / repo_count}")
    repo_totals.info(f"missing_repo_count\t{missing_repo_count}")
    repo_totals.info(f"missing_repo_ratio_thread\t{missing_repo_count / (end_index - start_index)}")
    repo_totals.info(f"parsed_repos\t{parsed_repos}")


def aggregate_stats(repos_root, outputs_root):
    logs = [f.path for f in os.scandir(outputs_root) if ".log" in f.name]
    stats = {"repos_count_thread": 0, "repo_percentage_processed_by_thread": 0, "packages_generated": 0,
             "packages_generated_ratio": 0, "missing_repo_count": 0, "missing_repo_ratio_thread": 0, "parsed_repos": []}

    for log in logs:
        with open(log, "r") as f:
            for line in f.readlines():
                label, value = line.split("\t")
                if label == "parsed_repos":
                    stats[label].append(value.replace('[', '').replace(']', '').replace('\n', ''))
                else:
                    stats[label] += float(value)

        f.close()
    # stats["parsed_repos"] = [item for sublist in stats["parsed_repos"] for item in sublist]
    # print(stats["parsed_repos"])

    with open(f"{outputs_root}/total_stats.txt", "w") as f:
        for key in stats.keys():
            f.write(f"{key}\t{stats[key]}\n")
        all_repos = collect_repos(repos_root)
        parsed_repos = stats["parsed_repos"]
        skipped_repos = [x for x in all_repos if x not in parsed_repos]
        f.write(f"skipped_repos\t{skipped_repos}")
    f.close()
    # print(stats)


def start_processes(processes):
    for process in processes:
        process.start()


def join_processes(processes):
    for process in processes:
        process.join()


def main():
    parser = argparse.ArgumentParser(
        prog='Parse repositories',
        description='Extract packages from all downloaded repositories',
    )

    parser.add_argument('-t', '--threads', default=12)

    args = parser.parse_args()

    REPOS_PATH = "/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/repositories-test/"
    PACKAGES_PATH = "/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/packages/"
    OUTPUTS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/outputs/"

    NUM_THREADS = int(args.threads)

    repositories = collect_repos(repos_path=REPOS_PATH)
    repo_count = len(repositories)
    processes = []
    # repos_list, repo_count, packages_path, outputs_root, num_threads, thread_id,
    # missing_repositories, repo_totals):
    for i in range(0, int(NUM_THREADS)):
        missing_repositories = createLoggerPlain(filename=f"{OUTPUTS_ROOT}missing_repositories-{i}.log",
                                                 project_name=f"missing_repositories-{i}", level=logging.INFO)
        repositories_totals = createLoggerPlain(filename=f"{OUTPUTS_ROOT}repo_stats/stats-{i}.log",
                                                project_name=f"stats-{i}", level=logging.INFO)

        processes.append(Process(target=parse_repo, args=(repositories, repo_count, PACKAGES_PATH,
                                                          NUM_THREADS, i, missing_repositories, repositories_totals,)))

    start_processes(processes)
    join_processes(processes)


if __name__ == '__main__':
    # main()
    REPOS_PATH = "/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/repositories-test/"
    OUTPUTS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/outputs/repo_stats/"
    aggregate_stats(outputs_root=OUTPUTS_ROOT, repos_root=REPOS_PATH)
    # REPOS_PATH = "/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/repositories-test/"
    #
    # repos = collect_repos(REPOS_PATH)
    #
    #
    # for i in range(0, 2):
    #     getYearMonthDayPage(repos[i])
