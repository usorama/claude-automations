# Security & Compliance Templates

## 1. Authentication & Authorization Templates

### JWT Authentication Implementation

```javascript
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const rateLimit = require('express-rate-limit');

class AuthenticationService {
  constructor() {
    this.jwtSecret = process.env.JWT_SECRET;
    this.jwtRefreshSecret = process.env.JWT_REFRESH_SECRET;
    this.tokenExpiry = '15m';
    this.refreshTokenExpiry = '7d';
  }

  async hashPassword(password) {
    const saltRounds = 12;
    return await bcrypt.hash(password, saltRounds);
  }

  async verifyPassword(password, hashedPassword) {
    return await bcrypt.compare(password, hashedPassword);
  }

  generateTokens(payload) {
    const accessToken = jwt.sign(payload, this.jwtSecret, {
      expiresIn: this.tokenExpiry,
      issuer: 'your-app',
      audience: 'your-app-users'
    });

    const refreshToken = jwt.sign(payload, this.jwtRefreshSecret, {
      expiresIn: this.refreshTokenExpiry,
      issuer: 'your-app',
      audience: 'your-app-users'
    });

    return { accessToken, refreshToken };
  }

  verifyAccessToken(token) {
    try {
      return jwt.verify(token, this.jwtSecret);
    } catch (error) {
      throw new Error('Invalid or expired access token');
    }
  }

  verifyRefreshToken(token) {
    try {
      return jwt.verify(token, this.jwtRefreshSecret);
    } catch (error) {
      throw new Error('Invalid or expired refresh token');
    }
  }
}

// Rate limiting middleware
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 requests per windowMs
  message: {
    error: 'Too many authentication attempts, please try again later.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Authentication middleware
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
      return res.status(401).json({ error: 'Access token required' });
    }

    const authService = new AuthenticationService();
    const decoded = authService.verifyAccessToken(token);
    
    // Additional token validation (e.g., check if user still exists)
    const user = await User.findById(decoded.userId);
    if (!user || !user.isActive) {
      return res.status(401).json({ error: 'Invalid user' });
    }

    req.user = decoded;
    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid or expired token' });
  }
};

// Role-based authorization middleware
const authorizeRoles = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};

module.exports = {
  AuthenticationService,
  authenticateToken,
  authorizeRoles,
  authLimiter
};
```

### OAuth 2.0 Implementation

```javascript
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const GitHubStrategy = require('passport-github2').Strategy;

class OAuthService {
  constructor() {
    this.setupGoogleStrategy();
    this.setupGitHubStrategy();
  }

  setupGoogleStrategy() {
    passport.use(new GoogleStrategy({
      clientID: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: "/auth/google/callback"
    }, async (accessToken, refreshToken, profile, done) => {
      try {
        // Check if user exists
        let user = await User.findOne({ googleId: profile.id });
        
        if (user) {
          return done(null, user);
        }

        // Create new user
        user = new User({
          googleId: profile.id,
          email: profile.emails[0].value,
          name: profile.displayName,
          avatar: profile.photos[0].value,
          provider: 'google'
        });

        await user.save();
        return done(null, user);
      } catch (error) {
        return done(error, null);
      }
    }));
  }

  setupGitHubStrategy() {
    passport.use(new GitHubStrategy({
      clientID: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
      callbackURL: "/auth/github/callback"
    }, async (accessToken, refreshToken, profile, done) => {
      try {
        let user = await User.findOne({ githubId: profile.id });
        
        if (user) {
          return done(null, user);
        }

        user = new User({
          githubId: profile.id,
          email: profile.emails?.[0]?.value,
          name: profile.displayName || profile.username,
          username: profile.username,
          avatar: profile.photos[0].value,
          provider: 'github'
        });

        await user.save();
        return done(null, user);
      } catch (error) {
        return done(error, null);
      }
    }));
  }
}

// OAuth routes
app.get('/auth/google', 
  passport.authenticate('google', { scope: ['profile', 'email'] })
);

app.get('/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    // Generate JWT tokens
    const authService = new AuthenticationService();
    const tokens = authService.generateTokens({
      userId: req.user._id,
      email: req.user.email
    });
    
    // Set secure cookies
    res.cookie('accessToken', tokens.accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 15 * 60 * 1000 // 15 minutes
    });

    res.redirect('/dashboard');
  }
);
```

## 2. Input Validation & Sanitization

