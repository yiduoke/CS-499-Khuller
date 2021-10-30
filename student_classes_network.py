from gurobipy import *
from functools import reduce
import csv
import re


model = Model()
obj = LinExpr()

credit_cap = 4

student_to_courses_dict = {}
course_to_students_dict = {}
course_capacities = {}

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
  model.addConstr(sum(student_vars[:y]) >= x)


with open('win22-requests-anon.csv', newline='') as csvfile:
  student_courses_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
  for row in student_courses_reader:
    if (row[0] == "Name"): # skip header row
      continue

    student = row[0]
    student_to_courses_dict[student] = []
    for i in range(1,6):
      course = row[i]
      if (course == "0"): # no class chosen
        continue

      x = model.addVar(vtype=GRB.BINARY, name=student + "_" + course)
      obj.addTerms(5-i, x) # the higher they rank the course, the higher the coefficient

      student_to_courses_dict[student].append(course)
      
      if course in course_to_students_dict:
        course_to_students_dict[course].append(student)
      else:
        course_to_students_dict[course] = [student]
        course_capacities[course] = 35 # course capacities not given in the CSV, thus I'm using a default value
    
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
    course_vars = [model.getVarByName(student + "_" + course) for student in this_course_potential_students]
    model.addConstr(sum(course_vars) <= course_capacities[course]) # course enrollment capacity constraint
    

model.setObjective(obj, GRB.MAXIMIZE)
model.optimize()


f = open("results.txt", "w")
total_enrollment = 0
got_over_2_of_top_4 = 0
for student in student_to_courses_dict:
  courses = student_to_courses_dict[student]
  vars = [model.getVarByName(student + "_" + course) for course in courses]
  [f.write(var.varName + ": " + str(var.x) + "\n") for var in vars]

  student_got_courses = reduce((lambda current_sum, b: current_sum + b.x), vars[:4], 0)
  if (student_got_courses >= min(2,len(student_to_courses_dict[student]))):
    got_over_2_of_top_4 += 1
  total_enrollment += student_got_courses
  f.write("student " + student + " got " + str(student_got_courses) + " courses from top 4\n\n")
  
f.write("total enrollment: " + str(total_enrollment) + "\n")
f.write("number of students getting at least 2 of top 4 courses: " + str(got_over_2_of_top_4))
f.close()





