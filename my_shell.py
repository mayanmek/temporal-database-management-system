import cmd
import datetime
import shlex
from typing import Optional

from myDB import MyDB
from pathlib import Path
import argparse


def _set_time_arg_parser(args):
    args = shlex.split(args)
    parser = argparse.ArgumentParser(prog="set_time",
                                     description="Sent you back (or forward) in time with the time machine")

    parser.add_argument(
        "date",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
        help="Date in YYYY-MM-DD format"
    )

    parser.add_argument(
        "time",
        type=lambda s: datetime.datetime.strptime(s, "%H:%M").time(),
        nargs="?",
        default=None,
        help="Time in HH:MM format"
    )

    try:
        return parser.parse_args(args)
    except:
        print()
        return None


def _unset_time_arg_parser(args):
    args = shlex.split(args)
    parser = argparse.ArgumentParser(prog="unset_time", description="Sent you back to real time")
    try:
        return parser.parse_args(args)
    except:
        print()
        return None


def _get_history_arg_parser(args):
    args = shlex.split(args)
    parser = argparse.ArgumentParser(prog="get_history",
                                     description="get the history of the patient for some range")

    parser.add_argument(
        "first_name",
        type=str,
        help="patient's first name"
    )

    parser.add_argument(
        "last_name",
        type=str,
        help="patient's last name"
    )

    parser.add_argument(
        "loinc_code",
        type=str,
        help="test's loinc code"
    )
    parser.add_argument(
        "--start-date", '-sd',
        default=None,
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
        help="Date in YYYY-MM-DD format for the beginning of the range, if not provided the range has no lower bound."
    )

    parser.add_argument(
        "--start-time", '-st',
        type=lambda s: datetime.datetime.strptime(s, "%H:%M").time(),
        default=None,
        help="Time in HH:MM format for the beginning of the range, will be ignored if start-date is not set"
    )

    parser.add_argument(
        "--end-date", '-ed',
        default=None,
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
        help="Date in YYYY-MM-DD format for the beginning of the range, if not provided the range has no upper bound."
    )
    parser.add_argument(
        "--end-time", '-et',
        type=lambda s: datetime.datetime.strptime(s, "%H:%M").time(),
        default=None,
        help="Time in HH:MM format for the end of the range, will be ignored if start-date is not set"
    )

    try:
        return parser.parse_args(args)
    except:
        print()
        return None


def _get_result_arg_parser(args):
    args = shlex.split(args)
    parser = argparse.ArgumentParser(prog="get_result",
                                     description="get the result of the patient at specific date (and time if provided)")

    parser.add_argument(
        "first_name",
        type=str,
        help="patient's first name"
    )

    parser.add_argument(
        "last_name",
        type=str,
        help="patient's last name"
    )

    parser.add_argument(
        "loinc_code",
        type=str,
        help="test's loinc code"
    )

    parser.add_argument(
        "date",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
        help="Date in YYYY-MM-DD format"
    )

    parser.add_argument(
        "time",
        type=lambda s: datetime.datetime.strptime(s, "%H:%M").time(),
        nargs="?",
        default=None,
        help="Time in HH:MM format"
    )

    try:
        return parser.parse_args(args)
    except:
        print()
        return None

def _update_arg_parser(args):
    args = shlex.split(args)
    parser = argparse.ArgumentParser(prog="update",
                                     description="update or delete row from the df")

    parser.add_argument(
        "first_name",
        type=str,
        help="patient's first name"
    )

    parser.add_argument(
        "last_name",
        type=str,
        help="patient's last name"
    )

    parser.add_argument(
        "loinc_code",
        type=str,
        help="test's loinc code"
    )

    parser.add_argument(
        "date",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
        help="Date in YYYY-MM-DD format"
    )

    parser.add_argument(
        "time",
        type=lambda s: datetime.datetime.strptime(s, "%H:%M").time(),
        nargs="?",
        default=None,
        help="Time in HH:MM format"
    )
    parser.add_argument(
        "value",
        type=lambda a: int(a) if a.lower() != "none" else None,
        help="Date in YYYY-MM-DD format"
    )

    try:
        return parser.parse_args(args)
    except:
        print()
        return None



