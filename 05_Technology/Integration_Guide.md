# 🔗 Integration Guide - Neural Marketing Consciousness System

## 🎯 Integration Overview

This comprehensive integration guide provides system integrators, developers, and IT teams with everything needed to successfully integrate the Neural Marketing Consciousness System with existing business systems, third-party platforms, and custom applications.

---

## 📚 Table of Contents

1. [Integration Architecture](#integration-architecture)
2. [Authentication & Security](#authentication--security)
3. [Core Integrations](#core-integrations)
4. [CRM Integrations](#crm-integrations)
5. [Marketing Platform Integrations](#marketing-platform-integrations)
6. [Analytics Integrations](#analytics-integrations)
7. [Custom Integrations](#custom-integrations)
8. [Webhook Implementation](#webhook-implementation)
9. [Data Synchronization](#data-synchronization)
10. [Testing & Validation](#testing--validation)

---

## 🏗️ Integration Architecture

### System Architecture Overview

#### Core Components
- **API Gateway**: Central entry point for all integrations
- **Authentication Service**: Handles OAuth, API keys, and SSO
- **Data Processing Engine**: Transforms and processes data
- **Webhook Service**: Manages real-time event notifications
- **Sync Service**: Handles data synchronization

#### Integration Patterns
1. **REST API Integration**: Direct API calls for real-time data
2. **Webhook Integration**: Event-driven notifications
3. **Batch Integration**: Scheduled data imports/exports
4. **Real-time Streaming**: WebSocket connections for live data
5. **File-based Integration**: CSV, JSON, XML file transfers

### Data Flow Architecture

```
External System → API Gateway → Authentication → Data Processing → Neural Marketing System
                     ↓
                Webhook Service → External System (Real-time notifications)
```

---

## 🔐 Authentication & Security

### Authentication Methods

#### API Key Authentication
```bash
# Simple API key authentication
curl -X GET "https://api.neuralmarketing.com/v1/campaigns" \
     -H "Authorization: Bearer YOUR_API_KEY"
```

#### OAuth 2.0 Integration
```javascript
// OAuth 2.0 flow implementation
const oauth2 = require('simple-oauth2');

const client = oauth2.create({
  client: {
    id: 'your_client_id',
    secret: 'your_client_secret'
  },
  auth: {
    tokenHost: 'https://api.neuralmarketing.com',
    tokenPath: '/oauth/token',
    authorizePath: '/oauth/authorize'
  }
});

// Get access token
const tokenConfig = {
  scope: 'read write',
  grant_type: 'client_credentials'
};

const accessToken = await client.clientCredentials.getToken(tokenConfig);
```

#### SAML SSO Integration
```xml
<!-- SAML configuration example -->
<EntityDescriptor entityID="https://api.neuralmarketing.com/saml">
  <SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <AssertionConsumerService 
      Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
      Location="https://api.neuralmarketing.com/saml/acs"
      index="0" isDefault="true"/>
  </SPSSODescriptor>
</EntityDescriptor>
```

### Security Best Practices

#### API Security
```javascript
// Rate limiting implementation
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // limit each IP to 1000 requests per windowMs
  message: 'Too many requests from this IP'
});

// Request validation
const validateRequest = (req, res, next) => {
  const { body } = req;
  
  // Validate required fields
  if (!body.campaign_name || !body.budget) {
    return res.status(400).json({
      error: 'Missing required fields: campaign_name, budget'
    });
  }
  
  next();
};
```

#### Data Encryption
```javascript
// Encrypt sensitive data
const crypto = require('crypto');

function encryptData(data, key) {
  const cipher = crypto.createCipher('aes-256-cbc', key);
  let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return encrypted;
}

function decryptData(encryptedData, key) {
  const decipher = crypto.createDecipher('aes-256-cbc', key);
  let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return JSON.parse(decrypted);
}
```

---

## 🔌 Core Integrations

### REST API Integration

#### Basic API Client
```javascript
class NeuralMarketingClient {
  constructor(apiKey, baseURL = 'https://api.neuralmarketing.com/v1') {
    this.apiKey = apiKey;
    this.baseURL = baseURL;
  }

  async request(method, endpoint, data = null) {
    const url = `${this.baseURL}${endpoint}`;
    const options = {
      method,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Campaign methods
  async getCampaigns() {
    return this.request('GET', '/campaigns');
  }

  async createCampaign(campaignData) {
    return this.request('POST', '/campaigns', campaignData);
  }

  async updateCampaign(campaignId, campaignData) {
    return this.request('PUT', `/campaigns/${campaignId}`, campaignData);
  }

  async deleteCampaign(campaignId) {
    return this.request('DELETE', `/campaigns/${campaignId}`);
  }
}
```

#### Error Handling
```javascript
class APIError extends Error {
  constructor(message, status, response) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.response = response;
  }
}

async function handleAPIError(response) {
  if (!response.ok) {
    const errorData = await response.json();
    throw new APIError(
      errorData.message || 'API request failed',
      response.status,
      errorData
    );
  }
  return response.json();
}
```

### Batch Integration

#### CSV Data Import
```javascript
const csv = require('csv-parser');
const fs = require('fs');

async function importCampaignsFromCSV(filePath) {
  const campaigns = [];
  
  return new Promise((resolve, reject) => {
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => {
        campaigns.push({
          name: row.campaign_name,
          type: row.campaign_type,
          budget: parseFloat(row.budget),
          start_date: row.start_date,
          end_date: row.end_date
        });
      })
      .on('end', async () => {
        try {
          const results = await Promise.all(
            campaigns.map(campaign => client.createCampaign(campaign))
          );
          resolve(results);
        } catch (error) {
          reject(error);
        }
      })
      .on('error', reject);
  });
}
```

#### JSON Data Export
```javascript
async function exportCampaignsToJSON(startDate, endDate) {
  const campaigns = await client.getCampaigns({
    start_date: startDate,
    end_date: endDate
  });

  const exportData = {
    export_date: new Date().toISOString(),
    total_campaigns: campaigns.length,
    campaigns: campaigns.map(campaign => ({
      id: campaign.id,
      name: campaign.name,
      type: campaign.type,
      status: campaign.status,
      budget: campaign.budget,
      performance: {
        impressions: campaign.impressions,
        clicks: campaign.clicks,
        conversions: campaign.conversions
      }
    }))
  };

  return JSON.stringify(exportData, null, 2);
}
```

---

## 🏢 CRM Integrations

### Salesforce Integration

#### Salesforce API Client
```javascript
class SalesforceClient {
  constructor(accessToken, instanceUrl) {
    this.accessToken = accessToken;
    this.instanceUrl = instanceUrl;
  }

  async query(soql) {
    const response = await fetch(
      `${this.instanceUrl}/services/data/v52.0/query/?q=${encodeURIComponent(soql)}`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.json();
  }

  async createRecord(objectType, data) {
    const response = await fetch(
      `${this.instanceUrl}/services/data/v52.0/sobjects/${objectType}/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    );

    return response.json();
  }
}
```

#### Lead Synchronization
```javascript
async function syncLeadsToSalesforce(neuralMarketingClient, salesforceClient) {
  // Get leads from Neural Marketing
  const leads = await neuralMarketingClient.getLeads();
  
  // Transform data for Salesforce
  const salesforceLeads = leads.map(lead => ({
    FirstName: lead.first_name,
    LastName: lead.last_name,
    Email: lead.email,
    Company: lead.company,
    LeadSource: 'Neural Marketing',
    Status: 'New',
    Description: `Campaign: ${lead.campaign_name}`
  }));

  // Create leads in Salesforce
  const results = await Promise.all(
    salesforceLeads.map(lead => 
      salesforceClient.createRecord('Lead', lead)
    )
  );

  return results;
}
```

### HubSpot Integration

#### HubSpot API Client
```javascript
class HubSpotClient {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.baseURL = 'https://api.hubapi.com';
  }

  async createContact(contactData) {
    const response = await fetch(
      `${this.baseURL}/crm/v3/objects/contacts`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          properties: contactData
        })
      }
    );

    return response.json();
  }

  async updateContact(contactId, contactData) {
    const response = await fetch(
      `${this.baseURL}/crm/v3/objects/contacts/${contactId}`,
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          properties: contactData
        })
      }
    );

    return response.json();
  }
}
```

#### Contact Synchronization
```javascript
async function syncContactsToHubSpot(neuralMarketingClient, hubspotClient) {
  const contacts = await neuralMarketingClient.getContacts();
  
  const hubspotContacts = contacts.map(contact => ({
    email: contact.email,
    firstname: contact.first_name,
    lastname: contact.last_name,
    company: contact.company,
    phone: contact.phone,
    lead_source: 'Neural Marketing',
    campaign_name: contact.campaign_name
  }));

  const results = await Promise.all(
    hubspotContacts.map(contact => 
      hubspotClient.createContact(contact)
    )
  );

  return results;
}
```

---

## 📊 Marketing Platform Integrations

### Google Ads Integration

#### Google Ads API Client
```javascript
class GoogleAdsClient {
  constructor(developerToken, clientId, clientSecret, refreshToken) {
    this.developerToken = developerToken;
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.refreshToken = refreshToken;
  }

