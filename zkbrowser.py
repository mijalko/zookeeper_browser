from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
from flask import session
from flask import redirect
from flask import Blueprint
import collections
import datetime
import sys
import os

from kazoo.client import KazooClient

app = Flask(__name__)
app.secret_key = 'my secret key'
app.config['SESSION_TYPE'] = 'filesystem'
defaultZK = os.environ.get("ZOOKEEPER_SERVERS", "127.0.0.1:2181")

bp = Blueprint('zookeeper_browser', __name__, template_folder="templates", static_folder="static")



@bp.route('/', methods=["GET", "POST"])
def index():
    if "connection_string" not in session or not session["connection_string"]:
        return redirect(url_for("zookeeper_browser.connect"))

    connection_string = session["connection_string"]

    try:
        zk = KazooClient(hosts=connection_string, timeout=2)
        zk.start()
        connected = True
        session["connection_string"] = connection_string
    except Exception, ex:
        connected = False
        connection_error = "Cannot connect to zookeeoer. {}".format(str(ex))
        if "connection_string" in session:
            del session["connection_string"]
        return redirect(url_for("zookeeper_browser.connect"))
    try:
        # build path element
        path = request.args.get('path', "")
        path_elements = path.split("/")

        path_parts = []
        path_parts.append(("/", url_for("zookeeper_browser.index")))

        if request.method == 'POST':
            if "submitbtn" in request.form and request.form['submitbtn'] == "update":
                node_val = request.form.get('node_val', None)
                zk.set(path, node_val.encode('ascii', 'replace'))
            elif request.form["submitDocUpdate"] == "Delete" and path.strip() != '':
                path = path.rstrip('/')
                zk.delete("/" + path, recursive=True)
                # change path to parent
                path = path[:path.rfind('/')]

                return redirect(url_for("zookeeper_browser.index", path=path))
            elif request.form["submitDocUpdate"] == "Add":
                zk.ensure_path("/" + path.rstrip('/') + "/" + request.form["node_name"])
                # change path to parent

        current_path = ""

        for p in path_elements:
            if p == "":
                continue
            if len(current_path) == 0:
                current_path += p
            else:
                current_path += "/" + p
            path_parts.append((p, url_for("zookeeper_browser.index", path=current_path)))

        # list children
        children = zk.get_children(path)
        children_path = []
        for child in children:
            if len(path) > 0:
                children_path.append((child, url_for("zookeeper_browser.index", path=path + "/" + child)))
            else:
                children_path.append((child, url_for("zookeeper_browser.index", path=child)))

        # current path data
        node_data = zk.get(path)
        node_properties = []
        node_properties.append(("creation_transaction_id", node_data[1].creation_transaction_id))
        node_properties.append(("last_modified_transaction_id", node_data[1].last_modified_transaction_id))
        node_properties.append(("created", str(datetime.datetime.utcfromtimestamp(node_data[1].created))))
        node_properties.append(("last_modified", str(datetime.datetime.utcfromtimestamp(node_data[1].last_modified))))
        node_properties.append(("version", node_data[1].version))
        node_properties.append(("acl_version", node_data[1].acl_version))
        node_properties.append(("owner_session_id", node_data[1].owner_session_id))
        node_properties.append(("data_length", node_data[1].data_length))
        node_properties.append(("children_count", node_data[1].children_count))

        return render_template('index.html', path_parts=path_parts, children=children_path, node_properties=node_properties, data=node_data[0], path=path)
    finally:
        zk.stop()
        zk.close()


@bp.route('/connect', methods=["GET", "POST"])
def connect():
    connection_error = None
    connection_string = None
    if request.method == 'POST':
        connection_string = request.form.get('inputConStr', None)
        if connection_string is None or len(connection_string) < 1:
            connection_string = defaultZK

    if connection_string is not None:
        # try to connect
        try:
            zk = KazooClient(hosts=connection_string, timeout=2)
            zk.start()
            connected = True
            session["connection_string"] = connection_string
        except Exception, ex:
            connected = False
            connection_error = "Cannot connect to zookeeoer. {}".format(str(ex))
            if "connection_string" in session:
                del session["connection_string"]

        if connected:
            # redirect to index
            return redirect(url_for('zookeeper_browser.index'))

    return render_template('connect.html', connection_error=connection_error, defaultZK=defaultZK)

if __name__ == '__main__':
    #app.debug = True
    prefix = os.environ.get("BASE_URL", "/")
    if len(sys.argv) > 1:
	    prefix=sys.argv[1]

    app.register_blueprint(bp, url_prefix=prefix)
    app.run(host='0.0.0.0', port=4550)
