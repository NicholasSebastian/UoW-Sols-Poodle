from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
import time

# BEHOLD! SPAGHETTI CODE GALORE!

# self defined function to find the time in the string and 
# convert it from Australian time to Singaporean time.
def breakDown(word):
    new_word = []
    broken_array = list(str(word))
    condition = True

    for char in broken_array:
        if char.isdigit() and condition:
            if int(char) > 3:
                char = int(char) - 3
            else:
                char = int(char) + 9
            condition = False
        new_word.append(str(char))

    return("".join(new_word))

# self defined function to remove bullshit from descriptions.
def removeJargon(description, amount_of_bullshit):
    new_words = []
    
    for index, word in enumerate(description.split()):
        if index == (len(description.split()) - 2):
            word = breakDown(word)
        
        if index > amount_of_bullshit:
            new_words.append(word + " ")
    
    return("".join(new_words))

# where the actual program begins.
start_time = time.time()

# authentication.
print("[Poodle] Enter your username: ", end = '')
my_username = input()
print("[Poodle] Enter your password: ", end = '')
my_password = input()

# specifies Safari web browser to be used as the webdriver.
print("[Poodle] Opening safari web browser...")
driver = webdriver.Safari()

# opens the following link.
print("[Poodle] Opening moodle...")
print("[Poodle] This may take a while depending on your connection...")
url = "https://moodle.uowplatform.edu.au/login/index.php"
driver.get(url)

# give time for the initial loading of the website to prevent errors.
WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(("id","login")))

# finds the username and password forms.
username = driver.find_element_by_id("username")
password = driver.find_element_by_id("password")
login_button = driver.find_element_by_id("loginbtn")

# fills in the login form and submits.
print("[Poodle] Entering credentials...")
print("[Poodle] Program tends to get stuck here...")
username.send_keys(my_username)
password.send_keys(my_password)
login_button.send_keys(Keys.ENTER)
print("[Poodle] Logged in successfully!")

# passes the html page to the beautiful soup parser.
WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(("id","courses")))
print("[Poodle] Reading the page...")
moodle_html = BeautifulSoup(driver.page_source, "html.parser")

# finds all the courses in the html page.
course_list = moodle_html.findAll("div", {"class":"row courseovbox lead"})

# initializes arrays to store the course names and links.
course_names = []
course_links = []

# stores all the course names and links in the array.
print("[Poodle] Retrieving courses...")
for course in course_list:
    entry = course.find("div", {"class":"col-sm-8 span8"}).strong.a
    entry_name = entry.text.strip()

    if not "StartSmart" in entry_name:
        course_names.append(entry_name)
        course_links.append(entry['href'])

# initializes arrays to store the arrays of quiz/assignment information of each course.
quiz_names_array = []
quiz_links_array = []
quiz_deadline_array = []
quiz_status_array = []
assignment_names_array = []
assignment_links_array = []
assignment_deadline_array = []
assignment_status_array = []