  async getAccessToken() {
    const response = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        client_id: this.clientId,
        client_secret: this.clientSecret,
        refresh_token: this.refreshToken,
        grant_type: 'refresh_token'
      })
    });

    const data = await response.json();
    return data.access_token;
  }

  async createCampaign(campaignData) {
    const accessToken = await this.getAccessToken();
    
    const response = await fetch(
      `https://googleads.googleapis.com/v12/customers/${this.customerId}/campaigns:mutate`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
          'developer-token': this.developerToken
        },
        body: JSON.stringify({
          operations: [{
            create: campaignData
          }]
        })
      }
    );

    return response.json();
  }
}
```

### Facebook Marketing API Integration

#### Facebook API Client
```javascript
class FacebookMarketingClient {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.baseURL = 'https://graph.facebook.com/v18.0';
  }

  async createCampaign(campaignData) {
    const response = await fetch(
      `${this.baseURL}/act_${this.adAccountId}/campaigns`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(campaignData)
      }
    );

    return response.json();
  }

  async createAdSet(adSetData) {
    const response = await fetch(
      `${this.baseURL}/act_${this.adAccountId}/adsets`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(adSetData)
      }
    );

    return response.json();
  }
}
```

### Email Marketing Integration

#### Mailchimp Integration
```javascript
class MailchimpClient {
  constructor(apiKey, serverPrefix) {
    this.apiKey = apiKey;
    this.baseURL = `https://${serverPrefix}.api.mailchimp.com/3.0`;
  }

