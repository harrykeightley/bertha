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

    def get_total_marks(self):
        return self.total_marks
    
    def get_name(self):
        return self.name

    def get_score(self):
        marks = self.calculate_section_marks()
        return f"({marks} / {self.total_marks})"

    # Could be used to save how you marked a certain student.
    def get_summary(self):
        result = []
        result.append(str(self))
        for criteria in self.criteria:
            result.append(str(criteria))
        return "\n".join(result)

    def __str__(self):
        return (f"Section: {self.name}, {self.get_score()}")

    def __repr__(self):
        return f"Section({self.name}, {self.total_marks})"
    

class Criteria(object):

    def __init__(self, description, max_deductions):
        self.description = description
        self.max_deductions = max_deductions
        self.deductions = 0 # start off with full marks

    def make_deduction(self):
        self.deductions = min(self.max_deductions, self.deductions + 1)

    def reset(self):
        self.deductions = 0

    def get_deductions(self):
        return self.deductions

    def get_description(self):
        return self.description

    def is_forgiveable(self):
        return False

    def get_score(self):
        return f"-({self.deductions} / {self.max_deductions})"

    def __str__(self):
        return (f"Criteria({self.description[:15]}, {self.get_score()})")


class ForgiveableCriteria(Criteria):

    def __init__(self, description, max_deductions, total_lives):
        super().__init__(description, max_deductions)
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