class MyShell(cmd.Cmd):
    intro = "Welcome! Type help or ? to list commands.\n"
    prompt = "> "

    def __init__(self):
        super().__init__()
        self.db = MyDB(Path("dbs/project_db_2025.xlsx"))
        self.time: Optional[datetime.datetime] = None

    def _get_time(self):
        if self.time is None:
            return datetime.datetime.now()
        return self.time

    def do_set_time(self, arg):
        args = _set_time_arg_parser(arg)
        if args is None:
            return
        if args.time is None:
            args.time = datetime.time.max
        self.time = datetime.datetime.combine(args.date, args.time)
        print(f"time machine sent you to {self.time}")

    def do_unset_time(self, arg):
        args = _unset_time_arg_parser(arg)
        if args is None:
            return
        print(f"time machine sent you to back to the present")
        self.time = None

    def do_get_history(self, arg):
        args = _get_history_arg_parser(arg)
        if args is None:
            return

        loinc_full_name = self.db.get_name_by_loinc(args.loinc_code)
        if loinc_full_name is None:
            print(f"loinc name cannot be found for code \"{args.loinc_code}\"")
            return

        start_range = None
        if args.start_date is not None:
            start_range = datetime.datetime.combine(args.start_date,
                                                    args.start_time if args.start_time is not None else datetime.time.min)
        end_range = None
        if args.end_date is not None:
            end_range = datetime.datetime.combine(args.end_date,
                                                  args.end_time if args.end_time is not None else datetime.time.max)

        history = self.db.get_history(args.first_name,
                                      args.last_name,
                                      args.loinc_code,
                                      range_=(start_range, end_range),
                                      for_time=self._get_time())

        start_range_txt = "(-∞" if start_range is None else "[" + str(start_range)
        end_range_txt = "∞)" if end_range is None else str(start_range) + "]"
        print(
            f"For patient {args.first_name} {args.last_name}  the \"{loinc_full_name}\" test ({args.loinc_code}) results for the range({start_range_txt},{end_range_txt}) at {self._get_time()}:")
        print(history)

    def do_get_result(self, arg):
        args = _get_result_arg_parser(arg)
        if args is None:
            return

        loinc_full_name = self.db.get_name_by_loinc(args.loinc_code)
        if loinc_full_name is None:
            print(f"loinc name cannot be found for code \"{args.loinc_code}\"")
            return

        start_range = None
        end_range = None

        if args.time is not None:
            start_range = end_range = datetime.datetime.combine(args.date, args.time)
        else:
            start_range = datetime.datetime.combine(args.date, datetime.time.min)
            end_range = datetime.datetime.combine(args.date, datetime.time.max)

        history = self.db.get_history(args.first_name,
                                      args.last_name,
                                      args.loinc_code,
                                      range_=(start_range, end_range),
                                      for_time=self._get_time())
        if len(history) == 0:
            print(f"cannot find any test of \"{loinc_full_name}\" ({args.loinc_code}) for {args.first_name} {args.last_name} at {self._get_time()}")
        else:
            print(f"result of the test of \"{loinc_full_name}\" ({args.loinc_code}) for {args.first_name} {args.last_name} at {self._get_time()}:")
            print(history.iloc[-1])

    def do_update(self, arg):
        args = _update_arg_parser(arg)
        if args is None:
            return

        loinc_full_name = self.db.get_name_by_loinc(args.loinc_code)
        if loinc_full_name is None:
            print(f"loinc name cannot be found for code \"{args.loinc_code}\"")
            return

        start_range = None
        end_range = None

        if args.time is not None:
            start_range = end_range = datetime.datetime.combine(args.date, args.time)
        else:
            start_range = datetime.datetime.combine(args.date, datetime.time.min)
            end_range = datetime.datetime.combine(args.date, datetime.time.max)

        history = self.db.get_history(args.first_name,
                                      args.last_name,
                                      args.loinc_code,
                                      range_=(start_range, end_range),
                                      for_time=self._get_time())
        if len(history) == 0:
            print(
                f"cannot find any test of \"{loinc_full_name}\" ({args.loinc_code}) for {args.first_name} {args.last_name} at {self._get_time()}")
        else:
            row = history.iloc[-1]
            print(
                f"previus row for test \"{loinc_full_name}\" ({args.loinc_code}) for {args.first_name} {args.last_name} at {self._get_time()}:")
            print(row)
            new_row = self.db.add_row(args.first_name, args.last_name, args.loinc_code, row['Valid start time'], self._get_time(), args.value, row["Unit"])
            print("new row:")
            print(new_row)

    def do_exit(self, arg) -> bool:
        """
        Exit the shell
        """
        print("Goodbye!")
        return True
