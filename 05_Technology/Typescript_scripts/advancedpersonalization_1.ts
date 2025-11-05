import express from 'express';
import { advancedPersonalizationService } from '../services/advancedPersonalizationService';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// Obtener perfiles
router.get('/profiles', authenticateToken, (req, res) => {
  try {
    const { limit = 50, segment, region, industry } = req.query;
    
    // En una implementación real, esto vendría de una base de datos
    const profiles = []; // Placeholder
    
    res.json({
      success: true,
      data: profiles,
      count: profiles.length
    });
  } catch (error) {
    console.error('Error fetching personalization profiles:', error);
    res.status(500).json({ error: 'Failed to fetch personalization profiles' });
  }
});

// Obtener perfil específico
router.get('/profiles/:customerId', authenticateToken, (req, res) => {
  try {
    const { customerId } = req.params;
    const profile = advancedPersonalizationService.getProfile(customerId);
    
    if (!profile) {
      return res.status(404).json({ error: 'Personalization profile not found' });
    }
    
    res.json({
      success: true,
      data: profile
    });
  } catch (error) {
    console.error('Error fetching personalization profile:', error);
    res.status(500).json({ error: 'Failed to fetch personalization profile' });
  }
});

// Crear perfil
router.post('/profiles', authenticateToken, (req, res) => {
  try {
    const { customerId, email, ...initialData } = req.body;
    
    if (!customerId || !email) {
      return res.status(400).json({ 
        error: 'Missing required fields: customerId, email' 
      });
    }
    
    const profileId = advancedPersonalizationService.createProfile(customerId, email, initialData);
    
    res.status(201).json({
      success: true,
      data: { id: profileId },
      message: 'Personalization profile created successfully'
    });
  } catch (error) {
    console.error('Error creating personalization profile:', error);
    res.status(500).json({ error: 'Failed to create personalization profile' });
  }
});

// Actualizar perfil
router.put('/profiles/:customerId', authenticateToken, (req, res) => {
  try {
    const { customerId } = req.params;
    const updates = req.body;
    
    advancedPersonalizationService.updateProfile(customerId, updates);
    
    res.json({
      success: true,
      message: 'Personalization profile updated successfully'
    });
  } catch (error) {
    console.error('Error updating personalization profile:', error);
    res.status(500).json({ error: 'Failed to update personalization profile' });
  }
});

// Obtener personalización
router.get('/profiles/:customerId/personalization', authenticateToken, (req, res) => {
  try {
    const { customerId } = req.params;
    const personalization = advancedPersonalizationService.getPersonalization(customerId);
    
    res.json({
      success: true,
      data: personalization
    });
  } catch (error) {
    console.error('Error fetching personalization:', error);
    res.status(500).json({ error: 'Failed to fetch personalization' });
  }
});

// Obtener reglas
router.get('/rules', authenticateToken, (req, res) => {
  try {
    const rules = advancedPersonalizationService.getRules();
    
    res.json({
      success: true,
      data: rules,
      count: rules.length
    });
  } catch (error) {
    console.error('Error fetching personalization rules:', error);
    res.status(500).json({ error: 'Failed to fetch personalization rules' });
  }
});

// Obtener regla específica
router.get('/rules/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const rules = advancedPersonalizationService.getRules();
    const rule = rules.find(r => r.id === id);
    
    if (!rule) {
      return res.status(404).json({ error: 'Personalization rule not found' });
    }
    
    res.json({
      success: true,
      data: rule
    });
  } catch (error) {
    console.error('Error fetching personalization rule:', error);
    res.status(500).json({ error: 'Failed to fetch personalization rule' });
  }
});

// Crear regla
router.post('/rules', authenticateToken, (req, res) => {
  try {
    const ruleData = req.body;
    
    if (!ruleData.name || !ruleData.conditions || !ruleData.actions) {
      return res.status(400).json({ 
        error: 'Missing required fields: name, conditions, actions' 
      });
    }
    
    const ruleId = advancedPersonalizationService.createRule(ruleData);
    
    res.status(201).json({
      success: true,
      data: { id: ruleId },
      message: 'Personalization rule created successfully'
    });
  } catch (error) {
    console.error('Error creating personalization rule:', error);
    res.status(500).json({ error: 'Failed to create personalization rule' });
  }
});

