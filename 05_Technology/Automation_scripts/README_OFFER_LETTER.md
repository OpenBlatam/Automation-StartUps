# Offer Letter Automation

A Python-based system for generating professional offer letters automatically.

## Features

- ✅ Generate professional offer letters from simple parameters
- ✅ Support for multiple input formats (command-line, JSON)
- ✅ Automatic formatting of dates, currency, and benefits
- ✅ Flexible template system with professional formatting
- ✅ Company overview section (optional)
- ✅ **NEW:** Department and manager information
- ✅ **NEW:** Customizable HR contact details
- ✅ **NEW:** Flexible employment types and pay frequencies
- ✅ **NEW:** Configurable offer validity period
- ✅ **NEW:** Professional and simple format styles
- ✅ **NEW:** Company address support
- ✅ **NEW:** Enhanced error handling and validation
- ✅ Customizable output

## Installation

No special dependencies required - uses only Python standard library.

```bash
# Make script executable
chmod +x generate_offer_letter.py
```

## Usage

### Method 1: Command-Line Arguments

#### Basic Usage

```bash
python generate_offer_letter.py \
  --position "Software Engineer" \
  --salary "120000" \
  --start-date "2024-03-15" \
  --benefits "Health insurance" \
  --benefits "Dental coverage" \
  --benefits "401k matching" \
  --location "San Francisco, CA"
```

#### With Company Details

```bash
python generate_offer_letter.py \
  --position "Marketing Manager" \
  --salary "$95,000" \
  --start-date "2024-02-20" \
  --benefits "Health insurance" \
  --benefits "Dental coverage" \
  --benefits "401k matching" \
  --benefits "Unlimited PTO" \
  --location "New York, NY" \
  --company-name "TechCorp Inc." \
  --company-details "A leading technology company focused on innovation." \
  --candidate-name "John Doe" \
  --output offer_letter.txt
```

#### Using Comma-Separated Benefits

```bash
python generate_offer_letter.py \
  --position "Data Scientist" \
  --salary "130000" \
  --start-date "2024-04-01" \
  --benefits "Health insurance,Dental coverage,401k matching,Unlimited PTO" \
  --location "Remote (Global)"
```

### Method 2: JSON Input

Create a JSON file with your parameters:

```json
{
  "position_title": "Senior Software Engineer",
  "salary_amount": "140000",
  "start_date": "2024-03-15",
  "benefits": [
    "Health insurance",
    "Dental coverage",
    "401k matching",
    "Unlimited PTO"
  ],
  "location": "San Francisco, CA",
  "company_name": "TechCorp Inc.",
  "company_details": "A leading technology company...",
  "candidate_name": "Sarah Johnson",
  "output_file": "offer_letter.txt"
}
```

Then run:

```bash
python generate_offer_letter.py --json input.json
```

### Method 3: Using the Template Generator

For prompt-based generation:

```python
from offer_letter_template import generate_from_prompt

prompt = """Kindly generate an offer letter for a {position title} position, 
offering a {salary amount} salary and commencing on {start date}. 
The package encompasses a range of {list of benefits}. 
The designated work site is {location}. 
Additionally, provide a concise overview of the company, highlighting its {company details}."""

values = {
    'position_title': 'Senior Software Engineer',
    'salary_amount': '140000',
    'start_date': '2024-03-15',
    'benefits': ['Health insurance', 'Dental coverage', '401k matching'],
    'location': 'San Francisco, CA',
    'company_details': 'TechCorp is a leading technology company...'
}

letter = generate_from_prompt(prompt, values)
print(letter)
```

## Parameters

### Required Parameters

- `--position` / `--position-title`: Job position title
- `--salary` / `--salary-amount`: Salary amount (e.g., "120000" or "$120,000")
- `--start-date`: Start date (accepts various formats: YYYY-MM-DD, MM/DD/YYYY, etc.)
- `--benefits`: List of benefits (can be used multiple times or comma-separated)
- `--location`: Work location/site

### Optional Parameters

#### Basic Options
- `--company-name`: Company name (default: "[Company Name]")
- `--company-details`: Company overview/details
- `--company-address`: Company physical address
- `--candidate-name`: Candidate name (default: "[Candidate Name]")
- `--output` / `-o`: Output file path (default: print to stdout)
- `--json`: Load parameters from JSON file

