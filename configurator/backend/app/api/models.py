from app import db

class DevicesModel(db.Model):
    __tablename__ = 'Devices'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(100), nullable = False)
    hit = db.Column(db.String(100), nullable = False)
    ip = db.Column(db.String(100), nullable = False)
    timestamp = db.Column(db.Integer, nullable = False)

class MeshModel(db.Model):
    __tablename__ = 'Mesh'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(100), nullable = False)
    device_1_id = db.Column(db.Integer, nullable = False)
    device_2_id = db.Column(db.Integer, nullable = False)

class FirewallModel(db.Model):
    __tablename__ = 'Firewall'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    device_1_id = db.Column(db.Integer, nullable = False)
    device_2_id = db.Column(db.Integer, nullable = False)
    rule = db.Column(db.String(100), nullable = False)

class ACLModel(db.Model):
    __tablename__ = 'ACL'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    device_id = db.Column(db.Integer, nullable = False)
    mac1 = db.Column(db.Integer, nullable = False)
    mac2 = db.Column(db.Integer, nullable = False)
    rule = db.Column(db.String(100), nullable = False)


