from gurobipy import *
import csv
import re


model = Model()
obj = LinExpr()

credit_cap = 4

student_to_courses_dict = {}
course_to_students_dict = {}
course_to_time_dict = {}


with open('win22-requests-anon.csv', newline='') as csvfile:
  student_courses_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
  for row in student_courses_reader:
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

      

model.setObjective(obj, GRB.MAXIMIZE)


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

  print(beginning_and_end_times)
  time_index =  words_list.index(beginning_time_number[0])
  print("meow\n\n" + words_list[time_index-1])
  days_of_week = ParseCamelCase(words_list[time_index-1])
  time_ranges = [range(weekday_to_number_dict[x]*1440 + beginning_and_end_times[0], weekday_to_number_dict[x]*1440 + + beginning_and_end_times[1]) for x in days_of_week]
  return time_ranges


print(parse_course_time("CS 348 AI MWF 11:00 AM-11:50 AM"))
print(ParseCamelCase("MWF"))
print(ParseCamelCase("MW"))
print(ParseCamelCase("M"))
print(ParseCamelCase("TuTh"))


