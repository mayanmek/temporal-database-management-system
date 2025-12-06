import pandas as pd
import webview
from pandas import Series, DataFrame
from api import API
from datetime import time, datetime

def parse_html_date(date_str: str):
    """
    Convert a string from an HTML date input to datetime.date.
    Returns None if the input is invalid or empty.
    """
    try:
        if not date_str:  # empty string
            return None
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def parse_html_time(time_str: str) -> time | None:
    """
    Convert a string from an HTML time input to datetime.time.
    Returns None if the input is invalid or empty.
    """
    if not time_str:  # empty string or None
        return None

    for fmt in ("%H:%M:%S", "%H:%M"):  # try with seconds first, then without
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue

    return None  # if no format matched


def to_dict(df: DataFrame | Series | None):
    """
    Convert a DataFrame or a Series (single row) to a dictionary with headers and data.

    Returns:
        {
            "headers": list of column names,
            "data": list of rows (each row is a list of values)
        }
    """

    def convert_datetime(val):
        """Convert datetime.date or datetime.time to string."""
        if isinstance(val, pd.Timestamp):
            return val.isoformat()  # Converts to 'YYYY-MM-DD' or 'HH:MM:SS'
        return val

    if df is None:
        return None

    if isinstance(df, DataFrame):
        return {
            "headers": list(df.columns.to_list()),
            "data": df.map(convert_datetime).values.tolist()  # list of lists
        }
    elif isinstance(df, Series):
        return {
            "headers": df.index.tolist(),
            "data": [df.apply(convert_datetime).tolist()]  # single row wrapped in a list
        }
    else:
        raise TypeError("Input must be a pandas DataFrame or Series")


