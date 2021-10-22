from gurobipy import *
from functools import reduce
import csv
import re


model = Model()
obj = LinExpr()

credit_cap = 4

student_to_courses_dict = {}
course_to_students_dict = {}
course_to_time_dict = {}

def ParseCamelCase(string):
  return re.sub('([A-Z][a-z]*)', r' \1', re.sub('([A-Z]+)', r' \1', string)).split()

def parse_course_time(course_name):
  weekday_to_number_dict = {"M": 0, "Tu": 1, "W": 2, "Th": 3, "F": 4} # don't have Saturday and Sunday
  words_list = course_name.split(" ")
  beginning_time_number = re.findall("[0-9]+:[0-9]+", course_name)
  beginning_and_end_times = re.findall("[0-9]+:[0-9]+ [A|P]M", course_name)
  
  for i in range(2):
    time = beginning_and_end_times[i]
    if time[-2:] == "AM" or (time[-2:] == "PM" and time[:2] == "12"):
      beginning_and_end_times[i] = int(time[:2]) * 60 + int(time[3:5])
    else:
      beginning_and_end_times[i] = 720 + int(time[:2]) * 60 + int(time[3:5])

  time_index =  words_list.index(beginning_time_number[0])
  days_of_week = ParseCamelCase(words_list[time_index-1])
  time_ranges = [range(weekday_to_number_dict[x]*1440 + beginning_and_end_times[0], weekday_to_number_dict[x]*1440 + + beginning_and_end_times[1]) for x in days_of_week]
  # union = set(time_ranges[0]).union(time_ranges[1])
  union = reduce((lambda x, y: x.union(y)), time_ranges, set([]))
  return union


with open('win22-requests-anon.csv', newline='') as csvfile:
  student_courses_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
  for row in student_courses_reader:
    if (row[0] == "Name"): # skip header row
      continue

    for i in range(1,6):
      student = row[0]
      course = row[i]
      if (course == "0"): # no class chosen
        continue

      x = model.addVar(vtype=GRB.BINARY, name=student + "_" + course)
      obj.addTerms(5-i, x) # the higher they rank the course, the higher the coefficient

      if student in student_to_courses_dict:
        student_to_courses_dict[student].append(course)
      else:
        student_to_courses_dict[student] = [course]
      
      if course in course_to_students_dict:
        course_to_students_dict[course].append(student)
      else:
        course_to_students_dict[course] = [student]
      
      if course in course_to_time_dict:
        course_to_time_dict[course].append(parse_course_time(course))
      else:
        print(course)
        course_to_time_dict[course] = [parse_course_time(course)]

      

model.setObjective(obj, GRB.MAXIMIZE)



print(parse_course_time("CS 336 Algorithms TuTh 09:30 AM-10:50 AM"))


