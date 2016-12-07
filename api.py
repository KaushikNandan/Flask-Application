import datetime

from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:hi123@localhost/buildtr'
db = SQLAlchemy(app)

CHOICES = ['cash', 'credit']


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP())
    category = db.Column(db.String(20))
    type = db.Column(db.String(10))
    amount = db.Column(db.Float())

    def __init__(self):
        self.timestamp = datetime.datetime.now()

    def to_dict(self):
        exp = dict()
        exp['category'] = self.category
        exp['type'] = self.type
        exp['amount'] = self.amount
        exp['id'] = self.id
        exp['timestamp'] = self.timestamp
        return exp


@app.route('/expense', methods=['GET'])
def get():
    """
    Get all expenses from database
    """
    data = Expense.query.all()
    data = [ds.to_dict() for ds in data]
    return jsonify({'expenses': data})


@app.route('/expense/<int:key>', methods=['GET'])
def get_one(key):
    """
    Get one expense in json from databases specified by key (primary id)
    """
    data = Expense.query.get(key)
    if not data:
        abort(404)
    return jsonify(data.to_dict())


@app.route('/expense', methods=['POST'])
def post():
    """
    insert a record into the database
    and return: json data for the new row
    """
    category = request.form.get('category', None)
    type = request.form.get('type', None)
    amount = request.form.get('amount', None)

    if not (amount and type and category):
        abort(404)

    if type not in CHOICES:
        print type
        abort(404)

    ee = Expense()
    ee.amount = amount
    ee.category = category
    ee.type = type

    db.session.add(ee)
    db.session.commit()

    return jsonify(ee.to_dict())


@app.route('/expense/<key>', methods=['PUT'])
def put(key):
    """
    update an existing row
    and return updated json data
    """
    # Get old data from database
    old_data = Expense.query.get(key)

    if not old_data:
        return abort(404)

    # get request data
    category = request.form.get('category', None)
    type = request.form.get('type', None)
    amount = request.form.get('amount', None)

    if type and type not in CHOICES:
        abort(404)

    # update fields accordingly
    if category:
        old_data.category = category
    if type:
        old_data.type = type
    if amount:
        old_data.amount = amount

    # update into db now
    db.session.add(old_data)
    db.session.commit()

    return jsonify(old_data.to_dict())


@app.route('/expense/<key>', methods=['DELETE'])
def delete(key):
    """
    delete a row specified by pk key
    :param key: str, pk of the ro
    :return: empty json
    """
    # Get old data from database
    old_data = Expense.query.get(key)

    if not old_data:
        return abort(404)

    db.session.delete(old_data)
    db.session.commit()
    return jsonify({})


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
