#Author: Evan Kaseman
#Created: 5/29/2020
#Last Updated: 6/1/2020

#The purpose of this program is to create a failure tree for
#a self-learning expert system. This failure tree will be used
#to populate a Bayesian Network

import numpy as np
import pandas as pd
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD

# Defining the model structure. Define the network by just passing a list of edges.
model = BayesianModel([('inc_adj_of_range', 'default_of_goods'), ('default_of_goods', 'aftertreatment'), ('inc_width_set', 'dim_acc_outside_tol'), ('inc_feed', 'dim_acc_outside_tol'),('dim_acc_outside_tol','aftertreatment'),('dim_acc_outside_tol','selection')])
#model = BayesianModel([('R', 'G'), ('G', 'A'), ('W', 'T'), ('F', 'T'),('T','A'),('T','S')])

# Defining individual CPDs.
cpd_r = TabularCPD(variable='inc_adj_of_range', variable_card=2, values=[[0.6, 0.4]], state_names={'inc_adj_of_range': ['yes', 'no']})
cpd_w = TabularCPD(variable='inc_width_set', variable_card=2, values=[[0.8, 0.2]], state_names={'inc_width_set': ['yes', 'no']})
cpd_f = TabularCPD(variable='inc_feed', variable_card=2, values=[[0.7, 0.3]], state_names={'inc_feed': ['yes', 'no']})

cpd_g = TabularCPD(variable='default_of_goods', variable_card=2, values=[[0.7, 0.8],[0.3, 0.2]], evidence=['inc_adj_of_range'], evidence_card=[2], state_names={'default_of_goods': ['yes', 'no'], 'inc_adj_of_range': ['yes', 'no']})
cpd_t = TabularCPD(variable='dim_acc_outside_tol', variable_card=2, values=[[0.3, 0.6, 0.25, 0.15],[0.7, 0.4, 0.75, 0.85]], evidence=['inc_width_set','inc_feed'], evidence_card=[2,2], state_names={'dim_acc_outside_tol': ['yes', 'no'], 'inc_width_set': ['yes', 'no'], 'inc_feed': ['yes', 'no']})
cpd_a = TabularCPD(variable='aftertreatment', variable_card=2, values=[[0.8, 0.35, 0.12, 0.3],[0.2, 0.65, 0.88, 0.7]], evidence=['default_of_goods','dim_acc_outside_tol'], evidence_card=[2,2], state_names={'aftertreatment': ['yes', 'no'], 'default_of_goods': ['yes', 'no'], 'dim_acc_outside_tol': ['yes', 'no']})
cpd_s = TabularCPD(variable='selection', variable_card=2, values=[[0.8, 0.7],[0.2, 0.3]], evidence=['dim_acc_outside_tol'], evidence_card=[2], state_names={'selection': ['yes', 'no'], 'dim_acc_outside_tol': ['yes', 'no']})

model.add_cpds(cpd_r, cpd_w, cpd_f, cpd_g, cpd_t, cpd_a, cpd_s)
model.check_model()

print(cpd_r)
print(cpd_w)
print(cpd_f)
print(cpd_g)
print(cpd_t)
print(cpd_a)
print(cpd_s)