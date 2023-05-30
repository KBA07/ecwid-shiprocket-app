from flask import redirect
import connexion

from connexion.resolver import RestyResolver

BASE_PATH = "/portfolios/ecwid-shiprocket-app"

def index():
    return redirect(BASE_PATH + "/ui")

def create_flask_app():
    app = connexion.FlaskApp(__name__, specification_dir='openapi/')
    app.add_api('api.yaml', resolver=RestyResolver('api'), base_path=BASE_PATH)

    # Registering a redirect from base path to swagger UI
    app.add_url_rule(BASE_PATH, 'index', index)

    return app

if __name__ == "__main__":
    app = create_flask_app()
    app.run(port=8081)