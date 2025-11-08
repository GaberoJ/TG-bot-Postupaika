import psycopg2


class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host='',
            database='myproject',
            user='',
            password=''
        )

    def create_table(self, table_name, columns):
        cur = self.conn.cursor()
        columns_str = ', '.join(columns)

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            {columns_str}
        );
        """

        cur.execute(create_table_query)
        self.conn.commit()
        cur.close()

    def drop_table(self, table_name):
        cur = self.conn.cursor()

        drop_table_query = f"DROP TABLE IF EXISTS {table_name};"

        cur.execute(drop_table_query)
        self.conn.commit()
        cur.close()

    def insert_data(self, table_name, data):
        cur = self.conn.cursor()
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))

        insert_query = f"""
        INSERT INTO {table_name} ({columns}) 
        VALUES ({values})
        """

        cur.execute(insert_query, list(data.values()))
        self.conn.commit()
        cur.close()

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = DatabaseManager()

    # db.create_table("vuzi", [
    #     "name VARCHAR(255) NOT NULL UNIQUE",
    #     "city VARCHAR(100)",
    #     "link TEXT"
    # ])

    # test_data = {
    #     'name': 'Тестовый университет2',
    #     'city': 'Москва',
    #     'link_po': 'https://example.com'
    # }
    #
    # db.insert_data("vuzi", test_data)

    # db.drop_table("vuzi")

    db.close()
