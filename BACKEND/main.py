import sys

from api import app
from api.db.bootstrap import run_bootstrap


if len(sys.argv)>1 and sys.argv[1] == 'list':
    print(app.url_map)
elif __name__ == '__main__':
    with app.app_context():
        run_bootstrap()
    app.run(debug=True, port=5500)