```javascript
const { body, query, param, validationResult } = require('express-validator');
const DOMPurify = require('isomorphic-dompurify');
const { escape } = require('html-escaper');

class SecurityValidator {
  // SQL injection prevention
  static preventSQLInjection = [
    body('*').customSanitizer((value) => {
      if (typeof value === 'string') {
        return value.replace(/['"\\;]/g, '');
      }
      return value;
    })
  ];

  // XSS prevention
  static preventXSS = [
    body('*').customSanitizer((value) => {
      if (typeof value === 'string') {
        return DOMPurify.sanitize(escape(value));
      }
      return value;
    })
  ];

  // Email validation
  static validateEmail = [
    body('email')
      .isEmail()
      .normalizeEmail()
      .withMessage('Invalid email format')
  ];

  // Password validation
  static validatePassword = [
    body('password')
      .isLength({ min: 8, max: 128 })
      .withMessage('Password must be 8-128 characters')
      .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
      .withMessage('Password must contain uppercase, lowercase, number, and special character')
  ];

  // File upload validation
  static validateFileUpload = [
    body('filename')
      .matches(/^[a-zA-Z0-9._-]+$/)
      .withMessage('Invalid filename characters'),
    body('filesize')
      .isInt({ min: 1, max: 10 * 1024 * 1024 }) // 10MB max
      .withMessage('File size must be between 1 byte and 10MB'),
    body('mimetype')
      .isIn(['image/jpeg', 'image/png', 'image/gif', 'application/pdf'])
      .withMessage('Invalid file type')
  ];

  // Rate limiting validation
  static createRateLimit(windowMs, max, message) {
    return rateLimit({
      windowMs,
      max,
      message: { error: message },
      standardHeaders: true,
      legacyHeaders: false,
    });
  }
}

// Validation middleware
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: 'Validation failed',
      details: errors.array()
    });
  }
  next();
};

// Usage example
app.post('/api/users',
  SecurityValidator.preventSQLInjection,
  SecurityValidator.preventXSS,
  SecurityValidator.validateEmail,
  SecurityValidator.validatePassword,
  handleValidationErrors,
  createUser
);
```

## 3. Encryption & Data Protection

```javascript
const crypto = require('crypto');
const bcrypt = require('bcrypt');

class EncryptionService {
  constructor() {
    this.algorithm = 'aes-256-gcm';
    this.keyLength = 32;
    this.ivLength = 16;
    this.tagLength = 16;
    this.secretKey = process.env.ENCRYPTION_KEY || crypto.randomBytes(this.keyLength);
  }

  // Encrypt sensitive data
  encrypt(text) {
    try {
      const iv = crypto.randomBytes(this.ivLength);
      const cipher = crypto.createCipher(this.algorithm, this.secretKey);
      cipher.setAAD(Buffer.from('additional-data'));
      
      let encrypted = cipher.update(text, 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      const tag = cipher.getAuthTag();
      
      return {
        encrypted,
        iv: iv.toString('hex'),
        tag: tag.toString('hex')
      };
    } catch (error) {
      throw new Error('Encryption failed');
    }
  }

  // Decrypt sensitive data
  decrypt(encryptedData) {
    try {
      const { encrypted, iv, tag } = encryptedData;
      const decipher = crypto.createDecipher(this.algorithm, this.secretKey);
      
      decipher.setAAD(Buffer.from('additional-data'));
      decipher.setAuthTag(Buffer.from(tag, 'hex'));
      
      let decrypted = decipher.update(encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return decrypted;
    } catch (error) {
      throw new Error('Decryption failed');
    }
  }

  // Hash sensitive data (one-way)
  async hash(data) {
    const saltRounds = 12;
    return await bcrypt.hash(data, saltRounds);
  }

  // Generate secure random tokens
  generateSecureToken(length = 32) {
    return crypto.randomBytes(length).toString('hex');
  }

  // Generate API keys
  generateAPIKey() {
    const timestamp = Date.now().toString();
    const randomBytes = crypto.randomBytes(16).toString('hex');
    return `${timestamp}-${randomBytes}`;
  }
}

// Database encryption middleware
const encryptSensitiveFields = (schema) => {
  const encryptionService = new EncryptionService();
  
  schema.pre('save', function(next) {
    if (this.isModified('socialSecurityNumber')) {
      this.socialSecurityNumber = encryptionService.encrypt(this.socialSecurityNumber);
    }
    if (this.isModified('creditCardNumber')) {
      this.creditCardNumber = encryptionService.encrypt(this.creditCardNumber);
    }
    next();
  });

  schema.methods.decryptSensitiveData = function() {
    const encryptionService = new EncryptionService();
    return {
      ...this.toObject(),
      socialSecurityNumber: encryptionService.decrypt(this.socialSecurityNumber),
      creditCardNumber: encryptionService.decrypt(this.creditCardNumber)
    };
  };
};
```

