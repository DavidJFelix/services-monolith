# Services Monolith

This repository is the first pass on backend RESTful services for the Dinner Solutions app.
It uses a monolithic, but easily-divisible approach and should be easy to break apart into microservices or "nanoservices".

The Monolith uses no ORM or database control scheme, but has a minor database abstraction layer to assist in asynchronous access.
It currently uses RethinkDB as a backend, but is designed to be able to use a more traditional SQL database in the future if needed.

The project utilizes:

* Python 3.5+
* Asyncio
* Tornado
* RethinkDB

## Organization

The project is organized into the following structure:

* **app.py**: The "main" for the application. This contains the initialization and routes.
* **config.py**: The configuration for the application.
* **models/**: This is where the data objects and their business logic for CRUD operations lie.
  * **base.py**: This is the base model that defines a dictionary interface for working with python objects
  * **rethinkdb.py**: This is the rethinkdb specific synchronization code for CRUD operations on an object.
* **lib/**: This is where cross-cutting, technically specific code sits.
* **handlers/**: This is where responders to HTTP requests sit.
  * **base.py**: This is the base handler that sets defaults for the rest of the handlers
  * **diag.py**: This handler serves information about the server and is designed for diagnostic purposes for operators.
  * **api.py**: This handler is intended to serve information about the API to potential consumers

## Running the server (locally or otherwise)

The server uses docker as a mechanism for virtual environments.

*To Be Continued...* (pester David to finish this)