class WebViewAPI:
    def __init__(self):
        self.__api = API()

    def get_fnames(self):
        return self.__api.get_all_first_names()

    def get_lnames(self):
        return self.__api.get_all_last_names()

    def get_loinc(self):
        return self.__api.get_all_loinc()

    def get_result(self, first_name: str, last_name: str, loinc: str,
            valid_data: str, valid_time: str,
            trans_date: str, trans_time: str):

        valid_data = parse_html_date(valid_data)
        valid_time = parse_html_time(valid_time)
        trans_date = parse_html_date(trans_date)
        trans_time = parse_html_time(trans_time)

        if valid_data is None:
            return {
                "status": "error",
                "message": "valid date is mendetory"
            }

        loinc_name = self.__api.loinc2name(loinc)
        if loinc_name is None:
            return {
                "status": "error",
                "message": f"no such loinc number: `{loinc}`"
            }
        res = self.__api.get_res(
            first_name, last_name, loinc,
            valid_data, valid_time,
            trans_date, trans_time
        )

        if res is None:
            return {
                "status": "error",
                "message": f"no value for {loinc} ({loinc_name}) test result of {first_name} {last_name} from {valid_data} {valid_time if valid_time is not None else ''} "
                           f"from a perspective of a doctor that look {"now" if trans_date is None else f"{trans_date} {trans_time if trans_time is not None else ''}"}"
            }

        return {
            "status": "success",
            "message": f"the {loinc} ({loinc_name}) test result of {first_name} {last_name} from {valid_data} {valid_time if valid_time is not None else ''} "
                       f"from a perspective of a doctor that look {"now" if trans_date is None else f"{trans_date} {trans_time if trans_time is not None else ''}"}",
            "data": to_dict(res)
        }

    def delete(self, first_name: str, last_name: str, loinc: str,
            valid_data: str, valid_time: str,
            trans_date: str, trans_time: str):

        valid_data = parse_html_date(valid_data)
        valid_time = parse_html_time(valid_time)
        trans_date = parse_html_date(trans_date)
        trans_time = parse_html_time(trans_time)

        if valid_data is None:
            return {
                "status": "error",
                "message": "valid date is mendetory"
            }

        loinc_name = self.__api.loinc2name(loinc)
        if loinc_name is None:
            return {
                "status": "error",
                "message": f"no such loinc number: `{loinc}`"
            }
        res = self.__api.delete(
            first_name, last_name, loinc,
            valid_data, valid_time,
            trans_date, trans_time
        )

        if res is None:
            return {
                "status": "error",
                "message": f"no value for {loinc} ({loinc_name}) test result of {first_name} {last_name} from {valid_data} {valid_time if valid_time is not None else ''} "
                           f"from a perspective of a doctor that look {"now" if trans_date is None else f"{trans_date} {trans_time if trans_time is not None else ''}"}"
            }


        new_row = res['old']
        new_row["new Value"] = res['new']['Value']
        new_row["new Transaction time"] = res['new']['Transaction time']


        return {
            "status": "success",
            "message": f"the {loinc} ({loinc_name}) test result of {first_name} {last_name} from {valid_data} {valid_time if valid_time is not None else ''} was deleted"
                       f"from a perspective of a doctor that look {"now" if trans_date is None else f"{trans_date} {trans_time if trans_time is not None else ''}"}"
                       f"the old row was:",
            "data": to_dict(new_row)
        }

    def update(self, first_name: str, last_name: str, loinc: str,
            valid_data: str, valid_time: str,
            trans_date: str, trans_time: str, new_value: str):

        valid_data = parse_html_date(valid_data)
        valid_time = parse_html_time(valid_time)
        trans_date = parse_html_date(trans_date)
        trans_time = parse_html_time(trans_time)

        if valid_data is None:
            return {
                "status": "error",
                "message": "valid date is mendetory"
            }

        loinc_name = self.__api.loinc2name(loinc)
        if loinc_name is None:
            return {
                "status": "error",
                "message": f"no such loinc number: `{loinc}`"
            }
        res = self.__api.update(
            first_name, last_name, loinc,
            valid_data, valid_time,
            trans_date, trans_time,
            new_value
        )

        new_row = res['old']
        new_row["new Value"] = res['new']['Value']
        new_row["new Transaction time"] = res['new']['Transaction time']

        if res is None:
            return {
                "status": "error",
                "message": f"no value for {loinc} ({loinc_name}) test result of {first_name} {last_name} from {valid_data} {valid_time if valid_time is not None else ''} "
                           f"from a perspective of a doctor that look {"now" if trans_date is None else f"{trans_date} {trans_time if trans_time is not None else ''}"}"
            }

        return {
            "status": "success",
            "message": f"the {loinc} ({loinc_name}) test result of {first_name} {last_name} from {valid_data} {valid_time if valid_time is not None else ''} was updated"
                       f" from a perspective of a doctor that look {"now" if trans_date is None else f"{trans_date} {trans_time if trans_time is not None else ''}"} to have {new_value}, "
                       f"the new row is:",
            "data": to_dict(new_row)
        }

    def get_history(self, first_name: str, last_name: str, loinc: str,
            valid_data: str, valid_time: str,
            trans_start_date: str, trans_start_time: str,
            trans_end_date: str, trans_end_time: str):

        valid_data = parse_html_date(valid_data)
        valid_time = parse_html_time(valid_time)
        trans_start_date = parse_html_date(trans_start_date)
        trans_start_time = parse_html_time(trans_start_time)
        trans_end_date = parse_html_date(trans_end_date)
        trans_end_time = parse_html_time(trans_end_time)

        if valid_data is None:
            return {
                "status": "error",
                "message": "valid date is mendetory"
            }

        loinc_name = self.__api.loinc2name(loinc)
        if loinc_name is None:
            return {
                "status": "error",
                "message": f"no such loinc number: `{loinc}`"
            }

        res = self.__api.get_history(
            first_name, last_name, loinc,
            valid_data, valid_time,
            trans_start_date, trans_start_time,
            trans_end_date, trans_end_time
        )

        trans_start_str = "1900"
        if trans_start_date is not None:
            trans_start_str = f"{trans_start_date} {trans_start_time if trans_start_time is not None else ''}"

        trans_end_str = "now"
        if trans_end_date is not None:
            trans_end_str = f"{trans_end_date} {trans_end_time if trans_end_time is not None else ''}"
        return {
            "status": "success",
            "message": f"the {loinc} ({loinc_name}) test result of {first_name} {last_name} from {valid_data} {valid_time if valid_time is not None else ''}"
                       f" in Transaction time : [{trans_start_str}, {trans_end_str}]:",
            "data": to_dict(res)
        }


def main():
    global myAPI
    myAPI = API()
    webview.create_window("Database Management", "web/index.html", js_api=WebViewAPI())
    webview.start(debug=False)




if __name__ == '__main__':
    main()