# runs the following processes for every course:
for index, link in enumerate(course_links):
    
    print("[Poodle] Loading: " + str(index + 1) + " out of " + str(len(course_links)) + " courses.")

    # opens the course link.
    driver.get(link)

    # passes the html page to the beautiful soup parser.
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(("id","section-0")))
    course_html = BeautifulSoup(driver.page_source, "html.parser")

    # finds all the quizzes and assignments in the html page.
    quiz_list = course_html.findAll("li",{"class":"activity quiz modtype_quiz"})
    assignment_list = course_html.findAll("li",{"class":"activity assign modtype_assign"})

    # initializes arrays to store the quiz/assignment names and links.
    quiz_names = []
    quiz_links = []
    quiz_deadline = []
    quiz_status = []
    assignment_names = []
    assignment_links = []
    assignment_deadline = []
    assignment_status = []

    # stores all the quiz names and links in the array.
    for quiz in quiz_list:
        quiz_names.append(quiz.find("span",{"class":"instancename"}).text.strip())
        quiz_links.append(quiz.find("a")['href'])
    
    # opens each quiz link in the array.
    for quiz_link in quiz_links:
        driver.get(quiz_link)
        
        # passes the html page to the beautiful soup parser.
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(("id","page-content")))
        quiz_html = BeautifulSoup(driver.page_source, "html.parser")

        # finds the main information on the page.
        description = quiz_html.find("div",{"class":"box py-3 quizinfo"}).contents[2].text.strip()
        description2 = quiz_html.find("div",{"class":"box py-3 quizinfo"}).contents[4].text.strip()

        # reformats the information before storing in the array.
        if "opened" in description:
            quiz_status.append("NOW OPEN!!!")
            quiz_deadline.append(removeJargon(description, 3) + "- " \
            + removeJargon(description2, 4))

        elif "not be available until" in description:
            quiz_status.append("Not Available Yet")
            quiz_deadline.append(removeJargon(description, 6))

        elif "closed" in description:
            quiz_status.append("Quiz Closed")
            quiz_deadline.append(removeJargon(description, 3))

        else:
            quiz_status.append("Quiz Closed")
            quiz_deadline.append("Undefined")

    # stores all the assignment names and links in the array.
    for assignment in assignment_list:
        assignment_names.append(assignment.find("span",{"class":"instancename"}).text.strip())
        assignment_links.append(assignment.find("a")['href'])

    # opens each assignment link in the array.
    for assignment_link in assignment_links:
        driver.get(assignment_link)
        
        # passes the html page to the beautiful soup parser.
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(("id","page-content")))
        assignment_html = BeautifulSoup(driver.page_source, "html.parser")

        description = assignment_html.findAll("td",{"class":"cell c1 lastcol"})
        remaining = assignment_html.find("td",{"class":"earlysubmission cell c1 lastcol"})
        overdue = assignment_html.find("td",{"class":"overdue cell c1 lastcol"})

        # finds the assignment deadline on the page and it in the array.
        if remaining:
            if "submitted" in remaining.text.strip():
                assignment_status.append("Submitted")
                assignment_deadline.append(description[0].text.strip())
        elif overdue:
            if "overdue" in overdue.text.strip():
                assignment_status.append("Not Submitted")
                assignment_deadline.append(description[1].text.strip())
        elif "No attempt" in description[0].text.strip():
            assignment_status.append("NOW OPEN!!!")
            assignment_deadline.append(description[1].text.strip())
        else:
            assignment_status.append("Undefined")
            assignment_deadline.append("Undefined")

    # appends the arrays to their respective parent arrays.
    quiz_names_array.append(quiz_names)
    quiz_links_array.append(quiz_links)
    quiz_deadline_array.append(quiz_deadline)
    quiz_status_array.append(quiz_status)
    assignment_names_array.append(assignment_names)
    assignment_links_array.append(assignment_links)
    assignment_deadline_array.append(assignment_deadline)
    assignment_status_array.append(assignment_status)

# closes the webbrowser.
print("[Poodle] Information retrieval complete.")
driver.close()

# open a csv file and prepare to write on the file.
print("[Poodle] Exporting to CSV file...")
filename = "Moodle_Subjects.csv"
f = open(filename, "w")

# write the respective headers on the csv file.
headers = "Course Name, Tasks, Status, Deadline, Links\n"
f.write(headers)

# loop through all the courses in the array.
for i in range(len(course_names)):

    # write the course name to the csv file.
    f.write(course_names[i])

    # if there are any quizzes or assignments, write them onto the csv file.
    if quiz_names_array[i] or assignment_names_array[i]:
        for j in range(len(quiz_names_array[i])):
            f.write("," \
                + quiz_names_array[i][j].replace(",", " |") + "," \
                + quiz_status_array[i][j] + "," \
                + quiz_deadline_array[i][j].replace(",", " |") + "," \
                + quiz_links_array[i][j] + "\n")

        for j in range(len(assignment_names_array[i])):
            f.write("," \
                + assignment_names_array[i][j].replace(",", " |") + "," \
                + assignment_status_array[i][j] + "," \
                + assignment_deadline_array[i][j].replace(",", " |") + "," \
                + assignment_links_array[i][j] + "\n")
            
            if j == (len(assignment_names_array[i]) - 1):
                f.write("\n")
    
    # if there aren't any quizzes or assignments, skip a line.
    else:
        f.write(",None\n\n")

# close the csv file writer.
f.close()

# print time taken in console.
now_time = time.time()
print("[Poodle] Processes completed successfully!")
print("[Poodle] It took " + str(round(now_time - start_time, 1)) + " seconds to complete.")