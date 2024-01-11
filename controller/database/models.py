from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

base = declarative_base()


class DevicesModel(base):
    __tablename__ = 'Devices'
    id = sa.Column(sa.Integer, primary_key = True)
    name = sa.Column(sa.String(100), nullable = False)
    hit = sa.Column(sa.String(100), nullable = False)
    ip = sa.Column(sa.String(100), nullable = False)

class MeshModel(base):
    __tablename__ = 'Mesh'
    id = sa.Column(sa.Integer, primary_key = True)
    name = sa.Column(sa.String(100), nullable = False)
    device_1_id = sa.Column(sa.Integer, nullable = False)
    device_2_id = sa.Column(sa.Integer, nullable = False)

class FirewallModel(base):
    __tablename__ = 'Firewall'
    id = sa.Column(sa.Integer, primary_key = True)
    device_1_id = sa.Column(sa.Integer, nullable = False)
    device_2_id = sa.Column(sa.Integer, nullable = False)
    rule = sa.Column(sa.String(100), nullable = False)

class ACLModel(base):
    __tablename__ = 'Firewall'
    id = sa.Column(sa.Integer, primary_key = True)
    device_id = sa.Column(sa.Integer, nullable = False)
    mac1 = sa.Column(sa.Integer, nullable = False)
    mac2 = sa.Column(sa.Integer, nullable = False)
    rule = sa.Column(sa.String(100), nullable = False)

class HashesModel(base):
    __tablename__ = 'Hashes'
    id = sa.Column(sa.Integer, primary_key = True)
    device_id = sa.Column(sa.Integer, nullable = False)
    type = sa.Column(sa.String(8), nullable = False, default = "mesh")
    hash = sa.Column(sa.String(32), nullable = False)


