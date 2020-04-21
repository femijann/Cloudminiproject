from flask import Flask, request, jsonify
from cassandra.cluster import Cluster
import json
import requests
cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session = cluster.connect()
app = Flask(__name__)

@app.route('/')
def hello():
    name = request.args.get("name","World")
    return('<h1>Hello, {}!</h1>'.format(name))

@app.route('/regional', methods=['GET'])
def profile():
    rows = session.execute( """Select * From carbon_int.stats""")
    result = []
    for record in rows:
        result.append({"key": record.key,"fuel": record.fuel,"int_ind": record.int_ind,"intensity": record.intensity,"perc": record.perc,"region_desc": record.region_desc,"region_id": record.region_id})
    return jsonify(result)

@app.route('/regional/<postcode>', methods=['GET'])
def external(postcode):
    headers={'Accept':'application/json'}
    carbon_int_url_template = 'https://api.carbonintensity.org.uk/regional/postcode/{postcode}'
    carbon_int_url= carbon_int_url_template.format(postcode = postcode)
    resp = requests.get(carbon_int_url)
    if resp.ok:
        return jsonify(resp.json())
    else:
        print(resp.reason)

@app.route('/regional/', methods=['POST'])
def create():
    session.execute("""INSERT INTO carbon_int.stats(key,fuel,int_ind,intensity,perc,region_desc,region_id) VALUES ({},'{}',{},'{}',{},'{}',{}) """.format(int(request.json['key']),request.json['fuel'],int(request.json['int_ind']),request.json['intensity'],float(request.json['perc']),request.json['region_desc'], int(request.json['region_id'])))
    return jsonify({'message':'created: /regional/{}'.format(request.json['key'])}),  201

@app.route('/regional/', methods=['PUT'])
def update():
    session.execute("""UPDATE carbon_int.stats SET perc= {} WHERE key={}""".format(float(request.json['perc']),int(request.json['key'])))
    return jsonify({'message':'updated: /regional/{}'.format(request.json['key'])}),  200

@app.route('/regional/', methods=['DELETE'])
def delete():
    session.execute("""DELETE FROM carbon_int.stats WHERE key={}""".format(int(request.json['key'])))
    return jsonify({'message':'deleted: /regional/{}'.format(request.json['key'])}),  200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'))
