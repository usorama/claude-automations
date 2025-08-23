# API Development Templates

## 1. Express.js REST API Template

```javascript
const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const cors = require('cors');
const compression = require('compression');
const { body, validationResult } = require('express-validator');
const jwt = require('jsonwebtoken');

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests from this IP, please try again later.'
  }
});
app.use('/api/', limiter);

// General middleware
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Authentication middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
};

// Validation middleware
const validateRequest = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: 'Validation failed',
      details: errors.array()
    });
  }
  next();
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.API_VERSION || '1.0.0'
  });
});

// User routes
app.post('/api/users', [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8 }),
  body('name').trim().isLength({ min: 1 })
], validateRequest, async (req, res) => {
  try {
    const { email, password, name } = req.body;
    
    // Check if user exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(409).json({ error: 'User already exists' });
    }

    // Create user
    const hashedPassword = await bcrypt.hash(password, 12);
    const user = new User({
      email,
      password: hashedPassword,
      name
    });

    await user.save();

    // Generate token
    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.status(201).json({
      message: 'User created successfully',
      user: {
        id: user._id,
        email: user.email,
        name: user.name
      },
      token
    });
  } catch (error) {
    console.error('User creation error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/users', authenticateToken, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    const users = await User.find({}, '-password')
      .skip(skip)
      .limit(limit)
      .sort({ createdAt: -1 });

    const total = await User.countDocuments();

    res.json({
      users,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Users fetch error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? error.message : undefined
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
```

## 2. FastAPI Python Template

```python
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List
import jwt
from datetime import datetime, timedelta
import bcrypt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="API Template",
    description="Template for REST API development",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    created_at: datetime

class PaginatedResponse(BaseModel):
    items: List[UserResponse]
    page: int
    limit: int
    total: int
    pages: int

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

# User endpoints
@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    try:
        # Check if user exists (implement database logic)
        existing_user = await get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )
        
        # Hash password
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user (implement database logic)
        new_user = await create_user_in_db({
            "email": user.email,
            "password": hashed_password.decode('utf-8'),
            "name": user.name
        })
        
        # Generate token
        token_data = {
            "user_id": str(new_user.id),
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return UserResponse(
            id=str(new_user.id),
            email=new_user.email,
            name=new_user.name,
            created_at=new_user.created_at
        )
        
    except Exception as e:
        logger.error(f"User creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/api/users", response_model=PaginatedResponse)
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: str = Depends(get_current_user)
):
    try:
        skip = (page - 1) * limit
        users, total = await get_users_from_db(skip=skip, limit=limit)
        
        return PaginatedResponse(
            items=[UserResponse(
                id=str(user.id),
                email=user.email,
                name=user.name,
                created_at=user.created_at
            ) for user in users],
            page=page,
            limit=limit,
            total=total,
            pages=math.ceil(total / limit)
        )
    except Exception as e:
        logger.error(f"Users fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "detail": str(exc)}
    )

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Resource not found"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 3. OpenAPI Specification Template

```yaml
openapi: 3.0.3
info:
  title: API Template
  description: Template for REST API development
  version: 1.0.0
  contact:
    name: API Support
    email: support@example.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server
  - url: http://localhost:3000
    description: Development server

