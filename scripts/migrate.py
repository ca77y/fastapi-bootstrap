import alembic.config


def main():
    alembicArgs = ["--raiseerr", "upgrade", "head"]
    alembic.config.main(argv=alembicArgs)


if __name__ == "__main__":
    main()
