CRUD app boilerplate
---------------------

# Description

CRUD app skeleton with SqlAlchemy composition of mapped hierarchies:

* `Entity` and `Temporal Entity`
* XRelatedEntity, for example `ProfileRelatedEntity`

## Interesting parts

### DAO composition

This feature allows encapsulating relationships between database entities in Mixins.
Later we can add common behavior and compose our DAO expressing relations in a more declarative manner.
It makes for an easy way to share common code and makes it a little cleaner.
It's implemented here with ActiveRecord style classes.

### Async workers

A way to offload async work to separate processes that can be scaled independently.
It uses a redis backed queue.

### Database and handler interaction

`@transactional` decorator to remove boilerplate from handlers. It takes care of output normalization so we have our items and lists having the same base schema. It also takes care of the required `DB` parameter and commits or rollbacks the database transaction.

### Pagination

Some fiddling with types and parameters to make pagination easy and flexible. We can always fall back on creating a page by hand, but if we only need some filtering or ordering we can take care of it with a one-liner.

# Installation

Docker compose is used for dev, while prod env runs with `run-_.sh` scripts. It uses a local folder as a volume and watches for changes.

!!! After the first deployment it will take some time for uv to create venv, the server will start responding after it installs all dependencies. We need this in order not to corrupt local venv if we have one !!!

## Requirements

* OSX
* Docker

## Steps

1. `make build`
1. `make up`

## Status

`https://localhost:3000/api/v1/healthcheck`

