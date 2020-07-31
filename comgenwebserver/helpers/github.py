from github import Github


def get_github_instance(access_token):
    return Github(access_token)


def get_github_user_info(github_instance):
    return github_instance.get_user()


def get_github_user_repos(github_instance):
    user = get_github_user_info(github_instance)
    repos = user.get_repos('all')
    return repos
