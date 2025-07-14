import cv2
import sqlite3
import numpy as np


class DataBase:

    ####################____________________####################
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        print("Database connected!")

    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed!")

    ####################____________________####################
    def create_table(self, table_name):
        self.conn.execute(
            f"""
                CREATE TABLE IF NOT EXISTS '{table_name}' (
                name TEXT NOT NULL UNIQUE,
                img_1 BLOB,
                emb_1 BLOB,
                img_2 BLOB,
                emb_2 BLOB
                );
            """
        )
        self.conn.commit()

    def read_table(self):
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        return [table[0] for table in cursor.fetchall()]

    def update_table(self, old_table_name, new_table_name):
        self.conn.execute(f"ALTER TABLE '{old_table_name}' RENAME TO '{new_table_name}';")
        self.conn.commit()

    def delete_table(self, table_name):
        self.conn.execute(f"DROP TABLE IF EXISTS '{table_name}';")
        self.conn.commit()

    ####################____________________####################

    ####################____________________####################

    def create_face_name(self, table_name, face_name):
        self.conn.execute(f"INSERT INTO '{table_name}' (name) VALUES (?);", (face_name,))
        self.conn.commit()

    def read_face_names(self, table_name):
        cursor = self.conn.execute(f"SELECT name FROM '{table_name}' ORDER BY name;")
        return [row[0] for row in cursor.fetchall()]

    def update_face_name(self, table_name, old_face_name, new_face_name):
        self.conn.execute(f"UPDATE '{table_name}' SET name = ? WHERE name = ?;", (new_face_name, old_face_name))
        self.conn.commit()

    def delete_face_name(self, table_name, face_name):
        self.conn.execute(f"DELETE FROM '{table_name}' WHERE name = ?;", (face_name,))
        self.conn.commit()

    ####################____________________####################

    ####################____________________####################

    def create_image_1_from_path(self, table_name, face_name, file_name):
        img_blob = open(file_name, "rb").read()
        self.conn.execute(f"UPDATE '{table_name}' SET img_1 = ? WHERE name = ?;", (img_blob, face_name))
        self.conn.commit()

    def create_image_1_from_array(self, table_name, face_name, img_array):
        img_blob = cv2.imencode(".jpg", img_array)[1].tobytes()
        self.conn.execute(f"UPDATE '{table_name}' SET img_1 = ? WHERE name = ?;", (img_blob, face_name))
        self.conn.commit()

    def read_image_1(self, table_name, face_name):
        cursor = self.conn.execute(f"SELECT img_1 FROM '{table_name}' WHERE name = ?;", (face_name,))
        img_blob = cursor.fetchone()[0]
        if img_blob:
            img = cv2.imdecode(np.frombuffer(img_blob, np.uint8), cv2.IMREAD_COLOR)
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return None

    def update_image_1(self, table_name, face_name, file_name):
        img_blob = open(file_name, "rb").read()
        self.conn.execute(f"UPDATE '{table_name}' SET img_1 = ? WHERE name = ?;", (img_blob, face_name))
        self.conn.commit()

    def delete_image_1(self, table_name, face_name):
        self.conn.execute(f"UPDATE '{table_name}' SET img_1 = NULL WHERE name = ?;", (face_name,))
        self.conn.commit()

    ####################____________________####################

    ####################____________________####################

    def create_emb_1(self, table_name, face_name, emb):
        emb_blob = emb.tobytes()
        self.conn.execute(f"UPDATE '{table_name}' SET emb_1 = ? WHERE name = ?;", (emb_blob, face_name))
        self.conn.commit()

    def read_emb_1(self, table_name, face_name):
        cursor = self.conn.execute(f"SELECT emb_1 FROM '{table_name}' WHERE name = ?;", (face_name,))
        emb_blob = cursor.fetchone()[0]
        if emb_blob:
            return np.frombuffer(emb_blob, dtype=np.float32)
        return None

    def update_emb_1(self, table_name, face_name, emb):
        emb_blob = emb.tobytes()
        self.conn.execute(f"UPDATE '{table_name}' SET emb_1 = ? WHERE name = ?;", (emb_blob, face_name))
        self.conn.commit()

    def delete_emb_1(self, table_name, face_name):
        self.conn.execute(f"UPDATE '{table_name}' SET emb_1 = NULL WHERE name = ?;", (face_name,))
        self.conn.commit()

    ####################____________________####################

    ####################____________________####################

    def create_emb_2(self, table_name, face_name, emb):
        emb_blob = emb.tobytes()
        self.conn.execute(f"UPDATE '{table_name}' SET emb_2 = ? WHERE name = ?;", (emb_blob, face_name))
        self.conn.commit()

    def read_emb_2(self, table_name, face_name):
        cursor = self.conn.execute(f"SELECT emb_2 FROM '{table_name}' WHERE name = ?;", (face_name,))
        emb_blob = cursor.fetchone()[0]
        if emb_blob:
            return np.frombuffer(emb_blob, dtype=np.float32)
        return None

    def update_emb_2(self, table_name, face_name, emb):
        emb_blob = emb.tobytes()
        self.conn.execute(f"UPDATE '{table_name}' SET emb_2 = ? WHERE name = ?;", (emb_blob, face_name))
        self.conn.commit()

    def delete_emb_2(self, table_name, face_name):
        self.conn.execute(f"UPDATE '{table_name}' SET emb_2 = NULL WHERE name = ?;", (face_name,))
        self.conn.commit()

    ####################____________________####################

    ####################____________________####################

    def create_image_2_from_path(self, table_name, face_name, file_name):
        img_blob = open(file_name, "rb").read()
        self.conn.execute(f"UPDATE '{table_name}' SET img_2 = ? WHERE name = ?;", (img_blob, face_name))
        self.conn.commit()

    def create_image_2_from_array(self, table_name, face_name, img_array):
        img_blob = cv2.imencode(".jpg", img_array)[1].tobytes()
        self.conn.execute(f"UPDATE '{table_name}' SET img_2 = ? WHERE name = ?;", (img_blob, face_name))
        self.conn.commit()

    def read_image_2(self, table_name, face_name):
        cursor = self.conn.execute(f"SELECT img_2 FROM '{table_name}' WHERE name = ?;", (face_name,))
        img_blob = cursor.fetchone()[0]
        if img_blob:
            img = cv2.imdecode(np.frombuffer(img_blob, np.uint8), cv2.IMREAD_COLOR)
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return None

    def update_image_2(self, table_name, face_name, file_name):
        img_blob = open(file_name, "rb").read()
        self.conn.execute(f"UPDATE '{table_name}' SET img_2 = ? WHERE name = ?;", (img_blob, face_name))
        self.conn.commit()

    def delete_image_2(self, table_name, face_name):
        self.conn.execute(f"UPDATE '{table_name}' SET img_2 = NULL WHERE name = ?;", (face_name,))
        self.conn.commit()

    ####################____________________####################

    ####################____________________####################

    def read_name_emb1_emb2(self, table_name):
        cursor = self.conn.execute(f"SELECT name, emb_1, emb_2 FROM '{table_name}';")
        results = []
        for row in cursor.fetchall():
            name = row[0]
            emb_1 = np.frombuffer(row[1], dtype=np.float32) if row[1] else None
            emb_2 = np.frombuffer(row[2], dtype=np.float32) if row[2] else None
            results.append((name, emb_1, emb_2))
        return results

    ####################____________________####################
