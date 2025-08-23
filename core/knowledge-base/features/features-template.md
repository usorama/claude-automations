# Feature Development Templates

## 1. Feature Specification Template

```markdown
# Feature Specification: [Feature Name]

## Overview
Brief description of the feature and its purpose.

## Business Context
- **Problem Statement**: What problem does this feature solve?
- **Business Goals**: What business objectives does this support?
- **Success Metrics**: How will we measure success?
- **Target Users**: Who will use this feature?

## User Stories
As a [user type], I want [goal] so that [benefit].

### Acceptance Criteria
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]

## Technical Requirements
- **API Endpoints**: List of required endpoints
- **Database Changes**: Schema changes and migrations
- **Dependencies**: External services or libraries
- **Performance Requirements**: Response times, throughput
- **Security Requirements**: Authentication, authorization, data protection

## Design Requirements
- **User Interface**: Wireframes, mockups, design system components
- **User Experience**: User flows, interaction patterns
- **Accessibility**: WCAG compliance requirements
- **Responsive Design**: Mobile, tablet, desktop considerations

## Implementation Plan
### Phase 1: Backend (Days 1-2)
- [ ] API endpoint implementation
- [ ] Database schema changes
- [ ] Business logic implementation
- [ ] Unit testing

### Phase 2: Frontend (Days 3-4)
- [ ] UI component development
- [ ] User interaction implementation
- [ ] Integration with backend APIs
- [ ] Testing and validation

### Phase 3: Integration (Day 5)
- [ ] End-to-end testing
- [ ] User acceptance testing
- [ ] Performance optimization
- [ ] Bug fixes and refinements

### Phase 4: Launch (Day 6)
- [ ] Feature flag setup
- [ ] Deployment preparation
- [ ] Monitoring configuration
- [ ] Documentation updates

## Testing Strategy
- **Unit Tests**: Backend logic, frontend components
- **Integration Tests**: API endpoints, database interactions
- **E2E Tests**: Complete user workflows
- **Accessibility Tests**: Screen reader, keyboard navigation
- **Performance Tests**: Load testing, response times

## Rollout Plan
- **Feature Flags**: Gradual rollout strategy
- **User Segments**: Target user groups for initial rollout
- **Monitoring**: Key metrics to track during rollout
- **Rollback Plan**: Steps to disable feature if issues arise

## Documentation
- [ ] API documentation updates
- [ ] User documentation and help articles
- [ ] Developer documentation
- [ ] Training materials for support team

## Risk Assessment
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Risk 1 | High | Low | Mitigation strategy |
| Risk 2 | Medium | Medium | Mitigation strategy |

## Open Questions
- [ ] Question 1: Details and resolution
- [ ] Question 2: Details and resolution
```

## 2. React Component Template

