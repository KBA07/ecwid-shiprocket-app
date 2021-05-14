import connexion

from connexion.resolver import RestyResolver

app = connexion.FlaskApp(__name__, specification_dir='openapi/')
app.add_api('api.yaml', resolver=RestyResolver('api'))


if __name__ == "__main__":
    app.run(port=8081)