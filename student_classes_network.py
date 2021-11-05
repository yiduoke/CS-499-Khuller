from gurobipy import *
from functools import reduce
import csv
import re
import json


model = Model()
obj = LinExpr()
obj2 = LinExpr()
fairness_constraint = 0

credit_cap = 4

student_to_courses_dict = {}
course_to_students_dict = {}
course_to_MS_students_dict = {}
course_capacities = {}
course_MS_capacities = {}

course_stats = {}

def ParseCamelCase(string):
  return re.sub('([A-Z][a-z]*)', r' \1', re.sub('([A-Z]+)', r' \1', string)).split()

def parse_course_time(course_name):
  weekday_to_number_dict = {"M": 0, "Tu": 1, "W": 2, "Th": 3, "F": 4} # don't have Saturday and Sunday
  words_list = course_name.split(" ")
  beginning_time_number = re.findall("[0-9]+:[0-9]+", course_name)
  beginning_and_end_times = re.findall("[0-9]+:[0-9]+ [A|P]M", course_name)
  
  # converting Weekday hh:mm XM-hh:mm XM to integers
  for i in range(2):
    time = beginning_and_end_times[i]
    if time[-2:] == "AM" or (time[-2:] == "PM" and time[:2] == "12"):
      beginning_and_end_times[i] = int(time[:2]) * 60 + int(time[3:5])
    else:
      beginning_and_end_times[i] = 720 + int(time[:2]) * 60 + int(time[3:5])

  time_index =  words_list.index(beginning_time_number[0])
  days_of_week = ParseCamelCase(words_list[time_index-1])
  time_ranges = [range(weekday_to_number_dict[x]*1440 + beginning_and_end_times[0], weekday_to_number_dict[x]*1440 + + beginning_and_end_times[1]) for x in days_of_week]
  union = reduce((lambda x, y: x.union(y)), time_ranges, set())
  return union

def must_have_x_of_top_y_courses(x, y, student_vars):
  model.addConstr(sum(student_vars[:y]) >= min(len(student_vars), x))

with open('win22-course-data.csv', newline='') as csvfile:
  y = 4 # top y of student preferences
  courses_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
  for row in courses_reader:
    if (row[0] == "SIS Number"): # skip header row
      continue
    course = row[5]
    course_capacities[course] = int(row[1])
    course_MS_capacities[course] = int(row[2][:-1])/100 * course_capacities[course]
    

with open('win22-requests-anon.csv', newline='') as csvfile:
  student_courses_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
  for row in student_courses_reader:
    if (row[0] == "Name"): # skip header row
      continue

    student = row[0]
    student_to_courses_dict[student] = []
    for i in range(1,6):
      course = row[i]
      if (len(course) < 2): # no class chosen
        continue

      x = model.addVar(vtype=GRB.BINARY, name=student + "_" + course)
      obj.addTerms(5-i, x) # the higher they rank the course, the higher the coefficient
      if (i <= y):
        obj2.addTerms(1, x)

      student_to_courses_dict[student].append(course)
      
      if (row[8][:2] == "MS"):
        if course in course_to_MS_students_dict:
          course_to_MS_students_dict[course].append(student)
        else:
          course_to_MS_students_dict[course] = [student]

      if course in course_to_students_dict:
          course_to_students_dict[course].append(student)
          if (i in course_stats[course]):
            course_stats[course][i] += 1
          else:
            course_stats[course][i] = 1
      else:
        course_to_students_dict[course] = [student]
        course_stats[course] = {}
        course_stats[course][i] = 1
        
    
    model.update()
    this_students_courses = student_to_courses_dict[student]
    this_student_vars = [model.getVarByName(student + "_" + course) for course in this_students_courses]
    model.addConstr(sum(this_student_vars) <= credit_cap) # student credit cap

    # must_have_x_of_top_y_courses(min(2, len(this_student_vars)), 4, this_student_vars)
    for course in this_students_courses:
      conflicts = set(filter(lambda x: len(parse_course_time(x).intersection(parse_course_time(course))) != 0, this_students_courses))
      conflict_vars = [model.getVarByName(student + "_" + course) for course in conflicts] if len(conflicts) > 1 else []
      model.addConstr(sum(conflict_vars) <= 1) # time conflict constraint

  for course in course_to_students_dict:
    this_course_potential_students = course_to_students_dict[course]
    this_course_potential_MS_students = course_to_MS_students_dict[course]
    course_vars = [model.getVarByName(student + "_" + course) for student in this_course_potential_students]
    course_MS_vars = [model.getVarByName(student + "_" + course) for student in this_course_potential_MS_students]
    model.addConstr(sum(course_vars) <= course_capacities[course]) # course enrollment capacity constraint
    model.addConstr(sum(course_MS_vars) <= course_MS_capacities[course]) # course MS enrollment capacity constraint
    

model.setObjectiveN(obj, 0, 1)
# model.setObjectiveN(obj2, 1, 0)
model.ModelSense = GRB.MAXIMIZE
model.optimize()


f = open("results.txt", "w")
total_enrollment = 0
got_2_of_top_4 = 0
assignments = {}
for student in student_to_courses_dict:
  assignments[student] = {}
  courses = student_to_courses_dict[student]
  vars = [model.getVarByName(student + "_" + course) for course in courses]
  for course in courses:
    assignments[student][course] = int(model.getVarByName(student + "_" + course).x)
  [f.write(var.varName + ": " + str(var.x) + "\n") for var in vars]

  student_got_courses = reduce((lambda current_sum, b: current_sum + b.x), vars[:4], 0)
  if (student_got_courses >= min(2,len(student_to_courses_dict[student]))):
    got_2_of_top_4 += 1
  total_enrollment += student_got_courses
  f.write("student " + student + " got " + str(student_got_courses) + " courses from top 4\n\n")
  
f.write("total enrollment: " + str(total_enrollment) + "\n")
f.write("number of students getting at least 2 of top 4 courses: " + str(got_2_of_top_4) + "\n")
f.write("total number of student: " + str(len(student_to_courses_dict)))
f.close()

f = open("course_stats.json", "w")
json.dump(course_stats, f)
f.close()

f = open("assignments.json", "w")
json.dump(assignments, f)
f.close()

