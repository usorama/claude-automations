# Performance Optimization Templates

## 1. Performance Testing with k6

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100
    { duration: '5m', target: 100 },  // Stay at 100
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],   // Error rate under 1%
    error_rate: ['rate<0.01'],
  },
};

export default function () {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:3000';
  
  // Test scenarios
  const scenarios = [
    () => testHomePage(baseUrl),
    () => testAPIEndpoint(baseUrl),
    () => testUserLogin(baseUrl),
    () => testDatabaseQuery(baseUrl),
  ];
  
  // Randomly select a scenario
  const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
  scenario();
  
  sleep(1);
}

function testHomePage(baseUrl) {
  const response = http.get(`${baseUrl}/`);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'content contains title': (r) => r.body.includes('<title>'),
  });
  
  errorRate.add(response.status !== 200);
  responseTime.add(response.timings.duration);
}

function testAPIEndpoint(baseUrl) {
  const params = {
    headers: {
      'Authorization': 'Bearer ' + __ENV.API_TOKEN,
      'Content-Type': 'application/json',
    },
  };
  
  const response = http.get(`${baseUrl}/api/users`, params);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
    'response is JSON': (r) => r.headers['Content-Type'].includes('json'),
  });
  
  errorRate.add(response.status !== 200);
  responseTime.add(response.timings.duration);
}

function testUserLogin(baseUrl) {
  const payload = JSON.stringify({
    email: `user${Math.random()}@example.com`,
    password: 'testpassword123'
  });
  
  const params = {
    headers: { 'Content-Type': 'application/json' },
  };
  
  const response = http.post(`${baseUrl}/auth/login`, payload, params);
  
  check(response, {
    'login status is 200 or 401': (r) => [200, 401].includes(r.status),
    'response time < 300ms': (r) => r.timings.duration < 300,
  });
  
  errorRate.add(![200, 401].includes(response.status));
  responseTime.add(response.timings.duration);
}

function testDatabaseQuery(baseUrl) {
  const response = http.get(`${baseUrl}/api/reports/dashboard`);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 1000ms': (r) => r.timings.duration < 1000,
    'data is present': (r) => JSON.parse(r.body).data.length > 0,
  });
  
  errorRate.add(response.status !== 200);
  responseTime.add(response.timings.duration);
}

// Teardown function
export function teardown(data) {
  console.log('Test completed. Check metrics for performance analysis.');
}
```

## 2. Database Query Optimization

```sql
-- Query optimization examples

-- 1. Index creation for common query patterns
CREATE INDEX CONCURRENTLY idx_users_email_active 
ON users (email) WHERE active = true;

