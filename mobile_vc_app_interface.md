# Mobile VC App Interface
## Cross-Platform Mobile Application

### Mobile App Architecture

#### React Native Implementation
**Cross-Platform Mobile App**
```javascript
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Dimensions
} from 'react-native';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';

const { width: screenWidth } = Dimensions.get('window');

const VCDashboard = () => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [dealsData, setDealsData] = useState([]);
  const [marketData, setMarketData] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [portfolio, deals, market] = await Promise.all([
        fetchPortfolioData(),
        fetchDealsData(),
        fetchMarketData()
      ]);
      
      setPortfolioData(portfolio);
      setDealsData(deals);
      setMarketData(market);
    } catch (error) {
      Alert.alert('Error', 'Failed to load dashboard data');
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboardData().finally(() => setRefreshing(false));
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <PortfolioOverview data={portfolioData} />
      <DealsPipeline data={dealsData} />
      <MarketIntelligence data={marketData} />
      <QuickActions />
    </ScrollView>
  );
};

const PortfolioOverview = ({ data }) => {
  if (!data) return <LoadingSpinner />;

  const chartConfig = {
    backgroundColor: '#ffffff',
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    decimalPlaces: 1,
    color: (opacity = 1) => `rgba(0, 122, 255, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
    style: {
      borderRadius: 16
    }
  };

  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Portfolio Performance</Text>
      
      <View style={styles.metricsRow}>
        <MetricCard
          title="IRR"
          value={`${data.irr}%`}
          trend={data.irrTrend}
          color="#4CAF50"
        />
        <MetricCard
          title="TVPI"
          value={`${data.tvpi}x`}
          trend={data.tvpiTrend}
          color="#2196F3"
        />
        <MetricCard
          title="DPI"
          value={`${data.dpi}x`}
          trend={data.dpiTrend}
          color="#FF9800"
        />
      </View>

      <LineChart
        data={{
          labels: data.performanceLabels,
          datasets: [{
            data: data.performanceData
          }]
        }}
        width={screenWidth - 32}
        height={220}
        chartConfig={chartConfig}
        bezier
        style={styles.chart}
      />
    </View>
  );
};

const DealsPipeline = ({ data }) => {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Deals Pipeline</Text>
      
      {data.map((deal, index) => (
        <DealCard key={index} deal={deal} />
      ))}
    </View>
  );
};

const DealCard = ({ deal }) => {
  const getScoreColor = (score) => {
    if (score >= 8) return '#4CAF50';
    if (score >= 6) return '#FF9800';
    return '#F44336';
  };

  return (
    <TouchableOpacity style={styles.dealCard}>
      <View style={styles.dealHeader}>
        <Text style={styles.dealName}>{deal.companyName}</Text>
        <View style={[styles.scoreBadge, { backgroundColor: getScoreColor(deal.score) }]}>
          <Text style={styles.scoreText}>{deal.score}/10</Text>
        </View>
      </View>
      
      <Text style={styles.dealSector}>{deal.sector} • {deal.stage}</Text>
      
      <View style={styles.dealMetrics}>
        <Text style={styles.dealMetric}>MRR: ${deal.mrr}K</Text>
        <Text style={styles.dealMetric}>Growth: {deal.growth}%</Text>
        <Text style={styles.dealMetric}>Team: {deal.teamSize}</Text>
      </View>
      
      <View style={styles.dealStatus}>
        <Text style={[styles.statusText, { color: getStatusColor(deal.status) }]}>
          {deal.status}
        </Text>
        <Text style={styles.dealDate}>{deal.date}</Text>
      </View>
    </TouchableOpacity>
  );
};

const MarketIntelligence = ({ data }) => {
  if (!data) return <LoadingSpinner />;

  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Market Intelligence</Text>
      
      <View style={styles.marketCards}>
        <MarketCard
          title="AI Sector"
          score={data.aiScore}
          trend={data.aiTrend}
          recommendation={data.aiRecommendation}
        />
        <MarketCard
          title="Climate Sector"
          score={data.climateScore}
          trend={data.climateTrend}
          recommendation={data.climateRecommendation}
        />
        <MarketCard
          title="Fintech Sector"
          score={data.fintechScore}
          trend={data.fintechTrend}
          recommendation={data.fintechRecommendation}
        />
      </View>
    </View>
  );
};