// Obtener estadísticas
router.get('/stats/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedPersonalizationService.getStats();
    
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching personalization stats:', error);
    res.status(500).json({ error: 'Failed to fetch personalization stats' });
  }
});

// Obtener dashboard
router.get('/dashboard/overview', authenticateToken, (req, res) => {
  try {
    const stats = advancedPersonalizationService.getStats();
    const rules = advancedPersonalizationService.getRules();
    
    const dashboard = {
      overview: {
        totalProfiles: stats.totalProfiles,
        totalRules: stats.totalRules,
        totalResults: stats.totalResults,
        averageConfidence: stats.averageConfidence
      },
      rules: rules.map(rule => ({
        id: rule.id,
        name: rule.name,
        enabled: rule.enabled,
        priority: rule.priority,
        performance: rule.performance
      })),
      topPerformingRules: stats.topPerformingRules.map(rule => ({
        id: rule.id,
        name: rule.name,
        conversions: rule.performance.conversions,
        satisfaction: rule.performance.satisfaction
      }))
    };
    
    res.json({
      success: true,
      data: dashboard
    });
  } catch (error) {
    console.error('Error fetching personalization dashboard:', error);
    res.status(500).json({ error: 'Failed to fetch personalization dashboard' });
  }
});

// Obtener segmentos
router.get('/segments/list', authenticateToken, (req, res) => {
  try {
    const segments = [
      {
        id: 'new_users',
        name: 'New Users',
        description: 'Users who have recently joined',
        criteria: {
          'journey.stage': 'awareness',
          'behavior.patterns.loginFrequency': { operator: 'less_than', value: 5 }
        },
        count: 0 // Would be calculated from actual data
      },
      {
        id: 'high_engagement',
        name: 'High Engagement Users',
        description: 'Users with high engagement scores',
        criteria: {
          'engagement.scores.overall': { operator: 'greater_than', value: 0.8 }
        },
        count: 0
      },
      {
        id: 'churn_risk',
        name: 'Churn Risk Users',
        description: 'Users at risk of churning',
        criteria: {
          'engagement.scores.overall': { operator: 'less_than', value: 0.3 },
          'behavior.patterns.loginFrequency': { operator: 'less_than', value: 2 }
        },
        count: 0
      },
      {
        id: 'premium_users',
        name: 'Premium Users',
        description: 'Users with premium subscriptions',
        criteria: {
          'preferences.product.pricing': 'premium'
        },
        count: 0
      },
      {
        id: 'enterprise_users',
        name: 'Enterprise Users',
        description: 'Users from enterprise companies',
        criteria: {
          'demographics.professional.companySize': 'enterprise'
        },
        count: 0
      }
    ];
    
    res.json({
      success: true,
      data: segments,
      count: segments.length
    });
  } catch (error) {
    console.error('Error fetching personalization segments:', error);
    res.status(500).json({ error: 'Failed to fetch personalization segments' });
  }
});

// Obtener plantillas de reglas
router.get('/rules/templates/list', authenticateToken, (req, res) => {
  try {
    const templates = [
      {
        id: 'new_user_onboarding',
        name: 'New User Onboarding',
        description: 'Personalize experience for new users',
        category: 'onboarding',
        conditions: [
          {
            field: 'journey.stage',
            operator: 'equals',
            value: 'awareness',
            weight: 1.0
          }
        ],
        actions: [
          {
            type: 'content',
            config: {
              showOnboarding: true,
              highlightFeatures: ['getting_started', 'tutorials']
            },
            weight: 1.0
          }
        ],
        priority: 1
      },
      {
        id: 'high_engagement_upsell',
        name: 'High Engagement Upsell',
        description: 'Show upsell offers to highly engaged users',
        category: 'upsell',
        conditions: [
          {
            field: 'engagement.scores.overall',
            operator: 'greater_than',
            value: 0.8,
            weight: 1.0
          }
        ],
        actions: [
          {
            type: 'offer',
            config: {
              type: 'upsell',
              features: ['premium', 'enterprise']
            },
            weight: 1.0
          }
        ],
        priority: 2
      },
      {
        id: 'churn_risk_intervention',
        name: 'Churn Risk Intervention',
        description: 'Intervene with users at risk of churning',
        category: 'retention',
        conditions: [
          {
            field: 'engagement.scores.overall',
            operator: 'less_than',
            value: 0.3,
            weight: 1.0
          }
        ],
        actions: [
          {
            type: 'notification',
            config: {
              type: 'retention_campaign',
              frequency: 'daily'
            },
            weight: 1.0
          }
        ],
        priority: 3
      }
    ];
    
    res.json({
      success: true,
      data: templates,
      count: templates.length
    });
  } catch (error) {
    console.error('Error fetching personalization rule templates:', error);
    res.status(500).json({ error: 'Failed to fetch personalization rule templates' });
  }
});

