from marshmallow import Schema, fields, EXCLUDE


class GithubRepoSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    html_url = fields.Str(required=True)
    archive_url = fields.URL(required=True)
    stargazers_count = fields.Integer(required=True)
    tracking = fields.Boolean(default=False)
