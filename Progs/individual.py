#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sqlite3
import typing as t
from pathlib import Path


def display_routes(routes: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Отобразить информацию о маршрутах
    """
    if routes:
        line = "+-{}-+-{}-+-{}-+".format(
            "-" * 4, "-" * 30, "-" * 20
        )
        print(line)
        print(
            "| {:^4} | {:^30} | {:^20} |".format(
                "№", "Место отправки", "Место прибытия"
            )
        )
        print(line)

        for id, station in enumerate(routes, 1):
            print(
                "| {:^4} | {:^30} | {:^20} |".format(
                    id,
                    station.get("start_point", ""),
                    station.get("second_station", ""),
                )
            )
            print(line)
    else:
        print("Список маршрутов пуст.")


def create_db(database_path: Path) -> None:
    """
    Создать базу данных для хранения информации о маршрутах.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Создать таблицу с информацией о маршрутах отправления.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS start (
            name_id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_point TEXT NOT NULL
        )
        """
    )

    # Создать таблицу с информацией о маршрутах.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS route (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_id INTEGER NOT NULL,
            first_station TEXT NOT NULL,
            second_station TEXT NOT NULL,
            FOREIGN KEY(name_id) REFERENCES start(name_id)
        )
        """
    )

    conn.close()


def add_route(database_path: Path, first: str, second: str) -> None:
    """
    Добавить информацию о маршруте в базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name_id FROM start WHERE start_point = ?
        """,
        (first,),
    )

    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            """
            INSERT INTO start (start_point) VALUES (?)
            """,
            (first,),
        )
        name_id = cursor.lastrowid
    else:
        name_id = row[0]

    cursor.execute(
        """
        INSERT INTO route (name_id, first_station, second_station)
        VALUES (?, ?, ?)
        """,
        (name_id, first, second),
    )
    conn.commit()
    conn.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать все маршруты.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Исправленный SQL-запрос для выборки всех маршрутов
    cursor.execute(
        """
        SELECT start.start_point, route.first_station, route.second_station
        FROM route
        INNER JOIN start ON start.name_id = route.name_id
        """
    )

    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "start_point": row[0],
            "first_station": row[1],
            "second_station": row[2],
        }
        for row in rows
    ]


def select_route(database_path: Path, find_end: str) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать указанный маршрут.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT start.start_point, route.first_station, route.second_station
        FROM route
        INNER JOIN start ON start.name_id = route.name_id
        WHERE route.second_station = ?
        """,
        (find_end,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "start_point": row[0],
            "first_station": row[1],
            "second_station": row[2],
        }
        for row in rows
    ]

def main(command_line=None):
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "individual.data"),
        help="Имя базы данных",
    )

    parser = argparse.ArgumentParser("routes")
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Добавить новый маршрут"
    )
    add.add_argument(
        "-f",
        "--first",
        action="store",
        required=True,
        help="Место отправки",
    )
    add.add_argument(
        "-s",
        "--second",
        action="store",
        required=True,
        help="Место прибытия",
    )

    _ = subparsers.add_parser(
        "display", parents=[file_parser], help="Показать все маршруты"
    )

    select = subparsers.add_parser(
        "select", parents=[file_parser], help="Выбрать маршрут"
    )
    select.add_argument(
        "--second",
        action="store",
        required=True,
        help="Название конечной точки",
    )

    args = parser.parse_args(command_line)

    if not args.command:
        parser.print_help()
        return

    db_path = Path(args.db)
    create_db(db_path)

    if args.command == "add":
        add_route(db_path, args.first, args.second)

    elif args.command == "display":
        display_routes(select_all(db_path))

    elif args.command == "select":
        display_routes(select_route(db_path, args.second))


if __name__ == "__main__":
    main()