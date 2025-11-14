#!/usr/bin/env python3
"""
Offer Letter Automation Script
Generates professional offer letters based on provided parameters.
Enhanced version with improved formatting and additional features.
"""

import argparse
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json
import sys


def format_currency(amount: str) -> str:
    """Format currency amount with commas."""
    try:
        # Remove any currency symbols and spaces
        clean_amount = amount.replace('$', '').replace(',', '').strip()
        num_amount = float(clean_amount)
        return f"${num_amount:,.2f}"
    except ValueError:
        return amount


def format_date(date_str: str) -> str:
    """Format date string to readable format."""
    try:
        # Try various date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%B %d, %Y')
            except ValueError:
                continue
        return date_str
    except:
        return date_str


def format_benefits(benefits: List[str], style: str = 'numbered') -> str:
    """Format list of benefits into a readable list.
    
    Args:
        benefits: List of benefit strings
        style: 'numbered', 'bulleted', or 'dashed'
    """
    if isinstance(benefits, str):
        # If it's a string, try to split by comma or newline
        benefits = [b.strip() for b in benefits.replace('\n', ',').split(',') if b.strip()]
    
    if not benefits:
        return "• Standard company benefits package"
    
    formatted = []
    for benefit in benefits:
        benefit = benefit.strip()
        if not benefit:
            continue
            
        if style == 'numbered':
            formatted.append(f"  {len(formatted) + 1}. {benefit}")
        elif style == 'bulleted':
            formatted.append(f"  • {benefit}")
        elif style == 'dashed':
            formatted.append(f"  - {benefit}")
        else:
            formatted.append(f"  • {benefit}")
    
    return '\n'.join(formatted) if formatted else "• Standard company benefits package"


def calculate_offer_deadline(days: int = 7) -> str:
    """Calculate offer deadline date."""
    deadline = datetime.now() + timedelta(days=days)
    return deadline.strftime('%B %d, %Y')


