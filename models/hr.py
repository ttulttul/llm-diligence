from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import Field, BaseModel, field_validator, ConfigDict
from datetime import date, datetime
import re
from .base import DiligentizerModel
from .contracts import Agreement

# Base class for HR-related agreements
class HRAgreement(Agreement):
    """A legal agreement specifically related to human resources matters.
    This model serves as the foundation for all HR-related agreements, capturing essential
    elements common to employment contracts, confidentiality agreements, stock options,
    and other HR legal documents. It provides a structured representation of agreements
    that govern the employer-employee relationship."""
    employer_name: Optional[str] = Field(None, description="Name of the employer entity")
    employee_name: Optional[str] = Field(None, description="Name of the employee")
    employment_relationship: Optional[str] = Field(None, description="Nature of the employment relationship")
    hr_document_type: Optional[str] = Field(None, description="Type of HR agreement document")

# Enums for HR document types

class EmploymentType(str, Enum):
    """Types of employment"""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERN = "intern"
    APPRENTICE = "apprentice"
    CONSULTANT = "consultant"
    SEASONAL = "seasonal"

class TerminationType(str, Enum):
    """Types of employment termination"""
    VOLUNTARY = "voluntary resignation"
    INVOLUNTARY = "involuntary termination"
    LAYOFF = "layoff"
    RETIREMENT = "retirement"
    END_OF_CONTRACT = "end of contract"
    MUTUAL_AGREEMENT = "mutual agreement"
    PROBATION_FAILURE = "probation failure"

class PerformanceRating(str, Enum):
    """Common performance rating scales"""
    EXCEPTIONAL = "exceptional"
    EXCEEDS_EXPECTATIONS = "exceeds expectations"
    MEETS_EXPECTATIONS = "meets expectations"
    NEEDS_IMPROVEMENT = "needs improvement"
    UNSATISFACTORY = "unsatisfactory"

class CompensationType(str, Enum):
    """Types of compensation"""
    SALARY = "salary"
    HOURLY = "hourly"
    COMMISSION = "commission"
    BONUS = "bonus"
    EQUITY = "equity"
    PROFIT_SHARING = "profit sharing"
    PIECE_RATE = "piece rate"
    HYBRID = "hybrid"

class BenefitType(str, Enum):
    """Types of employee benefits"""
    HEALTH_INSURANCE = "health insurance"
    DENTAL_INSURANCE = "dental insurance"
    VISION_INSURANCE = "vision insurance"
    LIFE_INSURANCE = "life insurance"
    DISABILITY_INSURANCE = "disability insurance"
    RETIREMENT_PLAN = "retirement plan"
    PAID_TIME_OFF = "paid time off"
    WELLNESS_PROGRAM = "wellness program"
    TUITION_REIMBURSEMENT = "tuition reimbursement"
    CHILDCARE = "childcare"
    FLEXIBLE_SPENDING_ACCOUNT = "flexible spending account"
    HEALTH_SAVINGS_ACCOUNT = "health savings account"
    STOCK_OPTIONS = "stock options"
    EMPLOYEE_ASSISTANCE_PROGRAM = "employee assistance program"

class VestingScheduleType(str, Enum):
    """Types of vesting schedules for equity compensation"""
    TIME_BASED = "time-based"
    PERFORMANCE_BASED = "performance-based"
    CLIFF = "cliff"
    GRADED = "graded"
    HYBRID = "hybrid"
    IMMEDIATE = "immediate"
    MILESTONE_BASED = "milestone-based"

class LeaveType(str, Enum):
    """Types of employee leave"""
    VACATION = "vacation"
    SICK = "sick"
    PERSONAL = "personal"
    BEREAVEMENT = "bereavement"
    PARENTAL = "parental"
    MEDICAL = "medical"
    MILITARY = "military"
    JURY_DUTY = "jury duty"
    SABBATICAL = "sabbatical"
    UNPAID = "unpaid"
    FMLA = "family and medical leave act"

# Base class for all HR documents
class HRDocument(DiligentizerModel):
    """A document related to human resources functions, processes, or employee information.
    This model serves as the foundation for all HR document types, capturing essential
    information such as document type, effective date, and related employee information.
    It provides a structured representation of HR documents across the employee lifecycle,
    from recruitment through separation."""
    document_type: Optional[str] = Field(None, description="Type of HR document")
    document_date: Optional[date] = Field(None, description="Date the document was created")
    effective_date: Optional[date] = Field(None, description="Date when the document becomes effective")
    expiration_date: Optional[date] = Field(None, description="Date when the document expires, if applicable")
    company_name: Optional[str] = Field(None, description="Name of the company or organization")
    department: Optional[str] = Field(None, description="Department related to the document")
    employee_name: Optional[str] = Field(None, description="Name of the employee, if applicable")
    employee_id: Optional[str] = Field(None, description="Employee ID, if applicable")
    confidentiality_level: Optional[str] = Field(None, description="Level of confidentiality (e.g., Public, Confidential, Highly Confidential)")

# Recruitment & Hiring Documents

class JobDescription(HRDocument):
    """A document outlining the responsibilities, qualifications, and details of a specific job position.
    This model captures the comprehensive details of a job posting, including role requirements,
    responsibilities, qualifications, and compensation information. It provides a structured
    representation of job opportunities for recruitment purposes."""
    job_title: str = Field(..., description="Title of the job position")
    job_code: Optional[str] = Field(None, description="Internal code or identifier for the position")
    employment_type: EmploymentType = Field(..., description="Type of employment (full-time, part-time, etc.)")
    location: str = Field(..., description="Location of the job")
    remote_eligible: Optional[bool] = Field(None, description="Whether the position is eligible for remote work")
    reports_to: Optional[str] = Field(None, description="Position or person this role reports to")
    salary_range: Optional[str] = Field(None, description="Salary or compensation range")
    job_summary: str = Field(..., description="Brief summary of the job")
    essential_duties: List[str] = Field(..., description="Essential duties and responsibilities")
    required_qualifications: List[str] = Field(..., description="Required qualifications and skills")
    preferred_qualifications: Optional[List[str]] = Field(None, description="Preferred qualifications and skills")
    education_requirements: Optional[str] = Field(None, description="Required education level")
    experience_requirements: Optional[str] = Field(None, description="Required years or type of experience")
    physical_requirements: Optional[List[str]] = Field(None, description="Physical requirements of the job")
    travel_requirements: Optional[str] = Field(None, description="Travel requirements, if any")
    benefits_summary: Optional[str] = Field(None, description="Summary of benefits offered")
    equal_opportunity_statement: Optional[str] = Field(None, description="Equal opportunity employer statement")
    posting_date: Optional[date] = Field(None, description="Date when the job was posted")
    closing_date: Optional[date] = Field(None, description="Deadline for applications")
    internal_only: Optional[bool] = Field(None, description="Whether the posting is for internal candidates only")

