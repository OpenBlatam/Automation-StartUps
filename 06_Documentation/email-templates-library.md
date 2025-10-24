# Email Templates Library

## Overview
This library contains ready-to-use email templates for referral contest campaigns, organized by user segment and campaign stage.

## Template Categories

### 1. Contest Invitation Templates

#### Power User Template
```html
Subject: 🏆 {first_name}, You're Our Referral Champion - Exclusive Contest Inside!

Hi {first_name},

As one of our top users with {total_referrals} successful referrals, you're automatically invited to our exclusive referral contest!

🎯 **Your Exclusive Benefits:**
- {premium_benefit}
- Leaderboard recognition
- Early access to new features

{referral_link}

{action}

Best,
{your_name}
```

#### New User Template
```html
Subject: 🎉 Welcome to Our Community - Join Our Referral Contest!

Hi {first_name},

Welcome to {company_name}! Since you joined us {days_since_join} days ago, we'd love to help you get the most out of our platform.

🎁 **Perfect for New Users:**
- {beginner_benefit}
- Step-by-step guidance
- Community support

{referral_link}

{action}

Welcome aboard!
{your_name}
```

#### Inactive User Template
```html
Subject: 👋 We Miss You, {first_name} - Come Back & Win {benefit}!

Hi {first_name},

We noticed you haven't been active lately. To welcome you back, we're offering you a special spot in our referral contest!

🔄 **Comeback Special:**
- {comeback_benefit}
- Double points for your first 3 referrals
- Personal onboarding session

{referral_link}

{action}

We're here to help!
{your_name}
```

### 2. Follow-up Email Templates

#### Progress Update (Day 2)
```html
Subject: 📊 {first_name}, Your Contest Progress - {current_referrals} Referrals!

Hi {first_name},

Great progress! You've made {current_referrals} referrals so far.

📈 **Your Stats:**
- Current position: #{current_position}
- Referrals made: {current_referrals}
- Points earned: {points_earned}
- Time remaining: {time_remaining}

{referral_link}

Keep it up!
{your_name}
```

#### Urgency Push (Day 5)
```html
Subject: ⏰ {first_name}, 48 Hours Left - Don't Miss {benefit}!

Hi {first_name},

The contest ends in 48 hours! You're currently #{current_position} with {current_referrals} referrals.

🚀 **Final Push:**
- Only {referrals_needed} more referrals to reach the next tier
- {time_remaining} remaining
- {current_participants} people competing

{referral_link}

{action}

{your_name}
```

#### Final Reminder (Day 7)
```html
Subject: 🔔 Final Hours - {first_name}, Last Chance to Win!

Hi {first_name},

This is it! The contest ends in {final_hours} hours.

🏁 **Final Stats:**
- Your referrals: {current_referrals}
- Your position: #{current_position}
- Prize: {benefit}

{referral_link}

{action}

Good luck!
{your_name}
```

### 3. Thank You Templates

#### Contest Winner
```html
Subject: 🎉 Congratulations {first_name} - You Won {benefit}!

Hi {first_name},

Congratulations! You've won our referral contest!

🏆 **Your Prize:**
{benefit}

📊 **Final Stats:**
- Total referrals: {final_referrals}
- Final position: #{final_position}
- Points earned: {final_points}

We'll be in touch soon to deliver your prize!

Thank you for being an amazing community member!

{your_name}
```

#### Contest Participant
```html
Subject: 👏 Thank You {first_name} - Contest Results Inside!

Hi {first_name},

Thank you for participating in our referral contest!

📊 **Your Results:**
- Total referrals: {final_referrals}
- Final position: #{final_position}
- Points earned: {final_points}

While you didn't win this time, you're still a valued member of our community. Keep an eye out for future contests!

{your_name}
```

### 4. Specialized Templates

#### Milestone Achievement
```html
Subject: 🎯 {first_name}, You've Reached {milestone} Referrals!

Hi {first_name},

Amazing work! You've just reached {milestone} referrals in our contest.

🎊 **Milestone Reward:**
{milestone_benefit}

📈 **Keep Going:**
- Current position: #{current_position}
- Next milestone: {next_milestone}
- Time remaining: {time_remaining}

{referral_link}

{action}

{your_name}
```

