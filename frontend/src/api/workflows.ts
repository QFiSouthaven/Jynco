import apiClient from './client'

export interface Workflow {
  id: string
  user_id: string
  name: string
  description?: string
  category: string
  workflow_json: Record<string, any>
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface WorkflowCreate {
  name: string
  description?: string
  category: string
  workflow_json: Record<string, any>
}

export interface WorkflowUpdate {
  name?: string
  description?: string
  category?: string
  workflow_json?: Record<string, any>
}

export const workflowsApi = {
  // List all workflows
  listWorkflows: async (params?: {
    category?: string
    include_defaults?: boolean
  }): Promise<Workflow[]> => {
    const queryParams = new URLSearchParams()
    if (params?.category) queryParams.append('category', params.category)
    if (params?.include_defaults !== undefined) {
      queryParams.append('include_defaults', params.include_defaults.toString())
    }

    const url = `/api/workflows/${queryParams.toString() ? '?' + queryParams.toString() : ''}`
    const response = await apiClient.get(url)
    return response.data
  },

  // Get workflow by ID
  getWorkflow: async (workflowId: string): Promise<Workflow> => {
    const response = await apiClient.get(`/api/workflows/${workflowId}`)
    return response.data
  },

  // Get workflow by name
  getWorkflowByName: async (name: string): Promise<Workflow> => {
    const response = await apiClient.get(`/api/workflows/by-name/${encodeURIComponent(name)}`)
    return response.data
  },

  // Create a new workflow
  createWorkflow: async (data: WorkflowCreate): Promise<Workflow> => {
    const response = await apiClient.post('/api/workflows/', data)
    return response.data
  },

  // Update a workflow
  updateWorkflow: async (workflowId: string, data: WorkflowUpdate): Promise<Workflow> => {
    const response = await apiClient.put(`/api/workflows/${workflowId}`, data)
    return response.data
  },

  // Delete a workflow
  deleteWorkflow: async (workflowId: string): Promise<void> => {
    await apiClient.delete(`/api/workflows/${workflowId}`)
  },

  // List all categories
  listCategories: async (): Promise<string[]> => {
    const response = await apiClient.get('/api/workflows/categories/list')
    return response.data
  },
}
