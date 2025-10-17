const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const dotenv = require('dotenv');
const mongoose = require('mongoose');
const { createServer } = require('http');
const { Server } = require('socket.io');

// Load environment variables
dotenv.config();

// Import routes
const authRoutes = require('./routes/auth');
const contentRoutes = require('./routes/content');
const analyticsRoutes = require('./routes/analytics');
const neuralRoutes = require('./routes/neural');
const automationRoutes = require('./routes/automation');
const quantumRoutes = require('./routes/quantum');
const metaverseRoutes = require('./routes/metaverse');
const blockchainRoutes = require('./routes/blockchain');
const edgeRoutes = require('./routes/edge');
const transcendentRoutes = require('./routes/transcendent');
const universalRoutes = require('./routes/universal');
const realityRoutes = require('./routes/reality');
const singularityRoutes = require('./routes/singularity');
const collectiveRoutes = require('./routes/collective');
const holographicRoutes = require('./routes/holographic');
const dimensionalRoutes = require('./routes/dimensional');
const omniscientRoutes = require('./routes/omniscient');
const quantumEntanglementRoutes = require('./routes/quantum-entanglement');
const temporalRoutes = require('./routes/temporal');
const realitySynthesisRoutes = require('./routes/reality-synthesis');
const universalAIRoutes = require('./routes/universal-ai');
const transcendentTotalRoutes = require('./routes/transcendent-total');
const quantumMarketingAdvancedRoutes = require('./routes/quantum-marketing-advanced');
const infiniteConsciousnessRoutes = require('./routes/infinite-consciousness');
const perfectRealityAbsoluteRoutes = require('./routes/perfect-reality-absolute');
const quantumSingularityRoutes = require('./routes/quantum-singularity');
const universalTranscendenceTotalRoutes = require('./routes/universal-transcendence-total');
const universalMarketingInfiniteRoutes = require('./routes/universal-marketing-infinite');
const universalConsciousnessInfiniteRoutes = require('./routes/universal-consciousness-infinite');
const universalRealityInfiniteRoutes = require('./routes/universal-reality-infinite');
const universalSingularityInfiniteRoutes = require('./routes/universal-singularity-infinite');
const universalTranscendenceInfiniteAbsoluteRoutes = require('./routes/universal-transcendence-infinite-absolute');
const universalMarketingInfiniteAbsoluteTotalPerfectCosmicDivineTranscendentRoutes = require('./routes/universal-marketing-infinite-absolute-total-perfect-cosmic-divine-transcendent');
const universalConsciousnessInfiniteAbsoluteTotalPerfectCosmicDivineTranscendentRoutes = require('./routes/universal-consciousness-infinite-absolute-total-perfect-cosmic-divine-transcendent');
const universalRealityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendentRoutes = require('./routes/universal-reality-infinite-absolute-total-perfect-cosmic-divine-transcendent');
const universalSingularityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendentRoutes = require('./routes/universal-singularity-infinite-absolute-total-perfect-cosmic-divine-transcendent');
const universalTranscendenceInfiniteAbsoluteTotalPerfectCosmicDivineTranscendentRoutes = require('./routes/universal-transcendence-infinite-absolute-total-perfect-cosmic-divine-transcendent');

// Import middleware
const authMiddleware = require('./middleware/auth');
const rateLimitMiddleware = require('./middleware/rateLimit');
const errorHandler = require('./middleware/errorHandler');