paths:
  /health:
    get:
      summary: Health check
      description: Check if the API is healthy
      operationId: healthCheck
      tags:
        - Health
      responses:
        '200':
          description: API is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: healthy
                  timestamp:
                    type: string
                    format: date-time
                  version:
                    type: string
                    example: 1.0.0

  /api/users:
    post:
      summary: Create a new user
      description: Register a new user account
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
            examples:
              user_example:
                summary: Example user creation
                value:
                  email: john@example.com
                  password: securepassword123
                  name: John Doe
      responses:
        '201':
          description: User created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserResponse'
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: User already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

    get:
      summary: Get users
      description: Retrieve a list of users with pagination
      operationId: getUsers
      tags:
        - Users
      security:
        - bearerAuth: []
      parameters:
        - name: page
          in: query
          description: Page number
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          description: Number of items per page
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 10
      responses:
        '200':
          description: Users retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedUsers'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    UserCreate:
      type: object
      required:
        - email
        - password
        - name
      properties:
        email:
          type: string
          format: email
          description: User's email address
        password:
          type: string
          minLength: 8
          description: User's password
        name:
          type: string
          minLength: 1
          description: User's full name

    UserResponse:
      type: object
      properties:
        id:
          type: string
          description: User's unique identifier
        email:
          type: string
          format: email
          description: User's email address
        name:
          type: string
          description: User's full name
        created_at:
          type: string
          format: date-time
          description: User creation timestamp

    PaginatedUsers:
      type: object
      properties:
        users:
          type: array
          items:
            $ref: '#/components/schemas/UserResponse'
        pagination:
          type: object
          properties:
            page:
              type: integer
              description: Current page number
            limit:
              type: integer
              description: Items per page
            total:
              type: integer
              description: Total number of items
            pages:
              type: integer
              description: Total number of pages

    Error:
      type: object
      properties:
        error:
          type: string
          description: Error message
        details:
          type: array
          items:
            type: object
          description: Detailed error information

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  responses:
    UnauthorizedError:
      description: Access token is missing or invalid
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    NotFoundError:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    ValidationError:
      description: Input validation failed
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

tags:
  - name: Health
    description: Health check endpoints
  - name: Users
    description: User management operations
```

## 4. GraphQL Schema Template

```graphql
# GraphQL Schema Template

scalar DateTime
scalar Upload

type Query {
  # Health check
  health: Health!
  
  # User queries
  user(id: ID!): User
  users(first: Int, after: String, filter: UserFilter): UserConnection!
  me: User
}

type Mutation {
  # User mutations
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(id: ID!): DeleteUserPayload!
  
  # Authentication
  login(input: LoginInput!): AuthPayload!
  refreshToken(refreshToken: String!): AuthPayload!
}

type Subscription {
  # Real-time updates
  userUpdated(userId: ID): User!
  userDeleted: ID!
}

# Types
type Health {
  status: String!
  timestamp: DateTime!
  version: String!
}

type User {
  id: ID!
  email: String!
  name: String!
  avatar: String
  isActive: Boolean!
  createdAt: DateTime!
  updatedAt: DateTime!
  
  # Relationships
  posts: [Post!]!
  followers: [User!]!
  following: [User!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  published: Boolean!
  author: User!
  createdAt: DateTime!
  updatedAt: DateTime!
}

# Connection types for pagination
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# Input types
input CreateUserInput {
  email: String!
  password: String!
  name: String!
  avatar: Upload
}

input UpdateUserInput {
  email: String
  name: String
  avatar: Upload
}

input LoginInput {
  email: String!
  password: String!
}

input UserFilter {
  email: String
  name: String
  isActive: Boolean
  search: String
}

# Payload types
type CreateUserPayload {
  user: User
  token: String
  errors: [Error!]
}

type UpdateUserPayload {
  user: User
  errors: [Error!]
}

type DeleteUserPayload {
  success: Boolean!
  errors: [Error!]
}

type AuthPayload {
  token: String
  refreshToken: String
  user: User
  errors: [Error!]
}

type Error {
  field: String
  message: String!
}

# Directives
directive @auth(requires: Role = USER) on FIELD_DEFINITION

enum Role {
  ADMIN
  MODERATOR
  USER
}
```

## 5. Docker Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - PORT=3000
      - DATABASE_URL=postgresql://user:password@postgres:5432/apidb
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your-jwt-secret
    depends_on:
      - postgres
      - redis
    volumes:
      - .:/app
      - /app/node_modules
    command: npm run dev

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=apidb
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Start application
CMD ["npm", "start"]
```