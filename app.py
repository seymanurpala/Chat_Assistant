import os

from flask import Flask

from backend.routes import bp

app = Flask(__name__)
app.register_blueprint(bp)


def is_debug_enabled():
    return os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes", "on"}


if __name__ == "__main__":
    app.run(debug=is_debug_enabled())
