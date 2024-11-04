from flask import Flask, request, jsonify
from flasgger import Swagger, LazyJSONEncoder
from flask_sqlalchemy import SQLAlchemy
from flasgger import swag_from


app = Flask(__name__)
app.json_encoder = LazyJSONEncoder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sports.db"
db = SQLAlchemy(app)


class SportsCompetitions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    participants = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "duration": self.duration,
            "location": self.location,
            "participants": self.participants,
            "year": self.year
        }


swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Спортивные состязания",
        "description": "API Документация спортивных состязаний",
    },
    "schemes": [
        "http",
        "https"
    ],
}

swagger = Swagger(app, template=swagger_template)


@swag_from("docs/sports.yaml")
@app.route("/all_sports", methods=["GET"])
def get_sports_competitions():
    sports = SportsCompetitions.query.all()
    return jsonify([c.to_dict() for c in sports])


@swag_from('docs/get_sport_by_id.yaml')
@app.route("/sport/<int:id>", methods=["GET"])
def get_sports_competition_by_id(id):
    sport = SportsCompetitions.query.get(id)
    if sport is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(sport.to_dict())


@swag_from('docs/create_sport.yaml')
@app.route("/sport", methods=["POST"])
def create_sports_competition():
    data = request.get_json()
    new_sport = SportsCompetitions(
        name=data['name'],
        duration=data['duration'],
        location=data['location'],
        participants=data['participants'],
        year=data['year']
    )
    db.session.add(new_sport)
    db.session.commit()
    return jsonify(new_sport.to_dict()), 201


@swag_from('docs/update_sport.yaml')
@app.route("/sport/<int:id>", methods=["PUT"])
def update_sports_competition(id):
    sport = SportsCompetitions.query.get(id)
    if sport is None:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    sport.name = data.get('name', sport.name)
    sport.duration = data.get('duration', sport.duration)
    sport.location = data.get('location', sport.location)
    sport.participants = data.get('participants', sport.participants)
    sport.year = data.get('year', sport.year)

    db.session.commit()
    return jsonify(sport.to_dict())


@swag_from('docs/patch_sport.yaml')
@app.route("/sport/<int:id>", methods=["PATCH"])
def patch_sports_competition(id):
    print('rerere', id)
    sport = SportsCompetitions.query.get(id)
    if sport is None:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    if 'name' in data:
        sport.name = data['name']
    if 'duration' in data:
        sport.duration = data['duration']
    if 'location' in data:
        sport.location = data['location']
    if 'participants' in data:
        sport.participants = data['participants']
    if 'year' in data:
        sport.year = data['year']

    db.session.commit()
    return jsonify(sport.to_dict())


@swag_from('docs/delete_sport.yaml')
@app.route("/sport/<int:id>", methods=["DELETE"])
def delete_sports_competition(id):
    sport = SportsCompetitions.query.get(id)
    if sport is None:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(sport)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"}), 204


@swag_from('docs/aggregations.yaml')
@app.route("/sport/aggregations", methods=["GET"])
def get_aggregations():
    aggregations = {}
    for column in ["duration", "participants", "year"]:
        aggregations[column] = {
            "min": db.session.query(db.func.min(getattr(SportsCompetitions, column))).scalar(),
            "max": db.session.query(db.func.max(getattr(SportsCompetitions, column))).scalar(),
            "avg": db.session.query(db.func.avg(getattr(SportsCompetitions, column))).scalar()
        }

    return jsonify(aggregations)

@swag_from('docs/sort.yaml')
@app.route("/sport/sort", methods=["GET"])
def sort_sport_competitions():
    sort_by = request.args.get("sort_by")
    order = request.args.get("order", "asc")
    sports = SportsCompetitions.query.order_by(
        getattr(SportsCompetitions, sort_by).asc() if order == "asc" else getattr(SportsCompetitions, sort_by).desc())

    return jsonify([c.to_dict() for c in sports])


if __name__ == '__main__':
    print(("* Loading model and Flask starting server..."
           "please wait until server has fully started"))

    app.run(host='0.0.0.0', threaded=True, port=8085, debug=False)