  async createCampaign(campaignData) {
    const response = await fetch(
      `${this.baseURL}/campaigns`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(campaignData)
      }
    );

    return response.json();
  }

  async addSubscribersToList(listId, subscribers) {
    const response = await fetch(
      `${this.baseURL}/lists/${listId}/members`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          members: subscribers.map(subscriber => ({
            email_address: subscriber.email,
            status: 'subscribed',
            merge_fields: {
              FNAME: subscriber.first_name,
              LNAME: subscriber.last_name
            }
          }))
        })
      }
    );

    return response.json();
  }
}
```

---

## 📈 Analytics Integrations

### Google Analytics Integration

#### Google Analytics API Client
```javascript
class GoogleAnalyticsClient {
  constructor(accessToken, propertyId) {
    this.accessToken = accessToken;
    this.propertyId = propertyId;
    this.baseURL = 'https://analyticsdata.googleapis.com/v1beta';
  }

  async getReport(dimensions, metrics, startDate, endDate) {
    const response = await fetch(
      `${this.baseURL}/properties/${this.propertyId}:runReport`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          dimensions: dimensions.map(dim => ({ name: dim })),
          metrics: metrics.map(metric => ({ name: metric })),
          dateRanges: [{
            startDate,
            endDate
          }]
        })
      }
    );

    return response.json();
  }
}
```

#### Analytics Data Synchronization
```javascript
async function syncAnalyticsData(neuralMarketingClient, gaClient) {
  const endDate = new Date().toISOString().split('T')[0];
  const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

  // Get data from Google Analytics
  const gaData = await gaClient.getReport(
    ['date', 'campaignName'],
    ['sessions', 'users', 'conversions'],
    startDate,
    endDate
  );

  // Transform and sync to Neural Marketing
  const analyticsData = gaData.rows.map(row => ({
    date: row.dimensionValues[0].value,
    campaign_name: row.dimensionValues[1].value,
    sessions: parseInt(row.metricValues[0].value),
    users: parseInt(row.metricValues[1].value),
    conversions: parseInt(row.metricValues[2].value)
  }));

  const results = await Promise.all(
    analyticsData.map(data => 
      neuralMarketingClient.createAnalyticsRecord(data)
    )
  );

  return results;
}
```

### Adobe Analytics Integration

#### Adobe Analytics API Client
```javascript
class AdobeAnalyticsClient {
  constructor(accessToken, companyId) {
    this.accessToken = accessToken;
    this.companyId = companyId;
    this.baseURL = 'https://analytics.adobe.io/api';
  }

