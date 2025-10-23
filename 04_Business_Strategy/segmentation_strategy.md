# Segmentation Strategy for Win-Back Campaign

## Subscriber Segmentation Framework

### 1. **High-Value Subscribers** (Previous Customers)
**Characteristics:**
- Purchased AI course, webinar, or SaaS
- High engagement history
- Premium subscriber status
- Lifetime value: $500+

**Win-Back Approach:**
- **Email 1:** Personal apology with specific product references
- **Email 2:** Exclusive access to new features and updates
- **Email 3:** VIP treatment with special offers
- **Expected Recapture Rate:** 25-30%

**Customization:**
- Use their purchase history in messaging
- Reference specific products they bought
- Offer exclusive early access to new features
- Include personalized success stories

---

### 2. **Free Subscribers** (Never Purchased)
**Characteristics:**
- Signed up for free content only
- Low engagement history
- Price-sensitive
- Lifetime value: $0

**Win-Back Approach:**
- **Email 1:** Focus on free value and community
- **Email 2:** Show free tools and resources they missed
- **Email 3:** Offer free trial or limited-time access
- **Expected Recapture Rate:** 15-20%

**Customization:**
- Emphasize free resources and community
- Highlight free tools and templates
- Offer free trial of premium features
- Focus on learning and growth benefits

---

### 3. **Long-Time Subscribers** (6+ months)
**Characteristics:**
- Subscribed for extended period
- Moderate engagement history
- Familiar with brand
- Lifetime value: $100-500

**Win-Back Approach:**
- **Email 1:** Nostalgic approach, reference their journey
- **Email 2:** Show evolution and improvements since they joined
- **Email 3:** Loyalty rewards and special recognition
- **Expected Recapture Rate:** 20-25%

**Customization:**
- Reference their subscription date
- Show how the brand has evolved
- Offer loyalty discounts and rewards
- Highlight community growth and achievements

---

### 4. **Recent Subscribers** (1-3 months)
**Characteristics:**
- New to the brand
- High initial engagement
- Still learning about offerings
- Lifetime value: $0-100

**Win-Back Approach:**
- **Email 1:** Welcome back with onboarding focus
- **Email 2:** Quick wins and easy-to-use tools
- **Email 3:** Simple value proposition and clear benefits
- **Expected Recapture Rate:** 18-22%

**Customization:**
- Focus on onboarding and getting started
- Emphasize ease of use and quick wins
- Provide clear value proposition
- Offer guided setup and support

---

### 5. **Webinar Attendees** (Attended Past Webinars)
**Characteristics:**
- Engaged with live content
- Interested in learning
- Higher conversion potential
- Lifetime value: $200-800

**Win-Back Approach:**
- **Email 1:** Reference specific webinar they attended
- **Email 2:** Show new webinar series and advanced content
- **Email 3:** Exclusive access to upcoming sessions
- **Expected Recapture Rate:** 22-28%

**Customization:**
- Reference specific webinar topics
- Highlight new webinar series
- Offer exclusive access to recordings
- Include testimonials from other attendees

---

### 6. **Course Enrollers** (Started but Didn't Complete)
**Characteristics:**
- Showed initial commitment
- May have faced obstacles
- High potential for re-engagement
- Lifetime value: $300-1000

**Win-Back Approach:**
- **Email 1:** Acknowledge their learning journey
- **Email 2:** Show course improvements and new modules
- **Email 3:** Offer completion support and certification
- **Expected Recapture Rate:** 25-30%

**Customization:**
- Reference specific course they started
- Show new modules and improvements
- Offer completion support and coaching
- Highlight certification and career benefits

---

## Segmentation Implementation

### Data Collection Requirements
1. **Purchase History:** Track all transactions and product usage
2. **Engagement Metrics:** Monitor opens, clicks, and interactions
3. **Subscription Date:** Track when they first subscribed
4. **Content Consumption:** Monitor which content they accessed
5. **Behavioral Data:** Track website visits and feature usage

### Segmentation Rules
```
IF subscriber.purchase_history > 0:
    segment = "high_value"
ELIF subscriber.subscription_date < 6_months_ago:
    segment = "long_time"
ELIF subscriber.subscription_date > 1_month_ago:
    segment = "recent"
ELIF subscriber.webinar_attendance > 0:
    segment = "webinar_attendee"
ELIF subscriber.course_enrollment > 0:
    segment = "course_enroller"
ELSE:
    segment = "free_subscriber"
```

### Personalization Variables
- **First Name:** [FIRST_NAME]
- **Last Purchase:** [LAST_PURCHASE]
- **Subscription Date:** [SUBSCRIPTION_DATE]
- **Course Progress:** [COURSE_PROGRESS]
- **Webinar Attendance:** [WEBINAR_COUNT]
- **Lifetime Value:** [LTV]

---

## Performance Expectations by Segment

| Segment | Expected Open Rate | Expected CTR | Expected Recapture Rate |
|---------|-------------------|--------------|------------------------|
| High-Value | 30-35% | 15-20% | 25-30% |
| Free Subscribers | 20-25% | 8-12% | 15-20% |
| Long-Time | 25-30% | 12-16% | 20-25% |
| Recent | 22-27% | 10-14% | 18-22% |
| Webinar Attendees | 28-33% | 14-18% | 22-28% |
| Course Enrollers | 30-35% | 16-20% | 25-30% |

---

## Segmentation Testing Strategy

### Phase 1: Basic Segmentation (Week 1-2)
- Test 3 main segments: High-Value, Free, Long-Time
- Use original email content with segment-specific personalization
- Measure performance differences

### Phase 2: Advanced Segmentation (Week 3-4)
- Add Webinar Attendees and Course Enrollers segments
- Customize content for each segment
- A/B test segment-specific messaging

### Phase 3: Micro-Segmentation (Week 5-6)
- Create sub-segments based on behavior patterns
- Test hyper-personalized content
- Optimize based on performance data

---

## Success Metrics by Segment

### High-Value Subscribers
- **Primary:** Revenue recovery and re-engagement
- **Secondary:** Upsell and cross-sell opportunities
- **Target:** 25% recapture rate, $200+ average order value

### Free Subscribers
- **Primary:** Conversion to paid subscribers
- **Secondary:** Engagement and community participation
- **Target:** 15% recapture rate, 5% conversion to paid

### Long-Time Subscribers
- **Primary:** Loyalty and retention
- **Secondary:** Referral and advocacy
- **Target:** 20% recapture rate, 10% referral rate

### Recent Subscribers
- **Primary:** Onboarding completion
- **Secondary:** Feature adoption and engagement
- **Target:** 18% recapture rate, 30% feature adoption

### Webinar Attendees
- **Primary:** Re-engagement with live content
- **Secondary:** Course enrollment and product purchase
- **Target:** 22% recapture rate, 15% course enrollment

### Course Enrollers
- **Primary:** Course completion and certification
- **Secondary:** Advanced course enrollment
- **Target:** 25% recapture rate, 40% course completion