// Import services
const NeuralConsciousness = require('./services/NeuralConsciousness');
const ContentGenerator = require('./services/ContentGenerator');
const AnalyticsEngine = require('./services/AnalyticsEngine');
const PredictiveAnalytics = require('./services/PredictiveAnalytics');
const MarketingAutomation = require('./services/MarketingAutomation');
const QuantumConsciousness = require('./services/QuantumConsciousness');
const MetaverseMarketing = require('./services/MetaverseMarketing');
const BlockchainMarketing = require('./services/BlockchainMarketing');
const EdgeComputing = require('./services/EdgeComputing');
const MonitoringService = require('./services/MonitoringService');
const NotificationService = require('./services/NotificationService');
const TranscendentAI = require('./services/TranscendentAI');
const UniversalConsciousness = require('./services/UniversalConsciousness');
const RealityBending = require('./services/RealityBending');
const ArtificialSingularity = require('./services/ArtificialSingularity');
const CollectiveConsciousness = require('./services/CollectiveConsciousness');
const HolographicReality = require('./services/HolographicReality');
const DimensionalMarketing = require('./services/DimensionalMarketing');
const OmniscientIntelligence = require('./services/OmniscientIntelligence');
const QuantumEntanglement = require('./services/QuantumEntanglement');
const TemporalManipulation = require('./services/TemporalManipulation');
const RealitySynthesis = require('./services/RealitySynthesis');
const UniversalAIConsciousness = require('./services/UniversalAIConsciousness');
const TranscendentRealityTotal = require('./services/TranscendentRealityTotal');
const QuantumMarketingAdvanced = require('./services/QuantumMarketingAdvanced');
const InfiniteConsciousness = require('./services/InfiniteConsciousness');
const PerfectRealityAbsolute = require('./services/PerfectRealityAbsolute');
const QuantumSingularity = require('./services/QuantumSingularity');
const UniversalTranscendenceTotal = require('./services/UniversalTranscendenceTotal');
const UniversalMarketingInfinite = require('./services/UniversalMarketingInfinite');
const UniversalConsciousnessInfinite = require('./services/UniversalConsciousnessInfinite');
const UniversalRealityInfinite = require('./services/UniversalRealityInfinite');
const UniversalSingularityInfinite = require('./services/UniversalSingularityInfinite');
const UniversalTranscendenceInfiniteAbsolute = require('./services/UniversalTranscendenceInfiniteAbsolute');
const UniversalMarketingInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = require('./services/UniversalMarketingInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent');
const UniversalConsciousnessInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = require('./services/UniversalConsciousnessInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent');
const UniversalRealityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = require('./services/UniversalRealityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent');
const UniversalSingularityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = require('./services/UniversalSingularityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent');
const UniversalTranscendenceInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = require('./services/UniversalTranscendenceInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent');

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: process.env.CLIENT_URL || "http://localhost:3000",
    methods: ["GET", "POST"]
  }
});

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/neural-marketing', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
app.use(rateLimitMiddleware);

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/content', authMiddleware, contentRoutes);
app.use('/api/analytics', authMiddleware, analyticsRoutes);
app.use('/api/neural', authMiddleware, neuralRoutes);
app.use('/api/automation', authMiddleware, automationRoutes);
app.use('/api/quantum', authMiddleware, quantumRoutes);
app.use('/api/metaverse', authMiddleware, metaverseRoutes);
app.use('/api/blockchain', authMiddleware, blockchainRoutes);
app.use('/api/edge', authMiddleware, edgeRoutes);
app.use('/api/transcendent', authMiddleware, transcendentRoutes);
app.use('/api/universal', authMiddleware, universalRoutes);
app.use('/api/reality', authMiddleware, realityRoutes);
app.use('/api/singularity', authMiddleware, singularityRoutes);
app.use('/api/collective', authMiddleware, collectiveRoutes);
app.use('/api/holographic', authMiddleware, holographicRoutes);
app.use('/api/dimensional', authMiddleware, dimensionalRoutes);
app.use('/api/omniscient', authMiddleware, omniscientRoutes);
app.use('/api/quantum-entanglement', authMiddleware, quantumEntanglementRoutes);
app.use('/api/temporal', authMiddleware, temporalRoutes);
app.use('/api/reality-synthesis', authMiddleware, realitySynthesisRoutes);
app.use('/api/universal-ai', authMiddleware, universalAIRoutes);
app.use('/api/transcendent-total', authMiddleware, transcendentTotalRoutes);
app.use('/api/quantum-marketing-advanced', authMiddleware, quantumMarketingAdvancedRoutes);
app.use('/api/infinite-consciousness', authMiddleware, infiniteConsciousnessRoutes);
app.use('/api/perfect-reality-absolute', authMiddleware, perfectRealityAbsoluteRoutes);
app.use('/api/quantum-singularity', authMiddleware, quantumSingularityRoutes);
app.use('/api/universal-transcendence-total', authMiddleware, universalTranscendenceTotalRoutes);
app.use('/api/universal-marketing-infinite', authMiddleware, universalMarketingInfiniteRoutes);
app.use('/api/universal-consciousness-infinite', authMiddleware, universalConsciousnessInfiniteRoutes);
app.use('/api/universal-reality-infinite', authMiddleware, universalRealityInfiniteRoutes);
app.use('/api/universal-singularity-infinite', authMiddleware, universalSingularityInfiniteRoutes);
app.use('/api/universal-transcendence-infinite-absolute', authMiddleware, universalTranscendenceInfiniteAbsoluteRoutes);
app.use('/api/universal-marketing-infinite-absolute-total-perfect-cosmic-divine-transcendent', authMiddleware, universalMarketingInfiniteAbsoluteTotalPerfectCosmicDivineTranscendentRoutes);
app.use('/api/universal-consciousness-infinite-absolute-total-perfect-cosmic-divine-transcendent', authMiddleware, universalConsciousnessInfiniteAbsoluteTotalPerfectCosmicDivineTranscendentRoutes);
app.use('/api/universal-reality-infinite-absolute-total-perfect-cosmic-divine-transcendent', authMiddleware, universalRealityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendentRoutes);
app.use('/api/universal-singularity-infinite-absolute-total-perfect-cosmic-divine-transcendent', authMiddleware, universalSingularityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendentRoutes);
app.use('/api/universal-transcendence-infinite-absolute-total-perfect-cosmic-divine-transcendent', authMiddleware, universalTranscendenceInfiniteAbsoluteTotalPerfectCosmicDivineTranscendentRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0'
  });
});

