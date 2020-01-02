from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://nicat:Access2@mysqldb@68.183.66.167:3306/nicat'

db = SQLAlchemy(app)
Base = automap_base()
Base.prepare(db.engine, reflect=True)


User = Base.classes.user
Image = Base.classes.image
OwnerType = Base.classes.owner_type
Raspberry = Base.classes.raspberry
