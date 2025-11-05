import { Request, Response, NextFunction } from 'express';
import { customerFeedbackService } from '../services/customerFeedbackService';

export interface FeedbackRequest extends Request {
  feedback?: any;
  analytics?: any;
}

// Middleware para validar datos de feedback
export const validateFeedbackData = (req: FeedbackRequest, res: Response, next: NextFunction) => {
  const { content, source, platform, language, region } = req.body;

  // Validaciones básicas
  if (!content || typeof content !== 'string' || content.trim().length === 0) {
    return res.status(400).json({
      error: 'Content is required and must be a non-empty string'
    });
  }

  if (content.length > 10000) {
    return res.status(400).json({
      error: 'Content must be less than 10,000 characters'
    });
  }

  if (source && !['social_media', 'survey', 'course_feedback', 'review', 'support_ticket', 'webinar', 'email'].includes(source)) {
    return res.status(400).json({
      error: 'Invalid source. Must be one of: social_media, survey, course_feedback, review, support_ticket, webinar, email'
    });
  }

  if (language && !['es', 'pt', 'en'].includes(language)) {
    return res.status(400).json({
      error: 'Invalid language. Must be one of: es, pt, en'
    });
  }

  if (region && !['MX', 'AR', 'CO', 'BR', 'CL', 'PE', 'UY', 'PY', 'BO', 'EC', 'VE', 'LATAM'].includes(region)) {
    return res.status(400).json({
      error: 'Invalid region. Must be a valid Latin American country code or LATAM'
    });
  }

  next();
};

// Middleware para enriquecer datos de feedback
export const enrichFeedbackData = async (req: FeedbackRequest, res: Response, next: NextFunction) => {
  try {
    const { content, language = 'es', region = 'LATAM' } = req.body;

    // Detectar idioma automáticamente si no se especifica
    if (!req.body.language) {
      req.body.language = detectLanguage(content);
    }

    // Detectar región automáticamente si no se especifica
    if (!req.body.region) {
      req.body.region = detectRegion(content, req.body.language);
    }

    // Agregar metadatos adicionales
    req.body.metadata = {
      ...req.body.metadata,
      userAgent: req.get('User-Agent'),
      ipAddress: req.ip,
      timestamp: new Date(),
      processedBy: 'feedback-middleware'
    };

    next();
  } catch (error) {
    console.error('Error enriching feedback data:', error);
    next();
  }
};

// Middleware para análisis de sentimiento en tiempo real
export const analyzeSentiment = async (req: FeedbackRequest, res: Response, next: NextFunction) => {
  try {
    const { content, language } = req.body;

    // Análisis básico de sentimiento
    const sentimentAnalysis = analyzeSentimentBasic(content, language);
    
    req.body.sentiment = sentimentAnalysis.sentiment;
    req.body.sentimentScore = sentimentAnalysis.score;
    req.body.metadata = {
      ...req.body.metadata,
      sentimentAnalysis: {
        confidence: sentimentAnalysis.confidence,
        keywords: sentimentAnalysis.keywords,
        emotionalTone: sentimentAnalysis.emotionalTone
      }
    };

    next();
  } catch (error) {
    console.error('Error analyzing sentiment:', error);
    next();
  }
};

// Middleware para detectar spam
export const detectSpam = (req: FeedbackRequest, res: Response, next: NextFunction) => {
  const { content } = req.body;

  const spamScore = calculateSpamScore(content);
  
  if (spamScore > 0.7) {
    return res.status(400).json({
      error: 'Content appears to be spam and has been rejected'
    });
  }

  req.body.metadata = {
    ...req.body.metadata,
    spamScore,
    isSpam: spamScore > 0.5
  };

  next();
};

// Middleware para rate limiting por IP
export const rateLimitByIP = (maxRequests: number = 100, windowMs: number = 15 * 60 * 1000) => {
  const requests = new Map<string, { count: number; resetTime: number }>();

  return (req: FeedbackRequest, res: Response, next: NextFunction) => {
    const ip = req.ip;
    const now = Date.now();
    const windowStart = now - windowMs;

    // Limpiar entradas expiradas
    for (const [key, value] of requests.entries()) {
      if (value.resetTime < now) {
        requests.delete(key);
      }
    }

    const ipData = requests.get(ip);
    
    if (!ipData) {
      requests.set(ip, { count: 1, resetTime: now + windowMs });
      next();
    } else if (ipData.count < maxRequests) {
      ipData.count++;
      next();
    } else {
      return res.status(429).json({
        error: 'Too many requests. Please try again later.',
        retryAfter: Math.ceil((ipData.resetTime - now) / 1000)
      });
    }
  };
};

