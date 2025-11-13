#!/usr/bin/env python3
"""
Funcionalidades Avanzadas para el Sistema de Cartas de Oferta
Incluye: generación HTML, modo batch, bonos, equity, validación avanzada
"""

import json
import csv
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os


def generate_html_offer_letter(
    position_title: str,
    salary_amount: str,
    start_date: str,
    benefits: List[str],
    location: str,
    company_name: str = "[Company Name]",
    company_details: Optional[str] = None,
    candidate_name: str = "[Candidate Name]",
    department: Optional[str] = None,
    manager_name: Optional[str] = None,
    manager_title: Optional[str] = None,
    employment_type: str = "Full-time",
    pay_frequency: str = "Bi-weekly",
    offer_validity_days: int = 7,
    hr_name: str = "[HR Manager Name]",
    hr_title: str = "[HR Manager Title]",
    hr_phone: str = "[Phone Number]",
    hr_email: str = "[Email Address]",
    company_address: Optional[str] = None,
    bonus_amount: Optional[str] = None,
    bonus_percentage: Optional[str] = None,
    equity_details: Optional[str] = None,
    sign_on_bonus: Optional[str] = None
) -> str:
    """Genera una carta de oferta en formato HTML profesional."""
    
    from generate_offer_letter import format_currency, format_date, format_benefits, calculate_offer_deadline
    
    formatted_salary = format_currency(salary_amount)
    formatted_start_date = format_date(start_date)
    formatted_benefits = format_benefits(benefits, style='bulleted')
    current_date = datetime.now().strftime('%B %d, %Y')
    offer_deadline = calculate_offer_deadline(offer_validity_days)
    
    # Get first name for greeting
    if candidate_name and candidate_name != "[Candidate Name]" and ' ' in candidate_name:
        greeting_name = candidate_name.split()[0]
    else:
        greeting_name = "[Candidate Name]"
    
    # Build compensation details
    compensation_html = f"""
        <div class="compensation-item">
            <strong>Base Salary:</strong> {formatted_salary} per year<br>
            <strong>Pay Frequency:</strong> {pay_frequency}
        </div>
    """
    
    if bonus_amount or bonus_percentage:
        bonus_text = ""
        if bonus_amount:
            bonus_text = f"<strong>Annual Bonus:</strong> {format_currency(bonus_amount)}"
        elif bonus_percentage:
            bonus_text = f"<strong>Annual Bonus:</strong> {bonus_percentage}% of base salary (performance-based)"
        compensation_html += f"""
        <div class="compensation-item">
            {bonus_text}
        </div>
    """
    
    if sign_on_bonus:
        compensation_html += f"""
        <div class="compensation-item">
            <strong>Sign-on Bonus:</strong> {format_currency(sign_on_bonus)}
        </div>
    """
    
    if equity_details:
        compensation_html += f"""
        <div class="compensation-item">
            <strong>Equity/Stock Options:</strong> {equity_details}
        </div>
    """
    
    # Position details
    position_details_html = f"""
        <li><strong>Position Title:</strong> {position_title}</li>
        <li><strong>Start Date:</strong> {formatted_start_date}</li>
        <li><strong>Work Location:</strong> {location}</li>
        <li><strong>Employment Type:</strong> {employment_type}</li>
    """
    
    if department:
        position_details_html = f"<li><strong>Department:</strong> {department}</li>" + position_details_html
    
    if manager_name:
        manager_info = f"<li><strong>Reports to:</strong> {manager_name}"
        if manager_title:
            manager_info += f", {manager_title}"
        manager_info += "</li>"
        position_details_html += manager_info
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offer Letter - {position_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        
        .letter-container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .date {{
            text-align: right;
            margin-bottom: 20px;
            color: #666;
        }}
        
        .recipient {{
            margin-bottom: 20px;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            color: #2c3e50;
            font-size: 18px;
            font-weight: bold;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }}
        
        .section-content {{
            margin-left: 20px;
        }}
        
        .section-content ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .section-content li {{
            margin-bottom: 10px;
            padding-left: 20px;
            position: relative;
        }}
        
        .section-content li:before {{
            content: "•";
            position: absolute;
            left: 0;
            color: #3498db;
            font-weight: bold;
        }}
        
        .compensation-item {{
            margin-bottom: 15px;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
        }}
        
        .benefits-list {{
            white-space: pre-line;
            margin-left: 20px;
        }}
        
        .signature-section {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
        }}
        
        .acceptance-section {{
            margin-top: 40px;
            padding: 20px;
            background-color: #f8f9fa;
            border: 2px solid #ddd;
        }}
        
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
        
        @media print {{
            body {{
                background-color: white;
                padding: 0;
            }}
            .letter-container {{
                box-shadow: none;
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="letter-container">
        <div class="header">
            <h1>OFFER OF EMPLOYMENT</h1>
        </div>
        
        <div class="date">
            Date: {current_date}
        </div>
        
        <div class="recipient">
            <p>{candidate_name}</p>
            <p>[Address]</p>
        </div>
        
        <p>Dear {greeting_name},</p>
        
        <div class="section">
            <p><strong>CONFIDENTIAL OFFER OF EMPLOYMENT</strong></p>
            <p>We are delighted to extend an offer for the position of <strong>{position_title}</strong> at {company_name}. 
            After careful consideration of your impressive background and the value you would bring to 
            our team, we believe you are the ideal candidate for this role.</p>
        </div>
        
        <div class="section">
            <div class="section-title">POSITION DETAILS</div>
            <div class="section-content">
                <ul>
                    {position_details_html}
                </ul>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">COMPENSATION PACKAGE</div>
            <div class="section-content">
                {compensation_html}
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">COMPREHENSIVE BENEFITS PACKAGE</div>
            <div class="section-content">
                <div class="benefits-list">{formatted_benefits}</div>
            </div>
        </div>
"""
    
    if company_details:
        html += f"""
        <div class="section">
            <div class="section-title">COMPANY OVERVIEW</div>
            <div class="section-content">
                <p>{company_details}</p>
            </div>
        </div>
"""
    
    html += f"""
        <div class="section">
            <div class="section-title">TERMS AND CONDITIONS</div>
            <div class="section-content">
                <ul>
                    <li>This offer is valid for {offer_validity_days} days from the date of this letter (until {offer_deadline})</li>
                    <li>Employment is at-will, meaning either party may terminate the employment relationship at any time, with or without cause or notice</li>
                    <li>Background check and reference verification are required</li>
                    <li>You will be required to sign our standard employment agreement and confidentiality agreement</li>
                    <li>This offer is contingent upon successful completion of all pre-employment requirements and verification of your eligibility to work</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">NEXT STEPS</div>
            <div class="section-content">
                <p>Please indicate your acceptance of this offer by:</p>
                <ol>
                    <li>Signing and returning this letter by {offer_deadline}</li>
                    <li>Completing the pre-employment requirements (background check, references)</li>
                    <li>Confirming your start date availability</li>
                    <li>Providing any required documentation (ID, work authorization, etc.)</li>
                </ol>
                <p>We are excited about the possibility of you joining our team and contributing to our continued success. 
                Your expertise and experience align perfectly with our strategic goals, and we look forward to welcoming you to {company_name}.</p>
            </div>
        </div>
        
        <div class="signature-section">
            <p>Sincerely,</p>
            <br>
            <p><strong>{hr_name}</strong><br>
            {hr_title}<br>
            {company_name}"""
    
    if company_address:
        html += f"<br>{company_address}"
    
    html += f"""<br>
            Phone: {hr_phone}<br>
            Email: {hr_email}</p>
        </div>
        
        <div class="acceptance-section">
            <div class="section-title">ACCEPTANCE SECTION</div>
            <p>I, {candidate_name}, accept the terms of this offer of employment as outlined above.</p>
            <br>
            <p>Signature: _________________ Date: _________</p>
            <br>
            <p>Print Name: _________________</p>
        </div>
        
        <div class="footer">
            <p>This is a confidential document. Please do not share without authorization.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def generate_batch_offer_letters(csv_file: str, output_dir: str = "offer_letters") -> List[str]:
    """Genera múltiples cartas de oferta desde un archivo CSV."""
    from generate_offer_letter import generate_offer_letter
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    generated_files = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Parse benefits from CSV (comma-separated or semicolon-separated)
                    benefits_str = row.get('benefits', '')
                    if ';' in benefits_str:
                        benefits = [b.strip() for b in benefits_str.split(';') if b.strip()]
                    else:
                        benefits = [b.strip() for b in benefits_str.split(',') if b.strip()]
                    
                    # Generate filename
                    candidate_name = row.get('candidate_name', f'candidate_{row_num}').replace(' ', '_')
                    position = row.get('position_title', 'position').replace(' ', '_')
                    filename = f"{candidate_name}_{position}.txt"
                    output_path = os.path.join(output_dir, filename)
                    
                    # Generate offer letter
                    offer_letter = generate_offer_letter(
                        position_title=row.get('position_title', ''),
                        salary_amount=row.get('salary_amount', ''),
                        start_date=row.get('start_date', ''),
                        benefits=benefits,
                        location=row.get('location', ''),
                        company_name=row.get('company_name'),
                        company_details=row.get('company_details'),
                        company_address=row.get('company_address'),
                        candidate_name=row.get('candidate_name'),
                        department=row.get('department'),
                        manager_name=row.get('manager_name'),
                        manager_title=row.get('manager_title'),
                        employment_type=row.get('employment_type', 'Full-time'),
                        pay_frequency=row.get('pay_frequency', 'Bi-weekly'),
                        offer_validity_days=int(row.get('offer_validity_days', 7)),
                        hr_name=row.get('hr_name'),
                        hr_title=row.get('hr_title'),
                        hr_phone=row.get('hr_phone'),
                        hr_email=row.get('hr_email'),
                        format_style=row.get('format_style', 'professional')
                    )
                    
                    # Save to file
                    with open(output_path, 'w', encoding='utf-8') as out_file:
                        out_file.write(offer_letter)
                    
                    generated_files.append(output_path)
                    print(f"✓ Generated: {output_path}")
                    
                except Exception as e:
                    print(f"✗ Error processing row {row_num}: {e}", file=sys.stderr)
                    continue
        
        print(f"\n✓ Successfully generated {len(generated_files)} offer letters in '{output_dir}'")
        return generated_files
        
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing CSV file: {e}", file=sys.stderr)
        sys.exit(1)


def validate_offer_data(data: Dict) -> tuple[bool, List[str]]:
    """Valida los datos de una oferta y retorna (is_valid, errors)."""
    errors = []
    
    # Required fields
    required_fields = ['position_title', 'salary_amount', 'start_date', 'location']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Validate salary
    if data.get('salary_amount'):
        try:
            salary = data['salary_amount'].replace('$', '').replace(',', '').strip()
            float(salary)
            if float(salary) <= 0:
                errors.append("Salary must be greater than 0")
        except ValueError:
            errors.append("Invalid salary amount format")
    
    # Validate date
    if data.get('start_date'):
        from generate_offer_letter import format_date
        formatted = format_date(data['start_date'])
        if formatted == data['start_date'] and not any(fmt in data['start_date'] for fmt in ['/', '-']):
            errors.append("Invalid date format. Use YYYY-MM-DD, MM/DD/YYYY, or similar")
    
    # Validate email if provided
    if data.get('hr_email') and '@' not in data['hr_email']:
        errors.append("Invalid HR email format")
    
    # Validate offer validity days
    if data.get('offer_validity_days'):
        try:
            days = int(data['offer_validity_days'])
            if days < 1 or days > 30:
                errors.append("Offer validity days should be between 1 and 30")
        except ValueError:
            errors.append("Invalid offer validity days format")
    
    return len(errors) == 0, errors


def create_csv_template(output_file: str = "offer_letter_template.csv"):
    """Crea un archivo CSV de plantilla para procesamiento batch."""
    headers = [
        'position_title', 'salary_amount', 'start_date', 'benefits', 'location',
        'company_name', 'company_details', 'company_address', 'candidate_name',
        'department', 'manager_name', 'manager_title', 'employment_type',
        'pay_frequency', 'offer_validity_days', 'hr_name', 'hr_title',
        'hr_phone', 'hr_email', 'format_style'
    ]
    
    # Example row
    example_row = [
        'Software Engineer', '120000', '2024-03-15',
        'Health insurance;Dental coverage;401k matching', 'San Francisco, CA',
        'TechCorp Inc.', 'A leading technology company', '123 Tech St, SF, CA',
        'John Doe', 'Engineering', 'Jane Smith', 'Engineering Manager',
        'Full-time', 'Bi-weekly', '7', 'Jane HR', 'HR Manager',
        '(415) 555-0123', 'hr@techcorp.com', 'professional'
    ]
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(example_row)
    
    print(f"✓ CSV template created: {output_file}")
    print(f"  Edit this file and use: python generate_offer_letter.py --batch {output_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced offer letter features')
    parser.add_argument('--html', action='store_true', help='Generate HTML version')
    parser.add_argument('--batch', dest='csv_file', help='Process batch from CSV file')
    parser.add_argument('--create-template', action='store_true', help='Create CSV template')
    parser.add_argument('--validate', dest='json_file', help='Validate JSON offer data')
    
    args = parser.parse_args()
    
    if args.create_template:
        create_csv_template()
    elif args.batch:
        generate_batch_offer_letters(args.batch)
    elif args.validate:
        with open(args.validate, 'r') as f:
            data = json.load(f)
        is_valid, errors = validate_offer_data(data)
        if is_valid:
            print("✓ Offer data is valid")
        else:
            print("✗ Validation errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
    else:
        parser.print_help()






