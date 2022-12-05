from threading import Thread
import time
import pika

from flask import Flask, json, jsonify, request
from flask_cors import cross_origin, CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from models import Role, User, Device, Measurement
from requests import *


from models import Base

que = 'coada_vietii'

DATABASE_URI = "postgresql://postgres:password@database:5432/utilitiesDB"
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.secret_key = '16827398671235867591423'
engine = create_engine(DATABASE_URI, echo=False)

if not database_exists(engine.url):
	create_database(engine.url)

Session = sessionmaker(bind=engine)
session = Session()

url = 'amqps://ynwbwptb:jv1dmvdqmuEFSABp9fSoZYOAsM5ha69j@goose.rmq2.cloudamqp.com:5671/ynwbwptb'


def thread_iepure():
    print('HERE')
    def callback(ch, method, properties, body):
        print('Received: ' + str(body))

    connection = pika.BlockingConnection(pika.connection.URLParameters(url))
    channel = connection.channel()
    channel.queue_declare(queue=que)

    channel.basic_consume(queue=que, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()



# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


########################################################################################################
# User requests
########################################################################################################
@app.route(request_all_users, methods=['GET'])
def get_all_users():
    users = session.query(User).all()
    result = []
    for i in users:
        result.append({'id': i.id, 'username': i.username, 'name': i.name, 'role_id': i.role_id})
    if len(result) < 1:
        return '0'
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route(request_user, methods=['GET'])
def get_user():
    users = session.query(User).all()
    data = request.json
    for i in users:
        print(str(i.id) + " " + str(data['id']) + "\n")
        if i.id == data['id']:
            result = {'id': i.id, 'username': i.username, 'name': i.name, 'role_id': i.role_id}
            print(result)
            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
    return '0'


@app.route(request_add_user, methods=['POST'])
@cross_origin()
def create_user():
    data = request.json
    user = User(username=data['username'], password=['password'], name=data['name'], role_id=data['role_id'])
    session.add(user)
    session.commit()
    users = session.query(User).all()
    for i in users:
        if i.id == user.id:
            result = {'id': i.id, 'username': i.username, 'password': i.password, 'name': i.name, 'role_id': i.role_id}
            print(result)
            return jsonify(result)
    return jsonify({'id': '404',
                    'name': 'not_found'})


@app.route(request_update_user, methods=['PUT'])
@cross_origin()
def update_user():
    data = request.json
    user = session.query(User).filter_by(id=data['id']).first()
    user.password = data['password']
    user.username = data['username']
    user.name = data['name']
    user.role_id = data['role_id']
    session.commit()
    return jsonify({'id': user.id, 'name': user.name, 'role_id': user.role_id})


@app.route(request_delete_user, methods=['DELETE'])
@cross_origin()
def delete_user():
    data = request.json
    user = session.query(User).filter_by(id=data['id']).first()
    session.delete(user)
    session.commit()
    users = session.query(User).all()
    result = []
    for i in users:
        result.append({'id': i.id, 'name': i.name, 'role_id': i.role_id})
    return jsonify(result)


@app.route(request_login_user, methods=['POST'])
@cross_origin()
def login_user():
    users = session.query(User).all()
    data = request.json
    for i in users:
        if i.username == data['username'] and i.password == data['password']:
            result = {'none': 'ok', 'id': i.id, 'username': i.username, 'name': i.name, 'role_id': i.role_id}
            return jsonify(result)
    return jsonify({'none': 'none'})


@app.route(request_associate_device, methods=['PUT'])
@cross_origin()
def associates_device():
    data = request.json
    user = session.query(User).filter_by(id=data['user_id']).first()
    device = session.query(Device).filter_by(id=data['device_id']).first()
    if user is not None:
        if device is not None:
            device.user_id = user.id
            result = {'id': device.id, 'description': device.description, 'address': device.address,
                      'max_energy': device.max_energy,
                      'user_id': device.user_id}
            return jsonify(result)
    return '0'


########################################################################################################
# Device requests
########################################################################################################
@app.route(request_all_devices, methods=['GET'])
@cross_origin()
def get_all_devices():
    users = session.query(Device).all()
    result = []
    for i in users:
        result.append(
            {'id': i.id, 'description': i.description, 'address': i.address, 'max_energy': i.max_energy,
             'user_id': i.user_id})
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return jsonify(result)


@app.route(request_device, methods=['GET'])
def get_device():
    users = session.query(Device).all()
    data = request.json
    for i in users:
        if i.id == data['id']:
            result = {'id': i.id, 'description': i.description, 'address': i.address, 'max_energy': i.max_energy,
                      'user_id': i.user_id}
            return jsonify(result)
    return jsonify({'none': 'none'})


@app.route(request_all_for_user, methods=['POST'])
@cross_origin()
def get_devices_by_user_id():
    devices = session.query(Device).all()
    data = request.json
    result = []
    print(data['user_id'])
    for i in devices:
        if i.user_id == data['user_id']:
            result.append({'id': i.id, 'description': i.description, 'address': i.address, 'max_energy': i.max_energy,
                           'user_id': i.user_id})
    print(result)
    return jsonify(result)


@app.route(request_add_device, methods=['POST'])
@cross_origin()
def create_device():
    data = request.json
    print(data)
    user = Device(description=data['description'], address=data['address'], max_energy=data['max_energy'])
    session.add(user)
    session.commit()
    users = session.query(Device).all()
    for i in users:
        if i.id == user.id:
            result = {'id': i.id, 'description': i.description, 'address': i.address, 'max_energy': i.max_energy,
                      'user_id': i.user_id}
            print(result)
            return jsonify(result)
    return jsonify({'id': '404',
                    'name': 'not_found'})


@app.route(request_update_device, methods=['POST'])
@cross_origin()
def update_device():
    data = request.json
    user = session.query(Device).filter_by(id=data['id']).first()
    if data['description']:
        user.description = data['description']
    if data['address']:
        user.address = data['address']
    if data['max_energy']:
        user.max_energy = data['max_energy']
    if data['user_id'] == '0':
        user.user_id = None
    else:
        user.user_id = data['user_id']
    session.commit()
    return jsonify(
        {'id': user.id, 'description': user.description, 'address': user.address, 'max_energy': user.max_energy,
         'user_id': user.user_id})


@app.route(request_delete_device, methods=['DELETE'])
def delete_device():
    data = request.json
    user = session.query(Device).filter_by(id=data['id']).first()
    session.delete(user)
    session.commit()
    users = session.query(Device).all()
    result = []
    for i in users:
        result.append({'id': i.id, 'description': i.description, 'address': i.address, 'max_energy': i.max_energy,
                       'user_id': i.user_id})
    return jsonify(result)


########################################################################################################
# Measurements requests
########################################################################################################
@app.route(request_all_measurements, methods=['GET'])
def get_all_measurements():
    users = session.query(Measurement).all()
    result = []
    for i in users:
        result.append(
            {'id': i.id, 'timestamp': i.timestamp, 'energy': i.energy, 'device_id': i.device_id})
    return jsonify(result)


@app.route(request_all_for_device, methods=['POST'])
@cross_origin()
def get_all_measurements_by_device_id():
    data = request.json
    measurements = session.query(Measurement).all()
    result = []
    print(data['device_id'])
    for i in measurements:
        if i.device_id == data['device_id']:
            result.append(
                {'id': i.id, 'timestamp': i.timestamp, 'energy': i.energy, 'device_id': i.device_id})
    print(result)
    return jsonify(result)


@app.route(request_measurement, methods=['GET'])
@cross_origin()
def get_measurement():
    users = session.query(Measurement).all()
    data = request.json
    for i in users:
        if i.id == data['id']:
            result = {'id': i.id, 'timestamp': i.timestamp, 'energy': i.energy, 'device_id': i.device_id}
            return jsonify(result)
    return jsonify({'id': '404',
                    'name': 'not_found'})


@app.route(request_add_measurement, methods=['POST'])
def create_measurement():
    data = request.json
    user = Measurement(timestamp=data['timestamp'], energy=data['energy'], device_id=data['device_id'])
    session.add(user)
    session.commit()
    users = session.query(Measurement).all()
    for i in users:
        if i.id == user.id:
            result = {'id': i.id, 'timestamp': i.timestamp, 'energy': i.energy, 'device_id': i.device_id}
            print(result)
            return jsonify(result)
    return jsonify({'id': '404',
                    'name': 'not_found'})


@app.route(request_update_measurement, methods=['POST'])
def update_measurement():
    data = request.json
    user = session.query(Measurement).filter_by(id=data['id']).first()
    user.name = data['name']
    user.role_id = data['role_id']
    session.commit()
    return jsonify({'id': user.id, 'timestamp': user.timestamp, 'energy': user.energy, 'device_id': user.device_id})


@app.route(request_delete_measurement, methods=['DELETE'])
def delete_measurement():
    data = request.json
    user = session.query(Measurement).filter_by(id=data['id']).first()
    session.delete(user)
    session.commit()
    users = session.query(Measurement).all()
    result = []
    for i in users:
        result.append({'id': i.id, 'timestamp': i.timestamp, 'energy': i.energy, 'device_id': i.device_id})
    return jsonify(result)


@app.route('/example-insert', methods=['GET'])
def example_insert():
    # roles
    admin_role = Role(role="admin")
    basic_role = Role(role="basic")
    # users
    user1 = User(username='John232', password='asdfgh', name="John", role_id=1)
    user2 = User(username='Mary20', password='asdfgh', name="Mary", role_id=2)
    user3 = User(username='Alex34', password='asdfgh', name="Alex", role_id=2)
    user4 = User(username='Marin_12', password='asdfgh', name="Marin", role_id=2)
    # devices
    device1 = Device(description="electric meter", address="str2", max_energy=2400.0)
    device2 = Device(description="electric meter", address="str3", max_energy=1400.0)
    device3 = Device(description="electric meter", address="str4", max_energy=4400.0)
    device4 = Device(description="electric meter", address="str5", max_energy=5400.0)
    # measurements
    m1 = Measurement(timestamp="2012-03-16 00:00:00+0000", energy=34.0, device_id=1)
    m2 = Measurement(timestamp="2012-03-16 00:00:00+0000", energy=35.0, device_id=1)
    m3 = Measurement(timestamp="2012-03-16 00:00:00+0000", energy=22.0, device_id=1)
    m4 = Measurement(timestamp="2012-03-16 00:00:00+0000", energy=10.0, device_id=2)
    m5 = Measurement(timestamp="2012-03-16 00:00:00+0000", energy=100.0, device_id=2)
    m6 = Measurement(timestamp="2012-03-16 00:00:00+0000", energy=230.0, device_id=2)
    m7 = Measurement(timestamp="2012-03-16 00:00:00+0000", energy=140.0, device_id=2)
    m8 = Measurement(timestamp="2012-03-16 00:00:00+0000", energy=30.0, device_id=2)
    m9 = Measurement(timestamp="2012-03-16 00:00:00+0000", energy=3.0, device_id=3)
    m10 = Measurement(timestamp="2012-03-16 00:00:00+0000", energy=23.0, device_id=3)

    session.add_all([admin_role, basic_role, user1, user2, user3, user4, device1, device2, device3, device4])
    session.add_all([m1, m2, m3, m4, m5, m6, m7, m8, m9, m10])
    session.commit()
    return "0"


@app.route('/example-select')
def example_select():
    users = session.query(User)
    for i in users:
        print(i)
    # with filter
    users = session.query(User).filter(User.role_id == 1).all()
    for i in users:
        print(i.name + ' ' + str(i.role) + "\n")
    return jsonify({'name': 'alice',
                    'email': 'alice@outlook.com'})


@app.route("/name/<name>")
def get_book_name(name):
    return "name : {}".format(name)


@app.route("/details")
def get_book_details():
    author = request.json.get('author')
    published = request.json.get('published')
    return "Author : {}, Published: {}".json(author, published)


th = Thread(target=thread_iepure)
th.start()

if __name__ == '__main__':
    app.run()