const QuickActions = () => {
  const actions = [
    { title: 'Evaluate Deal', icon: '📊', action: 'evaluate' },
    { title: 'Portfolio Review', icon: '📈', action: 'portfolio' },
    { title: 'Market Analysis', icon: '🌐', action: 'market' },
    { title: 'Risk Assessment', icon: '⚠️', action: 'risk' }
  ];

  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Quick Actions</Text>
      
      <View style={styles.actionsGrid}>
        {actions.map((action, index) => (
          <TouchableOpacity
            key={index}
            style={styles.actionButton}
            onPress={() => handleQuickAction(action.action)}
          >
            <Text style={styles.actionIcon}>{action.icon}</Text>
            <Text style={styles.actionTitle}>{action.title}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5'
  },
  section: {
    margin: 16,
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333'
  },
  metricsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16
  },
  dealCard: {
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF'
  },
  dealHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4
  },
  dealName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333'
  },
  scoreBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12
  },
  scoreText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 12
  },
  dealSector: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8
  },
  dealMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8
  },
  dealMetric: {
    fontSize: 12,
    color: '#666'
  },
  dealStatus: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  statusText: {
    fontSize: 12,
    fontWeight: 'bold'
  },
  dealDate: {
    fontSize: 12,
    color: '#666'
  },
  marketCards: {
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between'
  },
  actionButton: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginBottom: 8
  },
  actionIcon: {
    fontSize: 24,
    marginBottom: 8
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center'
  }
});

export default VCDashboard;
```

### Deal Evaluation Mobile Interface

#### Interactive Deal Scoring
**Mobile Deal Evaluation Form**
```javascript
import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Slider,
  Picker
} from 'react-native';

const DealEvaluation = ({ dealId }) => {
  const [scores, setScores] = useState({
    problem: 5,
    solution: 5,
    traction: 5,
    team: 5,
    unitEconomics: 5,
    ask: 5,
    redFlags: 5
  });

  const [overallScore, setOverallScore] = useState(5);
  const [recommendation, setRecommendation] = useState('DEEP DIVE');

  const updateScore = (category, value) => {
    const newScores = { ...scores, [category]: value };
    setScores(newScores);
    
    // Calculate overall score
    const weights = {
      problem: 0.25,
      solution: 0.20,
      traction: 0.20,
      team: 0.15,
      unitEconomics: 0.10,
      ask: 0.05,
      redFlags: 0.05
    };
    
    const weightedScore = Object.keys(weights).reduce((sum, key) => 
      sum + (newScores[key] * weights[key]), 0);
    
    setOverallScore(weightedScore);
    
    // Update recommendation
    if (weightedScore >= 8.0) {
      setRecommendation('PASS');
    } else if (weightedScore >= 6.0) {
      setRecommendation('DEEP DIVE');
    } else if (weightedScore >= 4.0) {
      setRecommendation('DEEP DIVE (CAUTION)');
    } else {
      setRecommendation('REJECT');
    }
  };

  const ScoreSlider = ({ category, title, value, onValueChange }) => (
    <View style={styles.sliderContainer}>
      <Text style={styles.sliderTitle}>{title}</Text>
      <View style={styles.sliderRow}>
        <Text style={styles.sliderLabel}>1</Text>
        <Slider
          style={styles.slider}
          minimumValue={1}
          maximumValue={10}
          step={0.5}
          value={value}
          onValueChange={(val) => onValueChange(val)}
          minimumTrackTintColor="#007AFF"
          maximumTrackTintColor="#E0E0E0"
          thumbStyle={styles.sliderThumb}
        />
        <Text style={styles.sliderLabel}>10</Text>
      </View>
      <Text style={styles.sliderValue}>{value.toFixed(1)}</Text>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Deal Evaluation</Text>
        <View style={styles.scoreDisplay}>
          <Text style={styles.overallScore}>{overallScore.toFixed(1)}/10</Text>
          <Text style={styles.recommendation}>{recommendation}</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Problem Assessment (25%)</Text>
        <ScoreSlider
          category="problem"
          title="Market Pain Intensity"
          value={scores.problem}
          onValueChange={(val) => updateScore('problem', val)}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Solution Analysis (20%)</Text>
        <ScoreSlider
          category="solution"
          title="Technical Moat"
          value={scores.solution}
          onValueChange={(val) => updateScore('solution', val)}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Traction Metrics (20%)</Text>
        <ScoreSlider
          category="traction"
          title="MRR Growth"
          value={scores.traction}
          onValueChange={(val) => updateScore('traction', val)}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Team Evaluation (15%)</Text>
        <ScoreSlider
          category="team"
          title="Domain Expertise"
          value={scores.team}
          onValueChange={(val) => updateScore('team', val)}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Unit Economics (10%)</Text>
        <ScoreSlider
          category="unitEconomics"
          title="LTV/CAC Ratio"
          value={scores.unitEconomics}
          onValueChange={(val) => updateScore('unitEconomics', val)}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Funding Ask (5%)</Text>
        <ScoreSlider
          category="ask"
          title="Valuation Reasonableness"
          value={scores.ask}
          onValueChange={(val) => updateScore('ask', val)}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Red Flags Assessment (5%)</Text>
        <ScoreSlider
          category="redFlags"
          title="Risk Level"
          value={scores.redFlags}
          onValueChange={(val) => updateScore('redFlags', val)}
        />
      </View>

      <TouchableOpacity style={styles.saveButton}>
        <Text style={styles.saveButtonText}>Save Evaluation</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5'
  },
  header: {
    backgroundColor: 'white',
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0'
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333'
  },
  scoreDisplay: {
    alignItems: 'center'
  },
  overallScore: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF'
  },
  recommendation: {
    fontSize: 12,
    color: '#666',
    fontWeight: 'bold'
  },
  section: {
    backgroundColor: 'white',
    margin: 16,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333'
  },
  sliderContainer: {
    marginBottom: 16
  },
  sliderTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#333'
  },
  sliderRow: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  sliderLabel: {
    fontSize: 12,
    color: '#666',
    width: 20
  },
  slider: {
    flex: 1,
    height: 40,
    marginHorizontal: 8
  },
  sliderThumb: {
    backgroundColor: '#007AFF',
    width: 20,
    height: 20
  },
  sliderValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#007AFF',
    textAlign: 'center',
    marginTop: 8
  },
  saveButton: {
    backgroundColor: '#007AFF',
    margin: 16,
    padding: 16,
    borderRadius: 8,
    alignItems: 'center'
  },
  saveButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold'
  }
});