def generate_offer_letter(
    position_title: str,
    salary_amount: str,
    start_date: str,
    benefits: List[str],
    location: str,
    company_name: Optional[str] = None,
    company_details: Optional[str] = None,
    candidate_name: Optional[str] = None,
    output_file: Optional[str] = None,
    department: Optional[str] = None,
    manager_name: Optional[str] = None,
    manager_title: Optional[str] = None,
    employment_type: str = "Full-time",
    pay_frequency: str = "Bi-weekly",
    offer_validity_days: int = 7,
    hr_name: Optional[str] = None,
    hr_title: Optional[str] = None,
    hr_phone: Optional[str] = None,
    hr_email: Optional[str] = None,
    company_address: Optional[str] = None,
    format_style: str = "professional",
    bonus_amount: Optional[str] = None,
    bonus_percentage: Optional[str] = None,
    equity_details: Optional[str] = None,
    sign_on_bonus: Optional[str] = None
) -> str:
    """
    Generate an offer letter based on provided parameters.
    
    Args:
        position_title: The job position title
        salary_amount: The salary amount (can include currency symbol)
        start_date: The start date (various formats accepted)
        benefits: List of benefits or comma-separated string
        location: Work location/site
        company_name: Company name (optional, defaults to placeholder)
        company_details: Company overview/details (optional)
        candidate_name: Candidate's name (optional, defaults to placeholder)
        output_file: Output file path (optional)
        department: Department name (optional)
        manager_name: Manager's name (optional)
        manager_title: Manager's title (optional)
        employment_type: Type of employment (default: "Full-time")
        pay_frequency: Pay frequency (default: "Bi-weekly")
        offer_validity_days: Days offer is valid (default: 7)
        hr_name: HR contact name (optional)
        hr_title: HR contact title (optional)
        hr_phone: HR contact phone (optional)
        hr_email: HR contact email (optional)
        company_address: Company address (optional)
        format_style: Format style - "professional" or "simple" (default: "professional")
    
    Returns:
        The generated offer letter as a string
    """
    # Default values
    if company_name is None:
        company_name = "[Company Name]"
    
    if candidate_name is None:
        candidate_name = "[Candidate Name]"
    
    if hr_name is None:
        hr_name = "[HR Manager Name]"
    if hr_title is None:
        hr_title = "[HR Manager Title]"
    if hr_phone is None:
        hr_phone = "[Phone Number]"
    if hr_email is None:
        hr_email = "[Email Address]"
    
    # Format values
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
    
    # Build position details section
    position_details = f"• Position Title: {position_title}\n"
    position_details += f"• Start Date: {formatted_start_date}\n"
    position_details += f"• Work Location: {location}\n"
    position_details += f"• Employment Type: {employment_type}"
    
    if department:
        position_details = f"• Department: {department}\n" + position_details
    
    if manager_name:
        manager_info = f"• Reports to: {manager_name}"
        if manager_title:
            manager_info += f", {manager_title}"
        position_details += f"\n{manager_info}"
    
    # Generate offer letter header
    if format_style == "professional":
        header = f"""
{'='*75}
                    OFFER OF EMPLOYMENT
{'='*75}

Date: {current_date}

{candidate_name}
[Address]

Dear {greeting_name},

CONFIDENTIAL OFFER OF EMPLOYMENT

We are delighted to extend an offer for the position of {position_title} at {company_name}. 
After careful consideration of your impressive background and the value you would bring to 
our team, we believe you are the ideal candidate for this role.

"""
    else:
        header = f"""
{'='*70}
OFFER OF EMPLOYMENT
{'='*70}

Date: {current_date}

{candidate_name}
[Address]

Dear {greeting_name},

CONFIDENTIAL OFFER OF EMPLOYMENT

We are delighted to extend an offer for the position of {position_title} at {company_name}. 
After careful consideration of your impressive background and the value you would bring to 
our team, we believe you are the ideal candidate for this role.

"""
    
    # Build sections
    position_section = f"""
POSITION DETAILS
{'-'*75}
{position_details}

"""
    
    # Build compensation section with bonuses and equity
    compensation_items = [
        f"• Base Salary: {formatted_salary} per year",
        f"• Pay Frequency: {pay_frequency}"
    ]
    
    if bonus_amount:
        compensation_items.append(f"• Annual Bonus: {format_currency(bonus_amount)}")
    elif bonus_percentage:
        compensation_items.append(f"• Annual Bonus: {bonus_percentage}% of base salary (performance-based)")
    
    if sign_on_bonus:
        compensation_items.append(f"• Sign-on Bonus: {format_currency(sign_on_bonus)}")
    
    if equity_details:
        compensation_items.append(f"• Equity/Stock Options: {equity_details}")
    
    compensation_section = f"""
COMPENSATION PACKAGE
{'-'*75}
{chr(10).join(compensation_items)}

"""
    
    benefits_section = f"""
COMPREHENSIVE BENEFITS PACKAGE
{'-'*75}
{formatted_benefits}

"""
    
    # Company overview section
    company_section = ""
    if company_details:
        company_section = f"""
COMPANY OVERVIEW
{'-'*75}
{company_details}

"""
    
    # Terms and conditions section
    terms_section = f"""
TERMS AND CONDITIONS
{'-'*75}
• This offer is valid for {offer_validity_days} days from the date of this letter (until {offer_deadline})
• Employment is at-will, meaning either party may terminate the employment 
  relationship at any time, with or without cause or notice
• Background check and reference verification are required
• You will be required to sign our standard employment agreement and 
  confidentiality agreement
• This offer is contingent upon successful completion of all pre-employment 
  requirements and verification of your eligibility to work

"""
    
    # Next steps section
    next_steps_section = f"""
NEXT STEPS
{'-'*75}
Please indicate your acceptance of this offer by:
  1. Signing and returning this letter by {offer_deadline}
  2. Completing the pre-employment requirements (background check, references)
  3. Confirming your start date availability
  4. Providing any required documentation (ID, work authorization, etc.)

We are excited about the possibility of you joining our team and contributing 
to our continued success. Your expertise and experience align perfectly with 
our strategic goals, and we look forward to welcoming you to {company_name}.

"""
    
    # Signature section
    signature_section = f"""
Sincerely,

{hr_name}
{hr_title}
{company_name}"""
    
    if company_address:
        signature_section += f"\n{company_address}"
    
    signature_section += f"""
Phone: {hr_phone}
Email: {hr_email}

"""
    
    # Acceptance section
    acceptance_section = f"""
{'='*75}

ACCEPTANCE SECTION
{'-'*75}
I, {candidate_name}, accept the terms of this offer of employment as outlined 
above.

Signature: _________________ Date: _________

Print Name: _________________

{'='*75}
"""
    
    # Combine all sections
    offer_letter = (header + position_section + compensation_section + 
                   benefits_section + company_section + terms_section + 
                   next_steps_section + signature_section + acceptance_section)
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(offer_letter)
        print(f"✓ Offer letter saved to: {output_file}")
        
        # Track offer if tracker is available
        try:
            from offer_letter_tracker import track_offer
            track_offer(
                position_title=position_title,
                candidate_name=candidate_name or "[Candidate Name]",
                salary_amount=salary_amount,
                output_file=output_file,
                offer_type="text",
                template_used=None,
                department=department,
                location=location,
                employment_type=employment_type
            )
        except:
            pass  # Silently fail if tracker not available
    
    return offer_letter


