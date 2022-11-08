from tkinter import Tk, StringVar, IntVar, ttk, constants, Listbox

import db_connect

class Armory:
    def __init__(self, root):
        root.title("Local WoW Armory")
        self.db = db_connect.DBConnection()

        root.columnconfigure(0,weight=1)
        root.rowconfigure(0,weight=1)

        base_frame = ttk.Frame(root, padding=5)
        base_frame.grid(sticky=(constants.N,constants.W,constants.E))
        base_frame.columnconfigure(0,weight=1)
        base_frame.rowconfigure(0,weight=1)

        skills_base_frame = ttk.Frame(root)
        skills_base_frame.grid(sticky=(constants.N,constants.W,constants.E))
        skills_base_frame.columnconfigure(0,weight=1)
        skills_base_frame.rowconfigure(0,weight=1)

        bags_base_frame = ttk.Frame(root)
        bags_base_frame.grid(sticky=(constants.N,constants.W,constants.E))
        bags_base_frame.columnconfigure(0,weight=1)
        bags_base_frame.rowconfigure(0,weight=1)

        equipment_base_frame = ttk.Frame(root)
        equipment_base_frame.grid(sticky=(constants.N,constants.W,constants.E))
        equipment_base_frame.columnconfigure(0,weight=1)
        equipment_base_frame.rowconfigure(0,weight=1)
        
        self.selected_account = StringVar()
        account_label = ttk.Label(base_frame, text="Account")
        account_label.grid(column=0,row=0,sticky=(constants.N,constants.W))
        account_list = ttk.Combobox(base_frame, textvariable=self.selected_account)
        account_list.grid(column=1,row=0,sticky=(constants.N,constants.E))
        account_list.state(['readonly'])
        account_list.focus()

        self.accounts = self.db.get_all_accounts()
        account_list['values'] = [name for name in self.accounts.keys()]
        account_list.bind('<<ComboboxSelected>>',self.set_character_list)

        char_label = ttk.Label(base_frame, text="Character")
        char_label.grid(column=0,row=1,sticky=(constants.W))
        self.selected_char = StringVar()
        self.character_list = ttk.Combobox(base_frame, textvariable=self.selected_char)
        self.character_list.state(['readonly'])
        self.character_list.grid(column=1,row=1,sticky=(constants.E))
        self.character_list.bind('<<ComboboxSelected>>',self.set_character_data)

        self.character_data = StringVar()
        self.character_label = ttk.Label(base_frame,textvariable=self.character_data)
        self.xp_progress = ttk.Progressbar(base_frame,orient=constants.HORIZONTAL,mode='determinate')

        self.build_professions_frame(skills_base_frame)
        self.build_skills_frame(skills_base_frame)
        self.build_bags_frame(bags_base_frame)
        self.build_equipment_frame(equipment_base_frame)

    def build_professions_frame(self, parent):
        self.professions_frame = ttk.LabelFrame(parent, text='Professions')
        self.professions_frame.columnconfigure(0,weight=1)
        self.professions_frame.rowconfigure(0,weight=1)
        self.professions = []
        self.profession_list = StringVar(value=self.professions)
        self.professions_listbox = Listbox(self.professions_frame,width=20,listvariable=self.profession_list,exportselection=0)
        self.professions_listbox.bind('<<ListboxSelect>>', self.update_profession_progress)
        self.profession_progress = ttk.Progressbar(self.professions_frame,orient=constants.VERTICAL,mode='determinate')
        self.profession_max = IntVar()
        self.profession_cur = IntVar()
        self.profession_max_label = ttk.Label(self.professions_frame, textvariable=self.profession_max)
        self.profession_cur_label = ttk.Label(self.professions_frame, textvariable=self.profession_cur)
        
    def build_skills_frame(self, parent):
        self.skills_frame = ttk.LabelFrame(parent, text='Other Skills')
        self.skills_frame.columnconfigure(0,weight=1)
        self.skills_frame.rowconfigure(0,weight=1)
        self.skills = []
        self.skill_list = StringVar(value=self.skills)
        self.skills_listbox = Listbox(self.skills_frame,width=20,listvariable=self.skill_list,exportselection=0)
        self.skills_listbox.bind('<<ListboxSelect>>', self.update_skill_progress)
        self.skill_progress = ttk.Progressbar(self.skills_frame,orient=constants.VERTICAL,mode='determinate')
        self.skill_max = IntVar()
        self.skill_cur = IntVar()
        self.skill_max_label = ttk.Label(self.skills_frame, textvariable=self.skill_max)
        self.skill_cur_label = ttk.Label(self.skills_frame, textvariable=self.skill_cur)

    def build_bags_frame(self, parent):
        self.bags_frame = ttk.LabelFrame(parent, text='Bags')
        self.bags_frame.columnconfigure(0,weight=1)
        self.bags_frame.rowconfigure(0,weight=1)
        self.bags = []
        self.bags_list = StringVar(value=self.bags)
        self.bags_label = ttk.Label(self.bags_frame, textvariable=self.bags_list)

    def build_equipment_frame(self, parent):
        self.equipment_frame = ttk.LabelFrame(parent, text='Equipment')
        self.equipment_frame.columnconfigure(0,weight=1)
        self.equipment_frame.rowconfigure(0,weight=1)
        self.equipment = []
        self.equipment_list = StringVar(value=self.equipment)
        self.equipment_listbox = Listbox(self.equipment_frame,width=20,listvariable=self.equipment_list,exportselection=0)

    def set_character_list(self, *args):
        self.characters = self.accounts[self.selected_account.get()].get_characters()
        self.character_list['values'] = [name for name in self.characters.keys()]
        self.character_list.set('')
        self.clear_char_data()
    
    def clear_char_data(self):
        self.character_label.grid_remove()
        self.xp_progress.grid_remove()
        self.professions_frame.grid_remove()
        self.skills_frame.grid_remove()
        self.bags_frame.grid_remove()
        self.equipment_frame.grid_remove()

    def set_character_data(self, *args):
        self.character_data.set('\n' + str(self.characters[self.selected_char.get()]))
        self.character_label.grid(columnspan=2,row=2)
        current_xp = self.characters[self.selected_char.get()].get_xp()
        current_level = self.characters[self.selected_char.get()].get_level()
        self.xp_progress['maximum'] = self.db.get_xp_to_level(current_level)
        self.xp_progress['value'] = current_xp if current_level < 60 else self.xp_progress['maximum']
        self.xp_progress.grid(columnspan=2,row=3,sticky=(constants.N,constants.E,constants.W))
        
        self.set_profession_list()
        self.set_skills_list()
        self.set_bags_list()
        self.set_equipment_list()
        self.clear_selections()

    def clear_selections(self):
        self.skill_progress['value'] = 0
        self.skill_cur_label.grid_remove()
        self.skill_max_label.grid_remove()
        self.profession_progress['value'] = 0
        self.profession_cur_label.grid_remove()
        self.profession_max_label.grid_remove()
    
    def set_profession_list(self):
        self.professions_dict = self.characters[self.selected_char.get()].get_professions()
        self.professions = [skill for skill in self.professions_dict.keys()]
        self.professions.sort()
        self.profession_list.set(self.professions)
        self.professions_listbox['height'] = len(self.professions)
        self.professions_frame.grid(column=0,row=0,sticky=(constants.W,constants.N))
        self.professions_listbox.grid(column=0,rowspan=2,sticky=(constants.N,constants.S))
        self.profession_progress.grid(column=1,row=0,rowspan=2,padx=5,sticky=(constants.NS,constants.S))

    def set_skills_list(self):
        self.skills_dict = self.characters[self.selected_char.get()].get_skills()
        self.skills = [skill for skill in self.skills_dict.keys()]
        self.skill_list.set(self.skills)
        self.skills_listbox['height'] = len(self.skills)
        self.skills_frame.grid(column=1,row=0,sticky=(constants.N,constants.W))
        self.skills_listbox.grid(column=2,row=0,rowspan=2,sticky=(constants.N,constants.S))
        self.skill_progress.grid(column=1,row=0,rowspan=2,padx=5,sticky=(constants.N,constants.S))

    def set_bags_list(self):
        self.bags_dict = self.characters[self.selected_char.get()].get_bags()
        self.bags = ['{0:2d} {1}'.format(row['containerslots'],row['name']) for row in self.bags_dict]
        self.bags_list.set('\n'.join(self.bags))
        self.bags_frame.grid(column=0,row=0,sticky=(constants.N,constants.E,constants.W))
        self.bags_label.grid(column=0,row=0,sticky=(constants.N,constants.S,constants.E,constants.W))

    def set_equipment_list(self):
        self.equipment_dict = self.characters[self.selected_char.get()].get_equipment()
        self.equipment = ['{0}: {1}'.format(slot,item) for slot,item in self.equipment_dict.items()]
        self.equipment_list.set(self.equipment)
        self.equipment_listbox['height'] = len(self.equipment)
        self.equipment_frame.grid(column=0,row=0,sticky=(constants.E,constants.W,constants.N))
        self.equipment_listbox.grid(column=0,rowspan=2,sticky=(constants.N,constants.S,constants.E,constants.W))

    def update_skill_progress(self, *args):
        try:
            skill = self.skills[self.skills_listbox.curselection()[0]]
        except:
            return
        self.skill_progress['value'] = self.skills_dict[skill][0]
        self.skill_progress['maximum'] = self.skills_dict[skill][1]
        self.skill_cur.set(self.skills_dict[skill][0])
        self.skill_max.set(self.skills_dict[skill][1])
        self.skill_cur_label.grid(column=0,row=1,sticky=(constants.S,constants.E))
        self.skill_max_label.grid(column=0,row=0,sticky=(constants.N,constants.E))
    
    def update_profession_progress(self, *args):
        try:
            skill = self.professions[self.professions_listbox.curselection()[0]]
        except:
            return
        self.profession_progress['value'] = self.professions_dict[skill][0]
        self.profession_progress['maximum'] = self.professions_dict[skill][1]
        self.profession_cur.set(self.professions_dict[skill][0])
        self.profession_max.set(self.professions_dict[skill][1])
        self.profession_cur_label.grid(column=2,row=1,sticky=(constants.S,constants.W))
        self.profession_max_label.grid(column=2,row=0,sticky=(constants.N,constants.W))
            

def window():
    root = Tk()
    Armory(root)
    root.minsize(400,600)
    root.mainloop()

if __name__ == "__main__":
    window()