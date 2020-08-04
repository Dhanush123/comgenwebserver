from tempfile import TemporaryDirectory

from comgenwebserver.db.service import DBClient
from comgenwebserver.schema.githubuser import GithubUserSchema
from comgenwebserver.helpers.github import filter_tracking_repos, get_github_instance, get_github_user_info, get_github_commit_files, get_github_file_content, get_github_user_repo, update_github_file_content
from comgenwebserver.helpers.modelserverclient import get_commented_file


def get_repos_and_comment_commit_files():
    db = DBClient()
    users_records = [GithubUserSchema().load(user_record)
                     for user_record in db.get_users_with_tracking_repos()]

    users_with_tracking_repos = db.get_users_with_tracking_repos()
    tracking_repos = filter_tracking_repos(users_with_tracking_repos)
    print('tracking_repos', tracking_repos)

    for access_token, repos in tracking_repos.items():
        github_instance = get_github_instance(access_token)
        github_user = get_github_user_info(github_instance)
        temp_dir = TemporaryDirectory(prefix=str(github_user.id))
        for repo_dict in repos:
            repo = get_github_user_repo(github_instance, repo_dict['name'])
            commit_files = get_github_commit_files(github_user, repo)
            num_commit_files = len(commit_files)
            for i, commit_file in enumerate(commit_files):
                print('i, commit_file', i, commit_file.sha, commit_file.filename)
                if commit_file.filename[-2:] == 'py':
                    file_content = get_github_file_content(repo, commit_file)
                    commented_file_content = get_commented_file(
                        file_content)
                    update_github_file_content(
                        repo, commit_file, commented_file_content, f'ComGen commented - part {i}/{num_commit_files}')