```typescript
// components/FeatureComponent.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

import { Button, Input, Select, Alert, Loading } from '@/components/ui';
import { useToast } from '@/hooks/useToast';
import { trackEvent } from '@/utils/analytics';
import { featureApi } from '@/api/feature';

// Type definitions
interface FeatureData {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive';
  createdAt: string;
  updatedAt: string;
}

interface FeatureFormData {
  name: string;
  description: string;
  status: 'active' | 'inactive';
}

// Validation schema
const validationSchema = yup.object({
  name: yup
    .string()
    .required('Name is required')
    .min(3, 'Name must be at least 3 characters')
    .max(50, 'Name must be less than 50 characters'),
  description: yup
    .string()
    .required('Description is required')
    .max(200, 'Description must be less than 200 characters'),
  status: yup
    .string()
    .oneOf(['active', 'inactive'], 'Invalid status')
    .required('Status is required'),
});

// Props interface
interface FeatureComponentProps {
  featureId?: string;
  onSuccess?: (data: FeatureData) => void;
  onError?: (error: Error) => void;
  className?: string;
}

export const FeatureComponent: React.FC<FeatureComponentProps> = ({
  featureId,
  onSuccess,
  onError,
  className = '',
}) => {
  const [isEditing, setIsEditing] = useState(!featureId);
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  // Form setup
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FeatureFormData>({
    resolver: yupResolver(validationSchema),
    defaultValues: {
      name: '',
      description: '',
      status: 'active',
    },
  });

  // Fetch existing feature data
  const {
    data: featureData,
    isLoading,
    error: fetchError,
  } = useQuery(
    ['feature', featureId],
    () => featureApi.getById(featureId!),
    {
      enabled: !!featureId,
      onSuccess: (data) => {
        reset({
          name: data.name,
          description: data.description,
          status: data.status,
        });
      },
      onError: (error) => {
        showToast('Failed to load feature data', 'error');
        onError?.(error as Error);
      },
    }
  );

  // Create mutation
  const createMutation = useMutation(featureApi.create, {
    onSuccess: (data) => {
      showToast('Feature created successfully', 'success');
      queryClient.invalidateQueries(['features']);
      trackEvent('feature_created', { featureId: data.id });
      onSuccess?.(data);
    },
    onError: (error) => {
      showToast('Failed to create feature', 'error');
      onError?.(error as Error);
    },
  });

  // Update mutation
  const updateMutation = useMutation(
    (data: FeatureFormData) => featureApi.update(featureId!, data),
    {
      onSuccess: (data) => {
        showToast('Feature updated successfully', 'success');
        queryClient.invalidateQueries(['feature', featureId]);
        queryClient.invalidateQueries(['features']);
        trackEvent('feature_updated', { featureId: data.id });
        setIsEditing(false);
        onSuccess?.(data);
      },
      onError: (error) => {
        showToast('Failed to update feature', 'error');
        onError?.(error as Error);
      },
    }
  );

  // Form submission handler
  const onSubmit = useCallback(
    (data: FeatureFormData) => {
      if (featureId) {
        updateMutation.mutate(data);
      } else {
        createMutation.mutate(data);
      }
    },
    [featureId, updateMutation, createMutation]
  );

  // Handle edit toggle
  const handleEditToggle = useCallback(() => {
    setIsEditing(!isEditing);
    if (isEditing && featureData) {
      reset({
        name: featureData.name,
        description: featureData.description,
        status: featureData.status,
      });
    }
  }, [isEditing, featureData, reset]);

  // Loading state
  if (isLoading) {
    return (
      <div className={`feature-component ${className}`}>
        <Loading />
      </div>
    );
  }

  // Error state
  if (fetchError) {
    return (
      <div className={`feature-component ${className}`}>
        <Alert variant="error">
          Failed to load feature data. Please try again.
        </Alert>
      </div>
    );
  }

  return (
    <div className={`feature-component ${className}`}>
      <div className="feature-component__header">
        <h2>{featureId ? 'Edit Feature' : 'Create Feature'}</h2>
        {featureId && !isEditing && (
          <Button variant="secondary" onClick={handleEditToggle}>
            Edit
          </Button>
        )}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="feature-form">
        <div className="form-group">
          <Input
            label="Feature Name"
            {...register('name')}
            error={errors.name?.message}
            disabled={!isEditing}
            required
            aria-describedby="name-help"
          />
          <div id="name-help" className="form-help">
            Enter a descriptive name for the feature
          </div>
        </div>

        <div className="form-group">
          <Input
            label="Description"
            type="textarea"
            {...register('description')}
            error={errors.description?.message}
            disabled={!isEditing}
            required
            aria-describedby="description-help"
          />
          <div id="description-help" className="form-help">
            Provide a detailed description of the feature
          </div>
        </div>

        <div className="form-group">
          <Select
            label="Status"
            {...register('status')}
            error={errors.status?.message}
            disabled={!isEditing}
            required
            options={[
              { value: 'active', label: 'Active' },
              { value: 'inactive', label: 'Inactive' },
            ]}
          />
        </div>

        {isEditing && (
          <div className="form-actions">
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting}
              loading={isSubmitting}
            >
              {featureId ? 'Update Feature' : 'Create Feature'}
            </Button>
            {featureId && (
              <Button
                type="button"
                variant="secondary"
                onClick={handleEditToggle}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            )}
          </div>
        )}
      </form>
    </div>
  );
};

export default FeatureComponent;
```

