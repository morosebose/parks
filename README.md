# parks

## Description 
This project has three main code files. All three do the same thing:
- Show the user a list of states and ask user to pick up to five
- For the chosen states, display a list of national parks therein. The data is from an API call to the US National Parks Service.
- Allow the user to choose national parks whose data can be written out to JSON files.
Each of the code files implements the code differently.
### lab4series.py : Serial implementation
API call to NPS is made by looping over all the requested states in series
### lab4threads.py : Multithreading implementation  
API call is made via concurrent threads, one thread per state. 
### lab4series.py : Multiprocessing implementation
API call is made via parallel processes, one process per state.

## Skills used
- Requests
- TKinter
- JSON
- Multithreading and multiprocessing

## Credits
- states_hash.json from [Michael Shafrir](https://gist.github.com/mshafrir/2646763)
- Parks data from [US National Parks Service API](https://www.nps.gov/subjects/developer/get-started.htm)
- Lab 4 for CIS 41B (Advanced Python Programming) at De Anza College, Spring 2023.
- Professor: Clare Nguyen
- Author: Surajit A. Bose, © 2023
