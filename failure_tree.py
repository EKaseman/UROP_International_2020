#Author: Evan Kaseman
#Created: 5/29/2020
#Last Updated: 7/13/2020

#The purpose of this program is to create a failure tree for
#a self-learning expert system. This failure tree will be used
#to populate a Bayesian Network

#importing packages
import numpy as np
import pandas as pd
import tkinter as tk
import openpyxl as op
from tkinter import filedialog
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from networkx.drawing.nx_pydot import to_pydot

# Global variables
df = None
files = 0
processes = []

# Class to create process objects to store all aspects of process    
class Process:
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.errors = []
    #add new error to process        
    def add_error(self, error):
        self.errors.append(error)
    #access a single error in the process
    def get_error(self, index):
        return self.errors[index]
    #access all errors in the process
    def get_errors(self):
        return self.errors
    def __repr__(self):
        return f'{self.name!r}'

# Class to create error objects to store all aspects of the error
class Error:
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.causes = []
        self.effects = []
        self.detections = []
        self.actions = []
        self.total_cause_probability = 0
    #add new cause to the errors in the process
    def add_cause(self, cause, probability):
        self.total_cause_probability = self.total_cause_probability + probability
        self.causes.append(Cause(cause,probability)) 
    #access a single cause of the error in the process
    def get_cause(self, index):
        return self.causes[index]
    #access cause of errors in the process
    def get_causes(self):
        return self.causes
    #get total cause probability to calculate probabilty for each cause for the error
    def get_total_cause_prob(self):
        if (self.total_cause_probability <= 5):
            return 5 #since scale is originally from 1-5, if the occurance values don't add up to greater than 5, use 5 as the total probability
        else:
            return self.total_cause_probability #if total probability is greater than 5, use that number as the reference to calculate cause probabilities
    #add new effect of the errors in the process
    def add_effect(self, effect, severity):
        self.effects.append(Effect(effect, severity))
    #access a single effect of the error in the process
    def get_effect(self, index):
        return self.effects[index]
    #access effects of the errors in the process
    def get_effects(self):
        return self.effects
    #add new detection method for the error
    def add_detection_method(self, detection, probability):
        self.detections.append(Detection(detection,probability))
    #access a single detection method of the error in the process
    def get_detection_method(self, index):
        return self.detections[index]
    #access detection method of the errors in the process
    def get_detection_methods(self):
        return self.detections
    #add new action for the error
    def add_action(self, action_to_be_taken):
        self.actions.append(Action(action_to_be_taken))
    #access a single action of the error in the process
    def get_action(self, index):
        return self.action[index]
    #access actions for the errors in the process
    def get_actions(self):
        return self.actions
    def __repr__(self):
        return f'{self.name!r}'
    
# Class to create cause objects to store all aspects of the cause
class Cause:
    def __init__(self, name, probability):
        super().__init__()
        self.name = name
        self.probability = probability
    #set probability that this caused the error
    def set_occ_prob(self, probability):
        self.probability = probability
    #get probability that this caused the error
    def get_occ_prob(self):
        return self.probability
    def __repr__(self):
        return f'{self.name!r}'

# Class to create effect objects to store all aspects of the effect
class Effect:
    def __init__(self, name, severity):
        super().__init__()
        self.name = name
        self.severity = severity
    #set severity value of this effect
    def set_severity(self, severity):
        self.severity = severity
    #get severity value of this effect
    def get_severity(self):
        return self.severity
    def __repr__(self):
        return f'{self.name!r}'

# Class to create detection objects to store all aspects of the detection process
class Detection:
    def __init__(self, name, probability):
        super().__init__()
        self.name = name
        self.probability = probability
    #set probability of detection for this error
    def set_detection_probability(self, probability):
        self.probability = probability
    #get probability of detection for this error
    def get_detection_probability(self):
        return self.probability
    def __repr__(self):
        return f'{self.name!r}'

# Class to create action objects to store all aspects of action to be taken
class Action:
    def __init__(self, action_to_be_taken):
        super().__init__()
        self.action_to_be_taken = action_to_be_taken
    #set probability of detection for this error
    def set_action(self, action_to_be_taken):
        self.action_to_be_taken = action_to_be_taken
    #get probability of detection for this error
    def get_action(self):
        return self.action_to_be_taken
    def __repr__(self):
        return f'{self.action_to_be_taken!r}'