export default DealEvaluation;
```

### Offline Capabilities

#### Offline Data Sync
**Offline-First Architecture**
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-netinfo/netinfo';

class OfflineDataManager {
  constructor() {
    this.isOnline = true;
    this.pendingSync = [];
    this.setupNetworkListener();
  }

  setupNetworkListener() {
    NetInfo.addEventListener(state => {
      this.isOnline = state.isConnected;
      
      if (this.isOnline && this.pendingSync.length > 0) {
        this.syncPendingData();
      }
    });
  }

  async saveDealEvaluation(dealId, evaluation) {
    try {
      // Save locally first
      await AsyncStorage.setItem(
        `deal_evaluation_${dealId}`,
        JSON.stringify(evaluation)
      );

      if (this.isOnline) {
        // Sync to server
        await this.syncToServer('deal_evaluation', { dealId, evaluation });
      } else {
        // Queue for later sync
        this.pendingSync.push({
          type: 'deal_evaluation',
          data: { dealId, evaluation },
          timestamp: Date.now()
        });
      }
    } catch (error) {
      console.error('Error saving deal evaluation:', error);
    }
  }

  async loadDealEvaluation(dealId) {
    try {
      // Try to load from local storage first
      const localData = await AsyncStorage.getItem(`deal_evaluation_${dealId}`);
      
      if (localData) {
        return JSON.parse(localData);
      }

      // If not available locally and online, fetch from server
      if (this.isOnline) {
        const serverData = await this.fetchFromServer(`deal_evaluation_${dealId}`);
        
        // Cache locally
        await AsyncStorage.setItem(
          `deal_evaluation_${dealId}`,
          JSON.stringify(serverData)
        );
        
        return serverData;
      }

      return null;
    } catch (error) {
      console.error('Error loading deal evaluation:', error);
      return null;
    }
  }

  async syncPendingData() {
    for (const item of this.pendingSync) {
      try {
        await this.syncToServer(item.type, item.data);
        
        // Remove from pending list
        this.pendingSync = this.pendingSync.filter(i => i !== item);
      } catch (error) {
        console.error('Error syncing pending data:', error);
      }
    }
  }

  async syncToServer(type, data) {
    // Implementation for syncing to server
    const response = await fetch('/api/sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ type, data })
    });

    if (!response.ok) {
      throw new Error('Sync failed');
    }

    return response.json();
  }
}

export default OfflineDataManager;
```

