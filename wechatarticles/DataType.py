import csv
import os
import sqlite3


class DataType:
    def __init__(self):
        raise NotImplemented

    def read(self):
        raise NotImplemented

    def close(self):
        raise NotImplemented

    def write(self):
        raise NotImplemented


class CSV(DataType):
    def __init__(self, csv_fname, headers=None):
        """
        csv_fname : str,
        headers: list[str]
        """
        self.csv_fname = csv_fname
        self.headers = headers
        if not os.path.isfile(self.csv_fname):
            with open(self.csv_fname, "a", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerows([self.headers])

    def csv_helper(self, data_lst):
        """将指定信息写入csv文件"""
        with open(self.csv_fname, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            for line in data_lst:
                writer.writerows([line])

    def read(self, col_index):
        """
        col_index: int, 第x列的数据
        """
        with open(self.csv_fname, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f)
            data_lst = [str(line[col_index]).strip() for line in csv_reader][1:]
        data = list(set(data_lst))
        return data_lst

    def write(self, data_lst):
        """
        data: list[list[str]]
        """
        self.csv_helper(data_lst)


class Sqlite3(DataType):
    def __init__(self, dbname):
        self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname, check_same_thread=False)

    def _init_sql(self, create_sql, insert_sql):
        self.create_sql = create_sql
        self.insert_sql = insert_sql

    @property
    def table_name_lst(self):
        # 获取db文件中所有的table名字
        table_lst = self.conn.execute('select * from sqlite_master where type="table";')
        table_lst = list(table_lst.fetchall())
        table_name_lst = [item[1].strip() for item in table_lst]
        return table_name_lst

    def create(self, table_name):
        if table_name not in self.table_name_lst:
            self.conn.execute(self.create_sql.format(table_name))
            self.conn.commit()
        else:
            print("{}已有表{}".format(self.dbname, table_name))

    def write(self, table_name, data_lst):
        """
        table_name: str
        data_lst: tuple[str]
        """
        try:
            self.conn.execute(self.insert_sql.format(table_name), (*data_lst,))
        except Exception as e:
            print(e, data_lst[0])
        finally:
            self.conn.commit()

    def read(self, col_name, table_name):
        """
        col_name: str
        table_name: str
        """
        x = list(self.conn.execute("SELECT {} FROM '{}'".format(col_name, table_name)))
        self.conn.commit()
        data_lst = list(map(lambda item: item[0], x))
        print("[{}]表已存在{}条数据".format(table_name, len(data_lst)))
        return data_lst

    def read_all(self, table_name):
        table_res = self.conn.execute("SELECT * FROM '{}'".format(table_name))
        data_lst = table_res.fetchall()
        return data_lst

    def close(self):
        self.conn.close()
