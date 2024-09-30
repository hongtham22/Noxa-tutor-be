from noxa_be.accounts import models


class Enum(models.Choices):
    @classmethod
    def get_choices_display(cls):
        return [choice[1] for choice in cls.choices]
    
    @classmethod
    def map_display_to_value(cls, display):
        for choice in cls.choices:
            if choice[1] == display:
                return choice[0]
        return None

class Gender(Enum):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'
    
class Role(Enum):
    TUTOR = 'tutor', 'Tutor'
    PARENT = 'parent', 'Parent'

class EducationalBackground(Enum):
    HIGH_SHOOL_DIPLOMA = 'high_school_diploma', 'High School Diploma'
    BACHELOR_DEGREE = 'bachelor_degree', 'Bachelor Degree'
    BACHELOR_DEGREE_ENGINEERING = 'bachelor_degree_engineering', 'Bachelor Degree in Engineering'
    MASTER_DEGREE = 'master_degree', 'Master Degree'
    DOCTORATE_DEGREE = 'doctorate_degree', 'Doctorate Degree'
    
class Position(Enum):
    STUDENT = 'student', 'Student'
    WORKING = 'working', 'Working'

class Subject(Enum):
    MATH = 'math', 'Math'
    LITERATURE = 'literature', 'Literature'
    PHYSICS = 'physics', 'Physics'
    CHEMISTRY = 'chemistry', 'Chemistry'
    BIOLOGY = 'biology', 'Biology'
    ENGLISH = 'english', 'English'
    HISTORY = 'history', 'History'
    GEOGRAPHY = 'geography', 'Geography'
    ECONOMY = 'economy', 'Economy'
    COMPUTER_SCIENCE = 'computer_science', 'Computer Science'
    OTHER = 'other', 'Other'

class Status(Enum):
    PENDING_APPROVAL = 'pending_approval', 'Pending Approval'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    CLOSED = 'closed', 'Closed'