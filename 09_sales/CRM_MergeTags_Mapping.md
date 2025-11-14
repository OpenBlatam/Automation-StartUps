# 🔗 CRM Merge-Tags Mapping (HubSpot / Salesforce / WA API / Email)

## Campos base del kit
- {{first_name}}
- {{company}}
- {{industry}}
- {{email}}
- {{phone}}
- {{city}}
- {{variant_id}}

## HubSpot
- First name → `contact.firstname`
- Company → `company.name` (o `contact.company`)
- Industry → `company.industry`
- Email → `contact.email`
- Phone → `contact.phone`
- City → `contact.city`
- Variant → `deal.utm_content` o `contact.utm_content`

## Salesforce
- First name → `Lead.FirstName` / `Contact.FirstName`
- Company → `Lead.Company` / `Account.Name`
- Industry → `Account.Industry`
- Email → `Lead.Email`
- Phone → `Lead.Phone`
- City → `Lead.City`
- Variant → `CampaignMember.UTM_Content__c`

## WhatsApp Business API
- `{{1}}` first_name
- `{{2}}` day
- `{{3}}` time
- `{{4}}` link

## Email (ESP)
- Mailchimp: `*|FNAME|*`, `*|COMPANY|*`
- Sendgrid: `-first_name-`, `-company-`
- Klaviyo: `{{ first_name }}`, `{{ organization.name }}`

## Reglas
- Fallbacks: `{{first_name|amigo}}`
- Sanitizar mayúsculas/minúsculas
- Validar link + UTM antes de enviar
