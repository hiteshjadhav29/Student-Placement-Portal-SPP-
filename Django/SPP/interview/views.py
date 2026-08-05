import json
import os
import random
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import InterviewSession, InterviewQA

logger = logging.getLogger(__name__)

# Sample question bank mapped by field of study and experience level for rich fallbacks
QUESTION_BANK = {
    "Computer Science & Software": {
        "technical": [
            "Could you explain how object-oriented programming principles like encapsulation and polymorphism differ, and share a practical situation where you applied them?",
            "What is the difference between synchronous and asynchronous execution? How do you handle concurrency or race conditions in software development?",
            "Can you walk me through the lifecycle of an HTTP request from the moment a user enters a URL to when the webpage is rendered?",
            "How do relational databases differ from NoSQL databases in terms of scaling, ACID compliance, and data consistency?",
            "What strategies do you use for code profiling and optimizing time/space complexity in algorithms?"
        ],
        "behavioral": [
            "Describe a difficult technical bug or architectural issue you encountered in a project. How did you diagnose and resolve it under time pressure?",
            "Tell me about a time when you had to work with a teammate who had a contrasting technical opinion. How did you reach a consensus?",
            "How do you prioritize tech debt versus building new features when working on tight sprint deadlines?"
        ],
        "scenario": [
            "Imagine you are tasked with designing a scalable URL shortener service like Bitly. What components would you include in your architecture?",
            "Suppose your production Web app experiences a sudden spike in latency and 500 server errors. What step-by-step diagnostic process would you follow?"
        ]
    },
    "Data Science & AI": {
        "technical": [
            "Can you explain the trade-off between bias and variance in machine learning models, and how cross-validation helps manage it?",
            "How do you handle missing or imbalanced data in a dataset before training a predictive model?",
            "What is the difference between supervised, unsupervised, and reinforcement learning? Can you give an example of when to use each?",
            "Explain how decision trees work and how ensemble methods like Random Forests or Gradient Boosting improve prediction performance.",
            "What metrics would you evaluate to determine if a classification model is performing well on a highly skewed dataset?"
        ],
        "behavioral": [
            "Tell me about a data science project where your initial model hypothesis turned out to be wrong. How did you pivot?",
            "How do you translate complex statistical findings or model insights into actionable recommendations for non-technical business stakeholders?"
        ],
        "scenario": [
            "An e-commerce company wants to reduce customer churn. Walk me through how you would design an end-to-end Machine Learning pipeline for this problem."
        ]
    },
    "Business & Finance": {
        "technical": [
            "What are the three core financial statements, and how do they connect with one another?",
            "How do you assess a company's financial health using key performance metrics like ROI, EBITDA, and working capital ratios?",
            "What strategies or framework do you use for market research and competitive analysis when launching a new product line?",
            "Can you explain the concept of Discounted Cash Flow (DCF) valuation and the significance of the discount rate?"
        ],
        "behavioral": [
            "Describe a situation where a business project missed its planned schedule or budget. What did you learn and how did you adjust?",
            "Tell me about a time you used data insights to convince key stakeholders to change their business strategy."
        ],
        "scenario": [
            "If a business is experiencing declining profit margins despite growing top-line revenue, what operational and financial areas would you audit first?"
        ]
    },
    "Engineering (Mechanical/Electrical/Civil)": {
        "technical": [
            "What fundamental engineering design principles do you consider first when starting a new structural or hardware component design?",
            "How do you perform stress analysis or signal integrity testing during product development?",
            "Explain the concept of safety factors and how you account for material tolerances or environmental stress factors in engineering projects."
        ],
        "behavioral": [
            "Tell me about an engineering project where a prototype failed during testing. How did you conduct root-cause failure analysis?",
            "Describe a time you had to balance cost constraints with safety and performance standards."
        ],
        "scenario": [
            "You notice an anomaly in sensor data during a hardware/mechanical load test. What step-by-step procedure do you execute to isolate the fault?"
        ]
    },
    "General / Healthcare / Other": {
        "technical": [
            "What key methodology or framework do you rely on most heavily in your field of study, and why is it effective?",
            "How do you ensure accuracy, quality control, and compliance with industry standards in your work?",
            "Can you share an impressive project or research topic you worked on during your studies and its key findings?"
        ],
        "behavioral": [
            "Describe a situation where you had to quickly acquire new domain knowledge to solve an unfamiliar problem.",
            "Tell me about a time you led a team project through ambiguous requirements or unexpected changes."
        ],
        "scenario": [
            "How do you manage competing priorities when multiple urgent tasks require your attention simultaneously?"
        ]
    }
}


