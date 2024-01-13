from app import db

class Users(db.Model):
	__tablename__ = "Users";

	id                 = db.Column(db.Integer,      nullable=False, primary_key=True, autoincrement = True)
	username           = db.Column(db.String(100),  nullable=False)
	password           = db.Column(db.String(100),  nullable=False)
	salt               = db.Column(db.String(100),  nullable=False)


