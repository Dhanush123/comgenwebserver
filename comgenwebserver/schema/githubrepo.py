from marshmallow import Schema, fields, pre_dump


class GithubRepoSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    html_url = fields.Str(required=True)
    archive_url = fields.URL(required=True)
    stargazers_count = fields.Integer(required=True)