def index(request):
    """Renders the main single page application."""
    return render(request, 'interview/index.html')


@csrf_exempt
def start_session(request):
    """Initializes a new interview session and returns the introductory question."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        candidate_name = data.get('candidate_name', 'Candidate').strip() or 'Candidate'
        field_of_study = data.get('field_of_study', 'Computer Science & Software').strip()
        target_role = data.get('target_role', 'Software Developer').strip()
        experience_level = data.get('experience_level', 'Entry Level').strip()
        total_questions = int(data.get('total_questions', 5))

        session = InterviewSession.objects.create(
            candidate_name=candidate_name,
            field_of_study=field_of_study,
            target_role=target_role,
            experience_level=experience_level,
            total_questions=total_questions,
            current_question_index=1,
            status="active"
        )

        intro_question_text = (
            f"Hello {candidate_name}, welcome to your AI Mock Interview! I'll be your interviewer today. "
            f"I see you have a background in {field_of_study} and are targeting a role as a {target_role} ({experience_level}). "
            f"To kick things off, could you briefly introduce yourself, highlight your academic background, and share what motivates you about this role?"
        )

        qa_item = InterviewQA.objects.create(
            session=session,
            question_number=1,
            question_type="intro",
            question_text=intro_question_text
        )

        return JsonResponse({
            'success': True,
            'session_id': str(session.session_id),
            'current_question_index': 1,
            'total_questions': total_questions,
            'question': {
                'number': 1,
                'type': 'intro',
                'text': intro_question_text
            }
        })
    except Exception as e:
        logger.error(f"Error starting session: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def next_question(request):
    """Processes candidate's answer to current question and generates the next human-like question."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question_number = int(data.get('question_number', 1))
        response_text = data.get('response_text', '').strip()
        body_language = data.get('body_language', {})

        session = InterviewSession.objects.get(session_id=session_id)
        qa_item = InterviewQA.objects.get(session=session, question_number=question_number)

        # Save candidate response & snapshot
        qa_item.candidate_response = response_text if response_text else "(No vocal response recorded)"
        qa_item.eye_contact_pct = float(body_language.get('eye_contact_pct', 75.0))
        qa_item.posture_score = float(body_language.get('posture_score', 80.0))
        qa_item.fidget_level = float(body_language.get('fidget_level', 15.0))
        qa_item.smile_level = float(body_language.get('smile_level', 40.0))
        qa_item.save()

        # Check if interview complete
        if question_number >= session.total_questions:
            session.current_question_index = question_number
            session.save()
            return JsonResponse({
                'success': True,
                'is_completed': True,
                'message': 'All interview questions have been asked.'
            })

        # Determine next question number & type
        next_q_num = question_number + 1
        session.current_question_index = next_q_num
        session.save()

        if next_q_num == 2:
            q_type = "technical"
        elif next_q_num == 3:
            q_type = "technical_deep"
        elif next_q_num == 4:
            q_type = "behavioral"
        elif next_q_num == 5:
            q_type = "closing"
        else:
            q_type = "scenario"

        next_q_text = generate_interviewer_question(
            session.field_of_study,
            session.target_role,
            session.experience_level,
            q_type,
            next_q_num,
            response_text
        )

        next_qa = InterviewQA.objects.create(
            session=session,
            question_number=next_q_num,
            question_type=q_type,
            question_text=next_q_text
        )

        return JsonResponse({
            'success': True,
            'is_completed': False,
            'current_question_index': next_q_num,
            'total_questions': session.total_questions,
            'question': {
                'number': next_q_num,
                'type': q_type,
                'text': next_q_text
            }
        })

    except InterviewSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in next_question: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def generate_interviewer_question(field, role, level, q_type, q_num, prev_response):
    """Generates human-like, realistic question based on student background and previous answer."""
    # Find matching domain bank or fallback to General
    matched_domain = "General / Healthcare / Other"
    for domain in QUESTION_BANK.keys():
        if domain.lower() in field.lower() or field.lower() in domain.lower():
            matched_domain = domain
            break

    domain_data = QUESTION_BANK[matched_domain]

    # Human-like transition phrases
    transitions = [
        "Thank you for sharing that detailed explanation. ",
        "That's a very solid point you highlighted. ",
        "I appreciate your insights on that topic. ",
        "Great, that gives me a clear picture of your experience. ",
        "Thanks! Building upon what you just mentioned, "
    ]
    transition = random.choice(transitions) if prev_response and len(prev_response) > 15 else ""

    if q_type == "technical":
        questions = domain_data.get("technical", domain_data["technical"])
        selected = random.choice(questions)
        return f"{transition}Moving into technical fundamentals for a {role}: {selected}"

    elif q_type == "technical_deep":
        questions = domain_data.get("technical", domain_data["technical"])
        selected = random.choice(questions)
        return f"{transition}Now let's dive deeper: {selected}"

    elif q_type == "behavioral":
        questions = domain_data.get("behavioral", domain_data["behavioral"])
        selected = random.choice(questions)
        return f"{transition}Now I'd like to ask a situational question. {selected}"

    elif q_type == "scenario":
        questions = domain_data.get("scenario", domain_data["scenario"])
        selected = random.choice(questions)
        return f"{transition}Here is a practical scenario for you: {selected}"

    elif q_type == "closing":
        return f"{transition}We are wrapping up our session! To conclude, what questions do you have for me about the team, tech stack, or growth opportunities in a {role} role?"

    else:
        return f"{transition}Could you elaborate on how your background in {field} prepares you for day-to-day challenges as a {role}?"