## 3. API Implementation Template

```typescript
// api/feature.ts
import { apiClient } from '@/utils/apiClient';
import { ApiResponse, PaginatedResponse } from '@/types/api';

export interface Feature {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'inactive';
  metadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export interface CreateFeatureRequest {
  name: string;
  description: string;
  status: 'active' | 'inactive';
  metadata?: Record<string, any>;
}

export interface UpdateFeatureRequest {
  name?: string;
  description?: string;
  status?: 'active' | 'inactive';
  metadata?: Record<string, any>;
}

export interface FeatureQueryParams {
  page?: number;
  limit?: number;
  status?: 'active' | 'inactive';
  search?: string;
  sortBy?: 'name' | 'createdAt' | 'updatedAt';
  sortOrder?: 'asc' | 'desc';
}

export const featureApi = {
  // Get all features with pagination and filtering
  getAll: async (params: FeatureQueryParams = {}): Promise<PaginatedResponse<Feature>> => {
    const response = await apiClient.get<PaginatedResponse<Feature>>('/features', {
      params,
    });
    return response.data;
  },

  // Get feature by ID
  getById: async (id: string): Promise<Feature> => {
    const response = await apiClient.get<ApiResponse<Feature>>(`/features/${id}`);
    return response.data.data;
  },

  // Create new feature
  create: async (data: CreateFeatureRequest): Promise<Feature> => {
    const response = await apiClient.post<ApiResponse<Feature>>('/features', data);
    return response.data.data;
  },

  // Update existing feature
  update: async (id: string, data: UpdateFeatureRequest): Promise<Feature> => {
    const response = await apiClient.patch<ApiResponse<Feature>>(`/features/${id}`, data);
    return response.data.data;
  },

  // Delete feature
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/features/${id}`);
  },

  // Bulk operations
  bulkUpdate: async (ids: string[], data: UpdateFeatureRequest): Promise<Feature[]> => {
    const response = await apiClient.patch<ApiResponse<Feature[]>>('/features/bulk', {
      ids,
      data,
    });
    return response.data.data;
  },

  bulkDelete: async (ids: string[]): Promise<void> => {
    await apiClient.delete('/features/bulk', {
      data: { ids },
    });
  },

  // Feature analytics
  getAnalytics: async (id: string, dateRange?: { start: string; end: string }) => {
    const response = await apiClient.get(`/features/${id}/analytics`, {
      params: dateRange,
    });
    return response.data;
  },
};
```

## 4. Backend API Controller Template

```typescript
// controllers/featureController.ts
import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';
import { FeatureService } from '@/services/featureService';
import { ApiError } from '@/utils/apiError';
import { asyncHandler } from '@/utils/asyncHandler';
import { logger } from '@/utils/logger';

export class FeatureController {
  constructor(private featureService: FeatureService) {}

  // Get all features
  getFeatures = asyncHandler(async (req: Request, res: Response) => {
    const {
      page = 1,
      limit = 10,
      status,
      search,
      sortBy = 'createdAt',
      sortOrder = 'desc',
    } = req.query;

    const result = await this.featureService.getFeatures({
      page: Number(page),
      limit: Number(limit),
      status: status as string,
      search: search as string,
      sortBy: sortBy as string,
      sortOrder: sortOrder as 'asc' | 'desc',
      userId: req.user.id,
    });

    res.json({
      success: true,
      data: result.features,
      pagination: {
        page: result.page,
        limit: result.limit,
        total: result.total,
        pages: Math.ceil(result.total / result.limit),
      },
    });
  });

  // Get feature by ID
  getFeature = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    const feature = await this.featureService.getFeatureById(id, req.user.id);
    
