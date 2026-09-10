import calendar
from datetime import date

from django.utils.timezone import localdate

from courses.models import (
    Achievement,
    Attendance,
    StudentAchievement,
    StudentProgress,
)

def check_and_award_achievements(student):
    achievements = Achievement.objects.filter(is_active=True)

    for achievement in achievements:
        # Skip if already earned
        if StudentAchievement.objects.filter(
            student=student,
            achievement=achievement
        ).exists():
            continue

        # 🔹 XP based achievement
        progress = StudentProgress.objects.filter(
            student=student
        ).first()

        if progress and progress.xp_earned >= achievement.xp_required:
            StudentAchievement.objects.create(
                student=student,
                achievement=achievement
            )


def get_attendance_month_data(student, year, month):
    """Build a week-by-week calendar grid for one month, marking each day
    Present (tapped in), Absent (day has passed, no tap-in) or Future/Other-month."""
    today = localdate()
    present_dates = set(
        Attendance.objects.filter(
            student=student, date__year=year, date__month=month
        ).values_list('date', flat=True)
    )

    weeks = []
    week = []
    for d in calendar.Calendar(firstweekday=0).itermonthdates(year, month):
        if d.month != month:
            status = 'other-month'
        elif d > today:
            status = 'future'
        elif d in present_dates:
            status = 'present'
        else:
            status = 'absent'

        week.append({
            'date': d,
            'day': d.day,
            'in_month': d.month == month,
            'status': status,
            'is_today': d == today,
        })
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)

    total_elapsed = sum(
        1 for wk in weeks for day in wk
        if day['in_month'] and day['status'] in ('present', 'absent')
    )
    present_count = sum(
        1 for wk in weeks for day in wk if day['status'] == 'present'
    )

    return {
        'weeks': weeks,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'present_count': present_count,
        'absent_count': total_elapsed - present_count,
        'total_elapsed': total_elapsed,
    }


def get_attendance_yearly_summary(student, year):
    """Month-by-month present/absent totals for a year, counting only days up to today."""
    today = localdate()
    rows = []
    total_present = 0
    total_elapsed = 0

    for month in range(1, 13):
        first_day = date(year, month, 1)
        if first_day > today:
            rows.append({
                'month': calendar.month_name[month],
                'present': None,
                'absent': None,
                'elapsed': 0,
            })
            continue

        last_day = date(year, month, calendar.monthrange(year, month)[1])
        elapsed_end = min(last_day, today)
        elapsed_days = (elapsed_end - first_day).days + 1

        present = Attendance.objects.filter(
            student=student, date__year=year, date__month=month, date__lte=today
        ).count()
        absent = elapsed_days - present

        rows.append({
            'month': calendar.month_name[month],
            'present': present,
            'absent': absent,
            'elapsed': elapsed_days,
        })
        total_present += present
        total_elapsed += elapsed_days

    return {
        'rows': rows,
        'year': year,
        'total_present': total_present,
        'total_absent': total_elapsed - total_present,
        'total_elapsed': total_elapsed,
    }
