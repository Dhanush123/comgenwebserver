from marshmallow import Schema, fields

from comgenwebserver.schema.githubrepo import GithubRepoSchema


class GithubUserSchema(Schema):
    id = fields.Str(required=True)
    access_token = fields.Str(required=True)
    login = fields.Str(required=True)
    name = fields.Str(required=True)
    html_url = fields.URL(required=True)
    repos = fields.List(fields.Nested(GithubRepoSchema), required=True)
