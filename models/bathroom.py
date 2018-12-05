import datetime
import psycopg2
import config


class Bathroom:
    def __init__(self, floor, number, status):
        self.floor = floor
        self.number = number
        self.status = status

    def open(self):
        status = 'open'

    def close(self):
        status = 'close'

    def log(self):
        sql = """INSERT INTO doorlog(floor, bathroom_number, status, log_time)
                 VALUES(%s) RETURNING id;"""
        conn = None
        log_id = None
        try:
            params = config()
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            cur.execute(sql, (self.floor, self.number, self.status, datetime.datetime.now()))
            log_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return log_id

