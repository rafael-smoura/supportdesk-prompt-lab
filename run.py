"""Entrypoint para execução local e WSGI (gunicorn run:app)."""
import os
from backend import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1" if os.getenv("APP_ENV", "development") != "production" else "0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("APP_ENV") == "development",
    )