#### Position Details
- `--department`: Department name
- `--manager-name`: Manager's name
- `--manager-title`: Manager's title
- `--employment-type`: Employment type (default: "Full-time")

#### Compensation
- `--pay-frequency`: Pay frequency (default: "Bi-weekly")

#### HR Contact
- `--hr-name`: HR contact name
- `--hr-title`: HR contact title
- `--hr-phone`: HR contact phone number
- `--hr-email`: HR contact email address

#### Offer Settings
- `--offer-validity-days`: Days offer is valid (default: 7)
- `--format-style`: Format style - "professional" or "simple" (default: "professional")

## Examples

### Example 1: Basic Offer Letter

```bash
python generate_offer_letter.py \
  --position "Software Engineer" \
  --salary "120000" \
  --start-date "2024-03-15" \
  --benefits "Health insurance" \
  --benefits "Dental coverage" \
  --benefits "401k matching" \
  --location "San Francisco, CA" \
  --output offer_letter.txt
```

### Example 2: Executive Offer with All Details

```bash
python generate_offer_letter.py \
  --position "VP of Engineering" \
  --salary "$180,000" \
  --start-date "2024-04-01" \
  --benefits "Premium health insurance,100% company-paid" \
  --benefits "Dental and vision coverage" \
  --benefits "401k with 6% matching" \
  --benefits "Unlimited PTO" \
  --benefits "Stock options" \
  --benefits "$10,000 annual learning budget" \
  --location "New York, NY (Hybrid)" \
  --company-name "TechCorp AI Solutions" \
  --company-address "123 Tech Street, New York, NY 10001" \
  --company-details "TechCorp AI Solutions is a leading technology company focused on artificial intelligence and machine learning innovation. We are committed to creating cutting-edge solutions that transform industries and improve lives." \
  --candidate-name "Michael Chen" \
  --department "Engineering" \
  --manager-name "Jane Smith" \
  --manager-title "Chief Technology Officer" \
  --hr-name "Jennifer Martinez" \
  --hr-title "Senior HR Manager" \
  --hr-phone "(212) 555-0123" \
  --hr-email "hr@techcorp.com" \
  --offer-validity-days 10 \
  --format-style "professional" \
  --output offer_letter_michael_chen.txt
```

### Example 3: Using JSON File

```bash
# Create input.json with your parameters
python generate_offer_letter.py --json example_offer_letter_input.json
```

## Output Format

The generated offer letter includes:

- **Header**: Date and recipient information
- **Position Details**: Title, start date, location
- **Compensation Package**: Salary information
- **Benefits Package**: Formatted list of benefits
- **Company Overview**: (if provided)
- **Terms and Conditions**: Standard employment terms
- **Next Steps**: Instructions for acceptance
- **Acceptance Section**: Signature area

## Date Formats Supported

- `YYYY-MM-DD` (e.g., "2024-03-15")
- `MM/DD/YYYY` (e.g., "03/15/2024")
- `DD/MM/YYYY` (e.g., "15/03/2024")
- `YYYY/MM/DD` (e.g., "2024/03/15")

## Currency Formats Supported

- `120000` → `$120,000.00`
- `$120000` → `$120,000.00`
- `$120,000` → `$120,000.00`
- `120000.50` → `$120,000.50`

## Tips

1. **Benefits Format**: You can provide benefits as:
   - Multiple `--benefits` flags: `--benefits "Item 1" --benefits "Item 2"`
   - Comma-separated string: `--benefits "Item 1,Item 2,Item 3"`

2. **Company Details**: Include this for a more personalized offer letter that helps candidates understand your company culture and values.

3. **Output File**: If you don't specify `--output`, the letter will be printed to stdout, which is useful for piping or quick previews.

4. **JSON Input**: Use JSON files for batch processing or when you have complex configurations.

## Integration

This script can be easily integrated into:

- HRIS systems
- Applicant Tracking Systems (ATS)
- Automated hiring workflows
- Email automation systems
- Document management systems

## Customization

To customize the template, edit the `generate_offer_letter()` function in `generate_offer_letter.py` and modify the template string.

## Support

For issues or questions, refer to the main documentation:
- `offer_letter_automation_system.md` - Complete system documentation

## License

This script is part of the document automation system.

