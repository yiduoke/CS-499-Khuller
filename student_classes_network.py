from gurobipy import *
import csv

with open('win22-requests-anon.csv', newline='') as csvfile:
  student_classes_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
  for row in student_classes_reader:
    # print(', '.join(row))
    print(', '.join([row[0],row[1],row[2],row[3],row[4],row[5]]))


m = Model()
credit_cap = 4


# edge_s_name001 = m.addVar(lb=0, ub=credit_cap, obj = 0, vtype=GRB.INTEGER, name="edge_s_name001")


