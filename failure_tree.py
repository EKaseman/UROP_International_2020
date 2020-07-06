#Author: Evan Kaseman
#Created: 5/29/2020
#Last Updated: 7/5/2020

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

#Class to create process objects to store all aspects of process    
class Process:
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.errors = []
    #    self.causes = []
    #    self.effects = []
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

    # Idea is to have this in as part of the process object to create the Bayesian Newtork to allow for 
    # errors to have the same causes or the same effects

    # #add new cause to the errors in the process
    # def add_cause(self, cause):
    #     self.causes.append(cause) 
    # #access cause of errors in the process
    # def get_causes(self):
    #     return self.causes
    # #add new effect of the errors in the process
    # def add_effect(self, effect):
    #     self.effects.append(effect)
    # #access effects of the errors in the process
    # def get_effect(self):
    #     return self.effects

#Class to create error objects to store all aspects of the error
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
    
#Class to create cause objects to store all aspects of the cause
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

#Class to create effect objects to store all aspects of the effect
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

#Class to create detection objects to store all aspects of the detection process
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

#Class to create action objects to store all aspects of action to be taken
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

def populate_data(df, files):
    for i in range(len(df)):
        if (df.at[i,1] != "NA"):
            curr_error = Error(df.at[i,1])
            curr_error.add_effect(df.at[i,2],df.at[i,3])
            curr_error.add_cause(df.at[i,5],df.at[i,6])
            curr_error.add_detection_method(df.at[i,8],df.at[i,9])
            curr_error.add_action(df.at[i,11])
            if ((i+1 == len(df)) or (df.at[i+1,1] != "NA")):
                processes[files].add_error(curr_error)
        else:
            curr_error.add_effect(df.at[i,2],df.at[i,3])
            curr_error.add_cause(df.at[i,5],df.at[i,6])
            curr_error.add_detection_method(df.at[i,8],df.at[i,9])
            curr_error.add_action(df.at[i,11])
            if ((i+1 == len(df)) or (df.at[i+1,1] != "NA")):
                processes[files].add_error(curr_error)

#list of processes in the weaving process
process_names = ['Finished Goods','Fixed Goods','Yarn','Washed Goods','Water-Repellent Goods','Warp Beam','Raw Goods']

#creating a list of Process objects 
processes = []
for x in range(len(process_names)):
    processes.append(Process(process_names[x]))

#### importing data from FMEA excel files
root= tk.Tk()

canvas1 = tk.Canvas(root, width = 300, height = 300, bg = 'grey')
canvas1.pack()

df = None # variable must exist in global namespace first
files = 0

def getExcel ():
    global df
    global files

    import_file_path = filedialog.askopenfilename()
    df = pd.read_excel(import_file_path, header=None, index_col=None, usecols="B:D,F,G,I,J,L", skiprows=range(10))
    df = df.replace(r'^\s+$', np.nan, regex=True).dropna(how='all')
    df = df.replace(np.nan, "NA", regex=True)
    populate_data(df,files)
    print (df)
    files = files + 1
    #df.to_excel("FMEA_Data.xlsx")
    
    
browseButton_Excel = tk.Button(text='Import Excel File', command=getExcel, bg='green', fg='white', font=('helvetica', 12, 'bold'))
canvas1.create_window(150, 150, window=browseButton_Excel)

root.mainloop()

# initialize the error cpd using the Maximum Entropy theory because the conditional probabilities are unknown
def get_initial_error_cpd(number_of_causes):
    values = []
    # using Maximum Entropy theory, each failure cause has an equal 1/s probability, where s is the total number of failure causes
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

# Create a list of Bayesian Models for each of the processes
models = []

# Create a Bayesian Network for each process and add it to the list of Bayesian Networks.  Then, plot the BN in an png file 
for p in range(files):
    temp_model = BayesianModel()
    for e in range(len(processes[p].get_errors())):
        temp_error = processes[p].get_error(e)
        for c in range(len(temp_error.get_causes())):
            temp_cause = temp_error.get_cause(c)
            q = temp_cause.get_occ_prob()/temp_error.get_total_cause_prob()
            temp_model.add_nodes_from([temp_cause,temp_error])
            temp_model.add_edge(temp_cause,temp_error)
            temp_cause_cpd = TabularCPD(variable = temp_cause, variable_card = 2, values = [[q,1-q]])
            temp_model.add_cpds(temp_cause_cpd)
        temp_error_cpd = TabularCPD(variable = temp_error, variable_card=2, 
                                    values = get_initial_error_cpd(len(temp_error.get_causes())), 
                                    evidence = temp_error.get_causes(), #included 'Unknown Cause' here to account for other causes not in system
                                    evidence_card = [2]*(len(temp_error.get_causes())))
        temp_model.add_cpds(temp_error_cpd)
        for f in range(len(temp_error.get_effects())):
            temp_effect = temp_error.get_effect(f)
            temp_model.add_nodes_from([temp_error,temp_effect])
            temp_model.add_edge(temp_error,temp_effect)
            ####### Not adding CPDs here for now as causes are main focus
    models.append(temp_model)
    #plotting Failure Tree
    dot = to_pydot(models[p])
    with open('failure_tree_graph_%s.png' % processes[p], 'wb') as f:
        f.write(dot.create_png())
    #print(temp_model.check_model())
    #Sample output of CPDs for causes and errors
    for e in range(len(processes[p].get_errors())):
        for c in range(len(processes[p].get_error(e).get_causes())):
            print(temp_model.get_cpds(processes[p].get_error(e).get_cause(c)))
        print(temp_model.get_cpds(processes[p].get_error(e)))

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