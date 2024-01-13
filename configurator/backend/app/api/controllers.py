# Flask related methods...
from flask import Blueprint, request, flash, g, session, jsonify

# importing os module
import os

# Database
from app import db

# System libraries
from datetime import datetime
# Regular expressions libraries
import re

# Trace back libary
import traceback

# Configuration
from app import config_ as config

# Security helpers
from app.utils.utils import is_valid_session, hash_password, get_subject
from app.utils.utils import hash_string
from app.utils.utils import hash_bytes

# Datetime utilities
from datetime import date

# Threading stuff
from time import sleep
import threading

# Logging 
import logging

# OS and representation stuff
import os
from binascii import hexlify

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Database models
from app.api.models import DevicesModel
from app.api.models import MeshModel
from app.api.models import FirewallModel
from app.api.models import ACLModel

# Security stuff
from Crypto.Hash import SHA256

# Blueprint
mod_api = Blueprint("api", __name__, url_prefix="/api")


@mod_api.teardown_request
def teardown(error=None):
    try:
        pass
    except Exception as e:
        print(e)

@mod_api.route("/get_devices/", methods=["GET"])
def get_devices():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    
    devices = db.session.query(DevicesModel).all()

    result = []
    for device in devices:
        result.append({
            "id": device.id,
            "hit": device.hit,
            "ip": device.ip,
            "timestamp": device.timestamp,
            "name": device.name
        })
    return jsonify({
        "auth_fail": False,
        "result": result
    }, 200)

@mod_api.route("/get_device/", methods=["GET"])
def get_device():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    
    data = request.get_json(force=True)

    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    device_id = data.get("device_id", "")

    device = db.session.query(DevicesModel).filter_by(id = device_id).first()
    if not device:
        return jsonify({
            "auth_fail": False,
            "result": result,
            "reason": "Device not found"
        }, 200)
    
    result = {
        "id": device.id,
        "hit": device.hit,
        "ip": device.ip,
        "timestamp": device.timestamp,
        "name": device.name
    }
    return jsonify({
        "auth_fail": False,
        "result": result
    }, 200)

@mod_api.route("/get_acl/", methods=["POST"])
def get_groups():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    device_id = data.get("device_id", "")
    acl_list = db.session.query(ACLModel).filter_by(device_id = device_id).all()
    result = []
    for rule in acl_list:
        result.append({
            "mac1": rule.mac1,
            "mac2": rule.mac2,
            "rule": rule.rule,
            "ud": rule.id
        })
    return jsonify({
        "auth_fail": False,
        "result": result
    }, 200)

@mod_api.route("/add_acl_record/", methods=["POST"])
def add_acl_record():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    
    device_id = data.get("device_id", "")
    source_mac = data.get("source_mac", "").replace(":", "").strip()
    dest_mac = data.get("destination_mac", "").replace(":", "").strip()
    rule = data.get("destination_mac", "")

    acl = db.session.query(ACLModel).filter_by(db.and_(device_id = device_id,\
                                                       mac1 = source_mac,\
                                                       mac2 = dest_mac,\
                                                       rule = rule)).first()
    if acl:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Rule already exists"
        }, 200)
    
    acl = ACLModel()
    acl.device_id = device_id
    acl.mac1 = source_mac
    acl.mac2 = dest_mac
    acl.rule = rule
    db.session.add(acl)
    db.commit()

    return jsonify({
        "auth_fail": False,
        "result": True
    }, 200)

@mod_api.route("/update_acl_record/", methods=["POST"])
def update_acl_record():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    
    id = data.get("id", None)
    source_mac = data.get("source_mac", "").replace(":", "").strip()
    dest_mac = data.get("destination_mac", "").replace(":", "").strip()
    rule = data.get("rule", "")

    acl = db.session.query(ACLModel).filter_by(db.and_(id = id)).first()

    if not acl:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Rule does not exist"
        }, 200)
    
    acl.mac1 = source_mac
    acl.mac2 = dest_mac
    acl.rule = rule
    db.session.commit()

    return jsonify({
        "auth_fail": False,
        "result": True
    }, 200)

@mod_api.route("/delete_acl_record/", methods=["POST"])
def delete_acl_record():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    
    id = data.get("id", None)
    
    acl = db.session.query(ACLModel).filter_by(db.and_(id = id)).first()

    if not acl:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Rule does not exist"
        }, 200)
    
    db.session.delete(acl)
    db.session.commit()

    return jsonify({
        "auth_fail": False,
        "result": True
    }, 200)

@mod_api.route("/get_firewall_rules/", methods=["POST"])
def get_firewall_rules():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    
    rules = db.session.query(FirewallModel).all()

    result = []
    for rule in rules:
        result.append({
            "device_1": rule.device_1_id,
            "device_2": rule.device_2_id,
            "rule": rule.rule
        });
    
    return jsonify({
        "auth_fail": False,
        "result": result
    }, 200)

