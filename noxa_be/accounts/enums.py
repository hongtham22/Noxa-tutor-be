from . import models
from django.db import models
import unicodedata

class Enum(models.TextChoices):
    @classmethod
    def get_choices_display(cls):
        return [choice[1] for choice in cls.choices]
    
    @classmethod
    def map_display_to_value(cls, display):
        display_normalized = unicodedata.normalize('NFC', str(display).strip().lower())

        for choice in cls.choices:
            label = choice[1]
            label_normalized = unicodedata.normalize('NFC', str(label).strip().lower()) 
            if label_normalized == display_normalized:
                return choice[0]
        return None
    
    @classmethod
    def map_value_to_display(cls, value):
        for choice in cls.choices:
            if choice[0] == value:
                return choice[1]
        return None

class Gender(Enum):
    MALE = 'male', 'Nam'
    FEMALE = 'female', 'Nữ'
    OTHER = 'other', 'Khác'
    
class Role(Enum):
    TUTOR = 'tutor', 'Gia sư'
    PARENT = 'parent', 'Phụ huynh'

class EducationalBackground(Enum):
    HIGH_SHOOL_DIPLOMA = 'high_school_diploma', 'Có bằng tốt nghiệp trung học phổ thông'
    BACHELOR_DEGREE = 'bachelor_degree', 'Có bằng cử nhân'
    BACHELOR_DEGREE_ENGINEERING = 'bachelor_degree_engineering', 'Có bằng kĩ sư'
    MASTER_DEGREE = 'master_degree', 'Có bằng thạc sĩ'
    DOCTORATE_DEGREE = 'doctorate_degree', 'Có bằng tiến sĩ'
    
class Position(Enum):
    STUDENT = 'student', 'Học sinh'
    WORKING = 'working', 'Đang đi làm'

class Subject(Enum):
    MATH = 'math', 'Toán'
    LITERATURE = 'literature', 'Văn học'
    PHYSICS = 'physics', 'Vật lý'
    CHEMISTRY = 'chemistry', 'Hóa học'
    BIOLOGY = 'biology', 'Sinh học'
    ENGLISH = 'english', 'Tiếng Anh'
    HISTORY = 'history', 'Lịch sử'
    GEOGRAPHY = 'geography', 'Địa lý'
    ECONOMY = 'economy', 'Kinh tế'
    COMPUTER_SCIENCE = 'computer_science', 'Khoa học máy tính'
    OTHER = 'other', 'Khác'

class Status(Enum):
    PENDING_APPROVAL = 'pending_approval', 'Đang chờ phê duyệt'
    APPROVED = 'approved', 'Đã phê duyệt'
    REJECTED = 'rejected', 'Bị từ chối'
    CLOSED = 'closed', 'Đã đóng'

class Weekday(Enum):
    MONDAY = 'monday', 'Thứ hai'
    TUESDAY = 'tuesday', 'Thứ ba'
    WEDNESDAY = 'wednesday', 'Thứ tư'
    THURSDAY = 'thursday', 'Thứ năm'
    FRIDAY = 'friday', 'Thứ sáu'
    SATURDAY = 'saturday', 'Thứ bảy'
    SUNDAY = 'sunday', 'Chủ nhật'