CREATE INDEX CONCURRENTLY idx_orders_user_created 
ON orders (user_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_products_category_price 
ON products (category_id, price) WHERE deleted_at IS NULL;

-- 2. Optimized query examples
-- Before: Slow query
SELECT u.*, p.name as profile_name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN profiles p ON u.id = p.user_id
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2023-01-01'
GROUP BY u.id, p.name;

-- After: Optimized with proper indexing and structure
WITH user_orders AS (
  SELECT user_id, COUNT(*) as order_count
  FROM orders
  WHERE created_at > '2023-01-01'
  GROUP BY user_id
)
SELECT u.*, p.name as profile_name, COALESCE(uo.order_count, 0) as order_count
FROM users u
LEFT JOIN profiles p ON u.id = p.user_id
LEFT JOIN user_orders uo ON u.id = uo.user_id
WHERE u.created_at > '2023-01-01'
  AND u.active = true;

-- 3. Partitioning for large tables
CREATE TABLE logs (
    id SERIAL,
    user_id INTEGER,
    action VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (created_at);

CREATE TABLE logs_2024_01 PARTITION OF logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE logs_2024_02 PARTITION OF logs
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 4. Query performance analysis
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT u.email, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = true
GROUP BY u.id, u.email
HAVING COUNT(o.id) > 5;
```

## 3. Caching Implementation

```javascript
// cache.js - Redis caching layer
const redis = require('redis');
const client = redis.createClient({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
  db: process.env.REDIS_DB || 0,
});

class CacheManager {
  constructor() {
    this.defaultTTL = 3600; // 1 hour
    this.client = client;
  }

  // Generic cache wrapper
  async wrap(key, asyncFunction, ttl = this.defaultTTL) {
    try {
      // Try to get from cache first
      const cached = await this.client.get(key);
      if (cached) {
        return JSON.parse(cached);
      }

      // Execute function and cache result
      const result = await asyncFunction();
      await this.client.setex(key, ttl, JSON.stringify(result));
      return result;
    } catch (error) {
      console.error('Cache error:', error);
      // Fallback to direct function execution
      return await asyncFunction();
    }
  }

  // User data caching
  async getUserData(userId) {
    return this.wrap(`user:${userId}`, async () => {
      const user = await User.findById(userId);
      return user;
    }, 1800); // 30 minutes
  }

  // API response caching
  async getAPIResponse(endpoint, params) {
    const cacheKey = `api:${endpoint}:${JSON.stringify(params)}`;
    return this.wrap(cacheKey, async () => {
      const response = await fetch(endpoint, { params });
      return response.json();
    }, 300); // 5 minutes
  }

  // Database query result caching
  async getCachedQuery(query, params, ttl = 600) {
    const cacheKey = `query:${Buffer.from(query).toString('base64')}:${JSON.stringify(params)}`;
    return this.wrap(cacheKey, async () => {
      const result = await db.query(query, params);
      return result.rows;
    }, ttl);
  }

  // Invalidate cache patterns
  async invalidatePattern(pattern) {
    const keys = await this.client.keys(pattern);
    if (keys.length > 0) {
      await this.client.del(...keys);
    }
  }

  // Cache warming for frequently accessed data
  async warmCache() {
    const popularUsers = await db.query('SELECT id FROM users ORDER BY last_active DESC LIMIT 100');
    
    for (const user of popularUsers.rows) {
      this.getUserData(user.id).catch(console.error);
    }
  }
}

// Application-level caching middleware
const cacheMiddleware = (ttl = 300) => {
  return async (req, res, next) => {
    // Skip cache for authenticated requests or POST/PUT/DELETE
    if (req.user || !['GET', 'HEAD'].includes(req.method)) {
      return next();
    }

    const cacheKey = `http:${req.originalUrl}`;
    
    try {
      const cached = await client.get(cacheKey);
      if (cached) {
        const data = JSON.parse(cached);
        res.set(data.headers);
        return res.status(data.status).send(data.body);
      }
    } catch (error) {
      console.error('Cache middleware error:', error);
    }

    // Override res.send to cache the response
    const originalSend = res.send;
    res.send = function(body) {
      // Cache successful responses
      if (res.statusCode === 200) {
        const cacheData = {
          status: res.statusCode,
          headers: res.getHeaders(),
          body: body
        };
        client.setex(cacheKey, ttl, JSON.stringify(cacheData));
      }
      
      return originalSend.call(this, body);
    };

    next();
  };
};

module.exports = { CacheManager, cacheMiddleware };
```

## 4. Frontend Performance Optimization

```javascript
// webpack.config.js - Optimized build configuration
const path = require('path');
const webpack = require('webpack');
const CompressionPlugin = require('compression-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  mode: 'production',
  entry: {
    main: './src/index.js',
    vendor: ['react', 'react-dom', 'lodash']
  },
  
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].[contenthash].js',
    chunkFilename: '[name].[contenthash].chunk.js',
    clean: true
  },

  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true
        }
      }
    },
    usedExports: true,
    sideEffects: false
  },

  plugins: [
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production')
    }),
    new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8
    }),
    process.env.ANALYZE && new BundleAnalyzerPlugin()
  ].filter(Boolean),

  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              ['@babel/preset-env', {
                targets: '> 0.25%, not dead',
                useBuiltIns: 'usage',
                corejs: 3
              }],
              '@babel/preset-react'
            ],
            plugins: [
              '@babel/plugin-transform-runtime',
              'react-hot-loader/babel'
            ]
          }
        }
      },
      {
        test: /\.(png|jpg|jpeg|gif|svg)$/,
        use: [
          {
            loader: 'url-loader',
            options: {
              limit: 8192,
              name: 'images/[name].[hash].[ext]'
            }
          },
          {
            loader: 'image-webpack-loader',
            options: {
              mozjpeg: { progressive: true, quality: 65 },
              optipng: { enabled: false },
              pngquant: { quality: [0.65, 0.90], speed: 4 },
              gifsicle: { interlaced: false },
              webp: { quality: 75 }
            }
          }
        ]
      }
    ]
  }
};
```

```javascript
// performance-utils.js - Frontend optimization utilities
import { lazy, Suspense } from 'react';

// Code splitting utility
export const createLazyComponent = (importFunc, fallback = <div>Loading...</div>) => {
  const LazyComponent = lazy(importFunc);
  
  return (props) => (
    <Suspense fallback={fallback}>
      <LazyComponent {...props} />
    </Suspense>
  );
};

// Image lazy loading component
export const LazyImage = ({ src, alt, className, ...props }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const imgRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={imgRef} className={className}>
      {isInView && (
        <img
          src={src}
          alt={alt}
          onLoad={() => setIsLoaded(true)}
          style={{
            opacity: isLoaded ? 1 : 0,
            transition: 'opacity 0.3s ease'
          }}
          {...props}
        />
      )}
    </div>
  );
};

// Performance monitoring hook
export const usePerformanceMonitor = (componentName) => {
  useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      // Track component render time
      if (window.gtag) {
        window.gtag('event', 'component_render_time', {
          event_category: 'Performance',
          event_label: componentName,
          value: Math.round(renderTime)
        });
      }
    };
  }, [componentName]);
};

// Resource prefetching
export const prefetchRoute = (routePath) => {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = routePath;
  document.head.appendChild(link);
};

// Virtual scrolling for large lists
export const VirtualizedList = ({ items, itemHeight, containerHeight, renderItem }) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  );
  
  const visibleItems = items.slice(startIndex, endIndex);
  
  return (
    <div
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.target.scrollTop)}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        {visibleItems.map((item, index) => (
          <div
            key={startIndex + index}
            style={{
              position: 'absolute',
              top: (startIndex + index) * itemHeight,
              height: itemHeight,
              width: '100%'
            }}
          >
            {renderItem(item, startIndex + index)}
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 5. Performance Monitoring Dashboard

```json
{
  "dashboard": {
    "title": "Application Performance Dashboard",
    "panels": [
      {
        "title": "Response Time Percentiles",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "99th percentile"
          }
        ],
        "thresholds": [
          {
            "value": 0.2,
            "color": "green"
          },
          {
            "value": 0.5,
            "color": "yellow"
          },
          {
            "value": 1.0,
            "color": "red"
          }
        ]
      },
      {
        "title": "Throughput",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{ method }} {{ status }}"
          }
        ]
      },
      {
        "title": "Database Query Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_statements_mean_time_ms",
            "legendFormat": "Mean query time"
          },
          {
            "expr": "pg_stat_statements_max_time_ms",
            "legendFormat": "Max query time"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total) * 100"
          }
        ],
        "format": "percent",
        "thresholds": "80,90"
      }
    ]
  }
}
```