// Middleware para logging de feedback
export const logFeedback = (req: FeedbackRequest, res: Response, next: NextFunction) => {
  const startTime = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const logData = {
      method: req.method,
      url: req.url,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      statusCode: res.statusCode,
      duration,
      timestamp: new Date(),
      feedbackId: req.body.id || 'unknown'
    };

    console.log('Feedback request:', JSON.stringify(logData));
  });

  next();
};

// Middleware para validar permisos de analytics
export const validateAnalyticsAccess = (req: FeedbackRequest, res: Response, next: NextFunction) => {
  const user = (req as any).user;
  
  if (!user) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  // Verificar permisos de analytics
  if (!user.permissions || !user.permissions.includes('analytics:read')) {
    return res.status(403).json({ error: 'Analytics access denied' });
  }

  next();
};

// Middleware para validar permisos de administración
export const validateAdminAccess = (req: FeedbackRequest, res: Response, next: NextFunction) => {
  const user = (req as any).user;
  
  if (!user) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  // Verificar permisos de administración
  if (!user.permissions || !user.permissions.includes('admin:write')) {
    return res.status(403).json({ error: 'Admin access denied' });
  }

  next();
};

// Funciones auxiliares
function detectLanguage(content: string): string {
  // Detección básica de idioma
  const spanishWords = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'muy', 'más', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'tres', 'años', 'hasta', 'desde', 'está', 'mi', 'porque', 'más', 'solo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene', 'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ese', 'ahora', 'cada', 'e', 'vida', 'otro', 'después', 'te', 'otros', 'aunque', 'esa', 'esas', 'estos', 'estas', 'están', 'estaba', 'estaban', 'estado', 'estados', 'estará', 'estarán', 'estaría', 'estarían', 'esté', 'estén', 'estuviera', 'estuvieran', 'estuvieron', 'estuvo', 'está', 'están', 'estaba', 'estaban', 'estado', 'estados', 'estará', 'estarán', 'estaría', 'estarían', 'esté', 'estén', 'estuviera', 'estuvieran', 'estuvieron', 'estuvo'];
  const portugueseWords = ['o', 'a', 'de', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas', 'numa', 'pelos', 'pelas', 'esse', 'eles', 'estava', 'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 'pelas', 'esse', 'eles', 'estava', 'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm'];
  const englishWords = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'ought', 'need', 'dare', 'used'];

  const contentLower = content.toLowerCase();
  
  let spanishCount = 0;
  let portugueseCount = 0;
  let englishCount = 0;

  spanishWords.forEach(word => {
    if (contentLower.includes(word)) spanishCount++;
  });

  portugueseWords.forEach(word => {
    if (contentLower.includes(word)) portugueseCount++;
  });

  englishWords.forEach(word => {
    if (contentLower.includes(word)) englishCount++;
  });

  if (portugueseCount > spanishCount && portugueseCount > englishCount) return 'pt';
  if (englishCount > spanishCount && englishCount > portugueseCount) return 'en';
  return 'es'; // Default to Spanish for LATAM
}

function detectRegion(content: string, language: string): string {
  // Detección básica de región basada en palabras clave
  const regionKeywords = {
    'MX': ['méxico', 'mexicano', 'mexicana', 'cdmx', 'guadalajara', 'monterrey'],
    'AR': ['argentina', 'argentino', 'argentina', 'buenos aires', 'córdoba', 'rosario'],
    'CO': ['colombia', 'colombiano', 'colombiana', 'bogotá', 'medellín', 'cali'],
    'BR': ['brasil', 'brasileiro', 'brasileira', 'são paulo', 'rio de janeiro', 'brasília'],
    'CL': ['chile', 'chileno', 'chilena', 'santiago', 'valparaíso', 'concepción'],
    'PE': ['perú', 'peruano', 'peruana', 'lima', 'arequipa', 'cusco'],
    'UY': ['uruguay', 'uruguayo', 'uruguaya', 'montevideo', 'paysandú', 'salto'],
    'PY': ['paraguay', 'paraguayo', 'paraguaya', 'asunción', 'ciudad del este', 'encarnación'],
    'BO': ['bolivia', 'boliviano', 'boliviana', 'la paz', 'santa cruz', 'cochabamba'],
    'EC': ['ecuador', 'ecuatoriano', 'ecuatoriana', 'quito', 'guayaquil', 'cuenca'],
    'VE': ['venezuela', 'venezolano', 'venezolana', 'caracas', 'maracaibo', 'valencia']
  };

  const contentLower = content.toLowerCase();
  
  for (const [region, keywords] of Object.entries(regionKeywords)) {
    if (keywords.some(keyword => contentLower.includes(keyword))) {
      return region;
    }
  }

  return 'LATAM'; // Default
}