def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate professional offer letters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python generate_offer_letter.py --position "Software Engineer" \\
    --salary "120000" --start-date "2024-03-15" \\
    --benefits "Health insurance,Dental coverage,401k matching" \\
    --location "San Francisco, CA"

  # With company details
  python generate_offer_letter.py --position "Marketing Manager" \\
    --salary "$95,000" --start-date "2024-02-20" \\
    --benefits "Health insurance" --benefits "Dental coverage" \\
    --benefits "401k matching" --benefits "Unlimited PTO" \\
    --location "New York, NY" --company-name "TechCorp Inc." \\
    --company-details "A leading technology company focused on innovation."

  # Using JSON input
  python generate_offer_letter.py --json input.json --output offer_letter.txt
        """
    )
    
    # Arguments (not required if JSON is provided)
    parser.add_argument('--position', '--position-title', dest='position_title',
                       help='Position title')
    parser.add_argument('--salary', '--salary-amount', dest='salary_amount',
                       help='Salary amount (e.g., "120000" or "$120,000")')
    parser.add_argument('--start-date', dest='start_date',
                       help='Start date (YYYY-MM-DD, MM/DD/YYYY, etc.)')
    parser.add_argument('--benefits', action='append', dest='benefits',
                       help='Benefit (can be used multiple times) or comma-separated string')
    parser.add_argument('--location',
                       help='Work location/site')
    
    # Optional arguments - Basic
    parser.add_argument('--company-name', dest='company_name',
                       help='Company name (default: [Company Name])')
    parser.add_argument('--company-details', dest='company_details',
                       help='Company overview/details')
    parser.add_argument('--company-address', dest='company_address',
                       help='Company address')
    parser.add_argument('--candidate-name', dest='candidate_name',
                       help='Candidate name (default: [Candidate Name])')
    parser.add_argument('--output', '-o', dest='output_file',
                       help='Output file path (default: print to stdout)')
    
    # Optional arguments - Position details
    parser.add_argument('--department', dest='department',
                       help='Department name')
    parser.add_argument('--manager-name', dest='manager_name',
                       help="Manager's name")
    parser.add_argument('--manager-title', dest='manager_title',
                       help="Manager's title")
    parser.add_argument('--employment-type', dest='employment_type',
                       default='Full-time',
                       help='Employment type (default: Full-time)')
    
    # Optional arguments - Compensation
    parser.add_argument('--pay-frequency', dest='pay_frequency',
                       default='Bi-weekly',
                       help='Pay frequency (default: Bi-weekly)')
    
    # Optional arguments - HR Contact
    parser.add_argument('--hr-name', dest='hr_name',
                       help='HR contact name')
    parser.add_argument('--hr-title', dest='hr_title',
                       help='HR contact title')
    parser.add_argument('--hr-phone', dest='hr_phone',
                       help='HR contact phone')
    parser.add_argument('--hr-email', dest='hr_email',
                       help='HR contact email')
    
    # Optional arguments - Offer settings
    parser.add_argument('--offer-validity-days', dest='offer_validity_days',
                       type=int, default=7,
                       help='Days offer is valid (default: 7)')
    parser.add_argument('--format-style', dest='format_style',
                       choices=['professional', 'simple'],
                       default='professional',
                       help='Format style (default: professional)')
    
    # JSON input option
    parser.add_argument('--json', dest='json_file',
                       help='Load parameters from JSON file')
    
    # Advanced options
    parser.add_argument('--bonus-amount', dest='bonus_amount',
                       help='Annual bonus amount')
    parser.add_argument('--bonus-percentage', dest='bonus_percentage',
                       help='Annual bonus percentage (e.g., "15%")')
    parser.add_argument('--equity', dest='equity_details',
                       help='Equity/stock options details')
    parser.add_argument('--sign-on-bonus', dest='sign_on_bonus',
                       help='Sign-on bonus amount')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML version instead of text')
    parser.add_argument('--batch', dest='csv_file',
                       help='Process batch from CSV file (see offer_letter_extras.py)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate input data before generating')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--template', dest='template_name',
                       help='Use a saved template (see offer_letter_templates.py)')
    
    # Handle interactive mode early (before parsing again)
    if '--interactive' in sys.argv or '-i' in sys.argv:
        from offer_letter_interactive import generate_interactive
        generate_interactive()
        return
    
    args = parser.parse_args()
    
    # Handle interactive mode
    if args.interactive:
        from offer_letter_interactive import generate_interactive
        generate_interactive()
        return
    
    # Handle template
    if args.template_name:
        from offer_letter_templates import load_template
        template = load_template(args.template_name)
        if template:
            # Merge template data with command line args
            template_data = template.get('data', {})
            if not args.json_file:
                # Use template as base
                args.position_title = args.position_title or template_data.get('position_title')
                args.salary_amount = args.salary_amount or template_data.get('salary_amount')
                args.start_date = args.start_date or template_data.get('start_date')
                args.location = args.location or template_data.get('location')
                if not args.benefits:
                    args.benefits = template_data.get('benefits', [])
                args.company_name = args.company_name or template_data.get('company_name')
                args.company_details = args.company_details or template_data.get('company_details')
                args.department = args.department or template_data.get('department')
                args.employment_type = args.employment_type or template_data.get('employment_type', 'Full-time')
                args.pay_frequency = args.pay_frequency or template_data.get('pay_frequency', 'Bi-weekly')
                args.bonus_percentage = args.bonus_percentage or template_data.get('bonus_percentage')
                args.bonus_amount = args.bonus_amount or template_data.get('bonus_amount')
                args.equity_details = args.equity_details or template_data.get('equity_details')
                args.sign_on_bonus = args.sign_on_bonus or template_data.get('sign_on_bonus')
                args.format_style = args.format_style if args.format_style != 'professional' else template_data.get('format_style', 'professional')
        else:
            print(f"❌ Template '{args.template_name}' not found", file=sys.stderr)
            sys.exit(1)
    
    # Handle JSON input
    if args.json_file:
        try:
            with open(args.json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: JSON file '{args.json_file}' not found.", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in file '{args.json_file}': {e}", file=sys.stderr)
            sys.exit(1)
        
        # Override with command-line args if provided (command-line takes precedence)
        position_title = args.position_title or json_data.get('position_title')
        salary_amount = args.salary_amount or json_data.get('salary_amount')
        start_date = args.start_date or json_data.get('start_date')
        benefits = args.benefits or json_data.get('benefits', [])
        location = args.location or json_data.get('location')
        company_name = args.company_name or json_data.get('company_name')
        company_details = args.company_details or json_data.get('company_details')
        company_address = args.company_address or json_data.get('company_address')
        candidate_name = args.candidate_name or json_data.get('candidate_name')
        department = args.department or json_data.get('department')
        manager_name = args.manager_name or json_data.get('manager_name')
        manager_title = args.manager_title or json_data.get('manager_title')
        employment_type = args.employment_type or json_data.get('employment_type', 'Full-time')
        pay_frequency = args.pay_frequency or json_data.get('pay_frequency', 'Bi-weekly')
        offer_validity_days = args.offer_validity_days if args.offer_validity_days != 7 else json_data.get('offer_validity_days', 7)
        hr_name = args.hr_name or json_data.get('hr_name')
        hr_title = args.hr_title or json_data.get('hr_title')
        hr_phone = args.hr_phone or json_data.get('hr_phone')
        hr_email = args.hr_email or json_data.get('hr_email')
        format_style = args.format_style if args.format_style != 'professional' else json_data.get('format_style', 'professional')
        output_file = args.output_file or json_data.get('output_file')
        json_data = json_data  # Keep reference for later use
    else:
        position_title = args.position_title
        salary_amount = args.salary_amount
        start_date = args.start_date
        benefits = args.benefits
        location = args.location
        company_name = args.company_name
        company_details = args.company_details
        company_address = args.company_address
        candidate_name = args.candidate_name
        department = args.department
        manager_name = args.manager_name
        manager_title = args.manager_title
        employment_type = args.employment_type
        pay_frequency = args.pay_frequency
        offer_validity_days = args.offer_validity_days
        hr_name = args.hr_name
        hr_title = args.hr_title
        hr_phone = args.hr_phone
        hr_email = args.hr_email
        format_style = args.format_style
        output_file = args.output_file
        json_data = {}  # Empty dict for non-JSON mode
    
    # Validate required fields (if not using JSON or JSON didn't provide them)
    if not args.json_file:
        if not position_title:
            parser.error('--position/--position-title is required (or use --json)')
        if not salary_amount:
            parser.error('--salary/--salary-amount is required (or use --json)')
        if not start_date:
            parser.error('--start-date is required (or use --json)')
        if not location:
            parser.error('--location is required (or use --json)')
    else:
        # Validate JSON provided required fields
        if not position_title:
            parser.error('position_title is required in JSON file')
        if not salary_amount:
            parser.error('salary_amount is required in JSON file')
        if not start_date:
            parser.error('start_date is required in JSON file')
        if not location:
            parser.error('location is required in JSON file')
    
    # Process benefits - handle both list and string formats
    if benefits:
        if len(benefits) == 1 and ',' in benefits[0]:
            # Single string with commas
            benefits = [b.strip() for b in benefits[0].split(',') if b.strip()]
        # Otherwise use the list as-is
    
    # Handle batch processing
    if args.csv_file:
        from offer_letter_extras import generate_batch_offer_letters
        generate_batch_offer_letters(args.csv_file)
        return
    
    # Handle HTML generation
    if args.html:
        from offer_letter_extras import generate_html_offer_letter
        html_content = generate_html_offer_letter(
            position_title=position_title,
            salary_amount=salary_amount,
            start_date=start_date,
            benefits=benefits or [],
            location=location,
            company_name=company_name,
            company_details=company_details,
            candidate_name=candidate_name,
            department=department,
            manager_name=manager_name,
            manager_title=manager_title,
            employment_type=employment_type,
            pay_frequency=pay_frequency,
            offer_validity_days=offer_validity_days,
            hr_name=hr_name,
            hr_title=hr_title,
            hr_phone=hr_phone,
            hr_email=hr_email,
            company_address=company_address,
            bonus_amount=args.bonus_amount or (json_data.get('bonus_amount') if args.json_file else None),
            bonus_percentage=args.bonus_percentage or (json_data.get('bonus_percentage') if args.json_file else None),
            equity_details=args.equity_details or (json_data.get('equity_details') if args.json_file else None),
            sign_on_bonus=args.sign_on_bonus or (json_data.get('sign_on_bonus') if args.json_file else None)
        )
        
        html_output = output_file or 'offer_letter.html'
        if not html_output.endswith('.html'):
            html_output += '.html'
        
        with open(html_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ HTML offer letter saved to: {html_output}")
        return
    
    # Validate if requested
    if args.validate:
        from offer_letter_extras import validate_offer_data
        data = {
            'position_title': position_title,
            'salary_amount': salary_amount,
            'start_date': start_date,
            'location': location,
            'hr_email': hr_email,
            'offer_validity_days': offer_validity_days
        }
        is_valid, errors = validate_offer_data(data)
        if not is_valid:
            print("✗ Validation errors:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
        print("✓ Validation passed")
    
    # Get bonus/equity from JSON if using JSON
    bonus_amount = args.bonus_amount
    bonus_percentage = args.bonus_percentage
    equity_details = args.equity_details
    sign_on_bonus = args.sign_on_bonus
    
    if args.json_file:
        bonus_amount = bonus_amount or json_data.get('bonus_amount')
        bonus_percentage = bonus_percentage or json_data.get('bonus_percentage')
        equity_details = equity_details or json_data.get('equity_details')
        sign_on_bonus = sign_on_bonus or json_data.get('sign_on_bonus')
    
    # Generate offer letter
    offer_letter = generate_offer_letter(
        position_title=position_title,
        salary_amount=salary_amount,
        start_date=start_date,
        benefits=benefits or [],
        location=location,
        company_name=company_name,
        company_details=company_details,
        candidate_name=candidate_name,
        output_file=output_file,
        department=department,
        manager_name=manager_name,
        manager_title=manager_title,
        employment_type=employment_type,
        pay_frequency=pay_frequency,
        offer_validity_days=offer_validity_days,
        hr_name=hr_name,
        hr_title=hr_title,
        hr_phone=hr_phone,
        hr_email=hr_email,
        company_address=company_address,
        format_style=format_style,
        bonus_amount=bonus_amount,
        bonus_percentage=bonus_percentage,
        equity_details=equity_details,
        sign_on_bonus=sign_on_bonus
    )
    
    # Print to stdout if no output file specified
    if not output_file:
        print(offer_letter)


if __name__ == '__main__':
    main()