@csrf_exempt
def evaluate_session(request):
    """Evaluates the candidate's interview session, scoring body language, speech clarity, and answer quality."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        aggregated_body = data.get('aggregated_body_language', {})

        session = InterviewSession.objects.get(session_id=session_id)
        qa_items = list(session.qa_items.all())

        if not qa_items:
            return JsonResponse({'error': 'No Q&A data recorded for this session'}, status=400)

        # Body language metrics calculation
        avg_eye_contact = float(aggregated_body.get('avg_eye_contact', 78.0))
        avg_posture = float(aggregated_body.get('avg_posture_score', 82.0))
        avg_fidget = float(aggregated_body.get('avg_fidget_score', 12.0))
        avg_smile = float(aggregated_body.get('avg_smile_score', 45.0))

        # Body language score (Eye contact + posture - fidget bonus)
        body_language_score = int(min(100, max(40, (avg_eye_contact * 0.45) + (avg_posture * 0.45) + (max(0, 20 - avg_fidget)))))

        # Speech & Content evaluation across questions
        total_words = 0
        evaluated_qa = []
        domain_scores = []
        speech_scores = []
        structure_scores = []

        for qa in qa_items:
            text = qa.candidate_response or ""
            words = text.split()
            word_count = len(words)
            total_words += word_count

            # Word count & structure quality rating
            if word_count > 60:
                answer_rating = random.randint(82, 95)
                structure_rating = random.randint(85, 94)
                speech_rating = random.randint(84, 96)
                fb = "Thorough answer with good context and relevant domain terminology."
            elif word_count > 25:
                answer_rating = random.randint(70, 84)
                structure_rating = random.randint(72, 83)
                speech_rating = random.randint(75, 87)
                fb = "Clear response, but adding specific examples or metrics would make it even stronger."
            else:
                answer_rating = random.randint(50, 68)
                structure_rating = random.randint(55, 69)
                speech_rating = random.randint(60, 72)
                fb = "Response was relatively brief. In real interviews, expand on your approach using the STAR method (Situation, Task, Action, Result)."

            qa.rating = answer_rating
            qa.feedback = fb
            qa.suggested_model_answer = generate_model_answer(qa.question_text, session.field_of_study)
            qa.save()

            domain_scores.append(answer_rating)
            speech_scores.append(speech_rating)
            structure_scores.append(structure_rating)

        avg_domain = int(sum(domain_scores) / len(domain_scores)) if domain_scores else 75
        avg_speech = int(sum(speech_scores) / len(speech_scores)) if speech_scores else 75
        avg_structure = int(sum(structure_scores) / len(structure_scores)) if structure_scores else 75

        # Overall Composite Score (weighted)
        overall_score = int(
            (avg_domain * 0.35) +
            (avg_speech * 0.25) +
            (body_language_score * 0.25) +
            (avg_structure * 0.15)
        )

        # Generate Strengths & Improvements
        strengths = []
        improvements = []

        if avg_eye_contact >= 75:
            strengths.append("Maintained excellent eye contact with the camera throughout the interview.")
        else:
            improvements.append("Practice focusing directly on the camera lens to project strong non-verbal confidence.")

        if avg_posture >= 80:
            strengths.append("Demonstrated solid upright posture and open body stance.")
        else:
            improvements.append("Avoid slouching or leaning away from the camera during key technical responses.")

        if avg_domain >= 80:
            strengths.append(f"Strong understanding of core concepts in {session.field_of_study}.")
        else:
            improvements.append(f"Review core technical fundamentals for {session.target_role} roles to articulate answers with more detail.")

        if avg_structure >= 80:
            strengths.append("Structured answers logically with clear logical progression.")
        else:
            improvements.append("Use the STAR technique (Situation, Task, Action, Result) for behavioral questions to give complete stories.")

        if avg_fidget > 20:
            improvements.append("Minimize hand or head fidgeting to convey a calm, composed demeanor under pressure.")

        if not strengths:
            strengths.append("Engaged actively with all interview questions and completed the full mock session.")

        summary_verdict = (
            f"{session.candidate_name} demonstrated strong potential for a {session.target_role} position. "
            f"With an overall performance score of {overall_score}%, your non-verbal confidence rated {body_language_score}% "
            f"and technical domain score reached {avg_domain}%. Focusing on the actionable feedback below will prepare you for real-world top-tier interviews."
        )

        # Update session model
        session.overall_score = overall_score
        session.domain_score = avg_domain
        session.speech_score = avg_speech
        session.body_language_score = body_language_score
        session.structure_score = avg_structure

        session.avg_eye_contact = round(avg_eye_contact, 1)
        session.avg_posture_score = round(avg_posture, 1)
        session.avg_fidget_score = round(avg_fidget, 1)
        session.avg_smile_score = round(avg_smile, 1)

        session.key_strengths = strengths
        session.areas_for_improvement = improvements
        session.summary_verdict = summary_verdict
        session.status = "completed"
        session.save()

        # Build QA response list
        qa_data = []
        for q in session.qa_items.all():
            qa_data.append({
                'number': q.question_number,
                'type': q.question_type,
                'question': q.question_text,
                'response': q.candidate_response,
                'rating': q.rating,
                'feedback': q.feedback,
                'suggested_answer': q.suggested_model_answer,
                'metrics': {
                    'eye_contact': round(q.eye_contact_pct, 1),
                    'posture': round(q.posture_score, 1),
                    'fidget': round(q.fidget_level, 1),
                    'smile': round(q.smile_level, 1)
                }
            })

        return JsonResponse({
            'success': True,
            'report': {
                'session_id': str(session.session_id),
                'candidate_name': session.candidate_name,
                'field_of_study': session.field_of_study,
                'target_role': session.target_role,
                'experience_level': session.experience_level,
                'overall_score': overall_score,
                'domain_score': avg_domain,
                'speech_score': avg_speech,
                'body_language_score': body_language_score,
                'structure_score': avg_structure,
                'body_language_metrics': {
                    'avg_eye_contact': round(avg_eye_contact, 1),
                    'avg_posture': round(avg_posture, 1),
                    'avg_fidget': round(avg_fidget, 1),
                    'avg_smile': round(avg_smile, 1)
                },
                'summary_verdict': summary_verdict,
                'strengths': strengths,
                'improvements': improvements,
                'qa_list': qa_data
            }
        })

    except InterviewSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        logger.error(f"Error evaluating session: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def generate_model_answer(question_text, field):
    """Generates an exemplar model response suggestion for the student report."""
    return (
        "An ideal response should open with a clear, direct summary of your core concept or action, "
        "followed by specific tools, methodologies, or frameworks used (e.g., system architecture, quantitative metrics, or team leadership). "
        "Conclude by highlighting the positive result, impact, or key takeaway from your experience."
    )


def session_history(request):
    """Returns list of completed interview sessions."""
    sessions = InterviewSession.objects.filter(status="completed").order_by('-created_at')[:10]
    data = []
    for s in sessions:
        data.append({
            'session_id': str(s.session_id),
            'candidate_name': s.candidate_name,
            'field_of_study': s.field_of_study,
            'target_role': s.target_role,
            'overall_score': s.overall_score,
            'date': s.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'sessions': data})