  async getReport(reportSuiteId, dimensions, metrics, startDate, endDate) {
    const response = await fetch(
      `${this.baseURL}/${this.companyId}/reports`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
          'x-api-key': this.apiKey
        },
        body: JSON.stringify({
          rsid: reportSuiteId,
          globalFilters: [{
            type: 'dateRange',
            dateRange: `${startDate}T00:00:00.000/${endDate}T23:59:59.999`
          }],
          dimension: dimensions,
          metricContainer: {
            metrics: metrics.map(metric => ({ id: metric }))
          }
        })
      }
    );

    return response.json();
  }
}
```

---

## 🛠️ Custom Integrations

### Custom API Development

#### Express.js Integration Server
```javascript
const express = require('express');
const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Authentication middleware
const authenticateRequest = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  
  if (!apiKey || apiKey !== process.env.INTEGRATION_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  next();
};

// Neural Marketing client
const neuralClient = new NeuralMarketingClient(process.env.NEURAL_API_KEY);

// Custom endpoints
app.post('/sync/campaigns', authenticateRequest, async (req, res) => {
  try {
    const { campaigns } = req.body;
    
    const results = await Promise.all(
      campaigns.map(campaign => neuralClient.createCampaign(campaign))
    );
    
    res.json({ success: true, results });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/campaigns/:id/analytics', authenticateRequest, async (req, res) => {
  try {
    const { id } = req.params;
    const analytics = await neuralClient.getCampaignAnalytics(id);
    
    res.json(analytics);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Integration server running on port 3000');
});
```

### Database Integration

#### PostgreSQL Integration
```javascript
const { Pool } = require('pg');

class DatabaseIntegration {
  constructor(connectionString) {
    this.pool = new Pool({ connectionString });
  }

  async syncCampaignsToDatabase(campaigns) {
    const client = await this.pool.connect();
    
    try {
      await client.query('BEGIN');
      
      for (const campaign of campaigns) {
        await client.query(
          `INSERT INTO campaigns (id, name, type, budget, status, created_at)
           VALUES ($1, $2, $3, $4, $5, $6)
           ON CONFLICT (id) DO UPDATE SET
           name = EXCLUDED.name,
           type = EXCLUDED.type,
           budget = EXCLUDED.budget,
           status = EXCLUDED.status,
           updated_at = NOW()`,
          [
            campaign.id,
            campaign.name,
            campaign.type,
            campaign.budget,
            campaign.status,
            campaign.created_at
          ]
        );
      }
      
      await client.query('COMMIT');
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  async getCampaignPerformance(startDate, endDate) {
    const query = `
      SELECT 
        c.name,
        c.type,
        c.budget,
        SUM(a.impressions) as total_impressions,
        SUM(a.clicks) as total_clicks,
        SUM(a.conversions) as total_conversions,
        ROUND(SUM(a.conversions)::numeric / SUM(a.clicks) * 100, 2) as conversion_rate
      FROM campaigns c
      LEFT JOIN analytics a ON c.id = a.campaign_id
      WHERE a.date BETWEEN $1 AND $2
      GROUP BY c.id, c.name, c.type, c.budget
      ORDER BY total_conversions DESC
    `;
    
    const result = await this.pool.query(query, [startDate, endDate]);
    return result.rows;
  }
}
```

---

## 🪝 Webhook Implementation

### Webhook Server Setup

#### Express.js Webhook Handler
```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

// Webhook signature verification
const verifyWebhookSignature = (payload, signature, secret) => {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
};

// Webhook endpoint
app.post('/webhooks/neural-marketing', express.raw({ type: 'application/json' }), (req, res) => {
  const signature = req.headers['x-neural-signature'];
  const payload = req.body;
  
  // Verify webhook signature
  if (!verifyWebhookSignature(payload, signature, process.env.WEBHOOK_SECRET)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  try {
    const event = JSON.parse(payload);
    
    // Process different event types
    switch (event.type) {
      case 'campaign.created':
        handleCampaignCreated(event.data);
        break;
      case 'campaign.updated':
        handleCampaignUpdated(event.data);
        break;
      case 'campaign.completed':
        handleCampaignCompleted(event.data);
        break;
      case 'user.registered':
        handleUserRegistered(event.data);
        break;
      default:
        console.log(`Unhandled event type: ${event.type}`);
    }
    
    res.json({ received: true });
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(400).json({ error: 'Invalid payload' });
  }
});

// Event handlers
async function handleCampaignCreated(campaignData) {
  console.log('New campaign created:', campaignData);
  
  // Sync to CRM
  await syncCampaignToCRM(campaignData);
  
  // Send notification
  await sendNotification('New campaign created', campaignData);
}

async function handleCampaignUpdated(campaignData) {
  console.log('Campaign updated:', campaignData);
  
  // Update CRM record
  await updateCampaignInCRM(campaignData);
}

async function handleCampaignCompleted(campaignData) {
  console.log('Campaign completed:', campaignData);
  
  // Generate report
  await generateCampaignReport(campaignData);
  
  // Archive campaign
  await archiveCampaign(campaignData);
}

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

### Webhook Testing

#### Webhook Testing Tool
```javascript
const axios = require('axios');

class WebhookTester {
  constructor(webhookUrl, secret) {
    this.webhookUrl = webhookUrl;
    this.secret = secret;
  }

  async testWebhook(eventType, eventData) {
    const payload = JSON.stringify({
      id: `evt_${Date.now()}`,
      type: eventType,
      created: new Date().toISOString(),
      data: eventData
    });

    const signature = crypto
      .createHmac('sha256', this.secret)
      .update(payload)
      .digest('hex');

    try {
      const response = await axios.post(this.webhookUrl, payload, {
        headers: {
          'Content-Type': 'application/json',
          'X-Neural-Signature': signature
        }
      });

      console.log('Webhook test successful:', response.status);
      return response.data;
    } catch (error) {
      console.error('Webhook test failed:', error.message);
      throw error;
    }
  }

  async testAllEvents() {
    const testEvents = [
      {
        type: 'campaign.created',
        data: {
          id: 'camp_test_123',
          name: 'Test Campaign',
          type: 'awareness',
          budget: 1000
        }
      },
      {
        type: 'campaign.updated',
        data: {
          id: 'camp_test_123',
          name: 'Updated Test Campaign',
          budget: 1500
        }
      },
      {
        type: 'user.registered',
        data: {
          id: 'user_test_123',
          email: 'test@example.com',
          name: 'Test User'
        }
      }
    ];

    const results = [];
    for (const event of testEvents) {
      try {
        const result = await this.testWebhook(event.type, event.data);
        results.push({ event: event.type, success: true, result });
      } catch (error) {
        results.push({ event: event.type, success: false, error: error.message });
      }
    }

    return results;
  }
}
```

---

## 🔄 Data Synchronization

### Real-time Sync

#### WebSocket Integration
```javascript
const WebSocket = require('ws');

class RealTimeSync {
  constructor(apiKey, baseURL = 'wss://api.neuralmarketing.com/v1/stream') {
    this.apiKey = apiKey;
    this.baseURL = baseURL;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    this.ws = new WebSocket(`${this.baseURL}?token=${this.apiKey}`);

    this.ws.on('open', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      
      // Subscribe to events
      this.subscribe(['campaigns', 'analytics', 'users']);
    });

    this.ws.on('message', (data) => {
      try {
        const event = JSON.parse(data);
        this.handleEvent(event);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    });

    this.ws.on('close', () => {
      console.log('WebSocket disconnected');
      this.reconnect();
    });

    this.ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  }

  subscribe(channels) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        channels: channels
      }));
    }
  }

  handleEvent(event) {
    switch (event.type) {
      case 'campaign.updated':
        this.syncCampaignToLocal(event.data);
        break;
      case 'analytics.updated':
        this.updateLocalAnalytics(event.data);
        break;
      case 'user.updated':
        this.syncUserToLocal(event.data);
        break;
    }
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts) * 1000;
      
      console.log(`Reconnecting in ${delay}ms...`);
      setTimeout(() => this.connect(), delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }
}
```

### Batch Sync

#### Scheduled Synchronization
```javascript
const cron = require('node-cron');

class BatchSync {
  constructor(neuralClient, localDatabase) {
    this.neuralClient = neuralClient;
    this.localDatabase = localDatabase;
  }

  startScheduledSync() {
    // Sync campaigns every hour
    cron.schedule('0 * * * *', () => {
      this.syncCampaigns();
    });

    // Sync analytics every 15 minutes
    cron.schedule('*/15 * * * *', () => {
      this.syncAnalytics();
    });

    // Full sync every day at 2 AM
    cron.schedule('0 2 * * *', () => {
      this.fullSync();
    });
  }

  async syncCampaigns() {
    try {
      console.log('Starting campaign sync...');
      
      const campaigns = await this.neuralClient.getCampaigns();
      await this.localDatabase.syncCampaigns(campaigns);
      
      console.log(`Synced ${campaigns.length} campaigns`);
    } catch (error) {
      console.error('Campaign sync failed:', error);
    }
  }

  async syncAnalytics() {
    try {
      console.log('Starting analytics sync...');
      
      const endDate = new Date();
      const startDate = new Date(endDate.getTime() - 24 * 60 * 60 * 1000);
      
      const analytics = await this.neuralClient.getAnalytics({
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString()
      });
      
      await this.localDatabase.syncAnalytics(analytics);
      
      console.log(`Synced ${analytics.length} analytics records`);
    } catch (error) {
      console.error('Analytics sync failed:', error);
    }
  }

  async fullSync() {
    try {
      console.log('Starting full sync...');
      
      await this.syncCampaigns();
      await this.syncAnalytics();
      await this.syncUsers();
      
      console.log('Full sync completed');
    } catch (error) {
      console.error('Full sync failed:', error);
    }
  }
}
```

---

## 🧪 Testing & Validation

### Integration Testing

#### Test Suite Setup
```javascript
const { expect } = require('chai');
const NeuralMarketingClient = require('./neural-marketing-client');

describe('Neural Marketing Integration', () => {
  let client;
  let testCampaignId;

  before(async () => {
    client = new NeuralMarketingClient(
      process.env.TEST_API_KEY,
      process.env.TEST_BASE_URL
    );
  });

  describe('Campaign Management', () => {
    it('should create a campaign', async () => {
      const campaignData = {
        name: 'Test Campaign',
        type: 'awareness',
        budget: 1000,
        start_date: '2024-01-01',
        end_date: '2024-01-31'
      };

      const campaign = await client.createCampaign(campaignData);
      
      expect(campaign).to.have.property('id');
      expect(campaign.name).to.equal('Test Campaign');
      expect(campaign.status).to.equal('draft');
      
      testCampaignId = campaign.id;
    });

    it('should retrieve a campaign', async () => {
      const campaign = await client.getCampaign(testCampaignId);
      
      expect(campaign.id).to.equal(testCampaignId);
      expect(campaign.name).to.equal('Test Campaign');
    });

    it('should update a campaign', async () => {
      const updateData = {
        budget: 1500,
        status: 'active'
      };

      const updatedCampaign = await client.updateCampaign(testCampaignId, updateData);
      
      expect(updatedCampaign.budget).to.equal(1500);
      expect(updatedCampaign.status).to.equal('active');
    });

    it('should delete a campaign', async () => {
      await client.deleteCampaign(testCampaignId);
      
      try {
        await client.getCampaign(testCampaignId);
        expect.fail('Campaign should not exist');
      } catch (error) {
        expect(error.status).to.equal(404);
      }
    });
  });

  describe('Analytics Integration', () => {
    it('should retrieve campaign analytics', async () => {
      const analytics = await client.getCampaignAnalytics(testCampaignId, {
        start_date: '2024-01-01',
        end_date: '2024-01-31'
      });

      expect(analytics).to.have.property('impressions');
      expect(analytics).to.have.property('clicks');
      expect(analytics).to.have.property('conversions');
    });
  });
});
```

### Data Validation

#### Schema Validation
```javascript
const Joi = require('joi');

const campaignSchema = Joi.object({
  name: Joi.string().required().max(100),
  type: Joi.string().valid('awareness', 'conversion', 'retention').required(),
  budget: Joi.number().positive().required(),
  start_date: Joi.date().iso().required(),
  end_date: Joi.date().iso().min(Joi.ref('start_date')).required(),
  target_audience: Joi.object({
    age_range: Joi.array().items(Joi.number().min(18).max(65)).length(2),
    interests: Joi.array().items(Joi.string()),
    location: Joi.string()
  }).optional()
});

function validateCampaignData(data) {
  const { error, value } = campaignSchema.validate(data);
  
  if (error) {
    throw new Error(`Validation error: ${error.details[0].message}`);
  }
  
  return value;
}
```

### Performance Testing

#### Load Testing
```javascript
const autocannon = require('autocannon');

async function loadTestAPI() {
  const result = await autocannon({
    url: 'https://api.neuralmarketing.com/v1/campaigns',
    connections: 10,
    pipelining: 1,
    duration: 30,
    headers: {
      'Authorization': `Bearer ${process.env.TEST_API_KEY}`
    }
  });

  console.log('Load test results:', {
    requests: result.requests.total,
    latency: result.latency.average,
    throughput: result.throughput.average
  });

  return result;
}
```

---

## 📋 Integration Checklist

### Pre-Integration
- [ ] Review API documentation
- [ ] Set up development environment
- [ ] Obtain API credentials
- [ ] Plan data mapping
- [ ] Design error handling
- [ ] Set up monitoring

### Development
- [ ] Implement authentication
- [ ] Create API client
- [ ] Handle rate limiting
- [ ] Implement retry logic
- [ ] Add logging
- [ ] Write unit tests

### Testing
- [ ] Test in sandbox environment
- [ ] Validate data accuracy
- [ ] Test error scenarios
- [ ] Performance testing
- [ ] Security testing
- [ ] User acceptance testing

### Deployment
- [ ] Deploy to staging
- [ ] Monitor integration health
- [ ] Gradual rollout
- [ ] Monitor performance
- [ ] Document issues
- [ ] Train users

### Post-Deployment
- [ ] Monitor system health
- [ ] Review logs regularly
- [ ] Update documentation
- [ ] Plan maintenance
- [ ] Gather feedback
- [ ] Optimize performance

---

## 📞 Support & Resources

### Integration Support
- **Documentation**: https://docs.neuralmarketing.com/integrations
- **API Reference**: https://api.neuralmarketing.com/docs
- **SDK Downloads**: https://github.com/neural-marketing/sdks
- **Community Forum**: https://community.neuralmarketing.com

### Technical Support
- **Integration Support**: integrations@neuralmarketing.com
- **API Support**: api-support@neuralmarketing.com
- **Emergency Support**: emergency@neuralmarketing.com
- **Phone**: 1-800-NEURAL-INT

### Resources
- **Postman Collection**: Download our API collection
- **Code Examples**: GitHub repository with examples
- **Video Tutorials**: Step-by-step integration guides
- **Webinars**: Monthly integration webinars

---

*This integration guide is regularly updated to reflect the latest API changes and integration patterns. Last updated: January 2024*

**© 2024 Neural Marketing Consciousness System. All rights reserved.**