class Resume(HRDocument):
    """A document summarizing a candidate's education, work experience, skills, and qualifications.
    This model captures the structured information from a candidate's resume, including personal
    details, work history, education, skills, and references. It enables systematic analysis and
    comparison of candidate qualifications."""
    candidate_name: str = Field(..., description="Name of the candidate")
    contact_information: Dict[str, str] = Field(..., description="Contact information (email, phone, address)")
    objective_statement: Optional[str] = Field(None, description="Career objective or summary statement")
    work_experience: List[Dict[str, Any]] = Field(..., description="Work experience history")
    education: List[Dict[str, Any]] = Field(..., description="Educational background")
    skills: List[str] = Field(..., description="Skills and competencies")
    certifications: Optional[List[Dict[str, Any]]] = Field(None, description="Professional certifications")
    languages: Optional[List[Dict[str, str]]] = Field(None, description="Languages and proficiency levels")
    references: Optional[List[Dict[str, str]]] = Field(None, description="Professional references")
    portfolio_url: Optional[str] = Field(None, description="URL to portfolio or professional website")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    additional_information: Optional[str] = Field(None, description="Additional relevant information")
    received_date: Optional[date] = Field(None, description="Date when the resume was received")
    position_applied_for: Optional[str] = Field(None, description="Position the candidate applied for")
    application_source: Optional[str] = Field(None, description="Source of the application (e.g., job board, referral)")

class JobApplication(HRDocument):
    """A formal application submitted by a candidate for a specific job position.
    This model captures the structured information from a job application form, including
    personal details, position applied for, work eligibility, and education and employment history.
    It provides a comprehensive view of a candidate's application for employment."""
    position_applied_for: str = Field(..., description="Job title being applied for")
    applicant_name: str = Field(..., description="Name of the applicant")
    contact_information: Dict[str, str] = Field(..., description="Contact information (email, phone, address)")
    application_date: date = Field(..., description="Date of application submission")
    resume_attached: Optional[bool] = Field(None, description="Whether a resume was attached")
    cover_letter_attached: Optional[bool] = Field(None, description="Whether a cover letter was attached")
    work_authorization: Optional[str] = Field(None, description="Work authorization status")
    education_history: List[Dict[str, Any]] = Field(..., description="Educational background")
    employment_history: List[Dict[str, Any]] = Field(..., description="Employment history")
    references: Optional[List[Dict[str, str]]] = Field(None, description="Professional references")
    criminal_history: Optional[str] = Field(None, description="Criminal history disclosure, if applicable")
    desired_salary: Optional[str] = Field(None, description="Desired salary or compensation")
    earliest_start_date: Optional[date] = Field(None, description="Earliest date the applicant can start")
    referral_source: Optional[str] = Field(None, description="How the applicant learned about the position")
    signature: Optional[bool] = Field(None, description="Whether the application was signed")
    equal_opportunity_information: Optional[Dict[str, Any]] = Field(None, description="Voluntary EEO information")
    application_status: Optional[str] = Field(None, description="Current status of the application")

class InterviewEvaluation(HRDocument):
    """A form used to assess a candidate's qualifications and fit during the interview process.
    This model captures the structured evaluation of a job candidate during an interview,
    including ratings across various competencies, strengths and weaknesses identified,
    and overall assessment and recommendations. It enables systematic comparison of
    candidates and supports data-driven hiring decisions."""
    candidate_name: str = Field(..., description="Name of the candidate")
    position: str = Field(..., description="Position being interviewed for")
    interviewer_name: str = Field(..., description="Name of the interviewer")
    interview_date: date = Field(..., description="Date of the interview")
    interview_type: str = Field(..., description="Type of interview (e.g., phone, in-person, panel)")
    competency_ratings: Dict[str, Any] = Field(..., description="Ratings for various competencies")
    technical_assessment: Optional[Dict[str, Any]] = Field(None, description="Assessment of technical skills")
    behavioral_assessment: Optional[Dict[str, Any]] = Field(None, description="Assessment of behavioral competencies")
    strengths: List[str] = Field(..., description="Identified strengths of the candidate")
    areas_of_concern: Optional[List[str]] = Field(None, description="Areas of concern or development")
    cultural_fit_assessment: Optional[str] = Field(None, description="Assessment of cultural fit")
    overall_rating: str = Field(..., description="Overall rating of the candidate")
    hiring_recommendation: str = Field(..., description="Recommendation regarding hiring")
    salary_recommendation: Optional[str] = Field(None, description="Recommended salary, if applicable")
    additional_comments: Optional[str] = Field(None, description="Additional comments or observations")
    next_steps: Optional[str] = Field(None, description="Recommended next steps in the process")

class OfferLetter(HRAgreement):
    """A formal letter extending an employment offer to a candidate.
    This model captures the details of an employment offer, including position, compensation,
    benefits, start date, and conditions of employment. It provides a structured representation
    of the terms offered to a potential employee."""
    candidate_name: str = Field(..., description="Name of the candidate receiving the offer")
    position_title: str = Field(..., description="Title of the position being offered")
    department: str = Field(..., description="Department the position belongs to")
    reporting_to: Optional[str] = Field(None, description="Position or person this role reports to")
    employment_type: EmploymentType = Field(..., description="Type of employment (full-time, part-time, etc.)")
    start_date: date = Field(..., description="Proposed start date")
    compensation: Dict[str, Any] = Field(..., description="Compensation details (salary, bonus, etc.)")
    benefits_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of benefits offered")
    work_location: str = Field(..., description="Primary work location")
    work_schedule: Optional[str] = Field(None, description="Expected work schedule")
    contingencies: Optional[List[str]] = Field(None, description="Contingencies for the offer (e.g., background check)")
    expiration_date: date = Field(..., description="Date by which the offer must be accepted")
    at_will_statement: Optional[str] = Field(None, description="At-will employment statement, if applicable")
    confidentiality_clause: Optional[str] = Field(None, description="Confidentiality requirements")
    non_compete_clause: Optional[str] = Field(None, description="Non-compete restrictions, if any")
    offer_accepted: Optional[bool] = Field(None, description="Whether the offer was accepted")
    acceptance_date: Optional[date] = Field(None, description="Date when the offer was accepted")
    authorized_by: str = Field(..., description="Person who authorized the offer")
    special_terms: Optional[str] = Field(None, description="Any special terms or conditions")