## 4. Security Headers & CORS Configuration

```javascript
const helmet = require('helmet');
const cors = require('cors');

// Security headers configuration
const securityHeaders = helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      scriptSrc: ["'self'", "https://apis.google.com"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://api.example.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
    },
  },
  hsts: {
    maxAge: 31536000, // 1 year
    includeSubDomains: true,
    preload: true
  },
  noSniff: true,
  xssFilter: true,
  referrerPolicy: { policy: "same-origin" }
});

// CORS configuration
const corsOptions = {
  origin: function (origin, callback) {
    const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [];
    
    // Allow requests with no origin (mobile apps, etc.)
    if (!origin) return callback(null, true);
    
    if (allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  exposedHeaders: ['X-Total-Count', 'X-Page-Count'],
  maxAge: 86400 // 24 hours
};

app.use(securityHeaders);
app.use(cors(corsOptions));

// Additional security middleware
app.use((req, res, next) => {
  // Remove server information
  res.removeHeader('X-Powered-By');
  
  // Add custom security headers
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  
  next();
});
```

## 5. Security Monitoring & Logging

```javascript
const winston = require('winston');
const { Loggly } = require('winston-loggly-bulk');

class SecurityLogger {
  constructor() {
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      defaultMeta: { service: 'security-service' },
      transports: [
        new winston.transports.File({ filename: 'logs/security-error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/security-combined.log' }),
        new winston.transports.Console({
          format: winston.format.simple()
        })
      ]
    });

    // Add external logging service in production
    if (process.env.NODE_ENV === 'production') {
      this.logger.add(new Loggly({
        token: process.env.LOGGLY_TOKEN,
        subdomain: process.env.LOGGLY_SUBDOMAIN,
        tags: ["security", "api"],
        json: true
      }));
    }
  }

  logSecurityEvent(eventType, details, req = null) {
    const logData = {
      eventType,
      details,
      timestamp: new Date().toISOString(),
      ip: req?.ip || req?.connection?.remoteAddress,
      userAgent: req?.get('User-Agent'),
      userId: req?.user?.id,
      sessionId: req?.sessionID
    };

    switch (eventType) {
      case 'AUTHENTICATION_FAILURE':
      case 'AUTHORIZATION_FAILURE':
      case 'SUSPICIOUS_ACTIVITY':
        this.logger.warn('Security Event', logData);
        break;
      case 'SECURITY_BREACH':
      case 'DATA_BREACH':
        this.logger.error('Critical Security Event', logData);
        this.sendSecurityAlert(logData);
        break;
      default:
        this.logger.info('Security Event', logData);
    }
  }

  sendSecurityAlert(logData) {
    // Implement alerting mechanism (email, Slack, PagerDuty, etc.)
    console.error('CRITICAL SECURITY ALERT:', logData);
    
    // Example: Send to external monitoring service
    // await this.sendToAlertingService(logData);
  }
}

// Security monitoring middleware
const securityMonitoring = (req, res, next) => {
  const securityLogger = new SecurityLogger();
  
  // Log all authentication attempts
  if (req.path.includes('/auth/') || req.path.includes('/login')) {
    securityLogger.logSecurityEvent('AUTHENTICATION_ATTEMPT', {
      path: req.path,
      method: req.method
    }, req);
  }

  // Monitor for suspicious patterns
  const suspiciousPatterns = [
    /script[^>]*>.*?<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /\b(union|select|insert|delete|update|drop)\b/gi
  ];

  const requestBody = JSON.stringify(req.body);
  const requestQuery = JSON.stringify(req.query);
  
  suspiciousPatterns.forEach(pattern => {
    if (pattern.test(requestBody) || pattern.test(requestQuery)) {
      securityLogger.logSecurityEvent('SUSPICIOUS_ACTIVITY', {
        pattern: pattern.toString(),
        body: requestBody,
        query: requestQuery
      }, req);
    }
  });

  next();
};

module.exports = { SecurityLogger, securityMonitoring };
```

## 6. Compliance Templates

### GDPR Compliance Template

