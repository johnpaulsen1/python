from flask import Flask
from penguins.__init__ import (create_app, app)

if __name__ == "__main__":
    create_app()
    app.run(host='0.0.0.0')
