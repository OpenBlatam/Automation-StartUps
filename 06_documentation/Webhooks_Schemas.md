# 🧩 Webhooks Schemas (Contratos)

## IG DM Inbound
```
{
  "platform": "instagram",
  "event": "dm_inbound",
  "timestamp": "2025-10-30T15:10:00Z",
  "user": {"id":"ig_123","first_name":"Ana","username":"@ana"},
  "message": {"id":"m_1","text":"demo","lang":"ES"}
}
```

## Classifier Output
```
{
  "bucket": "interes",
  "keyword": "demo",
  "language": "ES",
  "confidence": 0.92
}
```

## Variant Selected
```
{
  "variant_id": "DM2-B2",
  "cta_group": "B",
  "cta_text": "AGENDA",
  "link": "https://...&utm_content=DM2-B2"
}
```

## Send Result
```
{
  "status": "sent",
  "channel": "instagram",
  "message_id": "m_2",
  "error": null
}
```

## Error Format
```
{
  "status": "error",
  "code": "RATE_LIMIT",
  "retry_in_sec": 120,
  "details": "Too Many Requests"
}
```
