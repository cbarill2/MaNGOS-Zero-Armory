from mysql import connector
from sys import argv

import account,character,config

class DBConnection:
    def __init__(self) -> None:
        self.accounts = {}
        self.xp_to_level = {}

    def get_account(self,account_name):
        acc = self.accounts.get(account_name)
        if acc is None:
            connection = connector.connect(**config.realm_db_config)
            cursor = connection.cursor(dictionary=True)
            query = """select * from account where username = %s"""
            cursor.execute(query, (account_name,))
            for row in cursor:
                acc = account.Account(row)
                self.accounts[account_name] = acc
            cursor.close()
            connection.close()
        return acc

    def get_all_accounts(self):
        connection = connector.connect(**config.realm_db_config)
        cursor = connection.cursor(dictionary=True)
        query = """select * from account"""
        cursor.execute(query)
        for row in cursor:
            acc = account.Account(row)
            self.accounts[row['username']] = acc
        cursor.close()
        connection.close()
        return self.accounts

    def get_xp_to_level(self, level):
        if self.xp_to_level.get(level) is None:
            conn = connector.connect(**config.world_db_config)
            cursor = conn.cursor(dictionary=True)
            query = """select * from player_xp_for_level"""
            cursor.execute(query)
            for row in cursor:
                self.xp_to_level[row['lvl']] = row['xp_for_next_level']
            cursor.close()
            conn.close()
        return self.xp_to_level[level]

    def print_all_character_skills(professions_only=False):
        cnx = connector.connect(**config.no_db_config)
        cursor = cnx.cursor()

        query = """SELECT c.name, cs.skill, cs.value, cs.max
        FROM character1.character_skills cs
        JOIN character1.characters c
        ON c.guid = cs.guid
        WHERE cs.max > 1
        """

        if professions_only:
            query += """and cs.skill IN (333 , 393, 202, 197, 186, 182, 171, 165, 164, 185)"""
        
        query += """order by c.name;"""
        cursor.execute(query)

        curr_char = ''
        for char_name,skill,current_value,max_value in cursor:
            if curr_char != char_name:
                curr_char = char_name
                print(curr_char.center(24))
            print("{0:18} {1:3}/{2:3}".format(character.skills.get(skill,skill), current_value, max_value))

        cursor.close()
        cnx.close()
        
        # printAllCharacterSkills(professions_only=True)
characters = {}

def get_character_by_name(char_name):
    toon = characters.get(char_name)
    if toon is None:
        connection = connector.connect(**config.character_db_config)
        cursor = connection.cursor(dictionary=True)
        query = """select * from characters where name = %s"""
        cursor.execute(query, (char_name,))
        row = cursor.fetchone()
        toon = character.Character(row)
        characters[char_name] = toon
        cursor.close()
        connection.close()
    return toon

def test_character(char_name):
    char = get_character_by_name(char_name)
    print(char)
    for skill,vals in char.get_skills(True).items():
        print(skill, vals[0], '/', vals[1])
    for letter in char.get_mail_in_mailbox():
        print('Subject: {}\nAttached: {} {}, {} Copper\nExpires: {}\n'.format(
            letter[0],letter[2],letter[1],letter[3],letter[4]))
    print('Active Quests:')
    for quest in char.get_quests():
        print('{}'.format(quest['title']))

if __name__=='__main__':
    if len(argv) > 1:
        char_name = argv[1]
    else:
        char_name = 'arr'
    # test_character(char_name)
    test_character('stew')