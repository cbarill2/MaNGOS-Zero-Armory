from mysql import connector

import config

class Character:
    def __init__(self, char_data) -> None:
        self.data = char_data
        self.skills = None
        self.professions = None
    
    def __str__(self) -> str:
        return '{}, Level {} {} {}'.format(self.data['name'], self.data['level'], self.get_race(), self.get_class())

    def __repr__(self) -> str:
        return '{} {}'.format(self.data['guid'], self.data['name'])
        
    def get_name(self) -> str:
        return self.data['name']

    def get_class(self) -> str:
        return config.classes[self.data['class']]

    def get_race(self) -> str:
        return config.races[self.data['race']]

    def get_level(self) -> int:
        return int(self.data['level'])
    
    def get_xp(self) -> int:
        return int(self.data['xp'])

    def get_professions(self):
        """Returns a dictionary: {Skill Name: (Current, Max)}"""
        if self.professions is None:
            self.query_skills()
        return self.professions
        
    def get_skills(self):
        """Returns a dictionary: {Skill Name: (Current, Max)}"""
        if self.skills is None:
            self.query_skills()
        return self.skills
    
    def query_skills(self):
        cnx = connector.connect(**config.character_db_config)
        cursor = cnx.cursor()

        query = """
        SELECT
            skill, value, max
        FROM
            character_skills
        WHERE
            guid = %s
            and max > 1;
        """
        
        cursor.execute(query,(self.data['guid'],))
        
        professions = (333, 393, 202, 197, 186, 182, 171, 165, 164, 185, 129, 356)
        result = cursor.fetchall()
        self.professions = {config.professions.get(x,x):(y,z) for x,y,z in result if x in professions}
        self.skills = {config.other_skills.get(x,x):(y,z) for x,y,z in result if x not in professions}

        cursor.close()
        cnx.close()

    def get_quests(self, active_only=True):
        cnx = connector.connect(**config.character_db_config)
        cursor = cnx.cursor(dictionary=True)

        query = """
        SELECT 
            qt.title, qs.*
        FROM
            character_queststatus qs
                JOIN
            mangos1.quest_template qt ON qs.quest = qt.entry
        WHERE qs.guid = %s;
        """

        cursor.execute(query,(self.data['guid'],))
        result = cursor.fetchall()
        if active_only:
            result = [quest for quest in result if quest['rewarded'] == 0]
        
        cursor.close()
        cnx.close()
        return result

    def get_equipment(self):
        """Returns a dictionary: {Gear Slot: Item Name}"""
        cnx = connector.connect(**config.character_db_config)
        cursor = cnx.cursor()

        query = """
        SELECT 
            ci.slot, it.name
        FROM
            character1.character_inventory ci
	    JOIN
            mangos1.item_template it ON it.entry = ci.item_template
        WHERE
            ci.guid = %s
            and bag = 0
            and slot < 19
        ORDER BY
            slot;
        """

        cursor.execute(query,(self.data['guid'],))
        result = {config.equipment_slots.get(slot,slot):name for slot,name in cursor}
        
        cursor.close()
        cnx.close()
        return result

    def get_bags(self):
        """Returns results as a list of dictionaries, with each column name a key"""
        cnx = connector.connect(**config.character_db_config)
        cursor = cnx.cursor(dictionary=True)

        query = """
        SELECT 
            it.name,
            it.containerslots,
            it.bonding
        FROM
            character_inventory ci
                JOIN
            mangos1.item_template it ON it.entry = ci.item_template
        WHERE
            ci.guid = %s
            and ci.slot > 18 AND ci.slot < 23
            and it.class IN (1 , 11)
        ORDER BY
            containerslots desc;
        """

        cursor.execute(query,(self.data['guid'],))
        result = cursor.fetchall()
        
        cursor.close()
        cnx.close()
        return result

    def get_mail_in_mailbox(self):
        """Returns a list of 5-tuples: (Subject, Item, Item Count, Money, Expiration Date)"""
        cnx = connector.connect(**config.character_db_config)
        cursor = cnx.cursor()
        query = """
        SELECT 
            m.subject,
            it.name AS Item,
            SUBSTRING_INDEX(SUBSTRING_INDEX(ii.data, ' ', 15),
                    ' ',
                    - 1) AS Count,
            m.money,
            FROM_UNIXTIME(m.expire_time) AS expires
        FROM
            mail m
                LEFT OUTER JOIN
            mail_items mi ON m.id = mi.mail_id
                INNER JOIN
            mangos1.item_template it ON it.entry = mi.item_template
                INNER JOIN
            item_instance ii ON mi.item_guid = ii.guid
        WHERE m.receiver = %s
            AND (m.checked = 2 or m.stationery = 62)
        ORDER BY expires;
        """

        cursor.execute(query,(self.data['guid'],))
        result = [(subj,item,count,money,expires) for subj,item,count,money,expires in cursor]

        cursor.close()
        cnx.close()

        return result