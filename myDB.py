import datetime

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

from pandas.core.interchange.dataframe_protocol import DataFrame


def _get_time(time: Optional[datetime.datetime]) -> datetime.datetime:
    """
    replace None with current time
    :param time: the datetime
    :return: `time` if time is not None, else the current time
    """
    if time is None:
        return datetime.datetime.now()
    else:
        return time

class MyDB:
    """
    MyDB class for my management of the DB
    """
    def __init__(self, db_path: Path, loinc_code_db_path: Path = Path("dbs/LoincTableCore.csv")):
        """
        :param db_path: path to the xlsx for the db
        :param loinc_code_db_path: the path to the csv of the loinc code
        """
        self.df = pd.read_excel(db_path)
        self.df = self.df.loc[:, ~self.df.columns.str.startswith("Unnamed")]
        self.df["Valid start time"] = pd.to_datetime(self.df["Valid start time"])
        self.df["Transaction time"] = pd.to_datetime(self.df["Transaction time"])

        self.loinc_df = pd.read_csv(loinc_code_db_path,  usecols=['LOINC_NUM', 'LONG_COMMON_NAME'])

        self.lastAdded = False
        self.lastUndo = None

    def redo(self):
        if self.lastUndo is None:
            return False

        # Add the row back safely
        self.df = pd.concat([self.df, pd.DataFrame([self.lastUndo])], ignore_index=True)
        self.lastUndo = None
        self.lastAdded = True
        return True

    def undo(self):
        if not self.lastAdded:
            return False

        # Store last row for redo
        self.lastUndo = self.df.iloc[-1].copy()
        self.df = self.df.iloc[:-1].copy()
        self.lastAdded = False
        return True

    def add_row(self, first_name: str, last_name: str, loinc_code: str, valid_start_time: datetime.datetime, transaction_time: datetime.datetime, value: Optional[str], unit: str):
        self.df.loc[len(self.df)] = (first_name, last_name, loinc_code, value, unit, valid_start_time, transaction_time)
        self.lastAdded = True
        return self.df.iloc[-1]

    def get_history(self, first_name: str, last_name: str, loinc_code: str, range_valid: tuple[datetime.datetime, datetime.datetime], range_trans: tuple[Optional[datetime.datetime], Optional[datetime.datetime]] = (None, None)):
        """
        :param first_name:
        :param last_name:
        :param loinc_code:
        :param range_valid:
        :param range_trans:
        :return:
        """

        df: DataFrame = self.df[
            (self.df["First name"] == first_name) &
            (self.df["Last name"] == last_name) &
            (self.df["LOINC-NUM"] == loinc_code) &
            (self.df["Valid start time"].dt.floor('T') >= range_valid[0]) &
            (self.df["Valid start time"].dt.floor('T') <= range_valid[1]) &
            (range_trans[0] is None or self.df["Transaction time"].dt.floor('T') >= range_trans[0]) &
            (range_trans[1] is None or self.df["Transaction time"].dt.floor('T') <= range_trans[1])
        ]

        good_groups = df.groupby("Valid start time")["Value"].apply(lambda s: s.notna().all())
        df = df[df["Valid start time"].isin(good_groups[good_groups].index)]
        df = df.loc[
            df.groupby("Valid start time")["Transaction time"].idxmax()
        ]

        return df[["Value", "Unit", "Valid start time", "Transaction time"]]

    def get_name_by_loinc(self, loinc: str) -> Optional[str]:
        df = self.loinc_df[self.loinc_df['LOINC_NUM'] == loinc]['LONG_COMMON_NAME']
        if len(df) == 0:
            return None
        return df.iloc[0]