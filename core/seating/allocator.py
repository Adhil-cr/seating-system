from students.models import Student
from halls.models import Hall


def simple_allocator():
    students = list(Student.objects.all())
    halls = list(Hall.objects.all())

    seat_map = []

    student_index = 0

    for hall in halls:
        for r in range(1, hall.rows + 1):
            for c in range(1, hall.columns + 1):
                for b in range(hall.seats_per_bench):
                    if student_index >= len(students):
                        return seat_map

                    seat_map.append({
                        "hall": hall,
                        "row": r,
                        "column": c,
                        "student": students[student_index]
                    })

                    student_index += 1

    return seat_map