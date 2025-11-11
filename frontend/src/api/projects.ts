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

export interface Segment {
  id: string
  project_id: string
  order_index: number
  prompt: string
  model_params: Record<string, any>
  status: 'pending' | 'generating' | 'completed' | 'failed'
  s3_asset_url?: string
  error_message?: string
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
  createSegment: async (projectId: string, data: { order_index: number; prompt: string; model_params: Record<string, any> }): Promise<Segment> => {
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
}
