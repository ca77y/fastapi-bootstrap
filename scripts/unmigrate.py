import alembic.config


def main():
    alembicArgs = ["--raiseerr", "downgrade", "-1"]
    alembic.config.main(argv=alembicArgs)


if __name__ == "__main__":
    main()
