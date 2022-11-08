from mysql import connector

import config, character

class Account:
    def __init__(self, acc_data) -> None:
        self.data = acc_data
        self.characters = {}
    
    def get_id(self):
        return self.data['id']

    def get_characters(self):
        if len(self.characters) == 0:
            cnx = connector.connect(**config.character_db_config)
            cursor = cnx.cursor(dictionary=True)

            query = """select * from characters where account = %s"""
            cursor.execute(query, (self.data['id'],))

            for row in cursor:
                self.characters[row['name']] = character.Character(row)

            cursor.close()
            cnx.close()
        return self.characters