#Author: Evan Kaseman
#Created: 5/29/2020
#Last Updated: 6/16/2020

#The purpose of this program is to create a failure tree for
#a self-learning expert system. This failure tree will be used
#to populate a Bayesian Network

import numpy as np
import pandas as pd
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from networkx.drawing.nx_pydot import to_pydot

errors = {'R': 'inc_adj_of_range','G': 'default_of_goods','W': 'inc_width_set','T': 'dim_acc_outside_tol','F': 'inc_feed','A': 'aftertreatment','S': 'selection',}

# Defining the model structure. Define the network by just passing a list of edges.
#model = BayesianModel([('inc_adj_of_range', 'default_of_goods'), ('default_of_goods', 'aftertreatment'), (errors['W'], 'dim_acc_outside_tol'), ('inc_feed', 'dim_acc_outside_tol'),('dim_acc_outside_tol','aftertreatment'),('dim_acc_outside_tol','selection')])
model = BayesianModel([(errors['R'], errors['G']), (errors['G'], errors['A']), (errors['W'], errors['T']), (errors['F'], errors['T']),(errors['T'],errors['A']),(errors['T'],errors['S'])])

# Defining individual CPDs.
cpd_r = TabularCPD(variable=errors['R'], variable_card=2, values=[[0.6, 0.4]], state_names={errors['R']: ['yes', 'no']})
cpd_w = TabularCPD(variable=errors['W'], variable_card=2, values=[[0.8, 0.2]], state_names={errors['W']: ['yes', 'no']})
cpd_f = TabularCPD(variable=errors['F'], variable_card=2, values=[[0.7, 0.3]], state_names={errors['F']: ['yes', 'no']})

cpd_g = TabularCPD(variable=errors['G'], variable_card=2, values=[[0.7, 0.8],[0.3, 0.2]], evidence=[errors['R']], evidence_card=[2], state_names={errors['G']: ['yes', 'no'], errors['R']: ['yes', 'no']})
cpd_t = TabularCPD(variable=errors['T'], variable_card=2, values=[[0.3, 0.6, 0.25, 0.15],[0.7, 0.4, 0.75, 0.85]], evidence=['inc_width_set',errors['F']], evidence_card=[2,2], state_names={errors['T']: ['yes', 'no'], 'inc_width_set': ['yes', 'no'], errors['F']: ['yes', 'no']})
cpd_a = TabularCPD(variable=errors['A'], variable_card=2, values=[[0.8, 0.35, 0.12, 0.3],[0.2, 0.65, 0.88, 0.7]], evidence=[errors['G'],errors['T']], evidence_card=[2,2], state_names={errors['A']: ['yes', 'no'], errors['G']: ['yes', 'no'], errors['T']: ['yes', 'no']})
cpd_s = TabularCPD(variable=errors['S'], variable_card=2, values=[[0.8, 0.7],[0.2, 0.3]], evidence=[errors['T']], evidence_card=[2], state_names={errors['S']: ['yes', 'no'], errors['T']: ['yes', 'no']})

#adding CPDs to the Bayesian Model
model.add_cpds(cpd_r, cpd_w, cpd_f, cpd_g, cpd_t, cpd_a, cpd_s)

#check to determine if everything in the model is correct
model.check_model()

#printing CPD's in a tabular format
print(cpd_r)
print(cpd_w)
print(cpd_f)
print(cpd_g)
print(cpd_t)
print(cpd_a)
print(cpd_s)

#plotting Failure Tree
dot = to_pydot(model)
with open('hello.png', 'wb') as f:
    f.write(dot.create_png())

print(model.local_independencies('default_of_goods'))