// Crear regla desde plantilla
router.post('/rules/from-template', authenticateToken, (req, res) => {
  try {
    const { templateId, customizations = {} } = req.body;
    
    if (!templateId) {
      return res.status(400).json({ error: 'Template ID is required' });
    }
    
    // Obtener plantilla (en implementación real, desde base de datos)
    const templates = [
      {
        id: 'new_user_onboarding',
        name: 'New User Onboarding',
        description: 'Personalize experience for new users',
        conditions: [
          {
            field: 'journey.stage',
            operator: 'equals',
            value: 'awareness',
            weight: 1.0
          }
        ],
        actions: [
          {
            type: 'content',
            config: {
              showOnboarding: true,
              highlightFeatures: ['getting_started', 'tutorials']
            },
            weight: 1.0
          }
        ],
        priority: 1,
        enabled: true,
        targetAudience: {
          segments: ['new_users'],
          demographics: {},
          behavior: {},
          psychographics: {}
        }
      }
    ];
    
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      return res.status(404).json({ error: 'Template not found' });
    }
    
    // Aplicar personalizaciones
    const ruleData = {
      ...template,
      ...customizations,
      name: customizations.name || template.name,
      description: customizations.description || template.description
    };
    
    const ruleId = advancedPersonalizationService.createRule(ruleData);
    
    res.status(201).json({
      success: true,
      data: { id: ruleId },
      message: 'Personalization rule created from template successfully'
    });
  } catch (error) {
    console.error('Error creating personalization rule from template:', error);
    res.status(500).json({ error: 'Failed to create personalization rule from template' });
  }
});

// Validar regla
router.post('/rules/validate', authenticateToken, (req, res) => {
  try {
    const { name, conditions, actions, targetAudience } = req.body;
    
    if (!name || !conditions || !actions) {
      return res.status(400).json({ error: 'Name, conditions, and actions are required' });
    }
    
    // Simular validación de regla
    const validation = {
      valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    // Validar condiciones
    if (!Array.isArray(conditions) || conditions.length === 0) {
      validation.errors.push('At least one condition is required');
    }
    
    for (let i = 0; i < conditions.length; i++) {
      const condition = conditions[i];
      if (!condition.field || !condition.operator || condition.value === undefined) {
        validation.errors.push(`Condition ${i + 1} must have field, operator, and value`);
      }
    }
    
    // Validar acciones
    if (!Array.isArray(actions) || actions.length === 0) {
      validation.errors.push('At least one action is required');
    }
    
    for (let i = 0; i < actions.length; i++) {
      const action = actions[i];
      if (!action.type || !action.config) {
        validation.errors.push(`Action ${i + 1} must have type and config`);
      }
    }
    
    // Sugerencias
    if (conditions.length > 10) {
      validation.warnings.push('Consider simplifying rules with many conditions');
    }
    
    if (!targetAudience || Object.keys(targetAudience).length === 0) {
      validation.suggestions.push('Consider adding target audience criteria for better targeting');
    }
    
    res.json({
      success: true,
      data: validation
    });
  } catch (error) {
    console.error('Error validating personalization rule:', error);
    res.status(500).json({ error: 'Failed to validate personalization rule' });
  }
});

export default router;

