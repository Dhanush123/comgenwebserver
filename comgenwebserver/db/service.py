import copy

from comgenwebserver.db import Repository
from comgenwebserver.db.mongo import MongoRepository
from comgenwebserver.schema.githubrepo import GithubRepoSchema
from comgenwebserver.schema.githubuser import GithubUserSchema
from comgenwebserver.helpers.github import get_github_instance, get_github_user_info, get_github_user_repos


class DBClient(object):
    def __init__(self, access_token, repo_client=Repository(adapter=MongoRepository)):
        self.access_token = access_token
        self.repo_client = repo_client

        if not access_token:
            raise Exception("access_token not provided")

    def create_user_info_and_repos(self):
        github_instance = get_github_instance(self.access_token)
        user_info = get_github_user_info(github_instance)
        user_repos = get_github_user_repos(github_instance)
        user_info_extracted = {"access_token": self.access_token, "id": user_info.id, "login": user_info.login,
                               "name": user_info.name, "html_url": user_info.html_url}

        repos_extracted = []
        for repo in user_repos:
            repo_extracted = {"id": repo.id, "name": repo.name, "html_url": repo.html_url,
                              "archive_url": repo.archive_url, "stargazers_count": repo.stargazers_count}
            repos_extracted.append(repo_extracted)
        user_info_extracted["repos"] = repos_extracted

        final_data = GithubUserSchema().dump(user_info_extracted)
        self.repo_client.create(final_data)
