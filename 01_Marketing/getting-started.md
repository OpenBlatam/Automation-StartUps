# 🚀 Getting Started
## Quick Start Guide for AI Marketing Course & SaaS Platform

Welcome to the AI Marketing Course & SaaS Platform! This guide will help you get up and running quickly.

---

## 📋 Prerequisites

Before you begin, ensure you have:

- **Node.js 18+** installed on your system
- **npm or yarn** package manager
- **PostgreSQL** database (local or cloud)
- **Copy.ai API key** (get one at [copy.ai](https://copy.ai))
- **Git** for version control

---

## ⚡ Quick Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/ai-marketing-course-saas.git
cd ai-marketing-course-saas
```

### **2. Install Dependencies**
```bash
npm install
# or
yarn install
```

### **3. Set Up Environment Variables**
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/ai_marketing_saas

# Copy.ai API
COPY_AI_API_KEY=your_copy_ai_api_key_here

# JWT Secret
JWT_SECRET=your_super_secret_jwt_key

# Email Service (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# File Storage (optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket
```

### **4. Set Up the Database**
```bash
# Run migrations
npm run db:migrate

# Seed initial data
npm run db:seed
```

### **5. Start the Development Server**
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

---

## 🎯 First Steps

### **1. Create Your Account**
1. Open `http://localhost:3000` in your browser
2. Click "Sign Up" to create a new account
3. Verify your email address
4. Complete your profile setup

### **2. Set Up Copy.ai Integration**
1. Go to Settings > Integrations
2. Enter your Copy.ai API key
3. Test the connection
4. Configure your preferences

### **3. Explore the Platform**
- **Dashboard**: Overview of your activities
- **Course**: Access to AI marketing courses
- **Content Generator**: Create marketing content
- **Sales Policies**: Generate sales policy frameworks
- **Templates**: Manage your content templates

---

## 📚 Course Quick Start

### **Module 1: AI Marketing Fundamentals**
1. Navigate to the Course section
2. Start with Module 1
3. Complete the interactive lessons
4. Take the assessment quiz
5. Move to the next module

### **Key Learning Objectives**
- Understand AI applications in marketing
- Master copy.ai platform capabilities
- Learn prompt engineering techniques
- Develop AI-driven content strategies

---

## 🛠️ SaaS Platform Quick Start

### **Generate Your First Sales Policy**
1. Go to Sales Policies > Create New
2. Select a template (Basic, Industry-Specific, or Enterprise)
3. Fill in your company information
4. Customize the policy parameters
5. Generate the policy using AI
6. Review and download the document

### **Create Marketing Content**
1. Navigate to Content Generator
2. Choose content type (Email, Social Media, Blog Post, etc.)
3. Select a template or create custom
4. Enter your requirements
5. Generate content with AI
6. Edit and customize as needed

---

## 🔧 Configuration

### **User Settings**
- **Profile**: Update your personal information
- **Preferences**: Configure platform settings
- **Integrations**: Manage third-party connections
- **Billing**: Manage subscription and payments

### **Team Settings** (Pro/Enterprise)
- **Team Members**: Invite and manage team members
- **Permissions**: Set user roles and permissions
- **Workspaces**: Organize projects and content
- **Branding**: Customize platform appearance

---

## 📊 Dashboard Overview

### **Main Dashboard**
- **Recent Activity**: Your latest actions and content
- **Quick Actions**: Common tasks and shortcuts
- **Analytics**: Performance metrics and insights
- **Notifications**: Important updates and alerts

### **Content Dashboard**
- **Generated Content**: All your AI-generated content
- **Templates**: Your saved templates
- **Favorites**: Bookmarked content and templates
- **Recent**: Recently accessed items

---

## 🎓 Course Dashboard

### **Progress Tracking**
- **Module Progress**: Track completion of each module
- **Assessment Scores**: View quiz and project scores
- **Certificates**: Download completion certificates
- **Learning Path**: Recommended next steps

### **Course Materials**
- **Video Lessons**: Interactive video content
- **Reading Materials**: PDFs and articles
- **Exercises**: Hands-on practice activities
- **Projects**: Real-world application projects

---

## 🚨 Troubleshooting

### **Common Issues**

#### **Database Connection Error**
```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Start PostgreSQL if needed
sudo service postgresql start
```

#### **Copy.ai API Error**
- Verify your API key is correct
- Check your API usage limits
- Ensure you have sufficient credits

#### **Port Already in Use**
```bash
# Kill process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
PORT=3001 npm run dev
```

### **Getting Help**
- **Documentation**: Check the full documentation
- **FAQ**: Common questions and answers
- **Support**: Contact our support team
- **Community**: Join our Discord community

---

## 🔄 Next Steps

### **Immediate Actions**
1. **Complete Profile Setup**: Add all required information
2. **Test Copy.ai Integration**: Generate your first content
3. **Start Course Module 1**: Begin your AI marketing journey
4. **Create First Sales Policy**: Generate a policy for your company

### **Short-term Goals**
1. **Complete Course Modules**: Finish all 4 modules
2. **Generate Content Regularly**: Use the platform daily
3. **Customize Templates**: Create your own templates
4. **Invite Team Members**: Set up team collaboration

### **Long-term Goals**
1. **Achieve Certification**: Complete the certification program
2. **Build Content Library**: Create a comprehensive content library
3. **Optimize Workflows**: Streamline your marketing processes
4. **Scale Operations**: Use advanced features for growth

---

## 📞 Support

If you need help getting started:

- **Email**: support@ai-marketing-saas.com
- **Discord**: [Join our community](https://discord.gg/ai-marketing-saas)
- **Documentation**: [Full documentation](./README.md)
- **Video Tutorials**: [YouTube channel](https://youtube.com/ai-marketing-saas)

---

*Welcome to the future of AI-powered marketing! 🚀*

