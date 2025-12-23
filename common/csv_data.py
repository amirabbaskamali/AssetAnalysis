import pandas as pd
from statistics import mean
from common.asset_rate import AssetRate


class CsvData:
    def __init__(self, data_file_name: str) -> None:
        self.file_name = data_file_name

    def _read_csv_data(self) -> pd.DataFrame:
        try:
            return pd.read_csv(self.file_name, encoding="utf-8")

        except FileNotFoundError:
            print(f"No file with name '{self.file_name}' in this directory.")

    def _extract_raw_data(self) -> list:
        df = self._read_csv_data()
        dates = df["Date"]
        prices = df["Price"]
        raw_data = [{"date": date[:-3], "price": round(float(price))} for date, price in zip(dates, prices)]

        return raw_data

    @staticmethod
    def _organize_daily_prices(raw_data: list) -> list:
        monthly_model = {"month": "value", "data": "value"}
        month_list = [raw_data[0]["date"]]
        daily_prices = []
        rate_list = []

        for day in raw_data:
            if day["date"] in month_list:
                rate_list.append(day["price"])
            else:
                if rate_list:
                    monthly_model["month"] = month_list[-1]
                    monthly_model["data"] = rate_list
                    daily_prices.append(monthly_model)
                    rate_list = []

                month_list.append(day["date"])
                rate_list.append(day["price"])
                monthly_model = {"month": day["date"], "data": rate_list}

        if rate_list:
            monthly_model["data"] = rate_list
            daily_prices.append(monthly_model)

        return daily_prices

    @staticmethod
    def _calculate_monthly_prices(daily_prices: list) -> list:
        monthly_prices = []
        previous_price = round(mean(daily_prices[0]["data"]))  # quantification for the first block of data

        for month in daily_prices:
            monthly_data = dict()
            monthly_data["year"] = month["month"][:4]
            monthly_data["month"] = month["month"][5:]
            monthly_data["rate"] = round(mean(month["data"]))
            monthly_data["change"] = round((monthly_data["rate"] - previous_price) / previous_price, 2)
            monthly_data["change"] = 0 if monthly_data["change"] == 0 else monthly_data["change"]  # avoiding -0

            monthly_prices.append(monthly_data)

            previous_price = monthly_data["rate"]

        return monthly_prices

    @staticmethod
    def _to_asset_rate_list(monthly_prices: list) -> list:
        asset_rate_list = [
            AssetRate(month_data["year"], month_data["month"], month_data["rate"], month_data["change"])
            for month_data in monthly_prices
        ]

        return asset_rate_list

    def get_data(self) -> list:
        csv_list = self._extract_raw_data()
        daily_prices = self._organize_daily_prices(csv_list)
        monthly_prices = self._calculate_monthly_prices(daily_prices)
        asset_rate_list = self._to_asset_rate_list(monthly_prices)

        return asset_rate_list
