import copy

from comgenwebserver.db import Repository
from comgenwebserver.db.mongo import MongoRepository
from comgenwebserver.schema.githubrepo import GithubRepoSchema
from comgenwebserver.schema.githubuser import GithubUserSchema
from comgenwebserver.helpers.github import get_github_instance, get_github_user_info, get_github_user_repos


class DBClient(object):
    def __init__(self, access_token='', db_client=Repository(adapter=MongoRepository)):
        self.access_token = access_token
        self.db_client = db_client
        self.github_instance = None
        if access_token:
            try:
                self.github_instance = get_github_instance(self.access_token)
            except:
                raise Exception(
                    "unable to get_github_instance from access_token")

    def dump_github_user(self, data):
        if '_id' in data:
            del data['_id']
        return GithubUserSchema().dump(data)

    def create_user_info_and_repos(self):
        try:
            user_info = get_github_user_info(self.github_instance)
            user_info_extracted = {'access_token': self.access_token, 'id': user_info.id, 'login': user_info.login,
                                   'name': user_info.name, 'html_url': user_info.html_url}
            user_info_extracted['repos'] = self.get_relevant_repos_info()

            final_data = self.dump_github_user(user_info_extracted)

            print("create_user_info_and_repos",
                  self.db_client.create(final_data))
            return True
        except Exception as e:
            print('error in create_user_info_and_repos', e)
            return False

    def get_relevant_repos_info(self):
        try:
            user_repos = get_github_user_repos(self.github_instance)
            repos_extracted = []
            for repo in user_repos:
                repo_extracted = {'id': repo.id, 'name': repo.name, 'html_url': repo.html_url,
                                  'archive_url': repo.archive_url, 'stargazers_count': repo.stargazers_count}
                repos_extracted.append(repo_extracted)
            return repos_extracted
        except Exception as e:
            print('error in get_relevant_repos_info', e)
            return []

    def get_user_record(self):
        user_info_latest = get_github_user_info(self.github_instance)
        user_info_found = self.db_client.find(
            {'id': f'{user_info_latest.id}'})
        print("user_info_found", user_info_found["id"])
        user_info_validated = self.dump_github_user(user_info_found)
        return user_info_validated

    def is_existing_user(self):
        try:
            return bool(self.get_user_record())
        except Exception as e:
            print('error in is_existing_user', e)
            return False

    def toggle_repo_tracking_status(self, repo_id, toggle_status):
        try:
            user_record = self.get_user_record()
            for repo in user_record['repos']:
                if repo['id'] == repo_id:
                    repo['tracking'] = toggle_status
                    break

            print('toggle_repo_tracking_status', self.db_client.update(
                {'id': f'{user_record["id"]}'}, user_record))
            return True
        except Exception as e:
            print('error in toggle_repo_tracking_status', e)
            return False

    def get_users_with_tracking_repos(self):
        return self.db_client.find_all({'repos.tracking': True})