```javascript
class GDPRComplianceService {
  constructor() {
    this.dataRetentionPeriods = {
      user_data: 365 * 2, // 2 years
      logs: 365, // 1 year
      analytics: 365 * 3 // 3 years
    };
  }

  // Data subject request handling
  async handleDataSubjectRequest(requestType, userId, email) {
    const securityLogger = new SecurityLogger();
    
    securityLogger.logSecurityEvent('GDPR_REQUEST', {
      requestType,
      userId,
      email,
      timestamp: new Date().toISOString()
    });

    switch (requestType) {
      case 'ACCESS':
        return await this.exportUserData(userId);
      case 'RECTIFICATION':
        return await this.updateUserData(userId);
      case 'ERASURE':
        return await this.deleteUserData(userId);
      case 'PORTABILITY':
        return await this.exportPortableData(userId);
      case 'OBJECTION':
        return await this.stopProcessing(userId);
    }
  }

  async exportUserData(userId) {
    // Collect all user data from various services
    const userData = await Promise.all([
      User.findById(userId).select('-password'),
      UserActivity.find({ userId }),
      UserPreferences.findOne({ userId }),
      // Add other data sources
    ]);

    return {
      personal_data: userData[0],
      activity_data: userData[1],
      preferences: userData[2],
      export_date: new Date().toISOString(),
      data_controller: 'Your Company Name'
    };
  }

  async deleteUserData(userId) {
    // Implement cascading deletion
    await Promise.all([
      User.findByIdAndDelete(userId),
      UserActivity.deleteMany({ userId }),
      UserPreferences.deleteOne({ userId }),
      // Add other data deletions
    ]);

    // Log deletion for compliance
    await ComplianceLog.create({
      action: 'USER_DATA_DELETION',
      userId,
      timestamp: new Date(),
      reason: 'GDPR_ERASURE_REQUEST'
    });
  }

  // Consent management
  async recordConsent(userId, consentType, consentGiven) {
    await ConsentRecord.create({
      userId,
      consentType,
      consentGiven,
      timestamp: new Date(),
      ipAddress: req.ip,
      userAgent: req.get('User-Agent')
    });
  }

  // Data retention management
  async enforceDataRetention() {
    const now = new Date();
    
    for (const [dataType, retentionDays] of Object.entries(this.dataRetentionPeriods)) {
      const cutoffDate = new Date(now.getTime() - (retentionDays * 24 * 60 * 60 * 1000));
      
      switch (dataType) {
        case 'user_data':
          await User.deleteMany({ 
            lastActive: { $lt: cutoffDate },
            accountStatus: 'inactive'
          });
          break;
        case 'logs':
          await SecurityLog.deleteMany({ 
            timestamp: { $lt: cutoffDate }
          });
          break;
        case 'analytics':
          await AnalyticsData.deleteMany({ 
            created_at: { $lt: cutoffDate }
          });
          break;
      }
    }
  }
}
```

### SOC 2 Compliance Template

```yaml
# soc2-controls.yaml
security_controls:
  access_controls:
    - control_id: "CC6.1"
      description: "Logical and physical access controls"
      implementation:
        - Multi-factor authentication required
        - Role-based access control implemented
        - Regular access reviews conducted
      evidence:
        - access_logs/
        - user_provisioning_records/
        - access_review_reports/

  system_operations:
    - control_id: "CC7.1"
      description: "System capacity monitoring"
      implementation:
        - Automated monitoring and alerting
        - Capacity planning procedures
        - Performance threshold management
      evidence:
        - monitoring_dashboards/
        - capacity_reports/
        - alert_configurations/

  change_management:
    - control_id: "CC8.1"
      description: "Change management procedures"
      implementation:
        - Formal change approval process
        - Change documentation requirements
        - Rollback procedures defined
      evidence:
        - change_requests/
        - deployment_logs/
        - rollback_procedures/

  risk_management:
    - control_id: "CC9.1"
      description: "Risk assessment procedures"
      implementation:
        - Regular risk assessments
        - Risk treatment plans
        - Risk monitoring processes
      evidence:
        - risk_assessments/
        - risk_registers/
        - treatment_plans/

monitoring_requirements:
  log_retention: "1 year minimum"
  audit_frequency: "Quarterly"
  evidence_collection: "Automated where possible"
  
compliance_automation:
  evidence_collection:
    - security_logs
    - access_logs
    - change_logs
    - monitoring_metrics
  
  reporting:
    - quarterly_compliance_reports
    - monthly_security_dashboards
    - annual_risk_assessments
```