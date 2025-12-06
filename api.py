import datetime
from typing import Optional

from pandas import Series
from pandas.core.interchange.dataframe_protocol import DataFrame

from myDB import MyDB
from pathlib import Path


class API:
    def __init__(self):
        self.db = MyDB(Path("dbs/project_db_2025.xlsx"))

    def get_history(
            self, first_name: str, last_name: str, loinc: str,
            valid_data: datetime.date, valid_time: Optional[datetime.time],
            start_date: Optional[datetime.date], start_time: Optional[datetime.time],
            end_date: Optional[datetime.date], end_time: Optional[datetime.time],
    ):
        if valid_time:
            valid_start = datetime.datetime.combine(valid_data, valid_time)
            valid_end = datetime.datetime.combine(valid_data, valid_time)
        else:
            valid_start = datetime.datetime.combine(valid_data, datetime.time.min)
            valid_end = datetime.datetime.combine(valid_data, datetime.time.max)

        valid_range = (valid_start, valid_end)

        start = None
        if start_date is not None:
            start = datetime.datetime.combine(start_date, start_time if start_time is not None else datetime.time.min)

        end = None
        if end_date is not None:
            end = datetime.datetime.combine(end_date, end_time if end_time is not None else datetime.time.max)

        trans_range = (start, end)

        return self.db.get_history(
            first_name, last_name, loinc,
            range_valid=valid_range,
            range_trans=trans_range
        )

    def get_res(
            self, first_name: str, last_name: str, loinc: str,
            valid_data: datetime.date, valid_time: Optional[datetime.time],
            trans_date: Optional[datetime.date], trans_time: Optional[datetime.time]
    ):
        data = self.get_history(first_name, last_name, loinc, valid_data, valid_time, None, None, trans_date, trans_time)

        if len(data) > 0:
            return data.iloc[-1]
        return None # can be deleted but more explicitly is better


    def update(
           self, first_name: str, last_name: str, loinc: str,
           valid_data: datetime.date, valid_time: Optional[datetime.time],
           trans_date: Optional[datetime.date], trans_time: Optional[datetime.time],
           value: Optional[str] = None
    ):
        data = self.get_res(first_name, last_name, loinc, valid_data, valid_time, trans_date, trans_time)
        if data is None:
            return None

        trans_datetime = datetime.datetime.now()
        if trans_date is not None:
            trans_datetime = datetime.datetime.combine(
                trans_date,
                trans_time if trans_time is not None else datetime.time.max
            )
        new_row = self.db.add_row(first_name, last_name, loinc, data["Valid start time"], trans_datetime, value, data["Unit"])
        return {
            "old": data,
            "new": new_row
        }

    def delete(
            self, first_name: str, last_name: str, loinc: str,
            valid_data: datetime.date, valid_time: Optional[datetime.time],
            trans_date: Optional[datetime.date], trans_time: Optional[datetime.time]
    ):
        return self.update(first_name, last_name, loinc,
           valid_data, valid_time,
           trans_date, trans_time)

    def get_all_first_names(self):
        return sorted(set(self.db.df["First name"]))

    def get_all_last_names(self):
        return sorted(set(self.db.df["Last name"]))

    def get_all_loinc(self):
        return sorted(set(self.db.df["LOINC-NUM"]))

    def loinc2name(self, loinc: str) -> str:
        return self.db.get_name_by_loinc(loinc)