class BackgroundCheckConsent(HRDocument):
    """A form documenting a candidate's consent to undergo a background check.
    This model captures the details of a background check authorization, including
    the types of checks to be performed, the candidate's personal information,
    and their formal consent. It provides a structured record of the authorization
    process for compliance and audit purposes."""
    candidate_name: str = Field(..., description="Name of the candidate")
    candidate_information: Dict[str, Any] = Field(..., description="Personal information for the check")
    check_types: List[str] = Field(..., description="Types of checks to be performed")
    authorization_statement: str = Field(..., description="Statement of authorization")
    fair_credit_reporting_act_disclosure: Optional[str] = Field(None, description="FCRA disclosure")
    state_specific_disclosures: Optional[Dict[str, str]] = Field(None, description="State-specific disclosures")
    consent_signature: bool = Field(..., description="Whether the consent was signed")
    signature_date: date = Field(..., description="Date of signature")
    authorized_by: str = Field(..., description="Person who requested the background check")
    vendor_name: Optional[str] = Field(None, description="Name of the background check vendor")
    results_disclosure_authorization: Optional[bool] = Field(None, description="Authorization to disclose results")
    expiration_date: Optional[date] = Field(None, description="Expiration date of the authorization")
    purpose_of_check: str = Field(..., description="Purpose for conducting the background check")

# Onboarding & Employment Agreements

class OnboardingPacket(HRDocument):
    """A collection of documents and information provided to new employees during the onboarding process.
    This model captures the comprehensive set of materials provided to new employees,
    including orientation schedules, company policies, benefits enrollment forms,
    and required legal documentation. It provides a structured representation of
    the onboarding process and materials."""
    employee_name: str = Field(..., description="Name of the new employee")
    position_title: str = Field(..., description="Title of the position")
    start_date: date = Field(..., description="Employee's start date")
    orientation_schedule: Dict[str, Any] = Field(..., description="Schedule of orientation activities")
    required_forms: List[str] = Field(..., description="Required forms to be completed")
    company_policies: List[str] = Field(..., description="Company policies to be reviewed")
    benefits_enrollment_information: Optional[Dict[str, Any]] = Field(None, description="Benefits enrollment details")
    it_setup_information: Optional[Dict[str, Any]] = Field(None, description="IT setup and access information")
    first_week_schedule: Optional[Dict[str, Any]] = Field(None, description="Schedule for the first week")
    mentor_information: Optional[Dict[str, str]] = Field(None, description="Information about assigned mentor")
    department_specific_materials: Optional[List[str]] = Field(None, description="Department-specific materials")
    training_requirements: Optional[List[str]] = Field(None, description="Required training programs")
    probationary_period_details: Optional[str] = Field(None, description="Details about probationary period")
    welcome_message: Optional[str] = Field(None, description="Welcome message from management")
    company_overview: Optional[str] = Field(None, description="Overview of the company")
    organizational_chart: Optional[bool] = Field(None, description="Whether an organizational chart is included")
    contact_information: Optional[Dict[str, str]] = Field(None, description="Key contact information")

class ConfidentialityAgreement(HRAgreement):
    """A legal agreement requiring an employee to maintain confidentiality of proprietary information.
    This model captures the details of a confidentiality or non-disclosure agreement,
    including the types of information considered confidential, the duration of the
    obligation, and the consequences of breach. It provides a structured representation
    of the confidentiality requirements imposed on employees or contractors."""
    party_name: str = Field(..., description="Name of the employee or contractor")
    company_name: str = Field(..., description="Name of the company")
    effective_date: date = Field(..., description="Date when the agreement becomes effective")
    confidential_information_definition: str = Field(..., description="Definition of confidential information")
    excluded_information: Optional[List[str]] = Field(None, description="Information excluded from confidentiality")
    permitted_use: str = Field(..., description="Permitted use of confidential information")
    disclosure_restrictions: str = Field(..., description="Restrictions on disclosure")
    duration_of_obligation: str = Field(..., description="Duration of confidentiality obligation")
    return_of_materials: Optional[str] = Field(None, description="Requirements for returning materials")
    remedies_for_breach: Optional[str] = Field(None, description="Remedies available for breach")
    jurisdiction: Optional[str] = Field(None, description="Governing law jurisdiction")
    survival_clause: Optional[str] = Field(None, description="Survival of obligations after termination")
    signature_party: bool = Field(..., description="Whether signed by the party")
    signature_company: bool = Field(..., description="Whether signed by the company")
    signature_date: date = Field(..., description="Date of signature")
    witness_signature: Optional[bool] = Field(None, description="Whether witnessed by a third party")

class TaxForm(HRDocument):
    """A government-required tax form completed by employees for payroll and tax purposes.
    This model captures the details of employment-related tax forms such as W-4, I-9,
    or other tax documentation. It provides a structured representation of tax-related
    information collected from employees for compliance with tax regulations."""
    form_type: str = Field(..., description="Type of tax form (e.g., W-4, I-9)")
    form_version: str = Field(..., description="Version or year of the form")
    employee_name: str = Field(..., description="Name of the employee")
    employee_address: str = Field(..., description="Address of the employee")
    social_security_number: Optional[str] = Field(None, description="Social security number (masked or partial)")
    filing_status: Optional[str] = Field(None, description="Tax filing status")
    allowances_claimed: Optional[int] = Field(None, description="Number of allowances claimed (for W-4)")
    additional_withholding: Optional[float] = Field(None, description="Additional withholding amount")
    exempt_status_claimed: Optional[bool] = Field(None, description="Whether exempt status is claimed")
    employer_identification_number: Optional[str] = Field(None, description="Employer identification number")
    employment_eligibility_verification: Optional[Dict[str, Any]] = Field(None, description="I-9 employment eligibility information")
    certification_signature: bool = Field(..., description="Whether the certification was signed")
    signature_date: date = Field(..., description="Date of signature")
    employer_completion: Optional[Dict[str, Any]] = Field(None, description="Information completed by employer")
    submission_date: date = Field(..., description="Date the form was submitted")
    expiration_date: Optional[date] = Field(None, description="Expiration date of the form, if applicable")

# Employee Policies & Procedures

