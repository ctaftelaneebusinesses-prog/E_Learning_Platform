from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='lesson_images/',
        null=True,
        blank=True
    )

    resource_link = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Quiz(models.Model):
    DIFFICULTY_CHOICES = (
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes'
    )

    title = models.CharField(max_length=200)

    # ✅ MARKS-BASED (CORE)
    total_marks = models.PositiveIntegerField(
        help_text="Total marks for the quiz",
        default=100
    )
    pass_mark = models.PositiveIntegerField(
        help_text="Minimum marks required to pass"
    )

    # ✅ ADMIN METADATA
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='EASY'
    )
    time_limit = models.PositiveIntegerField(
        help_text="Time in minutes",
        default=10
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ DERIVED (NO DB FIELD)
    @property
    def pass_percentage(self):
        if self.total_marks > 0:
            return int((self.pass_mark / self.total_marks) * 100)
        return 0

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )

    def __str__(self):
        return self.text[:50]

class StudentProgress(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )
    completed_lessons = models.PositiveIntegerField(default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    completion_percentage = models.FloatField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class Achievement(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    xp_required = models.PositiveIntegerField(help_text="XP required to unlock")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class StudentAchievement(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'achievement')

    def __str__(self):
        return f"{self.student.username} - {self.achievement.title}"

class LearningStreak(models.Model):
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='learning_streak'
    )
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.current_streak} days"


class StreakReward(models.Model):
    streak_days = models.PositiveIntegerField(help_text="Days required for reward", unique=True)
    bonus_xp = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.streak_days} Days → {self.bonus_xp} XP"

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CourseSkill(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    weight = models.PositiveIntegerField(
        default=1,
        help_text="Contribution weight of this course to the skill"
    )

    class Meta:
        unique_together = ('course', 'skill')

    def __str__(self):
        return f"{self.course.title} → {self.skill.name}"


class StudentSkill(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_score = models.FloatField(default=0)

    class Meta:
        unique_together = ('student', 'skill')

    def __str__(self):
        return f"{self.student.username} - {self.skill.name}"

class LearningSession(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learning_sessions'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.student.username} - {self.duration_minutes} mins"


class ActivityLog(models.Model):
    ACTIVITY_CHOICES = (
        ('LESSON_VIEW', 'Lesson Viewed'),
        ('QUIZ_ATTEMPT', 'Quiz Attempted'),
        ('COURSE_ENROLL', 'Course Enrolled'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.activity_type}"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')
        
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
class LessonCompletion(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"

class StudentQuizAttempt(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE
    )
    score = models.PositiveIntegerField()
    passed = models.BooleanField(default=False )
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'quiz')

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - {self.score}"
    
class LearningPath(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    priority_score = models.FloatField(default=0)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-priority_score']

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"

class Certificate(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    certificate_id = models.CharField(
        max_length=50,
        unique=True
    )

    issued_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class InstructorStudentChat(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="instructor_chats")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_chats")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "instructor", "student")


class InstructorStudentMessage(models.Model):
    chat = models.ForeignKey(
        InstructorStudentChat,
        related_name="messages",
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    attachment = models.FileField(upload_to="chat_attachments/", null=True, blank=True)
    voice_note = models.FileField(upload_to="chat_voice_notes/", null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.message[:30]}"


class MessageReaction(models.Model):
    message = models.ForeignKey(
        InstructorStudentMessage,
        related_name="reactions",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user")


class AILearningPathQuery(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ai_learning_path_queries"
    )
    role = models.CharField(max_length=255)
    suggestions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.username} → {self.role}"
