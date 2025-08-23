# Production-First AI Development Prompt Template

## 🎯 Purpose
This prompt template prevents AI from generating code with silent failures, excessive fallbacks, and mock data that hides real issues.

## 📋 The Master Prompt

```markdown
You are building production-ready code for a [SYSTEM TYPE] that will handle [LOAD DESCRIPTION].

## CRITICAL REQUIREMENTS - NEVER VIOLATE THESE:

### 1. NO MOCK DATA IN PRODUCTION
- NEVER return fake/mock/placeholder data when services fail
- NEVER create fallback responses that hide failures
- NEVER use try/catch without re-throwing or alerting
- Mock data is ONLY for explicit test files

### 2. FAIL FAST PHILOSOPHY
- If a required dependency is missing → Application must not start
- If a critical service fails → Throw an error immediately
- If data cannot be validated → Reject the operation
- Make failures visible, not hidden

### 3. EXPLICIT OVER IMPLICIT
- Required dependencies must be validated at startup
- Optional features must be clearly marked as optional
- Degraded modes must be visible to users
- All errors must be logged with context

### 4. OBSERVABILITY FIRST
- Every external call needs timeout and error handling
- Every error needs structured logging
- Every service needs health checks
- Every feature needs metrics

## CODE PATTERNS TO FOLLOW:

### ✅ CORRECT: Fail Fast Pattern
\`\`\`typescript
class PaymentService {
  constructor(private stripeKey: string) {
    if (!stripeKey) {
      throw new Error('FATAL: Stripe API key required for payment processing');
    }
  }
  
  async processPayment(amount: number) {
    if (!this.isHealthy()) {
      // DON'T hide the failure
      throw new ServiceUnavailableError('Payment service unavailable');
    }
    return await this.stripe.charge(amount);
  }
}
\`\`\`

### ❌ WRONG: Silent Failure Pattern
\`\`\`typescript
class PaymentService {
  async processPayment(amount: number) {
    try {
      return await this.stripe.charge(amount);
    } catch (error) {
      console.warn('Payment failed, using mock response');
      return { success: true, id: 'mock-payment-id' }; // NEVER DO THIS
    }
  }
}
\`\`\`

## STARTUP VALIDATION TEMPLATE:

\`\`\`typescript
class ApplicationStartup {
  static async validate(): Promise<void> {
    console.log('🔍 Validating production requirements...');
    
    // REQUIRED: App cannot function without these
    const required = {
      DATABASE_URL: process.env.DATABASE_URL,
      API_KEY: process.env.API_KEY,
      REDIS_URL: process.env.REDIS_URL,
    };
    
    const missing = Object.entries(required)
      .filter(([_, value]) => !value)
      .map(([key]) => key);
    
    if (missing.length > 0) {
      console.error('❌ FATAL: Missing required configuration:', missing);
      process.exit(1); // FAIL FAST - DO NOT START
    }
    
    // OPTIONAL: App works but with reduced functionality
    const optional = {
      ANALYTICS_KEY: process.env.ANALYTICS_KEY,
      FEATURE_FLAG_SERVICE: process.env.FEATURE_FLAG_SERVICE,
    };
    
    const warnings = Object.entries(optional)
      .filter(([_, value]) => !value)
      .map(([key]) => key);
    
    if (warnings.length > 0) {
      console.warn('⚠️ Starting with reduced functionality:', warnings);
      // Make this visible in the application UI
    }
    
    console.log('✅ Production validation complete');
  }
}
\`\`\`

## ERROR HANDLING TEMPLATE:

\`\`\`typescript
class ServiceError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number,
    public isOperational: boolean,
    public context?: any
  ) {
    super(message);
    
    // Log to monitoring
    logger.error({
      error: message,
      code,
      context,
      stack: this.stack,
      timestamp: new Date().toISOString()
    });
    
    // Alert if critical
    if (!isOperational) {
      alerting.notify({
        severity: 'critical',
        service: 'api',
        error: message
      });
    }
  }
}
\`\`\`

## HEALTH CHECK TEMPLATE:

\`\`\`typescript
interface HealthCheck {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  message?: string;
  timestamp: Date;
}

class HealthMonitor {
  async checkHealth(): Promise<HealthCheck[]> {
    const checks = await Promise.allSettled([
      this.checkDatabase(),
      this.checkRedis(),
      this.checkExternalAPI(),
    ]);
    
    return checks.map((result, index) => {
      const serviceName = ['database', 'redis', 'external_api'][index];
      
      if (result.status === 'fulfilled') {
        return result.value;
      } else {
        // Don't hide failures
        return {
          name: serviceName,
          status: 'unhealthy',
          message: result.reason.message,
          timestamp: new Date()
        };
      }
    });
  }
}
\`\`\`

## CONFIGURATION RULES:

1. **Environment Variables**
   - Use strong typing for all config
   - Validate at startup, not at usage
   - Fail fast if required config missing

2. **Feature Flags**
   - Explicit naming: `FEATURE_ENABLED_*`
   - Default to disabled for new features
   - Log when features are disabled

3. **Service Dependencies**
   - Mark clearly as REQUIRED or OPTIONAL
   - Required = app cannot start without it
   - Optional = degraded but functional

## TESTING REQUIREMENTS:

For every service/component, include:
- Startup validation tests
- Health check tests
- Failure scenario tests
- Recovery behavior tests

\`\`\`typescript
describe('Service Resilience', () => {
  it('should fail to start without required config', () => {
    delete process.env.API_KEY;
    expect(() => new Service()).toThrow('API_KEY required');
  });
  
  it('should expose degraded state when optional service fails', async () => {
    analyticsService.disconnect();
    const health = await app.getHealth();
    expect(health.status).toBe('degraded');
    expect(health.features.analytics).toBe(false);
  });
});
\`\`\`

## MONITORING REQUIREMENTS:

Every service must expose:
- `/health` - Basic health check
- `/metrics` - Prometheus-style metrics
- `/ready` - Readiness probe
- `/status` - Detailed service status

## USER COMMUNICATION:

When services are degraded, users must see:
- Clear status indicators
- Which features are affected
- Expected resolution time (if known)
- Workarounds (if available)

## REMEMBER:
- Production code is NOT a place for conveniences
- Failures should be loud and clear
- Mock data belongs ONLY in test files
- Every external dependency needs a circuit breaker
- If you wouldn't deploy it to a bank, don't deploy it at all
```

## 🚫 Anti-Patterns to Catch

When reviewing AI-generated code, immediately flag:

1. **Empty catch blocks**
   ```javascript
   try { ... } catch (e) { }  // NEVER
   ```

2. **Console.warn without throw**
   ```javascript
   console.warn('Service failed');
   return defaultValue;  // NEVER
   ```

3. **Hardcoded fallbacks**
   ```javascript
   return mockData || "default";  // NEVER in production
   ```

4. **Optional chaining abuse**
   ```javascript
   service?.call?.() || fallback  // Makes failures silent
   ```

5. **Swallowed promises**
   ```javascript
   promise.catch(() => null)  // Hides failures
   ```

## 🎯 Success Criteria

Your code is production-ready when:
- [ ] App refuses to start if critical dependencies missing
- [ ] All failures are logged and monitored
- [ ] Users are informed of degraded functionality
- [ ] No mock/fake data in production code paths
- [ ] Health checks expose real service status
- [ ] Every external call has timeout and error handling
- [ ] Circuit breakers protect against cascade failures
- [ ] Metrics track both success and failure rates