class EmployeeHandbook(HRDocument):
    """A comprehensive document outlining company policies, procedures, and expectations for employees.
    This model captures the structure and content of an employee handbook, including
    company policies, code of conduct, benefits information, and other important
    guidelines for employees. It provides a structured representation of the rules
    and expectations that govern the employment relationship."""
    company_name: str = Field(..., description="Name of the company")
    effective_date: date = Field(..., description="Date when the handbook becomes effective")
    version_number: str = Field(..., description="Version number of the handbook")
    welcome_message: Optional[str] = Field(None, description="Welcome message from leadership")
    company_history: Optional[str] = Field(None, description="Brief history of the company")
    mission_vision_values: Optional[Dict[str, str]] = Field(None, description="Mission, vision, and values statements")
    employment_policies: Dict[str, str] = Field(..., description="Employment policies and practices")
    code_of_conduct: str = Field(..., description="Code of conduct and ethical standards")
    anti_discrimination_policy: str = Field(..., description="Anti-discrimination and harassment policy")
    compensation_benefits: Dict[str, str] = Field(..., description="Compensation and benefits information")
    work_hours_attendance: Dict[str, str] = Field(..., description="Work hours and attendance policies")
    leave_policies: Dict[str, str] = Field(..., description="Leave and time-off policies")
    performance_expectations: Dict[str, str] = Field(..., description="Performance expectations and reviews")
    discipline_termination: Dict[str, str] = Field(..., description="Discipline and termination procedures")
    safety_security: Dict[str, str] = Field(..., description="Workplace safety and security policies")
    technology_use: Dict[str, str] = Field(..., description="Technology use and security policies")
    confidentiality_privacy: Dict[str, str] = Field(..., description="Confidentiality and privacy policies")
    acknowledgment_form: Optional[bool] = Field(None, description="Whether an acknowledgment form is included")
    at_will_statement: Optional[str] = Field(None, description="At-will employment statement, if applicable")
    amendments_process: Optional[str] = Field(None, description="Process for handbook amendments")
    table_of_contents: Optional[bool] = Field(None, description="Whether a table of contents is included")

class WorkplacePolicy(HRDocument):
    """A specific policy document addressing a particular aspect of workplace conduct or procedures.
    This model captures the details of individual workplace policies, such as
    anti-discrimination, safety, or technology use policies. It provides a structured
    representation of specific rules and guidelines that govern particular aspects
    of the employment relationship."""
    policy_title: str = Field(..., description="Title of the policy")
    policy_number: Optional[str] = Field(None, description="Policy reference number")
    effective_date: date = Field(..., description="Date when the policy becomes effective")
    revision_date: Optional[date] = Field(None, description="Date of last revision")
    version_number: Optional[str] = Field(None, description="Version number of the policy")
    purpose: str = Field(..., description="Purpose of the policy")
    scope: str = Field(..., description="Scope of the policy (who it applies to)")
    policy_statement: str = Field(..., description="Main policy statement")
    definitions: Optional[Dict[str, str]] = Field(None, description="Definitions of key terms")
    procedures: Optional[List[str]] = Field(None, description="Procedures for implementing the policy")
    responsibilities: Optional[Dict[str, List[str]]] = Field(None, description="Responsibilities of different parties")
    compliance_requirements: Optional[List[str]] = Field(None, description="Compliance requirements")
    consequences_of_violation: Optional[str] = Field(None, description="Consequences for policy violations")
    related_policies: Optional[List[str]] = Field(None, description="Related policies or documents")
    legal_references: Optional[List[str]] = Field(None, description="Relevant laws or regulations")
    exceptions_process: Optional[str] = Field(None, description="Process for requesting exceptions")
    review_cycle: Optional[str] = Field(None, description="Frequency of policy review")
    approved_by: str = Field(..., description="Person or body that approved the policy")
    contact_information: Optional[str] = Field(None, description="Contact for policy questions")

class CodeOfConduct(WorkplacePolicy):
    """A document outlining the ethical standards and expected behaviors for employees.
    This model captures the comprehensive ethical guidelines and behavioral expectations
    set forth by an organization, including core values, ethical principles, and specific
    conduct requirements. It provides a structured representation of the standards that
    employees are expected to uphold in their professional activities."""
    company_values: List[str] = Field(..., description="Core company values")
    ethical_principles: List[str] = Field(..., description="Guiding ethical principles")
    expected_behaviors: Dict[str, List[str]] = Field(..., description="Expected behaviors in different contexts")
    prohibited_behaviors: List[str] = Field(..., description="Explicitly prohibited behaviors")
    conflicts_of_interest: str = Field(..., description="Conflict of interest guidelines")
    gifts_entertainment: Optional[str] = Field(None, description="Guidelines on gifts and entertainment")
    confidential_information: str = Field(..., description="Handling of confidential information")
    company_resources: Optional[str] = Field(None, description="Use of company resources")
    reporting_violations: str = Field(..., description="Process for reporting violations")
    non_retaliation: str = Field(..., description="Non-retaliation policy")
    investigation_process: Optional[str] = Field(None, description="Process for investigating reported violations")
    disciplinary_actions: str = Field(..., description="Potential disciplinary actions")
    acknowledgment_required: bool = Field(..., description="Whether acknowledgment is required")
    training_requirements: Optional[str] = Field(None, description="Training requirements related to the code")
    ethics_resources: Optional[List[str]] = Field(None, description="Resources for ethical guidance")
    annual_certification: Optional[bool] = Field(None, description="Whether annual certification is required")

# Performance & Development

class PerformanceAppraisal(HRDocument):
    """A formal assessment of an employee's job performance over a specific period.
    This model captures the comprehensive evaluation of an employee's performance,
    including achievements, areas for improvement, goal attainment, and development plans.
    It provides a structured representation of performance feedback and assessment
    for employee development and performance management."""
    employee_name: str = Field(..., description="Name of the employee")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    position_title: str = Field(..., description="Title of the position")
    department: str = Field(..., description="Department")
    manager_name: str = Field(..., description="Name of the evaluating manager")
    review_period: str = Field(..., description="Period covered by the review")
    review_date: date = Field(..., description="Date of the review")
    performance_goals: List[Dict[str, Any]] = Field(..., description="Performance goals and achievements")
    competency_ratings: Dict[str, Any] = Field(..., description="Ratings for various competencies")
    strengths: List[str] = Field(..., description="Identified strengths")
    areas_for_improvement: List[str] = Field(..., description="Areas needing improvement")
    overall_rating: PerformanceRating = Field(..., description="Overall performance rating")
    manager_comments: str = Field(..., description="Comments from the manager")
    employee_comments: Optional[str] = Field(None, description="Comments from the employee")
    development_plan: Optional[Dict[str, Any]] = Field(None, description="Development plan")
    goals_for_next_period: Optional[List[Dict[str, Any]]] = Field(None, description="Goals for the next period")
    employee_signature: Optional[bool] = Field(None, description="Whether signed by the employee")
    manager_signature: bool = Field(..., description="Whether signed by the manager")
    hr_signature: Optional[bool] = Field(None, description="Whether signed by HR")
    signature_date: date = Field(..., description="Date of signature")
    next_review_date: Optional[date] = Field(None, description="Date of next scheduled review")

