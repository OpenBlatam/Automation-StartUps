---
title: "Quick Start Guide"
category: "06_documentation"
tags: ["guide"]
created: "2025-10-29"
path: "06_documentation/Quick_start_guides/quick_start_guide.md"
---

# 🚀 Quick Start Guide: Referral Contest Email System

## ⚡ Get Started in 15 Minutes

### Prerequisites
- Node.js 16+ installed
- SendGrid account (free tier available)
- Basic understanding of JavaScript
- Access to your user database

### Step 1: Project Setup (2 minutes)

```bash
# Create project directory
mkdir referral-contest-system
cd referral-contest-system

# Initialize project
npm init -y

# Install dependencies
npm install @sendgrid/mail express nodemailer dotenv
npm install --save-dev nodemon

# Create project structure
mkdir src templates scripts config
```

### Step 2: Environment Configuration (1 minute)

Create `.env` file:
```env
# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=contests@yourcompany.com
FROM_NAME=Your Company Name

# Database Configuration
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_database

# Application Configuration
APP_URL=https://yourdomain.com
CONTEST_DURATION=7
CONTEST_BENEFIT=$500 cash prize
```

### Step 3: Basic Email Service (3 minutes)

Create `src/emailService.js`:
```javascript
const sgMail = require('@sendgrid/mail');
require('dotenv').config();

sgMail.setApiKey(process.env.SENDGRID_API_KEY);

class EmailService {
    constructor() {
        this.fromEmail = process.env.FROM_EMAIL;
        this.fromName = process.env.FROM_NAME;
    }

    async sendContestInvitation(user, contestData) {
        const msg = {
            to: user.email,
            from: {
                email: this.fromEmail,
                name: this.fromName
            },
            subject: `🎉 ${user.first_name}, You're Invited to Win ${contestData.benefit}!`,
            html: this.generateEmailHTML(user, contestData),
            templateId: 'referral-contest-template'
        };

        try {
            await sgMail.send(msg);
            console.log(`✅ Email sent to ${user.email}`);
            return { success: true };
        } catch (error) {
            console.error(`❌ Email failed for ${user.email}:`, error);
            return { success: false, error: error.message };
        }
    }

    generateEmailHTML(user, contestData) {
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Referral Contest Invitation</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2c3e50;">🎉 Exclusive Referral Contest</h1>
                <p style="color: #7f8c8d;">You're invited to participate!</p>
            </div>

            <div style="margin-bottom: 25px;">
                <p>Hi ${user.first_name},</p>
                <p>I hope this email finds you well! I'm excited to share something special with you.</p>
            </div>

            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #2c3e50; margin-top: 0;">🎯 What You Can Win:</h2>
                <p style="font-size: 18px; font-weight: bold; color: #e74c3c;">${contestData.benefit}</p>
                
                <h3 style="color: #2c3e50;">🚀 How It Works:</h3>
                <ol style="color: #34495e;">
                    <li>Share your unique referral link with friends</li>
                    <li>Each successful referral earns you points</li>
                    <li>The more referrals, the higher your chances of winning!</li>
                </ol>
            </div>

            <div style="background-color: #3498db; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 25px;">
                <h3 style="margin-top: 0;">Your Personal Referral Link:</h3>
                <p style="font-size: 16px; word-break: break-all; background-color: white; color: #2c3e50; padding: 10px; border-radius: 4px;">${contestData.referralLink}</p>
            </div>

            <div style="text-align: center; margin-bottom: 30px;">
                <a href="${contestData.ctaLink}" style="background-color: #e74c3c; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px; display: inline-block;">Start Referring Now</a>
            </div>

            <div style="border-top: 1px solid #bdc3c7; padding-top: 20px; text-align: center; color: #7f8c8d;">
                <p>Best regards,<br>${this.fromName}</p>
            </div>

        </body>
        </html>
        `;
    }
}

module.exports = EmailService;
```

### Step 4: Contest Manager (5 minutes)

Create `src/contestManager.js`:
```javascript
const EmailService = require('./emailService');
const crypto = require('crypto');

class ContestManager {
    constructor() {
        this.emailService = new EmailService();
        this.contests = new Map();
    }

    createContest(contestData) {
        const contestId = crypto.randomUUID();
        const contest = {
            id: contestId,
            name: contestData.name,
            benefit: contestData.benefit,
            duration: contestData.duration || 7,
            startDate: new Date(),
            endDate: new Date(Date.now() + (contestData.duration || 7) * 24 * 60 * 60 * 1000),
            participants: new Map(),
            status: 'active'
        };

        this.contests.set(contestId, contest);
        return contest;
    }

    addParticipant(contestId, user) {
        const contest = this.contests.get(contestId);
        if (!contest) throw new Error('Contest not found');

        const referralLink = this.generateReferralLink(contestId, user.id);
        const participant = {
            userId: user.id,
            email: user.email,
            firstName: user.first_name,
            referralLink: referralLink,
            referrals: 0,
            points: 0,
            joinedAt: new Date()
        };

        contest.participants.set(user.id, participant);
        return participant;
    }

    generateReferralLink(contestId, userId) {
        const baseUrl = process.env.APP_URL || 'https://yourdomain.com';
        return `${baseUrl}/contest/${contestId}/ref/${userId}`;
    }

    async sendContestInvitations(contestId, users) {
        const contest = this.contests.get(contestId);
        if (!contest) throw new Error('Contest not found');

        const results = [];
        
        for (const user of users) {
            // Add user to contest
            const participant = this.addParticipant(contestId, user);
            
            // Send invitation email
            const contestData = {
                benefit: contest.benefit,
                referralLink: participant.referralLink,
                ctaLink: `${process.env.APP_URL}/contest/${contestId}`,
                duration: contest.duration
            };

            const result = await this.emailService.sendContestInvitation(user, contestData);
            results.push({
                userId: user.id,
                email: user.email,
                success: result.success,
                error: result.error
            });
        }

        return results;
    }

    getContestStats(contestId) {
        const contest = this.contests.get(contestId);
        if (!contest) throw new Error('Contest not found');

        const participants = Array.from(contest.participants.values());
        const totalReferrals = participants.reduce((sum, p) => sum + p.referrals, 0);

        return {
            contestId: contestId,
            totalParticipants: participants.length,
            totalReferrals: totalReferrals,
            averageReferrals: participants.length > 0 ? (totalReferrals / participants.length).toFixed(2) : 0,
            topParticipants: participants
                .sort((a, b) => b.referrals - a.referrals)
                .slice(0, 10)
        };
    }
}

module.exports = ContestManager;
```

### Step 5: Main Application (3 minutes)

Create `src/app.js`:
```javascript
const express = require('express');
const ContestManager = require('./contestManager');
require('dotenv').config();

const app = express();
const contestManager = new ContestManager();

app.use(express.json());

// Create a new contest
app.post('/api/contests', (req, res) => {
    try {
        const contest = contestManager.createContest(req.body);
        res.json({ success: true, contest });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Send contest invitations
app.post('/api/contests/:contestId/invite', async (req, res) => {
    try {
        const { contestId } = req.params;
        const { users } = req.body;
        
        const results = await contestManager.sendContestInvitations(contestId, users);
        res.json({ success: true, results });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// Get contest statistics
app.get('/api/contests/:contestId/stats', (req, res) => {
    try {
        const { contestId } = req.params;
        const stats = contestManager.getContestStats(contestId);
        res.json({ success: true, stats });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`📧 Referral contest system ready!`);
});
```

### Step 6: Test Script (1 minute)

Create `scripts/test-campaign.js`:
```javascript
const ContestManager = require('../src/contestManager');

async function testCampaign() {
    const contestManager = new ContestManager();
    
    // Create test contest
    const contest = contestManager.createContest({
        name: 'Holiday Referral Contest',
        benefit: '$500 cash prize',
        duration: 7
    });
    
    console.log('✅ Contest created:', contest.id);
    
    // Test users
    const testUsers = [
        { id: '1', email: 'test1@example.com', first_name: 'John' },
        { id: '2', email: 'test2@example.com', first_name: 'Sarah' },
        { id: '3', email: 'test3@example.com', first_name: 'Mike' }
    ];
    
    // Send invitations
    const results = await contestManager.sendContestInvitations(contest.id, testUsers);
    
    console.log('📧 Email results:');
    results.forEach(result => {
        console.log(`${result.success ? '✅' : '❌'} ${result.email}: ${result.success ? 'Sent' : result.error}`);
    });
    
    // Get stats
    const stats = contestManager.getContestStats(contest.id);
    console.log('📊 Contest stats:', stats);
}

testCampaign().catch(console.error);
```

### Step 7: Run Your First Campaign

```bash
# Start the server
npm start

# In another terminal, run the test
node scripts/test-campaign.js
```

## 🎯 Next Steps

### Immediate Actions (Next 30 minutes)
1. **Customize Templates**: Edit the email HTML in `emailService.js`
2. **Add Your Branding**: Update colors, fonts, and logo
3. **Test with Real Users**: Replace test emails with real user data
4. **Set Up Database**: Connect to your user database

### Advanced Features (Next Week)
1. **AI Personalization**: Implement dynamic content based on user behavior
2. **A/B Testing**: Set up automated testing for subject lines and content
3. **Analytics Dashboard**: Track open rates, click rates, and conversions
4. **Automated Follow-ups**: Create email sequences for different user segments

### Course Integration
This quick start guide is part of **Module 4: Email Marketing AI** of our AI Marketing Mastery Course. Students will:

- **Week 4, Session 1**: Build this system during live coding session
- **Week 4, Session 2**: Add AI personalization and segmentation
- **Week 4, Session 3**: Implement A/B testing and optimization
- **Week 4, Session 4**: Create analytics dashboard and reporting

## 📚 Learning Resources

### Required Reading
- [Email Templates Library](./email-templates-library.md)
- [AI Personalization Guide](./ai-personalization-guide.md)
- [A/B Testing Framework](./ab-testing-framework.md)

### Video Tutorials (Course Students)
- **Video 4.1**: AI Email Subject Line Optimization
- **Video 4.2**: Personalization at Scale
- **Video 4.3**: Email Sequence Automation

### Tools and Platforms
- **SendGrid**: Email delivery service
- **Express.js**: Web framework
- **Node.js**: Runtime environment
- **MongoDB/PostgreSQL**: Database options

## 🆘 Support

### Common Issues
1. **Emails not sending**: Check SendGrid API key and domain verification
2. **Template not rendering**: Verify HTML syntax and variable names
3. **Database connection**: Ensure credentials are correct in `.env`

### Getting Help
- **Course Students**: Use private Discord community
- **General Support**: Email support@yourcompany.com
- **Documentation**: Check troubleshooting guide

---

**🎓 Ready to master AI-powered email marketing? Enroll in our AI Marketing Mastery Course and build advanced systems like this one!**

*Next: [Email Templates Library](./email-templates-library.md)*



