from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from recruiters.models import Company, RecruiterProfile
from students.models import Student, Notification
from jobs.models import Job

User = get_user_model()


class JobBranchTargetingTest(TestCase):

    def setUp(self):
        self.recruiter_user = User.objects.create_user(
            username="recruiter1",
            email="recruiter@company.com",
            password="Password123",
            role="recruiter"
        )
        self.company = Company.objects.create(
            company_name="TechCorp",
            company_email="contact@techcorp.com",
            company_phone="1234567890",
            industry="IT",
            location="Pune"
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter_user,
            company=self.company,
            full_name="John Recruiter",
            designation="HR",
            phone="9876543210",
            gender="Male"
        )

        self.student_user_co = User.objects.create_user(
            username="student_co",
            email="co@student.com",
            password="Password123",
            role="student"
        )
        self.student_co = Student.objects.create(
            user=self.student_user_co,
            roll_number="CO01",
            phone="1111111111",
            branch="CO",
            semester=5,
            cgpa=8.5,
            date_of_birth="2002-01-01",
            gender="Male",
            address="Pune"
        )

        self.student_user_me = User.objects.create_user(
            username="student_me",
            email="me@student.com",
            password="Password123",
            role="student"
        )
        self.student_me = Student.objects.create(
            user=self.student_user_me,
            roll_number="ME01",
            phone="2222222222",
            branch="ME",
            semester=5,
            cgpa=7.5,
            date_of_birth="2002-01-01",
            gender="Female",
            address="Mumbai"
        )

    def test_job_target_branches_notification(self):
        self.client.login(username="recruiter1", password="Password123")

        response = self.client.post("/jobs/add/", {
            "job_title": "Software Engineer",
            "job_description": "Great python role",
            "required_skills": "Python, Django",
            "qualification": "B.E",
            "experience": "Fresher",
            "job_type": "Full-Time",
            "location": "Pune",
            "salary": "6 LPA",
            "vacancies": 2,
            "application_deadline": "2028-12-31",
            "status": "Open",
            "target_branches_list": ["CO"],
        })

        self.assertEqual(response.status_code, 302)

        # Check job created
        job = Job.objects.get(job_title="Software Engineer")
        self.assertIn("CO", job.target_branches)

        # Check notifications
        co_notifications = Notification.objects.filter(student=self.student_co)
        me_notifications = Notification.objects.filter(student=self.student_me)

        self.assertEqual(co_notifications.count(), 1)
        self.assertEqual(me_notifications.count(), 0)
