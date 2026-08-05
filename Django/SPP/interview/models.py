import uuid
from django.db import models

class InterviewSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate_name = models.CharField(max_length=100, default="Candidate")
    field_of_study = models.CharField(max_length=100)
    target_role = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=50, default="Entry Level")
    
    total_questions = models.IntegerField(default=5)
    current_question_index = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="active") # active, completed
    
    # Overall and category scores (0-100)
    overall_score = models.IntegerField(default=0)
    domain_score = models.IntegerField(default=0)
    speech_score = models.IntegerField(default=0)
    body_language_score = models.IntegerField(default=0)
    structure_score = models.IntegerField(default=0)
    
    # Aggregated Body Language Metrics
    avg_eye_contact = models.FloatField(default=0.0)
    avg_posture_score = models.FloatField(default=0.0)
    avg_fidget_score = models.FloatField(default=0.0)
    avg_smile_score = models.FloatField(default=0.0)
    
    # AI Summary
    key_strengths = models.JSONField(default=list)
    areas_for_improvement = models.JSONField(default=list)
    summary_verdict = models.TextField(blank=True, default="")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.candidate_name} - {self.field_of_study} ({self.target_role})"


class InterviewQA(models.Model):
    session = models.ForeignKey(InterviewSession, related_name="qa_items", on_delete=models.CASCADE)
    question_number = models.IntegerField()
    question_type = models.CharField(max_length=50, default="technical") # intro, technical, behavioral, scenario, closing
    question_text = models.TextField()
    candidate_response = models.TextField(blank=True, default="")
    
    # Body language snapshot for this specific question
    eye_contact_pct = models.FloatField(default=0.0)
    posture_score = models.FloatField(default=0.0)
    fidget_level = models.FloatField(default=0.0)
    smile_level = models.FloatField(default=0.0)
    
    # Question evaluation
    rating = models.IntegerField(default=0) # 0-100
    feedback = models.TextField(blank=True, default="")
    suggested_model_answer = models.TextField(blank=True, default="")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question_number']

    def __str__(self):
        return f"Q{self.question_number} for {self.session.session_id}"