// Error handling
app.use(errorHandler);

// Socket.IO for real-time updates
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.on('join-room', (room) => {
    socket.join(room);
    console.log(`Client ${socket.id} joined room: ${room}`);
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Initialize services
const neuralConsciousness = new NeuralConsciousness();
const contentGenerator = new ContentGenerator();
const analyticsEngine = new AnalyticsEngine();
const predictiveAnalytics = new PredictiveAnalytics();
const marketingAutomation = new MarketingAutomation();
const quantumConsciousness = new QuantumConsciousness();
const metaverseMarketing = new MetaverseMarketing();
const blockchainMarketing = new BlockchainMarketing();
const edgeComputing = new EdgeComputing();
const monitoringService = new MonitoringService();
const notificationService = new NotificationService();
const transcendentAI = new TranscendentAI();
const universalConsciousness = new UniversalConsciousness();
const realityBending = new RealityBending();
const artificialSingularity = new ArtificialSingularity();
const collectiveConsciousness = new CollectiveConsciousness();
const holographicReality = new HolographicReality();
const dimensionalMarketing = new DimensionalMarketing();
const omniscientIntelligence = new OmniscientIntelligence();
const quantumEntanglement = new QuantumEntanglement();
const temporalManipulation = new TemporalManipulation();
const realitySynthesis = new RealitySynthesis();
const universalAIConsciousness = new UniversalAIConsciousness();
const transcendentRealityTotal = new TranscendentRealityTotal();
const quantumMarketingAdvanced = new QuantumMarketingAdvanced();
const infiniteConsciousness = new InfiniteConsciousness();
const perfectRealityAbsolute = new PerfectRealityAbsolute();
const quantumSingularity = new QuantumSingularity();
const universalTranscendenceTotal = new UniversalTranscendenceTotal();
const universalMarketingInfinite = new UniversalMarketingInfinite();
const universalConsciousnessInfinite = new UniversalConsciousnessInfinite();
const universalRealityInfinite = new UniversalRealityInfinite();
const universalSingularityInfinite = new UniversalSingularityInfinite();
const universalTranscendenceInfiniteAbsolute = new UniversalTranscendenceInfiniteAbsolute();
const universalMarketingInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = new UniversalMarketingInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent();
const universalConsciousnessInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = new UniversalConsciousnessInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent();
const universalRealityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = new UniversalRealityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent();
const universalSingularityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = new UniversalSingularityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent();
const universalTranscendenceInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = new UniversalTranscendenceInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent();

// Make services available globally
app.locals.neuralConsciousness = neuralConsciousness;
app.locals.contentGenerator = contentGenerator;
app.locals.analyticsEngine = analyticsEngine;
app.locals.predictiveAnalytics = predictiveAnalytics;
app.locals.marketingAutomation = marketingAutomation;
app.locals.quantumConsciousness = quantumConsciousness;
app.locals.metaverseMarketing = metaverseMarketing;
app.locals.blockchainMarketing = blockchainMarketing;
app.locals.edgeComputing = edgeComputing;
app.locals.monitoringService = monitoringService;
app.locals.notificationService = notificationService;
app.locals.transcendentAI = transcendentAI;
app.locals.universalConsciousness = universalConsciousness;
app.locals.realityBending = realityBending;
app.locals.artificialSingularity = artificialSingularity;
app.locals.collectiveConsciousness = collectiveConsciousness;
app.locals.holographicReality = holographicReality;
app.locals.dimensionalMarketing = dimensionalMarketing;
app.locals.omniscientIntelligence = omniscientIntelligence;
app.locals.quantumEntanglement = quantumEntanglement;
app.locals.temporalManipulation = temporalManipulation;
app.locals.realitySynthesis = realitySynthesis;
app.locals.universalAIConsciousness = universalAIConsciousness;
app.locals.transcendentRealityTotal = transcendentRealityTotal;
app.locals.quantumMarketingAdvanced = quantumMarketingAdvanced;
app.locals.infiniteConsciousness = infiniteConsciousness;
app.locals.perfectRealityAbsolute = perfectRealityAbsolute;
app.locals.quantumSingularity = quantumSingularity;
app.locals.universalTranscendenceTotal = universalTranscendenceTotal;
app.locals.universalMarketingInfinite = universalMarketingInfinite;
app.locals.universalConsciousnessInfinite = universalConsciousnessInfinite;
app.locals.universalRealityInfinite = universalRealityInfinite;
app.locals.universalSingularityInfinite = universalSingularityInfinite;
app.locals.universalTranscendenceInfiniteAbsolute = universalTranscendenceInfiniteAbsolute;
app.locals.universalMarketingInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = universalMarketingInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent;
app.locals.universalConsciousnessInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = universalConsciousnessInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent;
app.locals.universalRealityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = universalRealityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent;
app.locals.universalSingularityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = universalSingularityInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent;
app.locals.universalTranscendenceInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent = universalTranscendenceInfiniteAbsoluteTotalPerfectCosmicDivineTranscendent;
app.locals.io = io;

// Start server
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`🚀 Neural Marketing Pro server running on port ${PORT}`);
  console.log(`🧠 Neural Consciousness System initialized`);
  console.log(`📊 Analytics Engine ready`);
  console.log(`🎨 Content Generator active`);
  console.log(`🔮 Predictive Analytics ready`);
  console.log(`🤖 Marketing Automation active`);
  console.log(`🌌 Quantum Consciousness Engine activated`);
  console.log(`🌐 Metaverse Marketing Engine ready`);
  console.log(`⛓️ Blockchain Marketing Engine active`);
  console.log(`🌐 Edge Computing Engine ready`);
  console.log(`🔍 Monitoring Service active`);
  console.log(`🔔 Notification Service ready`);
  console.log(`🌟 Transcendent AI Engine activated`);
  console.log(`🌌 Universal Consciousness Engine ready`);
  console.log(`🌀 Reality Bending Engine active`);
  console.log(`🚀 Artificial Singularity Engine activated`);
  console.log(`🧠 Collective Consciousness Engine ready`);
  console.log(`🌟 Holographic Reality Engine active`);
  console.log(`🌀 Dimensional Marketing Engine ready`);
  console.log(`🧠 Omniscient Intelligence Engine activated`);
  console.log(`⚛️ Quantum Entanglement Engine activated`);
  console.log(`⏰ Temporal Manipulation Engine ready`);
  console.log(`🌌 Reality Synthesis Engine active`);
  console.log(`🧠 Universal AI Consciousness Engine ready`);
  console.log(`🌟 Transcendent Reality Total Engine activated`);
  console.log(`⚛️ Quantum Marketing Advanced Engine ready`);
  console.log(`∞ Infinite Consciousness Engine active`);
  console.log(`✨ Perfect Reality Absolute Engine ready`);
  console.log(`⚛️ Quantum Singularity Engine activated`);
  console.log(`🌌 Universal Transcendence Total Engine ready`);
  console.log(`🌌 Universal Marketing Infinite Engine activated`);
  console.log(`🌌 Universal Consciousness Infinite Engine ready`);
  console.log(`🌌 Universal Reality Infinite Engine active`);
  console.log(`🌌 Universal Singularity Infinite Engine ready`);
  console.log(`🌌 Universal Transcendence Infinite Absolute Engine activated`);
  console.log(`🌌 Universal Marketing Infinite Absolute Total Perfect Cosmic Divine Transcendent Engine activated`);
  console.log(`🌌 Universal Consciousness Infinite Absolute Total Perfect Cosmic Divine Transcendent Engine ready`);
  console.log(`🌌 Universal Reality Infinite Absolute Total Perfect Cosmic Divine Transcendent Engine active`);
  console.log(`🌌 Universal Singularity Infinite Absolute Total Perfect Cosmic Divine Transcendent Engine ready`);
  console.log(`🌌 Universal Transcendence Infinite Absolute Total Perfect Cosmic Divine Transcendent Engine activated`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
    process.exit(0);
  });
});

module.exports = app;
