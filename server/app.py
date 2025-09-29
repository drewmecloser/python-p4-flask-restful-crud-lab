#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


# Custom error handler for 404 Not Found
@app.errorhandler(404)
def not_found(error):
    # This function is called if a resource is not found (e.g., in our PlantByID lookups)
    response_body = {"error": "Plant not found"}
    return make_response(jsonify(response_body), 404)


class Plants(Resource):
    """
    Resource for handling the collection of all plants (/plants)
    Supports GET (Read All) and POST (Create)
    """

    def get(self):
        # Retrieve all plants and convert them to dictionaries
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        # Create a new plant from the request JSON data
        try:
            data = request.get_json()

            new_plant = Plant(
                name=data['name'],
                image=data['image'],
                price=data['price'],
                # Assuming is_in_stock defaults to True or is provided
                is_in_stock=data.get('is_in_stock', True)
            )

            db.session.add(new_plant)
            db.session.commit()

            # Return the newly created plant with a 201 status code
            return make_response(new_plant.to_dict(), 201)
        except Exception as e:
            # Basic error handling for invalid POST data
            return make_response(jsonify({"errors": [str(e)]}), 400)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):
    """
    Resource for handling a single plant by ID (/plants/<int:id>)
    Supports GET (Read One), PATCH (Update), and DELETE (Destroy)
    """

    def get(self, id):
        # Retrieve a single plant by ID or raise 404
        plant = Plant.query.filter_by(id=id).first()
        if plant:
            return make_response(jsonify(plant.to_dict()), 200)
        # If plant not found, raise 404, which is handled by @app.errorhandler(404)
        return make_response(jsonify({"error": "Plant not found"}), 404)

    # --- REQUIRED DELIVERABLES ---

    def patch(self, id):
        # Retrieve the plant to update
        plant = Plant.query.filter_by(id=id).first()

        if not plant:
            # If plant not found, return 404 (handled by custom error handler)
            return make_response(jsonify({"error": "Plant not found"}), 404)

        try:
            # Get the JSON data from the request body
            data = request.get_json()

            # Update plant attributes based on the received data
            # The lab specifically mentions 'is_in_stock', but we iterate for flexibility
            for key, value in data.items():
                if hasattr(plant, key):
                    setattr(plant, key, value)

            # Commit the changes to the database
            db.session.commit()

            # Return the updated plant object with a 200 status code
            return make_response(jsonify(plant.to_dict()), 200)
        except Exception as e:
            # Handle potential validation errors or bad data updates
            return make_response(jsonify({"errors": [str(e)]}), 400)


    def delete(self, id):
        # Retrieve the plant to delete
        plant = Plant.query.filter_by(id=id).first()

        if not plant:
            # If plant not found, return 404
            return make_response(jsonify({"error": "Plant not found"}), 404)

        # Delete the plant from the database
        db.session.delete(plant)
        db.session.commit()

        # Return an empty response with status code 204 (No Content)
        # This is the standard response for successful deletion in REST
        return make_response('', 204)


api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    # Make sure you are running this from inside the 'server' directory
    # and the pipenv shell, and that the frontend is running in a separate terminal.
    app.run(port=5555, debug=True)
