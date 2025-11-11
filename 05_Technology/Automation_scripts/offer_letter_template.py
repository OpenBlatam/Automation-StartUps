#!/usr/bin/env python3
"""
Simple Offer Letter Template Generator
Generates offer letters from simple prompts with placeholders.
"""

import re
from datetime import datetime
from typing import Dict, Optional


def extract_placeholders(text: str) -> Dict[str, str]:
    """
    Extract placeholders from template text.
    Example: "{position title}" -> "position title"
    """
    placeholders = {}
    pattern = r'\{([^}]+)\}'
    matches = re.findall(pattern, text)
    
    for match in matches:
        key = match.strip().lower().replace(' ', '_')
        placeholders[key] = match.strip()
    
    return placeholders


def generate_from_prompt(prompt: str, values: Optional[Dict[str, str]] = None) -> str:
    """
    Generate offer letter from a prompt template.
    
    Args:
        prompt: The prompt text with placeholders like {position title}
        values: Dictionary of values to replace placeholders
    
    Returns:
        Generated offer letter
    """
    if values is None:
        values = {}
    
    # Extract placeholders from prompt
    placeholders = extract_placeholders(prompt)
    
    # Default template
    template = """
{'='*70}
OFFER OF EMPLOYMENT
{'='*70}

Date: {current_date}

[Candidate Name]
[Address]

Dear [Candidate First Name],

CONFIDENTIAL OFFER OF EMPLOYMENT

We are delighted to extend an offer for the position of {position_title} at {company_name}. 
After careful consideration of your impressive background and the value you would bring to 
our team, we believe you are the ideal candidate for this role.

POSITION DETAILS
----------------
• Position Title: {position_title}
• Start Date: {start_date}
• Work Location: {location}
• Employment Type: Full-time

COMPENSATION PACKAGE
--------------------
• Base Salary: {salary_amount} per year
• Pay Frequency: Bi-weekly

COMPREHENSIVE BENEFITS PACKAGE
-------------------------------
{benefits_list}

{company_overview_section}

TERMS AND CONDITIONS
--------------------
• This offer is valid for 7 days from the date of this letter
• Employment is at-will, meaning either party may terminate the employment 
  relationship at any time, with or without cause or notice
• Background check and reference verification are required
• You will be required to sign our standard employment agreement and 
  confidentiality agreement

NEXT STEPS
----------
Please indicate your acceptance of this offer by:
1. Signing and returning this letter within 7 days
2. Completing the pre-employment requirements
3. Confirming your start date availability

We are excited about the possibility of you joining our team and contributing 
to our continued success.

Sincerely,

[HR Manager Name]
[HR Manager Title]
{company_name}
Phone: [Phone Number]
Email: [Email Address]

{'='*70}

ACCEPTANCE SECTION
------------------
I, [Candidate Name], accept the terms of this offer of employment.

Signature: _________________ Date: _________

Print Name: _________________

{'='*70}
"""
    
    # Get values from prompt or use provided values
    position_title = values.get('position_title') or placeholders.get('position_title', '[Position Title]')
    salary_amount = values.get('salary_amount') or placeholders.get('salary_amount', '[Salary Amount]')
    start_date = values.get('start_date') or placeholders.get('start_date', '[Start Date]')
    location = values.get('location') or placeholders.get('location', '[Location]')
    company_name = values.get('company_name', '[Company Name]')
    
    # Handle benefits
    benefits_text = values.get('benefits') or placeholders.get('list_of_benefits', '')
    if isinstance(benefits_text, list):
        benefits_list = '\n'.join([f"• {b.strip()}" for b in benefits_text if b.strip()])
    else:
        # Try to parse comma-separated or newline-separated
        benefits = [b.strip() for b in benefits_text.replace('\n', ',').split(',') if b.strip()]
        benefits_list = '\n'.join([f"• {b.strip()}" for b in benefits])
    
    # Company overview
    company_details = values.get('company_details') or placeholders.get('company_details', '')
    if company_details:
        company_overview_section = f"""
COMPANY OVERVIEW
----------------
{company_details}

"""
    else:
        company_overview_section = ""
    
    # Format date
    try:
        formatted_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')
    except:
        try:
            formatted_date = datetime.strptime(start_date, '%m/%d/%Y').strftime('%B %d, %Y')
        except:
            formatted_date = start_date
    
    # Format salary
    try:
        clean_salary = salary_amount.replace('$', '').replace(',', '').strip()
        formatted_salary = f"${float(clean_salary):,.2f}"
    except:
        formatted_salary = salary_amount
    
    # Generate letter
    current_date = datetime.now().strftime('%B %d, %Y')
    
    letter = template.format(
        current_date=current_date,
        position_title=position_title,
        company_name=company_name,
        start_date=formatted_date,
        location=location,
        salary_amount=formatted_salary,
        benefits_list=benefits_list,
        company_overview_section=company_overview_section
    )
    
    return letter


def main():
    """Example usage."""
    # Example prompt 1
    prompt1 = """Kindly generate an offer letter for a {position title} position, 
offering a {salary amount} salary and commencing on {start date}. 
The package encompasses a range of {list of benefits}. 
The designated work site is {location}. 
Additionally, provide a concise overview of the company, highlighting its {company details}."""
    
    values1 = {
        'position_title': 'Senior Software Engineer',
        'salary_amount': '140000',
        'start_date': '2024-03-15',
        'benefits': ['Health insurance', 'Dental coverage', '401k matching', 'Unlimited PTO'],
        'location': 'San Francisco, CA',
        'company_details': 'TechCorp is a leading technology company focused on innovation and excellence.'
    }
    
    letter1 = generate_from_prompt(prompt1, values1)
    print("Example 1:")
    print(letter1)
    print("\n" + "="*70 + "\n")
    
    # Example prompt 2 (without company details)
    prompt2 = """Kindly generate an offer letter for the {position title} position, 
offering a {salary amount} salary and commencing on {start date}. 
The package encompasses a range of {list of benefits}. 
The designated work site is {location}. 
Additionally, provide a concise overview of the company."""
    
    values2 = {
        'position_title': 'Marketing Manager',
        'salary_amount': '95000',
        'start_date': '2024-02-20',
        'benefits': ['Premium health insurance', 'Dental and vision coverage', '401k with 4% matching', '20 days PTO'],
        'location': 'New York, NY'
    }
    
    letter2 = generate_from_prompt(prompt2, values2)
    print("Example 2:")
    print(letter2)


if __name__ == '__main__':
    main()




