import os
import subprocess
import pickle
from editor_commands import IDE_COMMAND

class SubmissionCrawler(object):

    def __init__(self, root_dir, name, save_file):
        self.name = name
        self.save_file = save_file
        self.root = root_dir
        self.total_students = 0
        self.current_student = None
        self.students = []

        try:
            with open(save_file, 'rb') as f:
                self.marked = pickle.load(f)
        except FileNotFoundError:
            self.marked = set()

        for root, dirs, _ in os.walk(root_dir):
            if root == self.root:
                self.total_students = len(dirs)
                self.students.extend([d for d in dirs if self.is_student_dir(d)])

    def student_index(self):
        if not self.current_student:
            return -1
        return self.students.index(self.current_student)  + 1

    def is_student_dir(self, dir):
        return dir.startswith('s') and dir[1:].isnumeric()

    def get_total_students(self):
        return self.total_students

    def skip_student(self):
        self.save_current_student()
        self.next_student()

    def next_student(self):
        if self.finished_marking():
            print("WARNING: You've finished marking")
            return

        unmarked = [s for s in self.students if s not in self.marked]
        self.current_student = unmarked[0]

        self.view_code()

    def view_code(self):
        folder = os.path.join(self.root, self.current_student)
        subprocess.Popen([*IDE_COMMAND, folder])

    def save_current_student(self):
        self.marked.add(self.current_student)
        self.save_state(self.save_file)

    def finished_marking(self):
        return len(self.marked) == len(self.students)

    def update_style(self, output):
        if not self.current_student:
            return

        self.save_current_student()

        style = os.path.join(self.root, self.current_student, 
            self.current_student + ".style")
        with open(style, 'w') as outfile:
            outfile.write(output)

    def save_state(self, save_file):
        with open(save_file, 'wb') as f:
            pickle.dump(self.marked, f) 

    def get_current_student(self):
        if not self.current_student:
            return "No current student"
        return self.current_student

    def is_marked(self):
        if not self.current_student:
            return False
        return self.current_student in self.marked