class PerformanceImprovementPlan(HRDocument):
    """A formal plan to address performance deficiencies and help an employee improve.
    This model captures the structured approach to addressing performance issues,
    including specific areas of concern, improvement goals, support resources,
    and evaluation criteria. It provides a comprehensive framework for guiding
    and monitoring an employee's performance improvement efforts."""
    employee_name: str = Field(..., description="Name of the employee")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    position_title: str = Field(..., description="Title of the position")
    department: str = Field(..., description="Department")
    manager_name: str = Field(..., description="Name of the manager")
    plan_start_date: date = Field(..., description="Start date of the plan")
    plan_end_date: date = Field(..., description="End date of the plan")
    performance_concerns: List[str] = Field(..., description="Specific performance concerns")
    expected_standards: List[str] = Field(..., description="Expected performance standards")
    improvement_goals: List[Dict[str, Any]] = Field(..., description="Specific improvement goals")
    action_steps: List[Dict[str, Any]] = Field(..., description="Action steps to achieve goals")
    resources_support: List[str] = Field(..., description="Resources and support provided")
    progress_review_schedule: List[date] = Field(..., description="Schedule for progress reviews")
    success_measures: List[str] = Field(..., description="Measures of successful improvement")
    consequences: str = Field(..., description="Consequences if improvement goals are not met")
    employee_input: Optional[str] = Field(None, description="Input from the employee")
    manager_comments: str = Field(..., description="Comments from the manager")
    hr_comments: Optional[str] = Field(None, description="Comments from HR")
    employee_signature: bool = Field(..., description="Whether signed by the employee")
    manager_signature: bool = Field(..., description="Whether signed by the manager")
    hr_signature: Optional[bool] = Field(None, description="Whether signed by HR")
    signature_date: date = Field(..., description="Date of signature")
    progress_notes: Optional[List[Dict[str, Any]]] = Field(None, description="Notes from progress reviews")
    final_outcome: Optional[str] = Field(None, description="Final outcome of the plan")

class TrainingDevelopmentPlan(HRDocument):
    """A structured plan for an employee's professional development and skill enhancement.
    This model captures the comprehensive approach to employee development,
    including skill gaps, learning objectives, training activities, and progress measures.
    It provides a structured framework for guiding and tracking an employee's
    professional growth and skill acquisition."""
    employee_name: str = Field(..., description="Name of the employee")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    position_title: str = Field(..., description="Title of the position")
    department: str = Field(..., description="Department")
    manager_name: str = Field(..., description="Name of the manager")
    plan_period: str = Field(..., description="Period covered by the plan")
    career_goals: Optional[List[str]] = Field(None, description="Employee's career goals")
    current_skills_assessment: Dict[str, Any] = Field(..., description="Assessment of current skills")
    skill_gaps: List[str] = Field(..., description="Identified skill gaps")
    development_objectives: List[Dict[str, Any]] = Field(..., description="Development objectives")
    training_activities: List[Dict[str, Any]] = Field(..., description="Planned training activities")
    resources_required: Optional[List[Dict[str, Any]]] = Field(None, description="Resources required")
    timeline: Dict[str, Any] = Field(..., description="Timeline for activities")
    success_measures: List[str] = Field(..., description="Measures of successful development")
    budget_allocation: Optional[float] = Field(None, description="Budget allocated for development")
    employee_responsibilities: List[str] = Field(..., description="Employee's responsibilities")
    manager_responsibilities: List[str] = Field(..., description="Manager's responsibilities")
    progress_review_schedule: Optional[List[date]] = Field(None, description="Schedule for progress reviews")
    employee_signature: Optional[bool] = Field(None, description="Whether signed by the employee")
    manager_signature: Optional[bool] = Field(None, description="Whether signed by the manager")
    signature_date: Optional[date] = Field(None, description="Date of signature")
    progress_notes: Optional[List[Dict[str, Any]]] = Field(None, description="Notes from progress reviews")
    completion_status: Optional[Dict[str, str]] = Field(None, description="Completion status of activities")

# Compensation & Benefits

class CompensationStructure(HRDocument):
    """A document outlining the organization's compensation framework, including salary ranges and pay grades.
    This model captures the comprehensive compensation framework of an organization,
    including pay grades, salary ranges, bonus structures, and equity components.
    It provides a structured representation of how compensation is determined
    and administered across different roles and levels."""
    effective_date: date = Field(..., description="Date when the structure becomes effective")
    revision_date: Optional[date] = Field(None, description="Date of last revision")
    approved_by: str = Field(..., description="Person or body that approved the structure")
    pay_philosophy: Optional[str] = Field(None, description="Company's compensation philosophy")
    market_positioning: Optional[str] = Field(None, description="Market positioning strategy")
    pay_grades: List[Dict[str, Any]] = Field(..., description="Pay grades and levels")
    salary_ranges: Dict[str, Dict[str, float]] = Field(..., description="Salary ranges by grade/position")
    bonus_structure: Optional[Dict[str, Any]] = Field(None, description="Bonus or incentive structure")
    equity_compensation: Optional[Dict[str, Any]] = Field(None, description="Equity compensation structure")
    allowances: Optional[Dict[str, Any]] = Field(None, description="Additional allowances")
    geographic_differentials: Optional[Dict[str, float]] = Field(None, description="Geographic pay differentials")
    promotion_guidelines: Optional[Dict[str, Any]] = Field(None, description="Guidelines for promotional increases")
    merit_increase_guidelines: Optional[Dict[str, Any]] = Field(None, description="Guidelines for merit increases")
    review_cycle: str = Field(..., description="Frequency of compensation review")
    special_compensation: Optional[Dict[str, Any]] = Field(None, description="Special compensation arrangements")
    governance_process: Optional[str] = Field(None, description="Process for governance and exceptions")
    benchmarking_methodology: Optional[str] = Field(None, description="Methodology for market benchmarking")
    confidentiality_statement: Optional[str] = Field(None, description="Statement on compensation confidentiality")

