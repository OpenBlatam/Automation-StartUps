import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { 
  Calendar, 
  Clock, 
  Users, 
  Play, 
  BookOpen,
  Award,
  CheckCircle,
  Star,
  Video,
  Download
} from 'lucide-react';

const WebinarSchedule = ({ user, onEnroll }) => {
  const [webinars, setWebinars] = useState([]);
  const [enrolledWebinars, setEnrolledWebinars] = useState([]);
  const [loading, setLoading] = useState(true);

  const webinarModules = [
    {
      id: 'module-1-1',
      title: 'The Science Behind Effective Testimonials',
      description: 'Learn the psychology of social proof and what makes testimonials compelling',
      duration: '90 minutes',
      date: '2024-01-15',
      time: '14:00 EST',
      instructor: 'Dr. Sarah Johnson',
      level: 'Beginner',
      category: 'Foundations',
      module: 1,
      session: 1,
      topics: [
        'Psychology of social proof',
        'Elements of compelling testimonials',
        'AI vs. human-written testimonials',
        'Legal and ethical considerations'
      ],
      materials: [
        'Testimonial Psychology Guide',
        'AI Ethics Checklist',
        'Template Library Access'
      ],
      enrolled: false
    },
    {
      id: 'module-1-2',
      title: 'AI Tools for Testimonial Generation',
      description: 'Master the art of prompt engineering and AI model selection',
      duration: '90 minutes',
      date: '2024-01-17',
      time: '14:00 EST',
      instructor: 'Mark Chen',
      level: 'Beginner',
      category: 'Foundations',
      module: 1,
      session: 2,
      topics: [
        'Introduction to AI testimonial platforms',
        'Prompt engineering for testimonials',
        'Quality assessment techniques',
        'A/B testing testimonial variations'
      ],
      materials: [
        'Prompt Engineering Playbook',
        'AI Model Comparison Chart',
        'Quality Assessment Rubric'
      ],
      enrolled: false
    },
    {
      id: 'module-2-1',
      title: 'E-commerce Testimonial Mastery',
      description: 'Create testimonials that drive conversions in online retail',
      duration: '90 minutes',
      date: '2024-01-22',
      time: '14:00 EST',
      instructor: 'Lisa Rodriguez',
      level: 'Intermediate',
      category: 'Industry-Specific',
      module: 2,
      session: 1,
      topics: [
        'Product-specific testimonial templates',
        'Conversion optimization through testimonials',
        'Visual testimonial integration',
        'Review management strategies'
      ],
      materials: [
        'E-commerce Testimonial Templates',
        'Conversion Optimization Guide',
        'Visual Integration Toolkit'
      ],
      enrolled: false
    },
    {
      id: 'module-2-2',
      title: 'B2B Testimonial Excellence',
      description: 'Craft testimonials that resonate with business decision-makers',
      duration: '90 minutes',
      date: '2024-01-24',
      time: '14:00 EST',
      instructor: 'David Kim',
      level: 'Intermediate',
      category: 'Industry-Specific',
      module: 2,
      session: 2,
      topics: [
        'Case study testimonials',
        'ROI-focused testimonials',
        'Executive testimonial strategies',
        'Long-form testimonial content'
      ],
      materials: [
        'B2B Testimonial Framework',
        'ROI Calculation Templates',
        'Executive Interview Guide'
      ],
      enrolled: false
    },
    {
      id: 'module-3-1',
      title: 'Platform Deep Dive & Advanced Features',
      description: 'Master the full potential of our AI testimonial platform',
      duration: '90 minutes',
      date: '2024-01-29',
      time: '14:00 EST',
      instructor: 'Alex Thompson',
      level: 'Advanced',
      category: 'Platform Mastery',
      module: 3,
      session: 1,
      topics: [
        'Advanced prompt customization',
        'Bulk testimonial generation',
        'Integration with marketing tools',
        'Analytics and performance tracking'
      ],
      materials: [
        'Advanced Platform Guide',
        'Integration Documentation',
        'Analytics Dashboard Tutorial'
      ],
      enrolled: false
    },
    {
      id: 'module-3-2',
      title: 'Automation & Workflow Optimization',
      description: 'Streamline your testimonial creation process with automation',
      duration: '90 minutes',
      date: '2024-01-31',
      time: '14:00 EST',
      instructor: 'Rachel Green',
      level: 'Advanced',
      category: 'Platform Mastery',
      module: 3,
      session: 2,
      topics: [
        'Automated testimonial campaigns',
        'CRM integration strategies',
        'Multi-channel distribution',
        'Performance optimization'
      ],
      materials: [
        'Automation Playbook',
        'CRM Integration Guide',
        'Multi-channel Strategy Template'
      ],
      enrolled: false
    },
    {
      id: 'module-4-1',
      title: 'Campaign Implementation Workshop',
      description: 'Hands-on workshop to create and launch testimonial campaigns',
      duration: '120 minutes',
      date: '2024-02-05',
      time: '14:00 EST',
      instructor: 'Multiple Instructors',
      level: 'Advanced',
      category: 'Implementation',
      module: 4,
      session: 1,
      topics: [
        'Live testimonial campaign creation',
        'Q&A session with experts',
        'Peer review and feedback',
        'Troubleshooting common issues'
      ],
      materials: [
        'Campaign Creation Checklist',
        'Peer Review Guidelines',
        'Troubleshooting Guide'
      ],
      enrolled: false
    },
    {
      id: 'module-4-2',
      title: 'Scaling Your Testimonial Strategy',
      description: 'Take your testimonial strategy to enterprise level',
      duration: '90 minutes',
      date: '2024-02-07',
      time: '14:00 EST',
      instructor: 'CEO Panel',
      level: 'Advanced',
      category: 'Implementation',
      module: 4,
      session: 2,
      topics: [
        'Enterprise-level testimonial strategies',
        'Team collaboration features',
        'Advanced analytics and reporting',
        'Future trends in AI testimonials'
      ],
      materials: [
        'Enterprise Strategy Guide',
        'Team Collaboration Manual',
        'Future Trends Report'
      ],
      enrolled: false
    }
  ];

  useEffect(() => {
    // Simulate loading user's enrolled webinars
    setTimeout(() => {
      setWebinars(webinarModules);
      setEnrolledWebinars([]); // Would be loaded from API
      setLoading(false);
    }, 1000);
  }, []);

  const handleEnroll = async (webinarId) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setEnrolledWebinars(prev => [...prev, webinarId]);
      setWebinars(prev => prev.map(webinar => 
        webinar.id === webinarId 
          ? { ...webinar, enrolled: true }
          : webinar
      ));
      
      if (onEnroll) {
        onEnroll(webinarId);
      }
    } catch (error) {
      console.error('Failed to enroll:', error);
    }
  };

  const getModuleColor = (module) => {
    const colors = {
      1: 'bg-blue-100 text-blue-800',
      2: 'bg-green-100 text-green-800',
      3: 'bg-purple-100 text-purple-800',
      4: 'bg-orange-100 text-orange-800'
    };
    return colors[module] || 'bg-gray-100 text-gray-800';
  };

  const getLevelColor = (level) => {
    const colors = {
      'Beginner': 'bg-green-100 text-green-800',
      'Intermediate': 'bg-yellow-100 text-yellow-800',
      'Advanced': 'bg-red-100 text-red-800'
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI Testimonial Writing Course
        </h1>
        <p className="text-gray-600 mb-4">
          Master the art of AI-powered testimonial writing with our comprehensive 8-week program
        </p>
        <div className="flex items-center justify-center space-x-6 text-sm text-gray-500">
          <div className="flex items-center space-x-1">
            <Calendar className="w-4 h-4" />
            <span>8 Weeks</span>
          </div>
          <div className="flex items-center space-x-1">
            <Video className="w-4 h-4" />
            <span>16 Live Sessions</span>
          </div>
          <div className="flex items-center space-x-1">
            <Award className="w-4 h-4" />
            <span>Certification</span>
          </div>
        </div>
      </div>

      {/* Course Progress */}
      <Card className="mb-8">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Course Progress</h3>
            <Badge variant="outline">
              {enrolledWebinars.length} of {webinars.length} sessions enrolled
            </Badge>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(enrolledWebinars.length / webinars.length) * 100}%` }}
            ></div>
          </div>
        </CardContent>
      </Card>

      {/* Webinar Modules */}
      <div className="space-y-8">
        {[1, 2, 3, 4].map(moduleNumber => {
          const moduleWebinars = webinars.filter(w => w.module === moduleNumber);
          const moduleTitle = {
            1: 'Foundations of AI Testimonial Writing',
            2: 'Advanced Testimonial Strategies',
            3: 'SaaS Platform Mastery',
            4: 'Implementation & Scaling'
          };

          return (
            <div key={moduleNumber}>
              <div className="flex items-center space-x-3 mb-6">
                <Badge className={getModuleColor(moduleNumber)}>
                  Module {moduleNumber}
                </Badge>
                <h2 className="text-2xl font-bold text-gray-900">
                  {moduleTitle[moduleNumber]}
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {moduleWebinars.map(webinar => (
                  <Card key={webinar.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg mb-2">{webinar.title}</CardTitle>
                          <p className="text-gray-600 text-sm mb-3">{webinar.description}</p>
                        </div>
                        {webinar.enrolled && (
                          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                        )}
                      </div>
                      
                      <div className="flex flex-wrap gap-2 mb-4">
                        <Badge className={getLevelColor(webinar.level)}>
                          {webinar.level}
                        </Badge>
                        <Badge variant="outline">
                          {webinar.duration}
                        </Badge>
                        <Badge variant="outline">
                          {webinar.category}
                        </Badge>
                      </div>
                    </CardHeader>

                    <CardContent>
                      {/* Session Details */}
                      <div className="space-y-3 mb-4">
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(webinar.date).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Clock className="w-4 h-4" />
                          <span>{webinar.time}</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Users className="w-4 h-4" />
                          <span>Instructor: {webinar.instructor}</span>
                        </div>
                      </div>

                      {/* Topics */}
                      <div className="mb-4">
                        <h4 className="font-medium text-gray-700 mb-2">Topics Covered:</h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {webinar.topics.map((topic, index) => (
                            <li key={index} className="flex items-start space-x-2">
                              <span className="text-blue-500 mt-1">•</span>
                              <span>{topic}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Materials */}
                      <div className="mb-4">
                        <h4 className="font-medium text-gray-700 mb-2">Course Materials:</h4>
                        <div className="flex flex-wrap gap-1">
                          {webinar.materials.map((material, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {material}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex space-x-2">
                        {webinar.enrolled ? (
                          <>
                            <Button className="flex-1" disabled>
                              <CheckCircle className="w-4 h-4 mr-2" />
                              Enrolled
                            </Button>
                            <Button variant="outline" size="sm">
                              <Download className="w-4 h-4" />
                            </Button>
                          </>
                        ) : (
                          <Button 
                            className="flex-1"
                            onClick={() => handleEnroll(webinar.id)}
                          >
                            <BookOpen className="w-4 h-4 mr-2" />
                            Enroll Now
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Certification Info */}
      <Card className="mt-8">
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <Award className="w-12 h-12 text-yellow-500" />
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                AI Testimonial Writing Specialist Certificate
              </h3>
              <p className="text-gray-600 mb-4">
                Complete all course modules and pass the final exam to earn your certification
              </p>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span>• Industry-recognized certification</span>
                <span>• LinkedIn badge</span>
                <span>• Continuing education credits</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default WebinarSchedule;



