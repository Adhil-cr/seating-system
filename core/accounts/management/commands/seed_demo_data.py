import csv
import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from students.models import Student, Subject, UploadHistory
from halls.models import Hall
from exams.models import Exam
from seating.models import SeatingAllocation, Seat


class Command(BaseCommand):
    help = "Seeds the default inspector demo account (admin/admin123) and sample data."

    def handle(self, *args, **options):
        self.stdout.write("==> Seeding inspector demo account and data...")

        User = get_user_model()
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@benchmap.in",
                "first_name": "Demo Inspector",
                "is_staff": True,
                "is_superuser": True,
                "role": "admin",
            }
        )
        admin_user.set_password("admin123")
        admin_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS("Created demo user: admin / admin123"))
        else:
            self.stdout.write(self.style.SUCCESS("Updated demo user: admin / admin123"))

        # 1. Seed Subjects
        subj_2021, _ = Subject.objects.get_or_create(code="2021")
        subj_4031, _ = Subject.objects.get_or_create(code="4031")
        subj_3011, _ = Subject.objects.get_or_create(code="3011")

        # 2. Seed Students for admin user
        existing_students = Student.objects.filter(user=admin_user).count()
        if existing_students < 10:
            csv_path = Path(settings.PROJECT_DIR) / "static" / "samples" / "sample_raw_students_input.csv"
            students_to_add = []

            if csv_path.exists():
                with open(csv_path, mode="r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for idx, row in enumerate(reader):
                        if idx >= 60:  # Seed 60 sample students
                            break
                        reg_no = row.get("Register No") or row.get("register_no") or f"REG{idx:04d}"
                        name = row.get("Student Name") or row.get("student_name") or f"Student {idx}"
                        branch = row.get("Branch") or row.get("department") or "Engineering"
                        sem = row.get("Semester") or 2
                        sub1 = row.get("Sub1") or row.get("subject_code") or ("2021" if idx % 2 == 0 else "4031")

                        students_to_add.append({
                            "reg_no": reg_no.strip(),
                            "name": name.strip(),
                            "branch": branch.strip(),
                            "sem": int(sem) if str(sem).isdigit() else 2,
                            "sub": str(sub1).strip().replace(".0", "")
                        })

            if not students_to_add:
                # Fallback realistic student records
                for i in range(1, 61):
                    code = "2021" if i % 2 == 0 else "4031"
                    dept = "Mechanical Engineering" if code == "2021" else "Electrical & Electronics Engineering"
                    students_to_add.append({
                        "reg_no": f"2401020{i:03d}",
                        "name": f"Candidate {i:02d}",
                        "branch": dept,
                        "sem": 2,
                        "sub": code
                    })

            for s in students_to_add:
                sub_obj, _ = Subject.objects.get_or_create(code=s["sub"])
                st, _ = Student.objects.get_or_create(
                    user=admin_user,
                    register_no=s["reg_no"],
                    defaults={
                        "name": s["name"],
                        "department": s["branch"],
                        "semester": s["sem"],
                        "subject_code": s["sub"],
                    }
                )
                st.subjects.add(sub_obj)

            UploadHistory.objects.get_or_create(
                user=admin_user,
                file_name="sample_raw_students_input.csv",
                defaults={"students_count": len(students_to_add)}
            )
            self.stdout.write(self.style.SUCCESS(f"Seeded {len(students_to_add)} students for admin user."))
        else:
            self.stdout.write(f"Admin already has {existing_students} students.")

        # 3. Seed Examination Halls
        hall_a, _ = Hall.objects.get_or_create(
            user=admin_user,
            name="Hall A - Main Block",
            defaults={"rows": 5, "columns": 6, "seats_per_bench": 1, "is_active": True}
        )
        hall_b, _ = Hall.objects.get_or_create(
            user=admin_user,
            name="Hall B - Science Block",
            defaults={"rows": 5, "columns": 6, "seats_per_bench": 1, "is_active": True}
        )
        self.stdout.write(self.style.SUCCESS("Halls verified: Hall A & Hall B (60 total capacity)."))

        # 4. Seed Exam
        exam, _ = Exam.objects.get_or_create(
            user=admin_user,
            name="B.Tech End Semester Exam - Session 1",
            defaults={
                "date": datetime.date.today(),
                "session": "AM",
                "subject_codes": ["2021", "4031"],
            }
        )
        exam.subjects.add(subj_2021, subj_4031)

        # 5. Seed Seating Allocation
        allocation, alloc_created = SeatingAllocation.objects.get_or_create(exam=exam)
        if Seat.objects.filter(allocation=allocation).count() == 0:
            students = list(Student.objects.filter(user=admin_user).order_by("register_no"))
            halls = [hall_a, hall_b]
            student_idx = 0

            # Interleaved allocation: alternate between subjects across benches
            for hall in halls:
                for r in range(1, hall.rows + 1):
                    for c in range(1, hall.columns + 1):
                        if student_idx < len(students):
                            Seat.objects.create(
                                allocation=allocation,
                                hall=hall,
                                row=r,
                                column=c,
                                student=students[student_idx]
                            )
                            student_idx += 1

            self.stdout.write(self.style.SUCCESS(f"Seeded seating allocation: {student_idx} seats allocated."))
        else:
            self.stdout.write("Seating allocation already populated.")

        self.stdout.write(self.style.SUCCESS("==> Inspector demo data setup complete!"))
