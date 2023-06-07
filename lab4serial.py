'''
CIS 41B Spring 2023
Surajit A. Bose
Lab 4 Serial
'''

import requests
import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.filedialog
import json
from collections import defaultdict
import os
import time

class MainWindow(tk.Tk) :
    
    ### Class attributes
    # Where to download parks data
    ENDPOINT = 'https://developer.nps.gov/api/v1/parks'
    # Authentication
    API_KEY = 'npVAOGK1AASuoK9zENNclrb7dVZ7DYynBwp3UkYL'
    # How many states user can choose
    CHOICE_NUM = 5
    
    def __init__(self) :
        '''
        Construct the main window with all necessary widgets.
        This window is open throughout, and changes depending on execution flow.
        
        Some widgets are configurable by other methods, 
        and so those widgets are instance attributes:
            - middle label 
            - listbox
            - button
            - bottom label
        
        Other instance attributes:
            states_abbrs, dictionary mapping postal abbreviations to state names
            chosen_states, the states chosen by the user
            parks_data, with the info about all the parks in the chosen states
            chosen_parks, with the info for the specific parks chosen by the user  
        '''
        super().__init__()
        self.title('US NPS')
        
        try :
            with open('states_hash.json', 'r') as sh :
                self.state_abbrs = json.load(sh)
        except IOError :
            tkmb.showerror('Error', '''Cannot open states_hash.json. 
                    Please check the file name and path and try again.
                    ''', parent = self)
            self.destroy()
            self.quit()
        
        self.chosen_states = []
        self.parks_data = {}
        self.chosen_parks = defaultdict(list)
        self.protocol('WM_DELETE_WINDOW', self.closeout)
        
        top_label = tk.Label(self, text = 'National Park Finder', font = ('Helvetica', 16, 'bold'))
        top_label.grid(row = 0, column = 1, pady = 10)
        
        self.mid_label = tk.Label(self, text = f'Select up to {MainWindow.CHOICE_NUM} states')
        self.mid_label.grid(row = 1, column = 1)
        
        frame = tk.Frame(self)
        sb = tk.Scrollbar(frame, orient = 'vertical')
        self.lb = tk.Listbox(frame, height = 10, width = 50, selectmode = 'multiple', yscrollcommand = sb.set)
        sb.config(command = self.lb.yview)
        self.lb.grid(row = 0, column = 0)
        for val in self.state_abbrs.values():  
            self.lb.insert(tk.END, val)
        sb.grid(row = 0, column = 1, sticky = 'NS')
        
        frame.grid(row = 2, column = 0, columnspan = 3, padx = 10, pady = 10)
        
        self.btn = tk.Button(self, text = 'Submit Choice', command = self.getValidStateChoice)
        self.btn.grid(row = 3, column = 1, padx = 5, pady = 5)
        
        self.btm_label = tk.Label(self, text = '')
        self.btm_label.grid(row = 4, column = 1, pady = 5)

    
    def getValidStateChoice(self) :
        '''
        Allow the user to choose up to CHOICE_NUM states.
        If user makes a valid number of choices, call method to get park data.
        Otherwise, show error message and wait for user to pick again.
        '''
        indices = self.lb.curselection()
        if 1 <= len(indices) <= MainWindow.CHOICE_NUM :
            for num, key in enumerate(self.state_abbrs.keys()) :
                if num in indices :
                    self.chosen_states.append(key)
            self.getParksData()
        else :
            tkmb.showerror('Error', 'Please choose at least 1 and no more than 5 states', parent = self)
            self.lb.selection_clear(0, tk.END)          


    def getParksData(self) :
        '''
        Download, parse, and save the data for all the parks in the states chosen by the user.
        Get info about all national parks in the selected states via call to NPS API.
        If any state has no national parks, display error message for that state.
        Store parks info for the selected states in the following data structure.
        The data structure is a dictionary of dictionaries of dictionaries.
            - A dictionary where the key is the states
            - The value is a nested dictionary where the key is the park name
            - The value is a dictionary where the keys are the labels for park info such as full name
            - The values are the actual info:
                - the park's full name
                - a description of the park
                - a string that specifies the activities available in the park
                - the url of the park.       
        After fetching the data, call the method to allow user to choose specific parks.
        '''
        how_many = len(self.chosen_states)
        raw_data = {}
        start = time.time()
        for abbr in self.chosen_states :
            raw_data[abbr] = requests.get(MainWindow.ENDPOINT, params = {'stateCode' : abbr, 'api_key' : MainWindow.API_KEY}).json()['data']
        print(f'API download time for {", ".join(self.chosen_states)} using single thread: {time.time() - start:.4f}s')
        for abbr, data in raw_data.items() :
            state = self.state_abbrs[abbr]
            self.parks_data[state] = {}
            if not data :               # special case where chosen territory, e.g., Palau, has no national parks
                tkmb.showerror('Error', f'No national parks in {state}', parent = self)
                how_many -= 1
                if how_many == 0 :      # if user has chosen no state with a national park, quit the program
                    tkmb.showerror('Fatal Error', 'No national parks in the chosen areas. Program will exit.', parent = self)
                    self.destroy()
                    self.quit()
            for park in data :          # general case
                park_name = park['name']
                self.parks_data[state][park_name] = {}
                park_activities = []
                for activity in park['activities'] :
                    park_activities.append(activity['name'])
                self.parks_data[state][park_name]['full name'] = park['fullName'] 
                self.parks_data[state][park_name]['description'] = park['description'] 
                self.parks_data[state][park_name]['activities'] = ', '.join(park_activities)
                self.parks_data[state][park_name]['url'] = park['url']  
        self.updateBottomLabel(how_many)
    
    
    def updateBottomLabel(self, how_many)  :
        display_string =  f'Displaying parks in {how_many} states'
        if how_many == 1 :
            display_string = display_string[:-1]
        self.btm_label.config(text = display_string)
        self.getChosenParks()
  

    def getChosenParks(self) :
        '''
        Update window display to show the list of parks.
        Allow user to choose parks.
        Call the method to get the data for just the chosen parks.
        '''
        self.mid_label.config(text = 'Select one or more parks to save park data to file')
        self.lb.delete(0, tk.END)
        parks_list = []
        for k in self.parks_data.keys():
            for key in self.parks_data[k].keys() :
                tup = (k, key)
                parks_list.append(tup)
                self.lb.insert(tk.END, f'{tup[0]}: {tup[1]}')
            self.btn.config(text = 'Save', command = lambda: self.getChosenParksData(parks_list))
    
  
    def getChosenParksData(self, parks_list) :
        '''
        Save a data structure of just the user's chosen parks.
        
        The data structure is a dictionary where the keys are state names.
        The values are lists of dictionaries.
        Each dictionary in the list has one key-value pair.
        The key is the park's name, the value the data such as full name etc.
        
        After creating the data structure, call the method to let the user
        choose the directory where this data will be written out in JSON form.
        
        @param parks_list a list of tuples where the first value in each tuple 
        is the state name, the second the park name.
        '''
        indices = self.lb.curselection()
        if indices:
            chosen_tups = [parks_list[ind] for ind in indices]
            for abbr in self.chosen_states :
                name = self.state_abbrs[abbr]
                parks = [tup[1] for tup in chosen_tups if tup[0] == name]
                for park in self.parks_data[name] :
                    if park in parks:
                        this_park = {}
                        this_park[park] = self.parks_data[name][park]
                        self.chosen_parks[name].append(this_park)
            try :
                self.goToChosenDirectory()
            except FileNotFoundError :
                self.lb.selection_clear(0, tk.END)
        else:
            tkmb.showerror('Error', 'Please choose at least one park', parent = self)
                
    
    def goToChosenDirectory(self) :
        '''
        Let the user navigate to the directory for JSON data.
        - If the user cancels or closes the navigation window without choosing 
          a directory, let the raised FileNotFoundError caught by the caller.
        - Otherwise, call the method to write out the data to JSON.
        '''
        tkmb.showinfo('Choose Directory', 'Choose a directory for the park data files', parent = self)
        directory = tk.filedialog.askdirectory(initialdir = '.')
        chosen_dir = os.path.join(directory)
        os.chdir(chosen_dir)
        self.writeFile()
    
    
    def writeFile(self) :
        '''
        Write out the data for the chosen parks to JSON, one JSON file per state.
        When done, display window telling user the filenames, then quit.
        '''
        saved_files = []
        for state in self.chosen_parks :
            filename = f'{state}.json'
            try : 
                with open (filename, 'w') as fh:
                    json.dump(self.chosen_parks[state], fh, indent = 4, ensure_ascii = False)
                    saved_files.append(filename)
            except IOError :
                tkmb.showerror('Error', f'Error writing file {filename}. Continuing to next file.', parent = self)
                continue
        tkmb.showinfo('Saved', f'Saved files: {", ".join(saved_files)}', parent = self)
        self.destroy()
        self.quit()
     
        
    def closeout(self) :
        '''
        Ask for user confirmation before closing main window.
        - If user confirms, close and quit gracefully
        - If user cancels, do nothing
        '''        
        close = tkmb.askokcancel('Confirm exit', 'Close all windows and quit?', parent = self)
        if close: 
            self.destroy()
            self.quit()
            
        
if __name__ == '__main__' :
    MainWindow().mainloop()
    