# Take FMEA Excel data and store the errors, causes, effects, etc. in each
# of the respective processes
def populate_data(df, files):
    # loop repeatedly until the last row of data is parsed and organized to be added to the
    # Bayesian Network 
    for i in range(len(df)):
        # Only enter this if statement if the row has a new error in the first column
        if (df.at[i,1] != "NA"):
            curr_error = Error(df.at[i,1])
            # Only add effect if the cell in column 2 is not "NA"
            if (df.at[i,2] != "NA"):
                curr_error.add_effect(df.at[i,2],df.at[i,3])
            # Only add cause if the cell in column 5 is not "NA"
            if (df.at[i,5] != "NA"):
                curr_error.add_cause(df.at[i,5],df.at[i,6])
            # Only add detection method if the cell in column 8 is not "NA"
            if (df.at[i,8] != "NA"):
                curr_error.add_detection_method(df.at[i,8],df.at[i,9])
            # Only add action if the cell in column 11 is not "NA"
            if (df.at[i,11] != "NA"):
                curr_error.add_action(df.at[i,11])
            # If the next row has a new error in it or if in the last row, add the error to the process
            if ((i+1 == len(df)) or (df.at[i+1,1] != "NA")):
                processes[files].add_error(curr_error)
        # If the row does not have a new error in the first column, this is an additional
        # cause and/or effect that is added to the current error
        else:
            if (df.at[i,2] != "NA"):
                curr_error.add_effect(df.at[i,2],df.at[i,3])
            if (df.at[i,5] != "NA"):
                curr_error.add_cause(df.at[i,5],df.at[i,6])
            if (df.at[i,8] != "NA"):
                curr_error.add_detection_method(df.at[i,8],df.at[i,9])
            if (df.at[i,11] != "NA"):
                curr_error.add_action(df.at[i,11])
            if ((i+1 == len(df)) or (df.at[i+1,1] != "NA")):
                processes[files].add_error(curr_error)

# Create a Bayesian Network for each process and add it to the list of Bayesian Networks.  Then, plot the BN in an png file
def create_network(models, processes, files): 
    for p in range(files):
        temp_model = BayesianModel()
        for e in range(len(processes[p].get_errors())):
            temp_error = processes[p].get_error(e)
            for c in range(len(temp_error.get_causes())):
                temp_cause = temp_error.get_cause(c)
                q = temp_cause.get_occ_prob()/temp_error.get_total_cause_prob()
                temp_cause.set_occ_prob(q)
                temp_model.add_nodes_from([temp_cause,temp_error])
                temp_model.add_edge(temp_cause,temp_error)
                temp_cause_cpd = TabularCPD(variable = temp_cause, variable_card = 2, values = [[q,1-q]])
                temp_model.add_cpds(temp_cause_cpd)
            temp_error_cpd = TabularCPD(variable = temp_error, variable_card=2, 
                                        values = get_initial_error_cpd(len(temp_error.get_causes())), 
                                        evidence = temp_error.get_causes(),
                                        evidence_card = [2]*(len(temp_error.get_causes())))
            temp_model.add_cpds(temp_error_cpd)
            for f in range(len(temp_error.get_effects())):
                temp_effect = temp_error.get_effect(f)
                temp_model.add_nodes_from([temp_error,temp_effect])
                temp_model.add_edge(temp_error,temp_effect)
        models.append(temp_model)
        #plotting Failure Tree
        dot = to_pydot(models[p])
        with open('failure_tree_graph_%s.png' % processes[p], 'wb') as f:
            f.write(dot.create_png())
        #Sample output of CPDs for causes and errors
        for e in range(len(processes[p].get_errors())):
            for c in range(len(processes[p].get_error(e).get_causes())):
                print(temp_model.get_cpds(processes[p].get_error(e).get_cause(c)))
            print(temp_model.get_cpds(processes[p].get_error(e)))

# Function to read in the Excel file from the FMEA data. The usecols argument of the read_excel method was used to select
# the appropriate columns of the dataset for the failures, causes, effects as well as the probability of occurrence, severity,
# and detection probability. Additionally, the actions to be taken to resolve the error are read in to provide the appropriate 
# suggestions for later action by the user.
def getExcel ():
    global df
    global files

    # Opens up file explorer for user to select the desired FMEA data from an Excel file
    import_file_path = filedialog.askopenfilename() 
    # Read the excel file in and store the FMEA data in a DataFrame
    df = pd.read_excel(import_file_path, header=None, index_col=None, usecols="B:D,F,G,I,J,L", skiprows=range(10))
    # Replace blank cells in the data with NaN. Then, remove rows at end of data
    # if they are completely empty.
    df = df.replace(r'^\s+$', np.nan, regex=True).dropna(how='all')
    # Replace NaN with the string "NA" so that it can be compared with type string later
    df = df.replace(np.nan, "NA", regex=True)
    # Replace "NA" with 1.0 for the columns associated with the probability of occurrence,
    # severity, or detection probability. Missing data is treated as a the lowest rating on
    # a 1-5 scale, which is a 1.0
    df = df.replace({3: "NA", 6: "NA", 9: "NA"}, 1)
    # Call populate_data method to store FMEA data in Bayesian Network
    populate_data(df,files)
    # Increment file count to keep track of how many processes are being evaluated
    files = files + 1

