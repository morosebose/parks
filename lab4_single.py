'''
CIS 41B Spring 2023
Surajit A. Bose
Lab 4 Single Thread
'''

import requests
import tkinter as tk
import tkinter.messagebox as tkmb
import json

class MainWindow(tk.Tk) :
    
    # Class attributes
    ENDPOINT = 'https://developer.nps.gov/api/v1/parks'
    API_KEY = 'npVAOGK1AASuoK9zENNclrb7dVZ7DYynBwp3UkYL'
    CHOICE_NUM = 5
    
    def __init__(self) :
        super().__init__()
        self.title('US NPS')
        
        # TODO: try/except
        with open('states_hash.json', 'r') as sh :
            self.state_data = json.load(sh)
        
        top_label = tk.Label(self, text = 'National Park Finder', font = ('Helvetica', 16, 'bold'))
        top_label.grid(row = 0, column = 1, pady = 10)
        
        self.mid_label = tk.Label(self, text = f'Select up to {MainWindow.CHOICE_NUM} states')
        self.mid_label.grid(row = 1, column = 1)
        
        frame = tk.Frame(self)
        sb = tk.Scrollbar(frame, orient = 'vertical')
        self.lb = tk.Listbox(frame, height = 10, width = 35, selectmode = 'multiple', yscrollcommand = sb.set)
        sb.config(command = self.lb.yview)
        for val in self.state_data.values() :
            self.lb.insert(tk.END, val)
        self.lb.grid(row = 0, column = 0)
        sb.grid(row = 0, column = 1, sticky = 'NS')
        
        frame.grid(row = 2, column = 0, columnspan = 3, padx = 10, pady = 10)
        
        self.btn = tk.Button(self, text = 'Submit Choice', command = self.validateAndProceed)
        self.btn.grid(row = 3, column = 1, padx = 5, pady = 5)
        
        self.btm_label = tk.Label(self, text = '')
        self.btm_label.grid(row = 4, column = 1, pady = 5)
        self.chosen_states = []
    
    def validateAndProceed(self) :
        indices = self.lb.curselection()
        if 1 <= len(indices) <= MainWindow.CHOICE_NUM :
            for num, key in enumerate(self.state_data.keys()) :
                if num in indices :
                    self.chosen_states.append(key)
            info = self.getParksInfo()
            self.showParkNames(info)
        else :
            tkmb.showerror('Error', 'Please choose at least 1 and no more than 5 states', parent = self)
            self.lb.selection_clear(0, tk.END)          


    def getParksInfo(self) :
        '''
        Parks info requested by user is stored in the following data structure:
            - A dictionary where the key is the states
            - The value is a nested dictionary where the key is the park name
            - the value is a dictionary where the keys are the labels for park info such as full name
            - the values are the actual info
        So the data structure is a dictionary of dictionaries of dictionaries.
        This structure is needed for writing out JSON. 
        Could have a dictionary of lists of dictionaries but I prefer this?
        '''
        self.btm_label.config(text = f'Displaying parks in {len(self.chosen_states)} states')
        parks_data = {}
        for state in self.chosen_states : 
            state_name = self.state_data[state]
            parks_data[state_name] = []
            data = requests.get(MainWindow.ENDPOINT, params = {'stateCode' : state, 'api_key' : MainWindow.API_KEY}).json()['data']
            for park in data :
                park_name = park['name']
                parks_data[state_name][park_name] = {}
                park_activities = []
                for activity in park['activities'] :
                    park_activities.append(activity['name'])
                parks_data[state_name][park_name]['full name'] = park['fullName'] 
                parks_data[state_name][park_name]['description'] = park['description'] 
                parks_data[state_name][park_name]['activities'] = park_activities
                parks_data[state_name][park_name]['url'] = park['url']         
        return parks_data
    
    
    def showParkNames(self, info) :
        self.mid_label.config(text = 'Select parks to save park info to file')
        self.lb.delete(0, tk.END)
        parks_list = []
        for k in info.keys():
            for key in info[k].keys() :
                tup = (k, key)
                parks_list.append(tup)
                self.lb.insert(tk.END, f'{tup[0]}: {tup[1]}')
        self.btn.config(text = 'Save', command = lambda: self.validateAndEnd(parks_list))
    
    def validateAndEnd(self, parks_list):
        indices = self.lb.curselection()
        if indices:
            for state in self.chosen_states :
                
                
        else: 
            tkmb.showerror('Error', 'Please choose at least one park')
    
        
if __name__ == '__main__' :
    MainWindow().mainloop()
    