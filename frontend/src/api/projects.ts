import apiClient from './client'

export interface Project {
  id: string
  user_id: string
  name: string
  description?: string
  created_at: string
  updated_at: string
  segments: Segment[]
}

export interface ModelParams {
  model: 'comfyui' | 'runway-gen3' | 'stability-ai' | 'mock-ai'
  duration?: number
  width?: number
  height?: number
  aspect_ratio?: string
  workflow?: Record<string, any>
  [key: string]: any
}

export interface Segment {
  id: string
  project_id: string
  order_index: number
  prompt: string
  model_params: ModelParams
  status: 'pending' | 'generating' | 'completed' | 'failed'
  s3_asset_url?: string
  error_message?: string
  error_code?: string
  created_at: string
  updated_at: string
}

export interface RenderJob {
  id: string
  project_id: string
  status: 'pending' | 'processing' | 'compositing' | 'completed' | 'failed'
  segments_total: number
  segments_completed: number
  segment_ids: string[]
  s3_final_url?: string
  error_message?: string
  created_at: string
  updated_at: string
}

export interface ComfyUIHealthStatus {
  status: 'online' | 'offline' | 'error'
  url?: string
  version?: string
  error?: string
}

export const projectsApi = {
  // Projects
  createProject: async (data: { name: string; description?: string }): Promise<Project> => {
    const response = await apiClient.post('/api/projects/', data)
    return response.data
  },

  listProjects: async (): Promise<Project[]> => {
    const response = await apiClient.get('/api/projects/')
    return response.data
  },

  getProject: async (projectId: string): Promise<Project> => {
    const response = await apiClient.get(`/api/projects/${projectId}`)
    return response.data
  },

  updateProject: async (projectId: string, data: { name?: string; description?: string }): Promise<Project> => {
    const response = await apiClient.put(`/api/projects/${projectId}`, data)
    return response.data
  },

  deleteProject: async (projectId: string): Promise<void> => {
    await apiClient.delete(`/api/projects/${projectId}`)
  },

  // Segments
  createSegment: async (projectId: string, data: { order_index: number; prompt: string; model_params: ModelParams }): Promise<Segment> => {
    const response = await apiClient.post(`/api/projects/${projectId}/segments`, data)
    return response.data
  },

  updateSegment: async (segmentId: string, data: Partial<Segment>): Promise<Segment> => {
    const response = await apiClient.put(`/api/segments/${segmentId}`, data)
    return response.data
  },

  deleteSegment: async (segmentId: string): Promise<void> => {
    await apiClient.delete(`/api/segments/${segmentId}`)
  },

  retrySegment: async (segmentId: string): Promise<Segment> => {
    const response = await apiClient.post(`/api/segments/${segmentId}/retry`)
    return response.data
  },

  // Render Jobs
  startRender: async (projectId: string): Promise<RenderJob> => {
    const response = await apiClient.post(`/api/projects/${projectId}/render`)
    return response.data
  },

  getRenderJob: async (renderJobId: string): Promise<RenderJob> => {
    const response = await apiClient.get(`/api/render-jobs/${renderJobId}`)
    return response.data
  },

  listRenderJobs: async (projectId: string): Promise<RenderJob[]> => {
    const response = await apiClient.get(`/api/projects/${projectId}/render-jobs`)
    return response.data
  },

  // Health Check
  checkComfyUIHealth: async (): Promise<ComfyUIHealthStatus> => {
    try {
      const response = await apiClient.get('/api/health/comfyui')
      return {
        status: 'online',
        url: response.data.url,
        version: response.data.version,
      }
    } catch (error: any) {
      return {
        status: error.response?.status === 503 ? 'offline' : 'error',
        error: error.response?.data?.detail || error.message || 'Failed to connect',
      }
    }
  },
}
