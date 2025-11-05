const mongoose = require('mongoose');

/**
 * MongoDB Connection Handler
 * Manages database connection with automatic reconnection
 */
class DatabaseManager {
  constructor() {
    this.isConnected = false;
    this.connectionAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectInterval = 5000;
  }

  /**
   * Connect to MongoDB
   */
  async connect() {
    try {
      const mongoUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/ai-marketing-saas';
      
      const options = {
        maxPoolSize: 10,
        minPoolSize: 2,
        serverSelectionTimeoutMS: 5000,
        socketTimeoutMS: 45000,
        connectTimeoutMS: 10000,
        bufferMaxEntries: 0,
        bufferCommands: false,
      };

      mongoose.set('strictQuery', false);
      
      await mongoose.connect(mongoUri, options);
      
      this.isConnected = true;
      this.connectionAttempts = 0;
      
      console.log('✅ MongoDB connected successfully');
      
      // Setup connection event handlers
      this.setupEventHandlers();
      
      return true;
    } catch (error) {
      console.error('❌ MongoDB connection error:', error.message);
      this.isConnected = false;
      
      // Try to reconnect
      if (this.connectionAttempts < this.maxReconnectAttempts) {
        this.connectionAttempts++;
        console.log(`Attempting to reconnect... (${this.connectionAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
          this.connect();
        }, this.reconnectInterval);
      } else {
        console.error('Max reconnection attempts reached. Please check your MongoDB connection.');
        process.exit(1);
      }
      
      return false;
    }
  }

  /**
   * Setup MongoDB event handlers
   */
  setupEventHandlers() {
    mongoose.connection.on('error', (err) => {
      console.error('MongoDB connection error:', err);
      this.isConnected = false;
    });

    mongoose.connection.on('disconnected', () => {
      console.warn('MongoDB disconnected');
      this.isConnected = false;
    });

    mongoose.connection.on('reconnected', () => {
      console.log('MongoDB reconnected');
      this.isConnected = true;
    });

    mongoose.connection.on('connected', () => {
      console.log('MongoDB connected');
      this.isConnected = true;
    });
  }

  /**
   * Disconnect from MongoDB
   */
  async disconnect() {
    try {
      await mongoose.disconnect();
      this.isConnected = false;
      console.log('MongoDB disconnected');
      return true;
    } catch (error) {
      console.error('Error disconnecting from MongoDB:', error);
      return false;
    }
  }

  /**
   * Get connection status
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      readyState: mongoose.connection.readyState,
      connectionAttempts: this.connectionAttempts,
    };
  }

  /**
   * Check if database is healthy
   */
  async healthCheck() {
    try {
      if (this.isConnected && mongoose.connection.readyState === 1) {
        await mongoose.connection.db.admin().ping();
        return { status: 'healthy', database: 'connected' };
      } else {
        return { status: 'unhealthy', database: 'disconnected' };
      }
    } catch (error) {
      return { status: 'unhealthy', database: 'error', error: error.message };
    }
  }
}

// Create singleton instance
const dbManager = new DatabaseManager();

// Default connection function
const connectDB = async () => {
  return await dbManager.connect();
};

module.exports = { connectDB, dbManager };



