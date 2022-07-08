from app import app
from app.database import *
with app.app_context():
    db.create_all()

app.run(debug=True)