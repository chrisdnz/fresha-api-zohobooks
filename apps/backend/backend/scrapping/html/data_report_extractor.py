from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from backend.utils.date import to_datetime
import datetime
import re

class TableParser(ABC):
    @abstractmethod
    def parse(self, table: BeautifulSoup) -> List[Dict[str, Any]]:
        pass

class SingleTableParser(TableParser):
    def __init__(self, date_time_fields: List[str], float_fields: List[str]):
        self.date_time_fields = date_time_fields
        self.float_fields = float_fields

    def parse(self, table: BeautifulSoup) -> List[Dict[str, Any]]:
        headers = self._extract_headers(table)
        rows = table.find('tbody').find_all('tr')
        return [self._parse_row(row, headers) for row in rows if len(row.find_all('td')) > 1]

    def _extract_headers(self, table: BeautifulSoup) -> List[str]:
        return [th.text.strip() for th in table.find('thead').find_all('th') if th.text.strip()]

    def _parse_row(self, row: BeautifulSoup, headers: List[str]) -> Dict[str, Any]:
        cells = row.find_all('td')
        return {header: self._parse_cell(header, cell.text.strip()) 
                for header, cell in zip(headers, cells) if cell.text.strip()}

    def _parse_cell(self, header: str, cell_text: str) -> Any:
        if header in self.date_time_fields:
            return to_datetime(cell_text, "%d %b %Y, %I:%M%p")
        elif header in ["Sale no.", "Items sold", "Payment no."]:
            return int(cell_text) if cell_text.isdigit() else None
        elif header in self.float_fields:
            return self._to_float(cell_text)
        return cell_text

    @staticmethod
    def _to_float(float_string: str) -> float:
        cleaned = re.sub(r'[^\d.]', '', float_string)
        return float(cleaned) if cleaned else None

class MultiTableParser(TableParser):
    def __init__(self, single_table_parser: SingleTableParser):
        self.single_table_parser = single_table_parser

    def parse(self, tables: List[BeautifulSoup]) -> List[Dict[str, Any]]:
        main_table_data = self.single_table_parser.parse(tables[0])
        sales_table_data = self._parse_sales_table(tables[1])
        return self._merge_table_data(main_table_data, sales_table_data)

    def _parse_sales_table(self, table: BeautifulSoup) -> List[Dict[str, Any]]:
        rows = table.find('tbody').find_all('tr')
        return [self._parse_sales_row(row.find('td')) for row in rows]

    def _parse_sales_row(self, cell: BeautifulSoup) -> Dict[str, Any]:
        sales_text = cell.text.strip() if cell else ''
        if not sales_text:
            return {'Sale no.': None}

        if self._is_int_valid(sales_text):
            return {'Sale no.': int(re.sub(r'[^\d.]', '', sales_text))}
        elif self._is_date_valid(sales_text):
            return {'Payment date': to_datetime(sales_text, "%d %b %Y, %I:%M%p")}
        elif self._is_float_valid(sales_text):
            return {'Payment amount': float(re.sub(r'[^\d.]', '', sales_text))}
        return {'Payment date': None, 'Sale no.': None}

    @staticmethod
    def _merge_table_data(main_data: List[Dict[str, Any]], sales_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {**main_row, **sales_row}
            for main_row, sales_row in zip(main_data, sales_data)
        ]

    @staticmethod
    def _is_int_valid(s: str) -> bool:
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_date_valid(s: str) -> bool:
        try:
            # Attempt to parse the string as a datetime
            datetime.datetime.strptime(s, "%d %b %Y, %I:%M%p")
            return True
        except ValueError:
            # If parsing fails, the string is not a valid date in the expected format
            return False


    @staticmethod
    def _is_float_valid(s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

class DataReportExtractor:
    def __init__(self, date_time_fields: List[str], float_fields: List[str]):
        self.single_table_parser = SingleTableParser(date_time_fields, float_fields)
        self.multi_table_parser = MultiTableParser(self.single_table_parser)

    def extract_data(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')

        if len(tables) == 1:
            return self.single_table_parser.parse(tables[0])
        else:
            return self.multi_table_parser.parse(tables)