#### Social Proof Template
```html
Subject: 👥 {first_name}, {friends_count} of Your Friends Are Already Participating!

Hi {first_name},

Great news! {friends_count} of your friends are already participating in our referral contest.

🤝 **Join Your Friends:**
- {friend_1_name} is currently #{friend_1_position}
- {friend_2_name} has made {friend_2_referrals} referrals
- {friend_3_name} is in the top 10!

{referral_link}

{action}

{your_name}
```

## Template Variables Reference

### Core Variables
```javascript
const templateVariables = {
    // User Information
    first_name: "John",
    last_name: "Doe",
    email: "john@example.com",
    
    // Contest Information
    benefit: "$500 cash prize",
    referral_link: "https://app.example.com/ref/abc123",
    action: "Start Referring Now",
    cta_link: "https://app.example.com/contest",
    
    // Progress Tracking
    current_referrals: 5,
    total_referrals: 12,
    current_position: 15,
    points_earned: 150,
    
    // Time Information
    time_remaining: "3 days, 12 hours",
    final_hours: "6 hours",
    days_since_join: 45,
    
    // Contest Details
    current_participants: 1247,
    contest_duration: "7 days",
    announcement_date: "December 15, 2023",
    
    // Milestones
    milestone: "10 referrals",
    next_milestone: "15 referrals",
    milestone_benefit: "Bonus 50 points",
    
    // Social Proof
    friends_count: 3,
    friend_1_name: "Sarah",
    friend_1_position: 8,
    friend_2_name: "Mike",
    friend_2_referrals: 7,
    friend_3_name: "Lisa",
    
    // Benefits by User Type
    premium_benefit: "Exclusive premium features + $200 cash",
    beginner_benefit: "Free premium upgrade + $100 cash",
    comeback_benefit: "Double points + $150 cash",
    
    // Company Information
    your_name: "Sarah Johnson",
    company_name: "YourSaaS App"
};
```

## Template Customization Examples

### Dynamic Subject Lines
```javascript
function generateSubjectLine(user, template) {
    const timeOfDay = getTimeOfDay();
    const userTier = user.tier;
    
    const subjectTemplates = {
        morning: {
            power_user: "🌅 Good morning {first_name} - Ready to dominate our contest?",
            new_user: "☀️ Morning {first_name} - Start your day with our contest!",
            default: "🌅 {first_name}, morning contest update inside!"
        },
        afternoon: {
            power_user: "🚀 {first_name}, afternoon power move - contest update!",
            new_user: "📈 {first_name}, perfect time to join our contest!",
            default: "📊 {first_name}, your contest progress update!"
        },
        evening: {
            power_user: "🌙 {first_name}, evening contest strategy inside!",
            new_user: "🌆 {first_name}, wind down with our contest!",
            default: "🌙 {first_name}, evening contest reminder!"
        }
    };
    
    return subjectTemplates[timeOfDay][userTier] || subjectTemplates[timeOfDay].default;
}
```

### Dynamic CTA Buttons
```javascript
function generateCTA(user, context) {
    const ctas = {
        power_user: {
            initial: "Dominate the Contest",
            reminder: "Maintain Your Lead",
            urgency: "Secure Victory"
        },
        new_user: {
            initial: "Get Started",
            reminder: "Keep Going",
            urgency: "Final Push"
        },
        inactive_user: {
            initial: "Come Back & Win",
            reminder: "Rejoin the Contest",
            urgency: "Last Chance"
        }
    };
    
    return ctas[user.segment][context] || "Join Now";
}
```

## Template Testing Framework

### A/B Test Configurations
```javascript
const abTestConfigs = {
    subjectLineTest: {
        name: "Subject Line Optimization",
        variants: [
            {
                id: "A",
                subject: "🎉 {first_name}, You're Invited to Win {benefit}!",
                weight: 50
            },
            {
                id: "B", 
                subject: "{first_name}, Exclusive Contest - {benefit} Awaits!",
                weight: 50
            }
        ],
        metrics: ["open_rate", "click_rate"]
    },
    
    ctaTest: {
        name: "CTA Button Optimization",
        variants: [
            {
                id: "A",
                text: "Start Referring Now",
                color: "#e74c3c",
                weight: 50
            },
            {
                id: "B",
                text: "Join the Contest",
                color: "#3498db", 
                weight: 50
            }
        ],
        metrics: ["click_rate", "conversion_rate"]
    },
    
    benefitTest: {
        name: "Benefit Presentation",
        variants: [
            {
                id: "A",
                benefit: "$500 cash prize",
                weight: 50
            },
            {
                id: "B",
                benefit: "Free premium subscription + $200 cash",
                weight: 50
            }
        ],
        metrics: ["open_rate", "click_rate", "conversion_rate"]
    }
};
```

