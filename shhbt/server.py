import os

from flask import Flask, Response, request

from shhbt.gitclient.gitlab import handle_gitlab_event
from shhbt.session import Session


def create_flask_app(config=None):
    app = Flask(__name__)

    if config is not None:
        app.config.update(config)

    @app.route("/", methods=["POST"])
    def handle_hook():
        if request.headers.get("X-Gitlab-Event") is not None:
            req = request.get_json()

            if req.get("event_type") == "merge_request":
                handle_gitlab_event(req)
                return Response(status=200)

        return Response(status=400)

    return app
