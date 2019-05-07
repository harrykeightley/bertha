import models
import tkinter as tk
import argparse
from crawler import SubmissionCrawler

CRITERIA = "a1_criteria.json"
STATE_FILE = "a1_state.pickle"

BG_COLOUR = "White"
RESET_BTN_COLOUR = "Orange"
MINUS_BTN_COLOUR = "Red"

LIVES_FONT = ("Helevetica", 14, "bold")
SECTION_FONT = ("Helevetica", 16, "bold")
CRITERIA_FONT = ("Helvetica", 14)
CRITERIA_INDENT = ' ' * 8

BTN_WIDTH = 5

class MarkingToolApp(tk.Frame):

    def __init__(self, master, student_dir, state, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.student_frame = StudentFrame(self, student_dir, state, self.build_style, self.reset)
        self.student_frame.pack(ipadx=10, ipady=10, padx=10, pady=10, side=tk.TOP)

        self.marking_frame = MarkingFrame(self, bd=1, relief='groove')
        self.big_reset = tk.Button(self, text='RESET ALL',
            command=self.reset)

        self.big_reset.pack(side=tk.TOP)
        self.marking_frame.pack(ipadx=10, ipady=10, padx=10, pady=10, side=tk.TOP)

        self.comment_header = tk.Label(self, text="Comments", font=SECTION_FONT)
        self.comment_header.pack(side=tk.TOP)

        self.comments = tk.Text(self, height=10, bd=1, relief='groove')
        self.comments.pack(fill=tk.X, expand=True, padx=10, pady=10, side=tk.TOP)

    def build_style(self):
        comments = self.comments.get("0.0", tk.END)
        n, c, s, g = self.marking_frame.get_section_marks()

        return (f"Naming: {n}/5\n"
                f"Commenting: {c}/6\n"
                f"Structure and layout: {s}/10\n"
                f"Good OO: {g}/4\n"
                f"General Comments: {comments}")
    
    def reset(self):
        self.marking_frame.reset()
        self.comments.delete(1.0, tk.END)


class StudentFrame(tk.Frame):

    def __init__(self, parent, student_dir, state, generate_style, reset_marks, **kwargs):
        self.parent = parent
        self.crawler = crawler = SubmissionCrawler(student_dir, "2002 A1 Marking", state)
        super().__init__(parent, **kwargs)

        self.number = tk.Label(self, 
            text=f"{crawler.student_index()}/{crawler.total_students}")
        self.number.grid(row=0, column=0)

        self.marked = tk.Label(self, text=f"Marked: {crawler.is_marked()}")
        self.marked.grid(row=1, column=0)

        self.student_no = tk.Label(self, text=crawler.get_current_student(),
            font=SECTION_FONT)
        self.student_no.grid(row=0, column=1)

        self.title = tk.Label(self, text=crawler.name)
        self.title.grid(row=1, column=1)

        # View code button
        self.view_code = tk.Button(self, text='VIEW', command=crawler.view_code)
        self.view_code.grid(row=0, column=2, rowspan=2,
               sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)

        # Update button
        update_functions = [
            lambda: crawler.update_style(generate_style()),
            self.refresh
        ]
        self.update_student = tk.Button(self, text='SAVE', 
            command=lambda: self.call_funcs(update_functions))
        self.update_student.grid(row=0, column=3, rowspan=2,
               sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)

        # Next button
        next_functions = [
            crawler.next_student,
            self.refresh,
            reset_marks,
        ]
        self.next = tk.Button(self, text='NEXT', 
            command=lambda: self.call_funcs(next_functions))
        self.next.grid(row=0, column=4, rowspan=2,
               sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)

        # Skip button
        skip_functions = [
            crawler.skip_student,
            self.refresh,
            reset_marks
        ]
        self.next = tk.Button(self, text='SKIP', 
            command=lambda: self.call_funcs(skip_functions))
        self.next.grid(row=0, column=5, rowspan=2,
               sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)

    def call_funcs(self, funcs):
        # I feel like this would already exist.
        for func in funcs:
            func()

    def refresh(self):
        self.student_no.config(text=self.crawler.get_current_student())
        self.number.config(text=f"{self.crawler.student_index()}"
                                f"/{self.crawler.total_students}")
        self.marked.config(text=f"Marked: {self.crawler.is_marked()}")   
        

class MarkingFrame(tk.Frame):

    def __init__(self, parent, **kwargs):
        self.parent = parent
        super().__init__(parent, **kwargs)

        self.sections = []

        self.section_models = models.build_ruberic_from_json(CRITERIA)
        for section_model in self.section_models:
            self.sections.append(MarkingSection(self, section_model))

    def reset(self):
        for section in self.sections:
            section.reset()

    def get_section_marks(self):
        return [section.get_marks() for section in self.sections]

    
class MarkingSection(object):

    def __init__(self, parent, section):
        self.parent = parent
        self.section = section

        self.text = tk.Label(parent, text=section.get_name(), font=SECTION_FONT)
        self.text.grid(columnspan=4, sticky=tk.W)

        self.table_index = self.text.grid_info()['row']
        self.table_index = int(self.table_index)

        self.score = tk.Label(parent, text=section.get_score(), font=SECTION_FONT)
        self.score.grid(row=self.table_index, column = 4)

        self.rows = []
        
        for i, criteria in enumerate(section.criteria, self.table_index + 1):
            row = CriteriaRow(parent, criteria, self.update_section)
            row.text.grid(row=i, sticky=tk.W)
            row.reset_btn.grid(row=i, column=1)
            row.decrement_btn.grid(row=i, column=2)
            if row.is_forgiveable():
                row.lives.grid(row=i, column=3, sticky=tk.E)
            row.score.grid(row=i, column=4)
            self.rows.append(row)

    def update_section(self):
        self.score.config(text=self.section.get_score())

    def reset(self):
        for row in self.rows:
            row.reset()

    def get_marks(self):
        return self.section.calculate_section_marks()
        
class CriteriaRow(object):

    def __init__(self, parent, criteria, parent_update):
        self.parent = parent
        self.criteria = criteria
        self.parent_update = parent_update

        self.text = tk.Label(parent, 
                     text=CRITERIA_INDENT + criteria.get_description(),
                     font=CRITERIA_FONT)

        self.score = tk.Label(parent, text=criteria.get_score())

        self.reset_btn = tk.Button(parent, text='o', command=self.reset,
                width=BTN_WIDTH, fg=RESET_BTN_COLOUR)
    
        self.decrement_btn = tk.Button(parent, text="-", command=self.deduction,
                width=BTN_WIDTH, fg=MINUS_BTN_COLOUR)

        if self.is_forgiveable():
            self.lives = tk.Label(parent, text=str(self.criteria.lives),
            fg='Red', font=LIVES_FONT)

    def is_forgiveable(self):
        return self.criteria.is_forgiveable()

    def get_lives(self):
        return self.lives

    def get_text(self):
        return self.text

    def update_row(self):
        self.text.config(text=CRITERIA_INDENT + self.criteria.get_description())
        self.score.config(text=self.criteria.get_score())
        self.parent_update()
        if self.is_forgiveable():
            self.lives.config(text=str(self.criteria.lives))

    def deduction(self):
        self.criteria.make_deduction()
        self.update_row()   

    def reset(self):
        self.criteria.reset()
        self.update_row() 


def main():
    # cmd line argument parsing
    parser = argparse.ArgumentParser(description="Get root directory")
    parser.add_argument("root", help="The root student directory containing"
                        " all the sXXXXXX... folders")

    parser.add_argument("-s", "--state", dest="state", default=STATE_FILE,
        help="State file containing current marking state")

    args = parser.parse_args()
    student_dir = args.root
    state = args.state

    # ooh tkinter my dear love, I'm back
    root = tk.Tk()
    root.title('2002 Marking')
    app = MarkingToolApp(root, student_dir, state, bg=BG_COLOUR)
    app.pack()
    root.mainloop()

if __name__ == "__main__":
    main()