    if (!feature) {
      throw new ApiError(404, 'Feature not found');
    }

    res.json({
      success: true,
      data: feature,
    });
  });

  // Create new feature
  createFeature = asyncHandler(async (req: Request, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new ApiError(400, 'Validation failed', errors.array());
    }

    const featureData = {
      ...req.body,
      createdBy: req.user.id,
    };

    const feature = await this.featureService.createFeature(featureData);

    logger.info('Feature created', {
      featureId: feature.id,
      userId: req.user.id,
      featureName: feature.name,
    });

    res.status(201).json({
      success: true,
      data: feature,
    });
  });

  // Update feature
  updateFeature = asyncHandler(async (req: Request, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new ApiError(400, 'Validation failed', errors.array());
    }

    const { id } = req.params;
    
    const feature = await this.featureService.updateFeature(id, req.body, req.user.id);

    logger.info('Feature updated', {
      featureId: feature.id,
      userId: req.user.id,
      changes: req.body,
    });

    res.json({
      success: true,
      data: feature,
    });
  });

  // Delete feature
  deleteFeature = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    await this.featureService.deleteFeature(id, req.user.id);

    logger.info('Feature deleted', {
      featureId: id,
      userId: req.user.id,
    });

    res.status(204).send();
  });

  // Feature analytics
  getFeatureAnalytics = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const { start, end } = req.query;

    const analytics = await this.featureService.getFeatureAnalytics(id, {
      start: start as string,
      end: end as string,
      userId: req.user.id,
    });

    res.json({
      success: true,
      data: analytics,
    });
  });
}
```

## 5. Feature Flag Configuration

```typescript
// utils/featureFlags.ts
import { FeatureFlagService } from '@/services/featureFlagService';

export interface FeatureFlag {
  key: string;
  enabled: boolean;
  rolloutPercentage: number;
  userSegments?: string[];
  metadata?: Record<string, any>;
}

export class FeatureFlagManager {
  constructor(private featureFlagService: FeatureFlagService) {}

  // Check if feature is enabled for user
  async isFeatureEnabled(
    featureKey: string,
    userId: string,
    userAttributes: Record<string, any> = {}
  ): Promise<boolean> {
    try {
      const flag = await this.featureFlagService.getFlag(featureKey);
      
      if (!flag || !flag.enabled) {
        return false;
      }

      // Check user segments
      if (flag.userSegments && flag.userSegments.length > 0) {
        const userSegment = await this.getUserSegment(userId, userAttributes);
        if (!flag.userSegments.includes(userSegment)) {
          return false;
        }
      }

      // Check rollout percentage
      if (flag.rolloutPercentage < 100) {
        const userHash = this.hashUserId(userId, featureKey);
        return userHash < flag.rolloutPercentage;
      }

      return true;
    } catch (error) {
      console.error(`Error checking feature flag ${featureKey}:`, error);
      return false; // Fail closed
    }
  }

  // React hook for feature flags
  useFeatureFlag(featureKey: string): {
    isEnabled: boolean;
    isLoading: boolean;
    error: Error | null;
  } {
    const [isEnabled, setIsEnabled] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);
    const { user } = useAuth();

    useEffect(() => {
      if (!user) return;

      this.isFeatureEnabled(featureKey, user.id, user.attributes)
        .then(setIsEnabled)
        .catch(setError)
        .finally(() => setIsLoading(false));
    }, [featureKey, user]);

    return { isEnabled, isLoading, error };
  }

  private hashUserId(userId: string, featureKey: string): number {
    // Simple hash function for consistent rollout
    let hash = 0;
    const input = `${userId}:${featureKey}`;
    
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    return Math.abs(hash) % 100;
  }

  private async getUserSegment(
    userId: string,
    attributes: Record<string, any>
  ): Promise<string> {
    // Implement user segmentation logic
    if (attributes.isPremium) return 'premium';
    if (attributes.isEmployee) return 'employee';
    if (attributes.isBetaTester) return 'beta';
    return 'standard';
  }
}
```