@mod_api.route("/add_firewall_record/", methods=["POST"])
def add_firewall_record():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    
    device_1_id = data.get("device_1_id", "")
    device_2_id = data.get("device_2_id", "")
    rule = data.get("rule", "")

    device = db.session.query(DevicesModel).filter_by(id = device_1_id).first()
    if not device:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Device not found"
        }, 200)

    device = db.session.query(DevicesModel).filter_by(id = device_2_id).first()
    if not device:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Device not found"
        }, 200)
    
    firewall_rule = db.session.query(FirewallModel).filter_by(db.and_(device_1_id = device_1_id, device_2_id = device_2_id, rule = rule)).first()
    if firewall_rule:
         return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Rule already exists"
        }, 200)
    
    firewall_rule = FirewallModel()
    firewall_rule.device_1_id = device_1_id
    firewall_rule.device_2_id = device_2_id
    firewall_rule.rule = rule
    db.session.add(firewall_rule)
    db.session.commit() 

    return jsonify({
        "auth_fail": False,
        "result": True
    }, 200)

@mod_api.route("/update_firewall_record/", methods=["POST"])
def update_firewall_record():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    
    id = data.get("id", None)
    device_1_id = data.get("device_1_id", "")
    device_2_id = data.get("device_2_id", "")
    rule = data.get("rule", "")

    device = db.session.query(DevicesModel).filter_by(id = device_1_id).first()
    if not device:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Device not found"
        }, 200)

    device = db.session.query(DevicesModel).filter_by(id = device_2_id).first()
    if not device:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Device not found"
        }, 200)
    
    firewall_rule = db.session.query(FirewallModel).filter_by(db.and_(device_1_id = device_1_id, device_2_id = device_2_id, rule = rule)).first()
    if firewall_rule:
         return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Rule already exists"
        }, 200)
    
    firewall_rule = db.session.query(FirewallModel).filter_by(db.and_(id = id)).first()
    if not firewall_rule:
         return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Rule does not exist"
        }, 200)
    
    firewall_rule.device_1_id = device_1_id
    firewall_rule.device_2_id = device_2_id
    firewall_rule.rule = rule
    db.session.commit() 

    return jsonify({
        "auth_fail": False,
        "result": True
    }, 200)

@mod_api.route("/delete_firewall_record/", methods=["POST"])
def delete_firewall_record():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    
    id = data.get("id", None)
    
    firewall_rule = db.session.query(FirewallModel).filter_by(db.and_(id = id)).first()
    if not firewall_rule:
         return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Rule does not exist"
        }, 200)
    
    db.session.delete(firewall_rule)
    db.session.commit() 

    return jsonify({
        "auth_fail": False,
        "result": True
    }, 200)

@mod_api.route("/get_mesh/", methods=["POST"])
def get_mesh():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    
    mesh = db.session.qeury(MeshModel).all()

    result = []
    for m in mesh:
        result.append({
            "device_1_id": mesh.device_1_id,
            "device_2_id": mesh.device_2_id
        })
    return jsonify({
        "auth_fail": False,
        "result": result
    }, 200)

@mod_api.route("/add_mesh/", methods=["POST"])
def add_mesh():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    
    mesh = db.session.qeury(MeshModel).all()

    result = []
    for m in mesh:
        result.append({
            "device_1_id": mesh.device_1_id,
            "device_2_id": mesh.device_2_id
        })
    return jsonify({
        "auth_fail": False,
        "result": True
    }, 200)

@mod_api.route("/update_mesh/", methods=["POST"])
def update_mesh():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    
    id = data.get("id", None)
    device_1_id = data.get("device_1_id", "")
    device_2_id = data.get("device_2_id", "")

    device = db.session.query(DevicesModel).filter_by(id = device_1_id).first()
    if not device:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Device not found"
        }, 200)

    device = db.session.query(DevicesModel).filter_by(id = device_2_id).first()
    if not device:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Device not found"
        }, 200)
    mesh = db.session.query(MeshModel).filter_by(id = id).first()
    if not mesh:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Mesh record was not found"
        }, 200)
    mesh.device_1_id = device_1_id
    mesh.device_2_id = device_2_id
    db.session.commit()
    return jsonify({
        "auth_fail": False,
        "result": True
    }, 200)

@mod_api.route("/delete_mesh/", methods=["POST"])
def delete_mesh():
    if not is_valid_session(request, config):
        return jsonify({"auth_fail": True}, 403)
    data = request.get_json(force=True)
    if not data:
        return jsonify({"auth_fail": False, "result": False}, 400)
    
    id = data.get("id", None)

    mesh = db.session.query(MeshModel).filter_by(id = id).first()
    if not mesh:
        return jsonify({
            "auth_fail": False,
            "result": False,
            "reason": "Mesh record was not found"
        }, 200)
    
    db.session.delete(mesh)
    db.session.commit()

    return jsonify({
        "auth_fail": False,
        "result": True
    }, 200)
    
    return jsonify({
        "auth_fail": False,
        "result": True
    }, 200)