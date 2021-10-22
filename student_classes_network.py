from gurobipy import *
import csv
import re


m = Model()
credit_cap = 4

def ParseCamelCase(string):
  return re.sub('([A-Z][a-z]*)', r' \1', re.sub('([A-Z]+)', r' \1', string)).split()

with open('win22-requests-anon.csv', newline='') as csvfile:
  student_classes_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
  for row in student_classes_reader:
    print(', '.join([row[0],row[1],row[2],row[3],row[4],row[5]]))

def parse_class_time(class_name):
  words_list = class_name.split(" ")
  time = re.findall("[0-9]+:[0-9]+", class_name)
  print(time)
  time_index =  words_list.index(time[0])
  return words_list[time_index-1]


print(parse_class_time("CS 348 AI MWF 11:00 AM-11:50 AM"))
print(ParseCamelCase("MWF"))
print(ParseCamelCase("MW"))
print(ParseCamelCase("M"))
print(ParseCamelCase("TuTh"))





# edge_s_name001 = m.addVar(lb=0, ub=credit_cap, obj = 0, vtype=GRB.INTEGER, name="edge_s_name001")