class BenefitsGuide(HRDocument):
    """A comprehensive document describing the employee benefits offered by the organization.
    This model captures the detailed information about an organization's benefits offerings,
    including health insurance, retirement plans, paid time off, and other employee benefits.
    It provides a structured representation of the complete benefits package available to employees."""
    effective_date: date = Field(..., description="Date when the benefits become effective")
    plan_year: str = Field(..., description="Benefits plan year")
    revision_date: Optional[date] = Field(None, description="Date of last revision")
    health_insurance: Dict[str, Any] = Field(..., description="Health insurance plans")
    dental_insurance: Optional[Dict[str, Any]] = Field(None, description="Dental insurance plans")
    vision_insurance: Optional[Dict[str, Any]] = Field(None, description="Vision insurance plans")
    life_insurance: Optional[Dict[str, Any]] = Field(None, description="Life insurance benefits")
    disability_insurance: Optional[Dict[str, Any]] = Field(None, description="Disability insurance benefits")
    retirement_plans: Dict[str, Any] = Field(..., description="Retirement plan options")
    paid_time_off: Dict[str, Any] = Field(..., description="Paid time off benefits")
    family_leave: Optional[Dict[str, Any]] = Field(None, description="Family and medical leave benefits")
    wellness_programs: Optional[Dict[str, Any]] = Field(None, description="Wellness program benefits")
    employee_assistance: Optional[Dict[str, Any]] = Field(None, description="Employee assistance program")
    tuition_assistance: Optional[Dict[str, Any]] = Field(None, description="Tuition assistance benefits")
    flexible_spending: Optional[Dict[str, Any]] = Field(None, description="Flexible spending accounts")
    health_savings: Optional[Dict[str, Any]] = Field(None, description="Health savings accounts")
    commuter_benefits: Optional[Dict[str, Any]] = Field(None, description="Commuter benefits")
    additional_benefits: Optional[Dict[str, Any]] = Field(None, description="Additional or unique benefits")
    eligibility_requirements: Dict[str, Any] = Field(..., description="Eligibility requirements by benefit")
    enrollment_procedures: Dict[str, Any] = Field(..., description="Procedures for enrollment")
    costs_contributions: Dict[str, Any] = Field(..., description="Costs and employee contributions")
    important_contacts: Dict[str, str] = Field(..., description="Contact information for benefits")
    legal_notices: Optional[List[str]] = Field(None, description="Required legal notices")

class BenefitsEnrollmentForm(HRDocument):
    """A form used by employees to select and enroll in available benefit plans.
    This model captures the detailed information collected during the benefits
    enrollment process, including employee information, selected plans, coverage levels,
    and dependent information. It provides a structured representation of an employee's
    benefits elections and enrollment decisions."""
    employee_name: str = Field(..., description="Name of the employee")
    employee_id: str = Field(..., description="Employee ID")
    enrollment_period: str = Field(..., description="Enrollment period (e.g., Open Enrollment, New Hire)")
    effective_date: date = Field(..., description="Date when benefits become effective")
    enrollment_type: str = Field(..., description="Type of enrollment (New, Change, Termination)")
    qualifying_life_event: Optional[str] = Field(None, description="Qualifying life event, if applicable")
    event_date: Optional[date] = Field(None, description="Date of qualifying event, if applicable")
    medical_plan_selection: Optional[Dict[str, Any]] = Field(None, description="Medical plan selection")
    dental_plan_selection: Optional[Dict[str, Any]] = Field(None, description="Dental plan selection")
    vision_plan_selection: Optional[Dict[str, Any]] = Field(None, description="Vision plan selection")
    life_insurance_selection: Optional[Dict[str, Any]] = Field(None, description="Life insurance selection")
    disability_insurance_selection: Optional[Dict[str, Any]] = Field(None, description="Disability insurance selection")
    retirement_plan_selection: Optional[Dict[str, Any]] = Field(None, description="Retirement plan selection")
    fsa_hsa_selection: Optional[Dict[str, Any]] = Field(None, description="FSA/HSA selections")
    additional_benefits_selection: Optional[Dict[str, Any]] = Field(None, description="Additional benefits selected")
    dependents_information: Optional[List[Dict[str, Any]]] = Field(None, description="Information about dependents")
    beneficiary_designations: Optional[List[Dict[str, Any]]] = Field(None, description="Beneficiary designations")
    waived_benefits: Optional[List[str]] = Field(None, description="Benefits waived by the employee")
    employee_contributions: Dict[str, float] = Field(..., description="Employee contribution amounts")
    authorization_signature: bool = Field(..., description="Whether authorization was signed")
    signature_date: date = Field(..., description="Date of signature")
    received_by: Optional[str] = Field(None, description="Person who received the form")
    processing_date: Optional[date] = Field(None, description="Date the form was processed")

# Separation & Offboarding

class TerminationLetter(HRDocument):
    """A formal letter documenting the termination of employment.
    This model captures the details of an employment termination notification,
    including the termination date, reason, final pay information, and benefits continuation.
    It provides a structured representation of the formal communication regarding
    the end of the employment relationship."""
    employee_name: str = Field(..., description="Name of the employee")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    position_title: str = Field(..., description="Title of the position")
    department: str = Field(..., description="Department")
    termination_date: date = Field(..., description="Date of termination")
    last_working_day: Optional[date] = Field(None, description="Last day of work, if different")
    termination_type: TerminationType = Field(..., description="Type of termination")
    termination_reason: str = Field(..., description="Reason for termination")
    notice_period: Optional[str] = Field(None, description="Notice period given")
    final_pay_information: Dict[str, Any] = Field(..., description="Information about final pay")
    benefits_continuation: Optional[Dict[str, Any]] = Field(None, description="Information about benefits continuation")
    cobra_information: Optional[Dict[str, Any]] = Field(None, description="COBRA information, if applicable")
    company_property_return: Optional[List[str]] = Field(None, description="Company property to be returned")
    non_compete_reminder: Optional[str] = Field(None, description="Reminder of non-compete obligations")
    confidentiality_reminder: Optional[str] = Field(None, description="Reminder of confidentiality obligations")
    reference_policy: Optional[str] = Field(None, description="Policy regarding references")
    outplacement_services: Optional[Dict[str, Any]] = Field(None, description="Outplacement services offered")
    appeal_process: Optional[str] = Field(None, description="Process for appealing the termination")
    authorized_by: str = Field(..., description="Person who authorized the termination")
    delivered_by: str = Field(..., description="Person who delivered the termination notice")
    delivery_method: str = Field(..., description="Method of delivery (in-person, mail, etc.)")
    delivery_date: date = Field(..., description="Date the notice was delivered")
    acknowledgment_signature: Optional[bool] = Field(None, description="Whether acknowledgment was signed")

