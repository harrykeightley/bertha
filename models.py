import json
import jsonpickle

def capped_decrement(num, cap):
    return max(cap, num - 1)


def build_ruberic_from_json(file):
    """(list<Section>) Build list of sections from json"""
    with open(file, "r") as json_file:
        return jsonpickle.decode(json_file.read())

class Section(object):

    def __init__(self, name, total_marks):
        self.name = name
        self.total_marks = total_marks
        self.criteria = []

    def add_criteria(self, criteria):
        if criteria not in self.criteria:
            self.criteria.append(criteria)

    def calculate_section_marks(self):
        deductions = sum([criteria.get_deductions() for criteria in self.criteria])
        section_total = self.total_marks - deductions
        section_total = max(section_total, 0)
        return min(section_total, self.total_marks) # can't have more marks than section
    
    def reset(self):
        for criteria in self.criteria:
            criteria.reset()
    
    def get_name(self):
        return self.name

    def get_score(self):
        marks = self.calculate_section_marks()
        return f"({marks} / {self.total_marks})"

    def __str__(self):
        return (f"Section: {self.name}, {self.get_score()}")

    def __repr__(self):
        return f"Section({self.name}, {self.total_marks})"
    

class Criteria(object):

    def __init__(self, description, total_marks, lower_cap=0):
        self.description = description
        self.total_marks = total_marks
        self.marks = total_marks # start off with full marks
        self.lower_cap = lower_cap

    def make_deduction(self):
        self.marks = capped_decrement(self.marks, self.lower_cap)

    def reset(self):
        self.marks = self.total_marks

    def get_deductions(self):
        return self.total_marks - self.marks

    def get_description(self):
        return self.description

    def get_total_marks(self):
        return self.total_marks

    def get_marks(self):
        return self.marks

    def is_forgiveable(self):
        return False

    def get_score(self):
        return f"({self.marks} / {self.total_marks})"

    def __str__(self):
        return (f"Criteria({self.description[:15]}, {self.get_score()})")


class ForgiveableCriteria(Criteria):

    def __init__(self, description, total_marks, total_lives):
        super().__init__(description, total_marks)
        self.total_lives = total_lives
        self.lives = total_lives

    def make_deduction(self):
        if self.lives == 0:
            super().make_deduction()
        self.lives = capped_decrement(self.lives, 0)
    
    def is_forgiveable(self):
        return True

    def reset(self):
        self.lives = self.total_lives
        super().reset()