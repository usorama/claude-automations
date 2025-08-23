# Documentation Templates

## 1. API Documentation Template (OpenAPI)

```yaml
# api-documentation.yaml
openapi: 3.0.3
info:
  title: Your API Documentation
  description: |
    Comprehensive API documentation with examples and interactive features.
    
    ## Authentication
    This API uses JWT tokens for authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    
    ## Rate Limiting
    API requests are limited to 1000 requests per hour per API key.
    
    ## Error Handling
    The API uses standard HTTP status codes and returns detailed error messages in JSON format.
    
  version: 1.0.0
  contact:
    name: API Support
    email: api-support@yourcompany.com
    url: https://yourcompany.com/support
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.yourcompany.com/v1
    description: Production server
  - url: https://staging-api.yourcompany.com/v1
    description: Staging server

paths:
  /users:
    get:
      summary: List users
      description: |
        Retrieve a paginated list of users with optional filtering and sorting.
        
        ### Usage Example
        ```bash
        curl -H "Authorization: Bearer $TOKEN" \
             "https://api.yourcompany.com/v1/users?page=1&limit=10"
        ```
        
        ### Response Format
        The response includes user data and pagination metadata.
        
      operationId: listUsers
      tags:
        - Users
      parameters:
        - name: page
          in: query
          description: Page number for pagination
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
            example: 1
        - name: limit
          in: query
          description: Number of items per page
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
            example: 20
        - name: sort
          in: query
          description: Sort field and direction
          required: false
          schema:
            type: string
            enum: [name_asc, name_desc, created_asc, created_desc]
            default: created_desc
            example: name_asc
      responses:
        '200':
          description: Users retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
              examples:
                success_response:
                  summary: Successful user list
                  value:
                    users:
                      - id: "123"
                        name: "John Doe"
                        email: "john@example.com"
                        created_at: "2024-01-01T00:00:00Z"
                    pagination:
                      page: 1
                      limit: 20
                      total: 100
                      pages: 5
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '403':
          $ref: '#/components/responses/ForbiddenError'
        '429':
          $ref: '#/components/responses/RateLimitError'

components:
  schemas:
    User:
      type: object
      description: User account information
      required:
        - id
        - name
        - email
        - created_at
      properties:
        id:
          type: string
          description: Unique user identifier
          example: "123e4567-e89b-12d3-a456-426614174000"
        name:
          type: string
          description: User's full name
          minLength: 1
          maxLength: 100
          example: "John Doe"
        email:
          type: string
          format: email
          description: User's email address
          example: "john@example.com"
        avatar:
          type: string
          format: uri
          description: URL to user's avatar image
          example: "https://example.com/avatars/john.jpg"
        created_at:
          type: string
          format: date-time
          description: Account creation timestamp
          example: "2024-01-01T00:00:00Z"
        updated_at:
          type: string
          format: date-time
          description: Last account update timestamp
          example: "2024-01-15T12:30:00Z"

    Pagination:
      type: object
      description: Pagination metadata
      properties:
        page:
          type: integer
          description: Current page number
          minimum: 1
          example: 1
        limit:
          type: integer
          description: Items per page
          minimum: 1
          maximum: 100
          example: 20
        total:
          type: integer
          description: Total number of items
          minimum: 0
          example: 100
        pages:
          type: integer
          description: Total number of pages
          minimum: 0
          example: 5

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT token-based authentication. Get your token from the /auth/login endpoint.
        
        Example:
        ```
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        ```

  responses:
    UnauthorizedError:
      description: Authentication required
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
                example: "Authentication required"
              code:
                type: string
                example: "UNAUTHORIZED"

    ForbiddenError:
      description: Insufficient permissions
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
                example: "Insufficient permissions"
              code:
                type: string
                example: "FORBIDDEN"

    RateLimitError:
      description: Rate limit exceeded
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
                example: "Rate limit exceeded"
              code:
                type: string
                example: "RATE_LIMIT_EXCEEDED"
              retry_after:
                type: integer
                description: Seconds to wait before retrying
                example: 3600

security:
  - bearerAuth: []

tags:
  - name: Users
    description: User management operations
    externalDocs:
      description: User management guide
      url: https://docs.yourcompany.com/guides/user-management
```

## 2. README Template