class SeveranceAgreement(HRAgreement):
    """A legal agreement outlining the terms of separation and any severance benefits.
    This model captures the comprehensive terms of a severance agreement,
    including financial compensation, benefits continuation, release of claims,
    and ongoing obligations. It provides a structured representation of the
    negotiated terms for an employee's separation from the organization."""
    employee_name: str = Field(..., description="Name of the employee")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    position_title: str = Field(..., description="Title of the position")
    department: str = Field(..., description="Department")
    separation_date: date = Field(..., description="Date of separation")
    agreement_date: date = Field(..., description="Date of the agreement")
    severance_payment: Dict[str, Any] = Field(..., description="Details of severance payment")
    payment_schedule: str = Field(..., description="Schedule for severance payments")
    benefits_continuation: Optional[Dict[str, Any]] = Field(None, description="Details of benefits continuation")
    cobra_subsidy: Optional[Dict[str, Any]] = Field(None, description="COBRA subsidy details, if applicable")
    outplacement_services: Optional[Dict[str, Any]] = Field(None, description="Outplacement services provided")
    reference_provision: Optional[str] = Field(None, description="Provisions regarding references")
    release_of_claims: str = Field(..., description="Release of claims provision")
    non_disparagement: Optional[str] = Field(None, description="Non-disparagement clause")
    confidentiality_provision: Optional[str] = Field(None, description="Confidentiality provisions")
    non_compete_provision: Optional[str] = Field(None, description="Non-compete provisions")
    non_solicitation_provision: Optional[str] = Field(None, description="Non-solicitation provisions")
    return_of_property: str = Field(..., description="Provisions for return of company property")
    cooperation_provision: Optional[str] = Field(None, description="Provisions for future cooperation")
    revocation_period: Optional[int] = Field(None, description="Revocation period in days, if applicable")
    consideration_period: Optional[int] = Field(None, description="Consideration period in days")
    governing_law: str = Field(..., description="Governing law jurisdiction")
    entire_agreement_clause: bool = Field(..., description="Whether entire agreement clause is included")
    employee_signature: bool = Field(..., description="Whether signed by the employee")
    company_signature: bool = Field(..., description="Whether signed by the company")
    signature_date: date = Field(..., description="Date of signature")

class ExitInterviewForm(HRDocument):
    """A form used to gather feedback from departing employees about their experience.
    This model captures the structured feedback collected during an exit interview,
    including reasons for leaving, job satisfaction factors, and suggestions for improvement.
    It provides valuable insights into employee experience and potential areas for
    organizational enhancement."""
    employee_name: str = Field(..., description="Name of the employee")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    position_title: str = Field(..., description="Title of the position")
    department: str = Field(..., description="Department")
    hire_date: date = Field(..., description="Date of hire")
    separation_date: date = Field(..., description="Date of separation")
    length_of_service: str = Field(..., description="Length of service")
    interviewer_name: str = Field(..., description="Name of the interviewer")
    interview_date: date = Field(..., description="Date of the exit interview")
    primary_reason_for_leaving: str = Field(..., description="Primary reason for leaving")
    secondary_reasons: Optional[List[str]] = Field(None, description="Secondary reasons for leaving")
    new_position_information: Optional[Dict[str, Any]] = Field(None, description="Information about new position, if applicable")
    job_satisfaction_ratings: Dict[str, Any] = Field(..., description="Ratings for various job satisfaction factors")
    supervisor_feedback: Dict[str, Any] = Field(..., description="Feedback about supervisor")
    company_culture_feedback: Dict[str, Any] = Field(..., description="Feedback about company culture")
    compensation_benefits_feedback: Dict[str, Any] = Field(..., description="Feedback about compensation and benefits")
    training_development_feedback: Dict[str, Any] = Field(..., description="Feedback about training and development")
    what_went_well: List[str] = Field(..., description="Aspects that went well")
    what_could_improve: List[str] = Field(..., description="Aspects that could improve")
    would_recommend_company: bool = Field(..., description="Whether would recommend company to others")
    would_consider_returning: bool = Field(..., description="Whether would consider returning in the future")
    additional_comments: Optional[str] = Field(None, description="Additional comments or feedback")
    interviewer_observations: Optional[str] = Field(None, description="Observations from the interviewer")
    follow_up_actions: Optional[List[str]] = Field(None, description="Recommended follow-up actions")
    confidentiality_statement: bool = Field(..., description="Whether confidentiality statement is included")

# Miscellaneous Compliance & Records

class EmployeeRecord(HRDocument):
    """A comprehensive file containing an employee's personal and employment information.
    This model captures the complete record of an employee's information,
    including personal details, employment history, compensation, benefits,
    performance, and other relevant documentation. It provides a structured
    representation of the employee's complete history with the organization."""
    employee_name: str = Field(..., description="Name of the employee")
    employee_id: str = Field(..., description="Employee ID")
    personal_information: Dict[str, Any] = Field(..., description="Personal information")
    contact_information: Dict[str, str] = Field(..., description="Contact information")
    emergency_contacts: List[Dict[str, str]] = Field(..., description="Emergency contacts")
    employment_information: Dict[str, Any] = Field(..., description="Employment information")
    position_history: List[Dict[str, Any]] = Field(..., description="History of positions held")
    compensation_history: List[Dict[str, Any]] = Field(..., description="History of compensation")
    benefits_enrollment: Dict[str, Any] = Field(..., description="Benefits enrollment information")
    performance_history: Optional[List[Dict[str, Any]]] = Field(None, description="Performance review history")
    training_certifications: Optional[List[Dict[str, Any]]] = Field(None, description="Training and certifications")
    disciplinary_actions: Optional[List[Dict[str, Any]]] = Field(None, description="Disciplinary actions, if any")
    awards_recognition: Optional[List[Dict[str, Any]]] = Field(None, description="Awards and recognition")
    education_verification: Optional[Dict[str, Any]] = Field(None, description="Education verification")
    employment_verification: Optional[Dict[str, Any]] = Field(None, description="Employment verification")
    background_check_results: Optional[Dict[str, Any]] = Field(None, description="Background check results")
    i9_documentation: Dict[str, Any] = Field(..., description="I-9 documentation")
    tax_withholding_information: Dict[str, Any] = Field(..., description="Tax withholding information")
    acknowledgments_signed: List[Dict[str, Any]] = Field(..., description="Policies and documents acknowledged")
    separation_information: Optional[Dict[str, Any]] = Field(None, description="Separation information, if applicable")
    record_access_log: Optional[List[Dict[str, Any]]] = Field(None, description="Log of access to the record")
    last_updated_date: date = Field(..., description="Date the record was last updated")
    last_updated_by: str = Field(..., description="Person who last updated the record")

