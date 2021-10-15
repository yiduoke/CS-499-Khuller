from gurobipy import *

students_class_preferences = {
  "name001": {1: "CS 348 AI MWF 11:00 AM-11:50 AM", 2: "CS 343 Operating Systems TuTh 09:30 AM-10:50 AM",	3: "CS 321 Programming languages TuTh 03:30 PM-04:50 PM"},
  "name002": {1: "CS 371 Knowledge Representation and Reasoning TuTh 02:00 PM-03:20 PM",	2: "CS 496 Visualization for Scientific Communication W 03:00 PM-05:50 PM",	3: "CS 396 Modeling Relationships with Causal Inference MW 05:00 PM-06:20 PM",	4: "CS 348 AI MWF 11:00 AM-11:50 AM",	5: "CS 349 ML MW 12:30 PM-01:50 PM"}, 
  "name003": {1: "CS 396 Generative Methods MW 08:00 AM-09:20 AM",	2: "CS 396 Intro to Web Development MWF 08:00 AM-08:50 AM",	3: "CS 396 Advanced Algorithm Design through the Lens of Competitive Programming F 02:00 PM-04:50 PM",	4: "CS 397/497 Data Privacy TuTh 03:30 PM-04:50 PM",	5: "CS 496 Distributed Systems in Challenging Environments MW 03:30 PM-04:50 PM"}, 
  "name004": {1: "CS 396 Communicating Computer Science MW 05:00 PM-06:20 PM",	2: "CS 396 Intro to Web Development MWF 08:00 AM-08:50 AM"}	
  }

m = Model()
credit_cap = 4
# first layer (source to students)
edge_s_name001 = m.addVar(lb=0, ub=credit_cap, obj = 0, vtype=GRB.INTEGER, name="edge_s_name001")
edge_s_name002 = m.addVar(lb=0, ub=credit_cap, obj = 0, vtype=GRB.INTEGER, name="edge_s_name002")
edge_s_name003 = m.addVar(lb=0, ub=credit_cap, obj = 0, vtype=GRB.INTEGER, name="edge_s_name003")
edge_s_name004 = m.addVar(lb=0, ub=credit_cap, obj = 0, vtype=GRB.INTEGER, name="edge_s_name004")

# second layer (students to wanted classes)
name001_class1 = m.addVar(lb=0, ub=1, obj = 1, vtype=GRB.BINARY, name="name001_class1")
name001_class2 = m.addVar(lb=0, ub=1, obj = 2, vtype=GRB.BINARY, name="name001_class2")
name001_class3 = m.addVar(lb=0, ub=1, obj = 3, vtype=GRB.BINARY, name="name001_class3")

name002_class1 = m.addVar(lb=0, ub=1, obj = 1, vtype=GRB.BINARY, name="name002_class1")
name002_class2 = m.addVar(lb=0, ub=1, obj = 2, vtype=GRB.BINARY, name="name002_class2")
name002_class3 = m.addVar(lb=0, ub=1, obj = 3, vtype=GRB.BINARY, name="name002_class3")
name002_class4 = m.addVar(lb=0, ub=1, obj = 4, vtype=GRB.BINARY, name="name002_class4")
name002_class5 = m.addVar(lb=0, ub=1, obj = 3, vtype=GRB.BINARY, name="name002_class5")

name003_class1 = m.addVar(lb=0, ub=1, obj = 1, vtype=GRB.BINARY, name="name003_class1")
name003_class2 = m.addVar(lb=0, ub=1, obj = 2, vtype=GRB.BINARY, name="name003_class2")
name003_class3 = m.addVar(lb=0, ub=1, obj = 3, vtype=GRB.BINARY, name="name003_class3")
name003_class4 = m.addVar(lb=0, ub=1, obj = 4, vtype=GRB.BINARY, name="name003_class4")
name003_class5 = m.addVar(lb=0, ub=1, obj = 3, vtype=GRB.BINARY, name="name003_class5")

name004_class1 = m.addVar(lb=0, ub=1, obj = 1, vtype=GRB.BINARY, name="name004_class1")
name004_class2 = m.addVar(lb=0, ub=1, obj = 2, vtype=GRB.BINARY, name="name004_class2")

# third layer (wanted classes to classes)
name001_class1_CS348_AI = m.addVar(lb=0, ub=0, obj = 1, vtype=GRB.BINARY, name="name001_class1_CS348_AI")
name001_class1_CS348_AI = m.addVar(lb=0, ub=0, obj = 1, vtype=GRB.BINARY, name="name001_class1_CS348_AI")