```markdown
# Project Name

[![Build Status](https://github.com/username/project/workflows/CI/badge.svg)](https://github.com/username/project/actions)
[![Coverage Status](https://coveralls.io/repos/github/username/project/badge.svg)](https://coveralls.io/github/username/project)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Brief project description explaining what this project does and why it's useful.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [Testing](#testing)
- [Deployment](#deployment)
- [FAQ](#faq)
- [Support](#support)
- [License](#license)

## Features

- ✅ **Feature 1**: Description of feature and its benefits
- ✅ **Feature 2**: Description of feature and its benefits
- ✅ **Feature 3**: Description of feature and its benefits
- 🚧 **Feature 4**: Planned feature (coming soon)

## Quick Start

Get up and running in less than 5 minutes:

```bash
# Clone the repository
git clone https://github.com/username/project.git
cd project

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to see your application running.

## Installation

### Prerequisites

- Node.js 18+ ([Download](https://nodejs.org/))
- PostgreSQL 14+ ([Download](https://postgresql.org/))
- Redis 6+ ([Download](https://redis.io/))

### Development Setup

1. **Clone and install dependencies**
   ```bash
   git clone https://github.com/username/project.git
   cd project
   npm install
   ```

2. **Database setup**
   ```bash
   # Create database
   createdb project_development
   
   # Run migrations
   npm run db:migrate
   
   # Seed initial data
   npm run db:seed
   ```

3. **Environment configuration**
   ```bash
   cp .env.example .env
   ```
   
   Update the following variables in `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/project_development
   REDIS_URL=redis://localhost:6379
   JWT_SECRET=your-secret-key
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

### Production Setup

See our [Deployment Guide](docs/deployment.md) for detailed production setup instructions.

## Usage

### Basic Usage

```javascript
const { ProjectClient } = require('project-sdk');

const client = new ProjectClient({
  apiKey: 'your-api-key',
  baseURL: 'https://api.yourproject.com'
});

// Create a new user
const user = await client.users.create({
  name: 'John Doe',
  email: 'john@example.com'
});

console.log('User created:', user.id);
```

### Advanced Usage

```javascript
// Bulk operations
const users = await client.users.createMany([
  { name: 'User 1', email: 'user1@example.com' },
  { name: 'User 2', email: 'user2@example.com' }
]);

// Pagination
const userList = await client.users.list({
  page: 1,
  limit: 20,
  sort: 'created_at:desc'
});

// Error handling
try {
  const user = await client.users.get('invalid-id');
} catch (error) {
  if (error.code === 'USER_NOT_FOUND') {
    console.log('User does not exist');
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | required | Your API authentication key |
| `baseURL` | string | `https://api.yourproject.com` | API base URL |
| `timeout` | number | `5000` | Request timeout in milliseconds |
| `retries` | number | `3` | Number of retry attempts |

## API Documentation

Full API documentation is available at:
- **Interactive Docs**: [https://docs.yourproject.com](https://docs.yourproject.com)
- **OpenAPI Spec**: [api-spec.yaml](docs/api-spec.yaml)
- **Postman Collection**: [postman-collection.json](docs/postman-collection.json)

### Authentication

All API requests require authentication using a Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.yourproject.com/v1/users
```

### Rate Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Authentication | 5 requests | 15 minutes |
| Read operations | 1000 requests | 1 hour |
| Write operations | 100 requests | 1 hour |

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `npm test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Submit a pull request

### Code Style

We use ESLint and Prettier for code formatting:

```bash
# Check code style
npm run lint

# Fix code style issues
npm run lint:fix

# Format code
npm run format
```

## Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run integration tests
npm run test:integration
```

### Test Coverage

We maintain >90% test coverage. Current coverage:

- **Statements**: 95%
- **Branches**: 92%
- **Functions**: 96%
- **Lines**: 95%

## Deployment

### Environment Variables

Required environment variables for production:

```env
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET=...
API_KEY=...
```

### Docker Deployment

```bash
# Build image
docker build -t project:latest .

# Run container
docker run -p 3000:3000 --env-file .env project:latest
```

### Kubernetes Deployment

See [k8s/](k8s/) directory for Kubernetes manifests.

## FAQ

**Q: How do I reset my API key?**
A: Contact support or use the dashboard at [https://dashboard.yourproject.com](https://dashboard.yourproject.com)

**Q: What's the rate limit for API calls?**
A: See the [Rate Limits](#rate-limits) section above.

**Q: Can I use this in production?**
A: Yes! This project is production-ready. See our [Production Checklist](docs/production-checklist.md).

## Support

- **Documentation**: [https://docs.yourproject.com](https://docs.yourproject.com)
- **Issues**: [GitHub Issues](https://github.com/username/project/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/project/discussions)
- **Email**: support@yourproject.com
- **Discord**: [Join our community](https://discord.gg/yourproject)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Contributor 1](https://github.com/contributor1) - Initial work
- [Contributor 2](https://github.com/contributor2) - Feature development
- [Library Name](https://github.com/library) - Awesome functionality

---

<p align="center">
  Made with ❤️ by <a href="https://yourcompany.com">Your Company</a>
</p>
```

## 3. User Guide Template

```markdown
# User Guide: Getting Started

## Welcome to [Product Name]

This guide will help you get started with [Product Name] quickly and efficiently.

### What You'll Learn

- How to set up your account
- Basic navigation and core features
- Common workflows and best practices
- Troubleshooting tips

### Prerequisites

Before you begin, make sure you have:
- [ ] A valid email address
- [ ] Administrative access to your organization (if applicable)
- [ ] Basic understanding of [relevant concepts]

## Step 1: Account Setup

### Creating Your Account

1. **Visit the signup page**: Go to [https://app.yourproduct.com/signup](https://app.yourproduct.com/signup)

2. **Enter your information**:
   ![Signup Form Screenshot](images/signup-form.png)
   
   - Email address (this will be your username)
   - Password (minimum 8 characters)
   - Organization name (optional)

3. **Verify your email**: Check your inbox for a verification email and click the confirmation link.

4. **Complete your profile**: Add additional information to personalize your experience.

### First Login

After verification, log in to your account:

1. Go to [https://app.yourproduct.com/login](https://app.yourproduct.com/login)
2. Enter your email and password
3. Click "Sign In"

> 💡 **Tip**: Bookmark the login page for quick access.

## Step 2: Dashboard Overview

When you first log in, you'll see the main dashboard:

![Dashboard Screenshot](images/dashboard-overview.png)

### Key Areas

| Area | Description | Actions Available |
|------|-------------|-------------------|
| **Navigation Menu** | Access to all features | Browse sections, search |
| **Quick Actions** | Common tasks | Create, import, export |
| **Recent Activity** | Your latest actions | View details, continue work |
| **Analytics** | Usage statistics | View reports, export data |

### Customizing Your Dashboard

You can customize your dashboard to fit your workflow:

1. Click the **"Customize"** button in the top right
2. Drag and drop widgets to rearrange them
3. Click **"Add Widget"** to include additional information
4. Save your changes

## Step 3: Core Features

### Feature 1: Data Management

**Purpose**: Organize and manage your data efficiently.

**How to use**:

1. **Upload data**:
   ```
   Navigate to Data → Upload
   Select your file (CSV, JSON, or Excel)
   Map columns to fields
   Click "Import"
   ```

2. **View and edit data**:
   - Click on any record to view details
   - Use the edit button to modify information
   - Apply filters to find specific records

3. **Export data**:
   - Select records you want to export
   - Choose format (CSV, PDF, Excel)
   - Click "Export" and download the file

### Feature 2: Reporting

**Purpose**: Generate insights from your data.

**Creating a report**:

1. Go to **Reports → New Report**
2. Select your data source
3. Choose visualization type:
   - Bar chart
   - Line graph
   - Pie chart
   - Table view
4. Configure filters and parameters
5. Save and share your report

**Sharing reports**:
- **Public link**: Generate a shareable URL
- **Email**: Send directly to team members
- **Embed**: Add to external websites

### Feature 3: Collaboration

**Purpose**: Work together with your team.

**Inviting team members**:

1. Go to **Settings → Team**
2. Click **"Invite Member"**
3. Enter their email address
4. Select their role:
   - **Admin**: Full access to all features
   - **Editor**: Can create and modify content
   - **Viewer**: Read-only access
5. Send the invitation

**Working with permissions**:
- Set project-level permissions
- Control access to sensitive data
- Monitor team activity

## Step 4: Advanced Workflows

### Automation Setup

Save time by automating repetitive tasks:

1. **Create an automation**:
   - Go to **Automation → New Rule**
   - Define trigger conditions
   - Set actions to perform
   - Test and activate

2. **Common automation examples**:
   - Send email notifications for new data
   - Generate reports on schedule
   - Update records based on conditions

### API Integration

Connect [Product Name] with other tools:

1. **Get your API key**:
   - Go to **Settings → API**
   - Click **"Generate New Key"**
   - Copy and store securely

2. **Basic API usage**:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        https://api.yourproduct.com/v1/data
   ```

3. **Available endpoints**:
   - `/data` - Manage your data
   - `/reports` - Generate reports
   - `/users` - User management

## Troubleshooting

### Common Issues

**Problem**: Can't log in
**Solution**: 
1. Check your email and password
2. Try password reset if needed
3. Clear browser cache and cookies
4. Contact support if issue persists

**Problem**: Data import fails
**Solution**:
1. Check file format (must be CSV, JSON, or Excel)
2. Ensure file size is under 10MB
3. Verify column headers match expected format
4. Remove any special characters

**Problem**: Reports not loading
**Solution**:
1. Check your internet connection
2. Try refreshing the page
3. Clear browser cache
4. Verify you have permission to view the report

### Getting Help

If you need additional assistance:

- **Help Center**: [https://help.yourproduct.com](https://help.yourproduct.com)
- **Video Tutorials**: [https://help.yourproduct.com/videos](https://help.yourproduct.com/videos)
- **Live Chat**: Available 9 AM - 5 PM EST
- **Email Support**: support@yourproduct.com
- **Community Forum**: [https://community.yourproduct.com](https://community.yourproduct.com)

## What's Next?

Now that you've mastered the basics, explore these advanced features:

- [ ] **Advanced reporting** - Create complex visualizations
- [ ] **Workflow automation** - Set up sophisticated rules
- [ ] **API development** - Build custom integrations
- [ ] **Team management** - Organize larger teams
- [ ] **Enterprise features** - SSO, advanced security

### Recommended Learning Path

1. **Week 1**: Master basic data management
2. **Week 2**: Create your first automated workflow
3. **Week 3**: Set up team collaboration
4. **Week 4**: Explore API integrations

### Additional Resources

- **Best Practices Guide**: [Link to guide]
- **Use Case Examples**: [Link to examples]
- **Webinar Series**: [Link to webinars]
- **Template Library**: [Link to templates]

---

*Last updated: [Date] | Version: [Version Number]*
```

## 4. Docusaurus Configuration

```javascript
// docusaurus.config.js
const config = {
  title: 'Your Project Documentation',
  tagline: 'Comprehensive documentation for developers and users',
  url: 'https://docs.yourproject.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'yourorg',
  projectName: 'yourproject',

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/yourorg/yourproject/tree/main/docs/',
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/yourorg/yourproject/tree/main/docs/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Your Project',
      logo: {
        alt: 'Your Project Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'getting-started',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/api',
          label: 'API',
          position: 'left',
        },
        {
          to: '/blog',
          label: 'Blog',
          position: 'left'
        },
        {
          href: 'https://github.com/yourorg/yourproject',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/getting-started',
            },
            {
              label: 'API Reference',
              to: '/api',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Discord',
              href: 'https://discord.gg/yourproject',
            },
            {
              label: 'Twitter',
              href: 'https://twitter.com/yourproject',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Blog',
              to: '/blog',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/yourorg/yourproject',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Your Company. Built with Docusaurus.`,
    },
    prism: {
      theme: require('prism-react-renderer/themes/github'),
      darkTheme: require('prism-react-renderer/themes/dracula'),
    },
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'yourproject',
      contextualSearch: true,
    },
  },

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'api',
        path: 'api',
        routeBasePath: 'api',
        sidebarPath: require.resolve('./sidebars-api.js'),
      },
    ],
  ],
};

module.exports = config;
```

## 5. Documentation CI/CD Pipeline

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
    paths: ['docs/**', 'api-spec.yaml']
  pull_request:
    branches: [main]
    paths: ['docs/**', 'api-spec.yaml']

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
      
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        
    - name: Install dependencies
      run: |
        cd docs
        npm install
        
    - name: Generate API docs
      run: |
        # Generate API documentation from OpenAPI spec
        npx @apidevtools/swagger-parser validate api-spec.yaml
        npx redoc-cli build api-spec.yaml --output docs/static/api.html
        
    - name: Lint documentation
      run: |
        # Check for broken links
        npm run lint:docs
        
        # Validate markdown
        npx markdownlint docs/**/*.md
        
    - name: Build documentation
      run: |
        cd docs
        npm run build
        
    - name: Test documentation
      run: |
        # Test that all examples work
        npm run test:docs
        
    - name: Deploy to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/build
        
    - name: Upload coverage
      if: github.ref == 'refs/heads/main'
      run: |
        # Upload documentation coverage metrics
        npm run coverage:docs
```