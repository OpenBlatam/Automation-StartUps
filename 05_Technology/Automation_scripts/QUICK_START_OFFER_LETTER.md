# Quick Start: Offer Letter Automation

## Your Prompts

You provided two prompts for generating offer letters:

### Prompt 1 (with company details):
```
Kindly generate an offer letter for a {position title} position, offering a {salary amount} salary and commencing on {start date}. The package encompasses a range of {list of benefits}. The designated work site is {location}. Additionally, provide a concise overview of the company, highlighting its {company details}.
```

### Prompt 2 (without company details):
```
Kindly generate an offer letter for the {position title} position, offering a {salary amount} salary and commencing on {start date}. The package encompasses a range of {list of benefits}. The designated work site is {location}. Additionally, provide a concise overview of the company.
```

## How to Use

### Example 1: With Company Details

```bash
python generate_offer_letter.py \
  --position "Senior Software Engineer" \
  --salary "140000" \
  --start-date "2024-03-15" \
  --benefits "Health insurance" \
  --benefits "Dental coverage" \
  --benefits "401k matching" \
  --benefits "Unlimited PTO" \
  --location "San Francisco, CA" \
  --company-name "TechCorp AI Solutions" \
  --company-details "TechCorp is a leading technology company focused on innovation and excellence. We are committed to creating cutting-edge solutions that transform industries." \
  --output offer_letter.txt
```

### Example 2: Without Company Details

```bash
python generate_offer_letter.py \
  --position "Marketing Manager" \
  --salary "95000" \
  --start-date "2024-02-20" \
  --benefits "Health insurance,Dental coverage,401k matching,20 days PTO" \
  --location "New York, NY" \
  --company-name "GlobalGrowth Marketing Agency" \
  --output offer_letter.txt
```

### Using JSON (Recommended for Complex Cases)

Create `input.json`:
```json
{
  "position_title": "Senior Software Engineer",
  "salary_amount": "140000",
  "start_date": "2024-03-15",
  "benefits": [
    "Health insurance - 100% company-paid",
    "Dental and vision coverage",
    "401k with 6% matching",
    "Unlimited PTO"
  ],
  "location": "San Francisco, CA",
  "company_name": "TechCorp AI Solutions",
  "company_details": "TechCorp is a leading technology company focused on innovation."
}
```

Then run:
```bash
python generate_offer_letter.py --json input.json
```

## Parameter Mapping

| Your Prompt Placeholder | Script Parameter | Example |
|------------------------|------------------|---------|
| `{position title}` | `--position` | "Software Engineer" |
| `{salary amount}` | `--salary` | "120000" or "$120,000" |
| `{start date}` | `--start-date` | "2024-03-15" or "03/15/2024" |
| `{list of benefits}` | `--benefits` (multiple) | "Health insurance" |
| `{location}` | `--location` | "San Francisco, CA" |
| `{company details}` | `--company-details` | "Company description..." |

## Quick Examples

### Minimal (Required Fields Only)
```bash
python generate_offer_letter.py \
  --position "Software Engineer" \
  --salary "120000" \
  --start-date "2024-03-15" \
  --benefits "Health insurance" \
  --location "San Francisco, CA"
```

### Complete (All Fields)
```bash
python generate_offer_letter.py \
  --position "Senior Software Engineer" \
  --salary "140000" \
  --start-date "2024-03-15" \
  --benefits "Health insurance" \
  --benefits "Dental coverage" \
  --benefits "401k matching" \
  --benefits "Unlimited PTO" \
  --location "San Francisco, CA" \
  --company-name "TechCorp Inc." \
  --company-details "A leading technology company focused on innovation." \
  --candidate-name "John Doe" \
  --output offer_letter_john_doe.txt
```

## Output

The script generates a professional offer letter with:
- ✅ Position details
- ✅ Compensation package
- ✅ Benefits list (formatted)
- ✅ Company overview (if provided)
- ✅ Terms and conditions
- ✅ Next steps
- ✅ Acceptance section

## Files Created

- `generate_offer_letter.py` - Main script
- `offer_letter_template.py` - Template-based generator
- `example_offer_letter_input.json` - Example JSON input
- `README_OFFER_LETTER.md` - Full documentation

## Need Help?

Run with `--help`:
```bash
python generate_offer_letter.py --help
```