function analyzeSentimentBasic(content: string, language: string): {
  sentiment: string;
  score: number;
  confidence: number;
  keywords: string[];
  emotionalTone: string;
} {
  const positiveWords = {
    'es': ['excelente', 'genial', 'fantástico', 'increíble', 'perfecto', 'recomiendo', 'satisfecho', 'feliz', 'contento', 'impresionante', 'maravilloso', 'increíble', 'bueno', 'buena', 'buenos', 'buenas'],
    'pt': ['excelente', 'ótimo', 'fantástico', 'incrível', 'perfeito', 'recomendo', 'satisfeito', 'feliz', 'impressionante', 'maravilhoso', 'incrível', 'bom', 'boa', 'bons', 'boas'],
    'en': ['excellent', 'great', 'fantastic', 'amazing', 'perfect', 'recommend', 'satisfied', 'happy', 'impressive', 'wonderful', 'incredible', 'good', 'nice', 'awesome']
  };

  const negativeWords = {
    'es': ['terrible', 'malo', 'horrible', 'pésimo', 'decepcionante', 'frustrante', 'problema', 'error', 'falla', 'insatisfecho', 'mal', 'mala', 'malos', 'malas', 'pésimo', 'pésima'],
    'pt': ['terrível', 'ruim', 'horrível', 'péssimo', 'decepcionante', 'frustrante', 'problema', 'erro', 'falha', 'insatisfeito', 'ruim', 'ruins'],
    'en': ['terrible', 'bad', 'horrible', 'awful', 'disappointing', 'frustrating', 'problem', 'error', 'failure', 'unsatisfied', 'poor', 'worst']
  };

  const words = positiveWords[language] || positiveWords['es'];
  const negativeWordsList = negativeWords[language] || negativeWords['es'];

  let score = 0;
  let positiveCount = 0;
  let negativeCount = 0;
  const foundKeywords: string[] = [];

  const contentLower = content.toLowerCase();

  words.forEach(word => {
    if (contentLower.includes(word)) {
      positiveCount++;
      score += 0.1;
      foundKeywords.push(word);
    }
  });

  negativeWordsList.forEach(word => {
    if (contentLower.includes(word)) {
      negativeCount++;
      score -= 0.1;
      foundKeywords.push(word);
    }
  });

  // Normalizar score entre -1 y 1
  score = Math.max(-1, Math.min(1, score));

  let sentiment = 'neutral';
  if (score > 0.2) sentiment = 'positive';
  else if (score < -0.2) sentiment = 'negative';
  else if (positiveCount > 0 && negativeCount > 0) sentiment = 'mixed';

  const confidence = Math.min(1, (Math.abs(score) + 0.1) * 2);
  
  let emotionalTone = 'neutral';
  if (sentiment === 'positive') emotionalTone = 'enthusiastic';
  else if (sentiment === 'negative') emotionalTone = 'frustrated';
  else if (sentiment === 'mixed') emotionalTone = 'conflicted';

  return {
    sentiment,
    score: parseFloat(score.toFixed(2)),
    confidence: parseFloat(confidence.toFixed(2)),
    keywords: foundKeywords,
    emotionalTone
  };
}

function calculateSpamScore(content: string): number {
  let score = 0;

  // Detectar patrones de spam
  const spamPatterns = [
    /(.)\1{4,}/g, // Caracteres repetidos
    /[A-Z]{10,}/g, // Muchas mayúsculas
    /https?:\/\/[^\s]+/g, // URLs
    /[0-9]{10,}/g, // Muchos números
    /[^\w\s]{5,}/g // Muchos caracteres especiales
  ];

  spamPatterns.forEach(pattern => {
    const matches = content.match(pattern);
    if (matches) {
      score += matches.length * 0.1;
    }
  });

  // Detectar palabras de spam
  const spamWords = ['viagra', 'casino', 'poker', 'lottery', 'winner', 'congratulations', 'free', 'click here', 'buy now', 'limited time'];
  spamWords.forEach(word => {
    if (content.toLowerCase().includes(word)) {
      score += 0.2;
    }
  });

  // Detectar longitud sospechosa
  if (content.length < 10) score += 0.3;
  if (content.length > 1000) score += 0.2;

  return Math.min(1, score);
}