class GrievanceForm(HRDocument):
    """A form used by employees to formally report workplace concerns or complaints.
    This model captures the detailed information about a workplace grievance,
    including the nature of the complaint, parties involved, desired resolution,
    and the processing of the grievance. It provides a structured representation
    of employee concerns and the organization's response process."""
    employee_name: str = Field(..., description="Name of the employee filing the grievance")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    position_title: str = Field(..., description="Title of the position")
    department: str = Field(..., description="Department")
    submission_date: date = Field(..., description="Date the grievance was submitted")
    grievance_type: str = Field(..., description="Type of grievance")
    grievance_description: str = Field(..., description="Detailed description of the grievance")
    parties_involved: List[str] = Field(..., description="Parties involved in the grievance")
    date_of_incident: Optional[date] = Field(None, description="Date of the incident, if applicable")
    prior_actions_taken: Optional[str] = Field(None, description="Actions taken prior to filing")
    desired_resolution: str = Field(..., description="Desired resolution or remedy")
    witnesses: Optional[List[str]] = Field(None, description="Witnesses to the incident or issue")
    supporting_documentation: Optional[List[str]] = Field(None, description="Supporting documentation attached")
    confidentiality_requested: Optional[bool] = Field(None, description="Whether confidentiality was requested")
    employee_signature: bool = Field(..., description="Whether signed by the employee")
    signature_date: date = Field(..., description="Date of signature")
    received_by: str = Field(..., description="Person who received the grievance")
    receipt_date: date = Field(..., description="Date the grievance was received")
    investigation_assigned_to: Optional[str] = Field(None, description="Person assigned to investigate")
    investigation_start_date: Optional[date] = Field(None, description="Date investigation started")
    investigation_end_date: Optional[date] = Field(None, description="Date investigation concluded")
    findings_summary: Optional[str] = Field(None, description="Summary of investigation findings")
    resolution_actions: Optional[List[str]] = Field(None, description="Actions taken to resolve the grievance")
    resolution_date: Optional[date] = Field(None, description="Date the grievance was resolved")
    follow_up_required: Optional[bool] = Field(None, description="Whether follow-up is required")
    follow_up_date: Optional[date] = Field(None, description="Date for follow-up, if required")
    case_closed_date: Optional[date] = Field(None, description="Date the case was closed")

class StockOptionAgreement(HRAgreement):
    """A legal agreement granting an employee the right to purchase company stock at a specified price within a defined timeframe.
    This model captures the comprehensive details of a stock option grant, including the number of shares,
    exercise price, vesting schedule, and expiration terms. It provides a structured representation of
    equity compensation arrangements, enabling analysis of vesting conditions, exercise provisions,
    and tax implications for both incentive and non-qualified stock options."""
    grant_date: date = Field(..., description="Date when the stock options were granted")
    option_type: str = Field(..., description="Type of stock option (e.g., ISO, NSO, RSU)")
    number_of_shares: int = Field(..., description="Total number of shares subject to the option")
    exercise_price: float = Field(..., description="Price per share at which the option can be exercised")
    currency: str = Field(..., description="Currency of the exercise price (e.g., USD, CAD)")
    fair_market_value_at_grant: Optional[float] = Field(None, description="Fair market value per share at grant date")
    vesting_commencement_date: date = Field(..., description="Date when the vesting period begins")
    vesting_schedule_type: VestingScheduleType = Field(..., description="Type of vesting schedule")
    vesting_period_years: float = Field(..., description="Total vesting period in years")
    cliff_period_months: Optional[int] = Field(None, description="Cliff vesting period in months, if applicable")
    vesting_frequency: str = Field(..., description="Frequency of vesting (e.g., monthly, quarterly, annually)")
    expiration_date: date = Field(..., description="Date when the option expires")
    post_termination_exercise_period_days: int = Field(..., description="Days to exercise after employment termination")
    accelerated_vesting_provisions: Optional[str] = Field(None, description="Provisions for accelerated vesting")
    transferability_restrictions: str = Field(..., description="Restrictions on transferring the options")
    stockholder_rights: Optional[str] = Field(None, description="Rights as a stockholder before exercise")
    tax_implications_summary: Optional[str] = Field(None, description="Summary of tax implications")
    governing_plan: str = Field(..., description="Stock plan governing the option grant")
    plan_administrator: str = Field(..., description="Administrator of the stock plan")
    amendment_provisions: Optional[str] = Field(None, description="Provisions for amending the agreement")
    special_terms: Optional[str] = Field(None, description="Any special or non-standard terms")
    company_signature: bool = Field(..., description="Whether signed by company representative")
    employee_signature: bool = Field(..., description="Whether signed by the employee")
    signature_date: date = Field(..., description="Date of signature")
    
    model_config = ConfigDict(
        title="Stock Option Agreement",
        description="Agreement granting employee rights to purchase company stock"
    )

class ComplianceDocument(HRDocument):
    """A document related to workplace compliance with laws, regulations, or internal policies.
    This model captures the details of compliance-related documentation,
    including the applicable regulations, compliance requirements, and verification
    of compliance activities. It provides a structured representation of the
    organization's compliance efforts and documentation."""
    document_title: str = Field(..., description="Title of the compliance document")
    compliance_area: str = Field(..., description="Area of compliance (e.g., Safety, EEO, Privacy)")
    applicable_regulations: List[str] = Field(..., description="Applicable laws or regulations")
    compliance_requirements: List[str] = Field(..., description="Specific compliance requirements")
    effective_date: date = Field(..., description="Date when requirements become effective")
    compliance_deadline: Optional[date] = Field(None, description="Deadline for compliance, if applicable")
    responsible_parties: List[str] = Field(..., description="Parties responsible for compliance")
    compliance_activities: List[Dict[str, Any]] = Field(..., description="Activities undertaken for compliance")
    verification_methods: List[str] = Field(..., description="Methods for verifying compliance")
    documentation_requirements: List[str] = Field(..., description="Required documentation")
    reporting_requirements: Optional[Dict[str, Any]] = Field(None, description="Reporting requirements")
    audit_schedule: Optional[str] = Field(None, description="Schedule for compliance audits")
    last_audit_date: Optional[date] = Field(None, description="Date of last compliance audit")
    audit_findings: Optional[List[Dict[str, Any]]] = Field(None, description="Findings from last audit")
    corrective_actions: Optional[List[Dict[str, Any]]] = Field(None, description="Corrective actions taken")
    compliance_status: str = Field(..., description="Current compliance status")
    next_review_date: date = Field(..., description="Date for next compliance review")
    prepared_by: str = Field(..., description="Person who prepared the document")
    approved_by: str = Field(..., description="Person who approved the document")
    approval_date: date = Field(..., description="Date of approval")
    distribution_list: List[str] = Field(..., description="List of document recipients")
