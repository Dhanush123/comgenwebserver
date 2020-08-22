from tempfile import NamedTemporaryFile  # , TemporaryDirectory,
from collections import OrderedDict
import csv
import ast
import inspect
import os

import astunparse

from comgenwebserver.db.service import DBClient
from comgenwebserver.schema.githubuser import GithubUserSchema
from comgenwebserver.helpers.github import filter_tracking_repos, get_github_instance, get_github_user_info, get_github_commit_files, get_github_file_content, get_github_user_repo, update_github_file_content
from comgenwebserver.helpers.astfunctionsextractor import ASTFunctionsExtractor
from comgenwebserver.constants import FUNCTION_NAME_COLUMN, AST_COLUMN, AST_CSV_FIELDNAMES
from comgenwebserver.helpers.model import get_model_predictions
from comgenwebserver.helpers.docstringinserter import DocstringInserter


def get_repos_and_comment_commit_files():

    # install_some_dependencies()

    db = DBClient()
    users_records = [GithubUserSchema().load(user_record)
                     for user_record in db.get_users_with_tracking_repos()]

    users_with_tracking_repos = db.get_users_with_tracking_repos()
    tracking_repos = filter_tracking_repos(users_with_tracking_repos)
    print('tracking_repos', tracking_repos)

    for access_token, repos in tracking_repos.items():
        github_instance = get_github_instance(access_token)
        github_user = get_github_user_info(github_instance)
        # with TemporaryDirectory(prefix=str(github_user.id)) as temp_dir:
        for repo_dict in repos:
            repo = get_github_user_repo(github_instance, repo_dict['name'])
            commit_files = get_github_commit_files(github_user, repo)
            num_commit_files = sum(
                [1 for commit_file in commit_files if is_commit_file_python(commit_file)])
            for i, commit_file in enumerate(commit_files):
                print('i, commit_file', i, commit_file.sha,
                      commit_file.filename)
                if is_commit_file_python(commit_file):
                    file_content = get_github_file_content(
                        repo, commit_file)
                    update_github_file_content(
                        repo, commit_file, get_comment_file_content(file_content, commit_file.filename), f'ComGen commented - part {i}/{num_commit_files}')

                    # update_github_file_content(
                    #     repo, commit_file, get_comment_file_content(temp_dir, file_content, commit_file.filename), f'ComGen commented - part {i}/{num_commit_files}')


def get_comment_file_content(file_content, py_filename):
    print("get_comment_file_content...")
    # os.path.join(temp_dir, py_filename)
    # temp_py_path = NamedTemporaryFile(suffix='.py')
    temp_py = NamedTemporaryFile(mode="a+", suffix='.py', delete=False)
    # temp_py_path.replace('.py', '-ast.csv')
    # temp_ast_csv_path = NamedTemporaryFile(suffix='.csv')
    temp_ast_csv = NamedTemporaryFile(mode="a+", suffix='.csv', delete=False)
    # temp_py_path.replace('.py', '-ast.txt')
    # temp_ast_txt_path = NamedTemporaryFile(suffix='.txt')
    temp_ast_txt = NamedTemporaryFile(mode="a+", suffix='.txt', delete=False)
    # with open(temp_py_path, 'a+') as temp_py_file:
    # temp_py_file.write(file_content)

    temp_py.write(file_content)
    temp_py.seek(0)
    # print("file_content!!!", file_content)
    # temp_py.seek(0)
    # print("temp py!!!", temp_py.read())

    # 1: py -> ast
    py_to_ast_converter = ASTFunctionsExtractor(
        temp_py, temp_ast_csv)  # temp_py_path, temp_ast_csv_path
    py_to_ast_converter.visit(py_to_ast_converter.ast_object)
    # 2: ast -> docstring preds
    preds_map = OrderedDict()
    asts = []
    # with open(temp_ast_csv_path, newline='') as temp_ast_csv_file:
    #     ast_reader = csv.reader(temp_ast_csv_file)
    #     for i, ast_row in enumerate(ast_reader):
    #         asts.append(ast_row[AST_COLUMN])
    #         preds_map[ast_row[FUNCTION_NAME_COLUMN]] = {
    #             'row_num': i, 'docstring': ''}
    temp_ast_csv.seek(0)
    ast_reader = csv.DictReader(
        temp_ast_csv, fieldnames=AST_CSV_FIELDNAMES)
    # temp_ast_csv.seek(0)
    # print('temp_ast_csv.read()', temp_ast_csv.read())
    i = 0
    for ast_row in ast_reader:
        asts.append(ast_row[AST_COLUMN])
        preds_map[ast_row[FUNCTION_NAME_COLUMN]] = {
            'row_num': i, 'docstring': ''}
        i += 1

    print("preds_map", preds_map)
    print("asts", asts)

    # with open(temp_ast_txt_path, 'a+') as temp_ast_file:
    # temp_ast_file.writelines(asts)
    temp_ast_txt.writelines(asts)
    temp_ast_txt.seek(0)

    # predictions = get_model_predictions(temp_ast_txt_path)
    predictions = get_model_predictions(temp_ast_txt)

    # 3: insert preds into full python file ast
    original_py_ast_tree = ast.parse(temp_py)  # temp_py_path
    docstring_inserter = DocstringInserter(preds_map)
    new_py_ast_tree = transformer.visit(original_py_ast_tree)
    ast.fix_missing_locations(new_py_ast_tree)
    new_py_code = astunparse.unparse(
        ast.parse(inspect.getsource(new_py_ast_tree)))

    temp_py.close()
    temp_ast_csv.close()
    temp_ast_txt.close()

    print('new_py_code', new_py_code)

    return new_py_code


def is_commit_file_python(commit_file):
    return commit_file.filename[-2:] == 'py'