### Template Performance Tracking
```javascript
async function trackTemplatePerformance(templateId, userId, action) {
    const metrics = {
        template_id: templateId,
        user_id: userId,
        action: action, // 'sent', 'opened', 'clicked', 'converted'
        timestamp: new Date(),
        user_segment: getUserSegment(userId),
        ab_test_variant: getABTestVariant(userId, templateId)
    };
    
    await db.template_metrics.insert(metrics);
    
    // Update template statistics
    await updateTemplateStats(templateId, action);
}

async function getTemplatePerformanceReport(templateId, dateRange) {
    const metrics = await db.template_metrics.find({
        template_id: templateId,
        timestamp: { $gte: dateRange.start, $lte: dateRange.end }
    });
    
    const stats = {
        sent: metrics.filter(m => m.action === 'sent').length,
        opened: metrics.filter(m => m.action === 'opened').length,
        clicked: metrics.filter(m => m.action === 'clicked').length,
        converted: metrics.filter(m => m.action === 'converted').length
    };
    
    return {
        template_id: templateId,
        date_range: dateRange,
        open_rate: (stats.opened / stats.sent * 100).toFixed(2),
        click_rate: (stats.clicked / stats.sent * 100).toFixed(2),
        conversion_rate: (stats.converted / stats.clicked * 100).toFixed(2),
        total_sent: stats.sent
    };
}
```

## Template Implementation Guide

### 1. Template Selection Logic
```javascript
function selectTemplate(user, campaignStage) {
    const userSegment = getUserSegment(user);
    const stage = campaignStage;
    
    const templateMap = {
        'power_user': {
            'initial': 'power_user_invitation',
            'reminder': 'power_user_progress',
            'urgency': 'power_user_final',
            'thank_you': 'power_user_winner'
        },
        'new_user': {
            'initial': 'new_user_invitation',
            'reminder': 'new_user_progress',
            'urgency': 'new_user_final',
            'thank_you': 'new_user_participant'
        },
        'inactive_user': {
            'initial': 'inactive_user_comeback',
            'reminder': 'inactive_user_progress',
            'urgency': 'inactive_user_final',
            'thank_you': 'inactive_user_participant'
        }
    };
    
    return templateMap[userSegment][stage] || 'default_template';
}
```

### 2. Template Rendering
```javascript
async function renderTemplate(templateId, user, variables) {
    const template = await getTemplate(templateId);
    const personalizedVariables = await getPersonalizedVariables(user);
    
    const allVariables = {
        ...templateVariables,
        ...personalizedVariables,
        ...variables
    };
    
    let renderedTemplate = template.content;
    
    // Replace variables
    Object.keys(allVariables).forEach(key => {
        const regex = new RegExp(`{${key}}`, 'g');
        renderedTemplate = renderedTemplate.replace(regex, allVariables[key]);
    });
    
    return renderedTemplate;
}
```

### 3. Template Validation
```javascript
function validateTemplate(template) {
    const errors = [];
    
    // Check for required variables
    const requiredVariables = ['first_name', 'referral_link', 'action'];
    requiredVariables.forEach(variable => {
        if (!template.content.includes(`{${variable}}`)) {
            errors.push(`Missing required variable: {${variable}}`);
        }
    });
    
    // Check for proper HTML structure
    if (!template.content.includes('<html>')) {
        errors.push('Template must include proper HTML structure');
    }
    
    // Check for CTA button
    if (!template.content.includes('href=') || !template.content.includes('{action}')) {
        errors.push('Template must include a call-to-action button');
    }
    
    return {
        isValid: errors.length === 0,
        errors: errors
    };
}
```

---

*This template library is part of the SaaS Marketing Automation System. For updates and support, contact the development team.*



