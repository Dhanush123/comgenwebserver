from collections import defaultdict
from base64 import b64encode, b64decode

from github import Github

from comgenwebserver.schema.githubuser import GithubUserSchema
from comgenwebserver.schema.githubrepo import GithubRepoSchema
from comgenwebserver.constants import COMGEN_BRANCH


def get_github_instance(access_token):
    return Github(access_token)


def get_github_user_info(github_instance):
    return github_instance.get_user()


def get_github_user_repos(github_instance):
    user = get_github_user_info(github_instance)
    repos = user.get_repos('all')
    return repos


def get_github_user_repo(github_instance, repo_name):
    user = get_github_user_info(github_instance)
    repo = user.get_repo(repo_name)
    return repo


def get_github_commit_files(github_user, repo):
    github_repo = github_user.get_repo(repo.name)
    latest_commit = github_repo.get_commits()[0]
    return latest_commit.files


def filter_tracking_repos(users_with_tracking_repos):
    tracking_repos = defaultdict(list)
    for user_record in users_with_tracking_repos:
        user_record = GithubUserSchema().load(user_record)
        for repo in user_record['repos']:
            repo = GithubRepoSchema().load(repo)
            if repo['tracking'] == True:
                tracking_repos[user_record['access_token']].append(repo)
    return tracking_repos


def get_repo_branches_list(repo):
    return list(repo.get_branches())


def create_comgen_branch(repo):
    head_commit = repo.get_commit('HEAD')
    ref = repo.create_git_ref(
        f'refs/heads/{COMGEN_BRANCH}', head_commit.sha)


def update_github_file_content(repo, old_file, new_file_content, commit_message):
    repo_has_comgen_branch = COMGEN_BRANCH in [
        branch.name for branch in get_repo_branches_list(repo)]
    if not repo_has_comgen_branch:
        create_comgen_branch(repo)
    repo.update_file(old_file.filename, commit_message,
                     new_file_content, old_file.sha, branch="comgen")


def get_github_file_content(repo, github_file):
    return base64ToString(repo.get_contents(github_file.filename).content)


def stringToBase64(s):
    return b64encode(s.encode('utf-8'))


def base64ToString(b):
    return b64decode(b).decode('utf-8')