### Push Notifications

#### Real-Time Alerts
**Push Notification System**
```javascript
import messaging from '@react-native-firebase/messaging';
import PushNotification from 'react-native-push-notification';

class NotificationManager {
  constructor() {
    this.setupPushNotifications();
    this.setupLocalNotifications();
  }

  async setupPushNotifications() {
    // Request permission
    const authStatus = await messaging().requestPermission();
    const enabled = authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
                   authStatus === messaging.AuthorizationStatus.PROVISIONAL;

    if (enabled) {
      // Get FCM token
      const token = await messaging().getToken();
      console.log('FCM Token:', token);

      // Listen for messages
      messaging().onMessage(async remoteMessage => {
        this.handleRemoteMessage(remoteMessage);
      });

      // Handle background messages
      messaging().setBackgroundMessageHandler(async remoteMessage => {
        this.handleBackgroundMessage(remoteMessage);
      });
    }
  }

  setupLocalNotifications() {
    PushNotification.configure({
      onNotification: function(notification) {
        console.log('NOTIFICATION:', notification);
      },
      requestPermissions: true,
    });

    PushNotification.createChannel(
      {
        channelId: 'vc-alerts',
        channelName: 'VC Alerts',
        channelDescription: 'Important VC notifications',
        importance: 4,
        vibrate: true,
      },
      (created) => console.log(`Channel created: ${created}`)
    );
  }

  sendDealAlert(dealId, message) {
    PushNotification.localNotification({
      channelId: 'vc-alerts',
      title: 'Deal Alert',
      message: message,
      data: { dealId },
      soundName: 'default',
      vibrate: true,
    });
  }

  sendPortfolioAlert(message) {
    PushNotification.localNotification({
      channelId: 'vc-alerts',
      title: 'Portfolio Alert',
      message: message,
      soundName: 'default',
      vibrate: true,
    });
  }

  handleRemoteMessage(remoteMessage) {
    // Handle foreground messages
    console.log('Foreground message:', remoteMessage);
    
    // Show local notification
    PushNotification.localNotification({
      channelId: 'vc-alerts',
      title: remoteMessage.notification.title,
      message: remoteMessage.notification.body,
      data: remoteMessage.data,
    });
  }

  handleBackgroundMessage(remoteMessage) {
    // Handle background messages
    console.log('Background message:', remoteMessage);
  }
}

export default NotificationManager;
```

### Security Features

#### Biometric Authentication
**Secure Mobile Access**
```javascript
import TouchID from 'react-native-touch-id';
import Keychain from 'react-native-keychain';

class BiometricAuth {
  async setupBiometricAuth() {
    try {
      const biometryType = await TouchID.isSupported();
      
      if (biometryType) {
        // Store credentials securely
        await Keychain.setInternetCredentials(
          'vc_app_credentials',
          'user@example.com',
          'secure_password'
        );
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Biometric setup failed:', error);
      return false;
    }
  }

  async authenticateWithBiometrics() {
    try {
      const biometryType = await TouchID.isSupported();
      
      if (biometryType) {
        const result = await TouchID.authenticate(
          'Authenticate to access VC Dashboard',
          {
            title: 'Authentication Required',
            subTitle: 'Use biometrics to access your portfolio',
            description: 'Place your finger on the sensor',
            fallbackLabel: 'Use Passcode',
            cancelLabel: 'Cancel'
          }
        );
        
        if (result) {
          // Retrieve credentials
          const credentials = await Keychain.getInternetCredentials('vc_app_credentials');
          return credentials;
        }
      }
      
      return null;
    } catch (error) {
      console.error('Biometric authentication failed:', error);
      return null;
    }
  }

  async logout() {
    try {
      // Clear stored credentials
      await Keychain.resetInternetCredentials('vc_app_credentials');
      return true;
    } catch (error) {
      console.error('Logout failed:', error);
      return false;
    }
  }
}

export default BiometricAuth;
```

This comprehensive mobile app interface provides a complete mobile experience for VC professionals, including real-time dashboards, deal evaluation tools, offline capabilities, push notifications, and biometric security. The app is designed to work seamlessly across iOS and Android platforms while maintaining the same functionality as the desktop version.



