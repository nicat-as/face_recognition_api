from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] =''

db = SQLAlchemy(app)
Base = automap_base()
Base.prepare(db.engine, reflect=True)


User = Base.classes.user
Image = Base.classes.image
OwnerType = Base.classes.owner_type
Raspberry = Base.classes.raspberry