# initialize the error cpd using the Maximum Entropy theory because the conditional probabilities are unknown
def get_initial_error_cpd(number_of_causes):
    values = []
    # Using Maximum Entropy theory, each failure cause has an equal 1/s probability, where s is the total number of failure causes.
    # This is used because the conditional probabilities of the errors given the causes are not known.
    # An initial CPD is established for each error based on the number of causes using this theory.
    # Once the model is trained with more data, these probabilities will more accurately reflect the 
    # true probabilities of the process.
    f = 1/number_of_causes
    if (number_of_causes == 1):
        values = [[1,0],[0,1]]
    elif (number_of_causes == 2):
        values = [[2*f,1*f,1*f,0*f],
                  [0*f,1*f,1*f,2*f]]
    elif (number_of_causes == 3):
        values = [[3*f,2*f,2*f,1*f,2*f,1*f,1*f,0*f],
                  [0*f,1*f,1*f,2*f,1*f,2*f,2*f,3*f]]
    elif (number_of_causes == 4):
        values = [[4*f,3*f,3*f,2*f,3*f,2*f,2*f,1*f,3*f,2*f,2*f,1*f,2*f,1*f,1*f,0*f],
                  [0*f,1*f,1*f,2*f,1*f,2*f,2*f,3*f,1*f,2*f,2*f,3*f,2*f,3*f,3*f,4*f]]
    elif (number_of_causes == 5):
        values = [[5*f,4*f,4*f,3*f,4*f,3*f,3*f,2*f,4*f,3*f,3*f,2*f,3*f,2*f,2*f,1*f,4*f,3*f,3*f,2*f,3*f,2*f,2*f,1*f,3*f,2*f,2*f,1*f,2*f,1*f,1*f,0*f],
                  [0*f,1*f,1*f,2*f,1*f,2*f,2*f,3*f,1*f,2*f,2*f,3*f,2*f,3*f,3*f,4*f,1*f,2*f,2*f,3*f,2*f,3*f,3*f,4*f,2*f,3*f,3*f,4*f,3*f,4*f,4*f,5*f]]
    else:
        values = []
    return values

# function definition for sort method to sort causes by occurrence probability
def sort_func(cause):
    return cause.get_occ_prob()

# prints ordered list of causes based on their occurrence probability
def get_ordered_cause_list(processes):
    for p in range(files):
        for e in range(len(processes[p].get_errors())):
            temp_error = processes[p].get_error(e)
            # sort method to sort by occurrence probability. Reverse is true so that it sorts from largest cause to smallest in
            # terms of probability
            temp_error.get_causes().sort(key=sort_func, reverse=True)
            # Print causes in order with their associated probability
            print('Error: {}'.format(temp_error))
            for c in range(len(temp_error.get_causes())):
                print('{}. Cause: {} | Probability: {}'.format(c+1,temp_error.get_cause(c), temp_error.get_cause(c).get_occ_prob()))  
            print()     

def main():    
    # list of processes in the weaving process
    process_names = ['Finished Goods','Fixed Goods','Yarn','Washed Goods','Water-Repellent Goods','Warp Beam','Raw Goods']

    # creating a list of Process objects 
    for x in range(len(process_names)):
        processes.append(Process(process_names[x]))
        
    #### importing data from FMEA excel files
    root = tk.Tk()

    canvas1 = tk.Canvas(root, width = 300, height = 300, bg = 'grey')
    canvas1.pack()

    browseButton_Excel = tk.Button(text='Import Excel File', command=getExcel, bg='green', fg='white', font=('helvetica', 12, 'bold'))
    quit_button = tk.Button(text = 'Click and Quit', command=root.destroy)
    canvas1.create_window(150, 150, window=browseButton_Excel)
    canvas1.create_window(150, 200, window=quit_button)

    root.mainloop()

    # Create a list of Bayesian Models for each of the processes
    models = []
    # Call function to create Bayesian network for each process
    create_network(models, processes, files)
    # Call function to list causes for each error for each process
    get_ordered_cause_list(processes)

if __name__ == "__main__":
    main()

# class Application(tk.Frame):
#     def __init__(self, master=None):
#         super().__init__(master)
#         self.master = master
#         self.pack()
#         self.create_widgets()

#     def create_widgets(self):
#         self.hi_there = tk.Button(self)
#         self.hi_there["text"] = "Hello World\n(click me)"
#         self.hi_there["command"] = self.say_hi
#         self.hi_there.pack(side="top")

#         self.quit = tk.Button(self, text="QUIT", fg="red",
#                               command=self.master.destroy)
#         self.quit.pack(side="bottom")

#     def say_hi(self):
#         print("hi there, everyone!")

# root = tk.Tk()
# app = Application(master=root)
# app.mainloop()