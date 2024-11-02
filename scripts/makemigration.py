import argparse

import alembic.config


def main():
    parser = argparse.ArgumentParser(description="Migrate database")
    parser.add_argument("comment", type=str, help="migration comment")
    args = parser.parse_args()

    alembicArgs = ["--raiseerr", "revision", "--autogenerate", "-m", args.comment]
    alembic.config.main(argv=alembicArgs)


if __name__ == "__main__":
    main()
