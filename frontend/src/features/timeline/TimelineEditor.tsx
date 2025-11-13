import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, ModelParams } from '../../api/projects'
import { workflowsApi, Workflow } from '../../api/workflows'
import { useProjectStore } from '../../store/useProjectStore'
import { FaPlus, FaPlay, FaSave, FaBook } from 'react-icons/fa'
import SegmentCard from './SegmentCard'
import ComfyUIStatus from '../../components/ComfyUIStatus'

type ModelType = 'comfyui' | 'runway-gen3' | 'stability-ai' | 'mock-ai'

const MODEL_OPTIONS: { value: ModelType; label: string; description: string }[] = [
  { value: 'comfyui', label: 'ComfyUI', description: 'Advanced workflow-based generation' },
  { value: 'mock-ai', label: 'Mock AI', description: 'Testing and development' },
  { value: 'runway-gen3', label: 'Runway Gen-3', description: 'High-quality video generation' },
  { value: 'stability-ai', label: 'Stability AI', description: 'Stable diffusion video' },
]

export default function TimelineEditor() {
  const { projectId } = useParams<{ projectId: string }>()
  const queryClient = useQueryClient()
  const { currentProject, setCurrentProject, addSegment, removeSegment } = useProjectStore()
  const [showAddSegment, setShowAddSegment] = useState(false)
  const [segmentPrompt, setSegmentPrompt] = useState('')

  // Model configuration state
  const [selectedModel, setSelectedModel] = useState<ModelType>('comfyui')
  const [duration, setDuration] = useState(5)
  const [width, setWidth] = useState(1024)
  const [height, setHeight] = useState(576)
  const [workflowJson, setWorkflowJson] = useState('')

  // Workflow library state
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null)
  const [showSaveWorkflow, setShowSaveWorkflow] = useState(false)
  const [workflowName, setWorkflowName] = useState('')
  const [workflowDescription, setWorkflowDescription] = useState('')
  const [workflowCategory, setWorkflowCategory] = useState('text-to-video')

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.getProject(projectId!),
    enabled: !!projectId,
  })

  // Fetch workflows for the selector
  const { data: workflows = [] } = useQuery({
    queryKey: ['workflows'],
    queryFn: () => workflowsApi.listWorkflows({ include_defaults: true }),
  })

  useEffect(() => {
    if (project) {
      setCurrentProject(project)
    }
  }, [project, setCurrentProject])

  const createSegmentMutation = useMutation({
    mutationFn: (data: { prompt: string; order_index: number; model_params: ModelParams }) =>
      projectsApi.createSegment(projectId!, data),
    onSuccess: (newSegment) => {
      addSegment(newSegment)
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      setShowAddSegment(false)
      setSegmentPrompt('')
      // Reset form
      setSelectedModel('comfyui')
      setDuration(5)
      setWidth(1024)
      setHeight(576)
      setWorkflowJson('')
    },
  })

  const deleteSegmentMutation = useMutation({
    mutationFn: projectsApi.deleteSegment,
    onSuccess: (_, segmentId) => {
      removeSegment(segmentId)
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const retrySegmentMutation = useMutation({
    mutationFn: projectsApi.retrySegment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
    onError: (error) => {
      console.error('Failed to retry segment:', error)
      alert('Failed to retry segment. Please try again.')
    },
  })

  const startRenderMutation = useMutation({
    mutationFn: () => projectsApi.startRender(projectId!),
    onSuccess: () => {
      alert('Render started! Check the dashboard for progress.')
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const saveWorkflowMutation = useMutation({
    mutationFn: workflowsApi.createWorkflow,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
      setShowSaveWorkflow(false)
      setWorkflowName('')
      setWorkflowDescription('')
      alert('Workflow saved successfully!')
    },
    onError: (error) => {
      console.error('Failed to save workflow:', error)
      alert('Failed to save workflow. Please try again.')
    },
  })

  const handleWorkflowSelect = (workflowId: string) => {
    const workflow = workflows.find((w) => w.id === workflowId)
    if (workflow) {
      setSelectedWorkflow(workflow)
      setWorkflowJson(JSON.stringify(workflow.workflow_json, null, 2))
    }
  }

  const handleSaveWorkflow = () => {
    if (!workflowName.trim() || !workflowJson.trim()) {
      alert('Please provide a workflow name and JSON')
      return
    }

    try {
      const workflowData = JSON.parse(workflowJson)
      saveWorkflowMutation.mutate({
        name: workflowName,
        description: workflowDescription,
        category: workflowCategory,
        workflow_json: workflowData,
      })
    } catch (e) {
      alert('Invalid JSON format. Please check your workflow.')
    }
  }

  const handleAddSegment = () => {
    if (segmentPrompt.trim()) {
      const orderIndex = currentProject?.segments.length || 0

      // Build model params
      const modelParams: ModelParams = {
        model: selectedModel,
        duration,
        width,
        height,
        aspect_ratio: `${width}:${height}`,
      }

      // Add workflow for ComfyUI if provided
      if (selectedModel === 'comfyui' && workflowJson.trim()) {
        try {
          modelParams.workflow = JSON.parse(workflowJson)
        } catch (e) {
          alert('Invalid JSON format for workflow. Please check your input.')
          return
        }
      }

      createSegmentMutation.mutate({
        prompt: segmentPrompt,
        order_index: orderIndex,
        model_params: modelParams,
      })
    }
  }

  if (isLoading) {
    return <div className="text-center py-12">Loading project...</div>
  }

  if (!currentProject) {
    return <div className="text-center py-12">Project not found</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">{currentProject.name}</h1>
          {currentProject.description && (
            <p className="text-gray-400">{currentProject.description}</p>
          )}
        </div>
        <button
          onClick={() => startRenderMutation.mutate()}
          disabled={currentProject.segments.length === 0 || startRenderMutation.isPending}
          className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg transition disabled:opacity-50"
        >
          <FaPlay />
          <span>{startRenderMutation.isPending ? 'Starting...' : 'Render Video'}</span>
        </button>
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Timeline</h2>
          <button
            onClick={() => setShowAddSegment(true)}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition"
          >
            <FaPlus />
            <span>Add Segment</span>
          </button>
        </div>

        {currentProject.segments.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <p>No segments yet. Add your first segment to get started!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {currentProject.segments
              .sort((a, b) => a.order_index - b.order_index)
              .map((segment) => (
                <SegmentCard
                  key={segment.id}
                  segment={segment}
                  onDelete={() => {
                    if (confirm('Delete this segment?')) {
                      deleteSegmentMutation.mutate(segment.id)
                    }
                  }}
                  onRetry={(segmentId) => retrySegmentMutation.mutate(segmentId)}
                />
              ))}
          </div>
        )}
      </div>

      {showAddSegment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Add New Segment</h2>
            <div className="space-y-4">
              {/* Model Selection */}
              <div>
                <label className="block text-sm font-medium mb-2">AI Model</label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value as ModelType)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                >
                  {MODEL_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label} - {option.description}
                    </option>
                  ))}
                </select>
              </div>

              {/* ComfyUI Status Indicator */}
              {selectedModel === 'comfyui' && (
                <div className="bg-gray-700 border border-gray-600 rounded p-3">
                  <ComfyUIStatus variant="inline" />
                </div>
              )}

              {/* Video Prompt */}
              <div>
                <label className="block text-sm font-medium mb-2">Video Prompt</label>
                <textarea
                  value={segmentPrompt}
                  onChange={(e) => setSegmentPrompt(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                  rows={4}
                  placeholder="Describe the video clip you want to generate..."
                />
              </div>

              {/* Common Parameters */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Width</label>
                  <input
                    type="number"
                    value={width}
                    onChange={(e) => setWidth(Number(e.target.value))}
                    className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                    min="256"
                    step="64"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Height</label>
                  <input
                    type="number"
                    value={height}
                    onChange={(e) => setHeight(Number(e.target.value))}
                    className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                    min="256"
                    step="64"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Duration (s)</label>
                  <input
                    type="number"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value))}
                    className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                    min="1"
                    max="30"
                  />
                </div>
              </div>

              {/* ComfyUI Workflow (optional) */}
              {selectedModel === 'comfyui' && (
                <div className="space-y-3">
                  {/* Workflow Selector */}
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Load from Workflow Library
                    </label>
                    <div className="flex space-x-2">
                      <select
                        value={selectedWorkflow?.id || ''}
                        onChange={(e) => handleWorkflowSelect(e.target.value)}
                        className="flex-1 bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                      >
                        <option value="">-- Select a workflow --</option>
                        {workflows.map((workflow) => (
                          <option key={workflow.id} value={workflow.id}>
                            {workflow.name} {workflow.is_default ? '(Default)' : ''} - {workflow.category}
                          </option>
                        ))}
                      </select>
                    </div>
                    {selectedWorkflow?.description && (
                      <p className="text-xs text-gray-400 mt-1 italic">
                        {selectedWorkflow.description}
                      </p>
                    )}
                  </div>

                  {/* Workflow JSON */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="block text-sm font-medium">
                        ComfyUI Workflow (JSON, optional)
                      </label>
                      <button
                        onClick={() => setShowSaveWorkflow(true)}
                        disabled={!workflowJson.trim()}
                        className="flex items-center space-x-1 text-xs bg-purple-600 hover:bg-purple-700 px-3 py-1 rounded disabled:opacity-50 transition"
                      >
                        <FaSave />
                        <span>Save as Workflow</span>
                      </button>
                    </div>
                    <textarea
                      value={workflowJson}
                      onChange={(e) => setWorkflowJson(e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white font-mono text-sm"
                      rows={6}
                      placeholder='{"nodes": [...], "connections": [...]}'
                    />
                    <p className="text-xs text-gray-400 mt-1">
                      Paste your ComfyUI workflow JSON here. Leave empty to use default workflow.
                    </p>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-2">
                <button
                  onClick={handleAddSegment}
                  disabled={!segmentPrompt.trim() || createSegmentMutation.isPending}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded disabled:opacity-50 transition"
                >
                  {createSegmentMutation.isPending ? 'Adding...' : 'Add Segment'}
                </button>
                <button
                  onClick={() => {
                    setShowAddSegment(false)
                    setSegmentPrompt('')
                    setWorkflowJson('')
                  }}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Save Workflow Modal */}
      {showSaveWorkflow && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4">Save Workflow</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Workflow Name</label>
                <input
                  type="text"
                  value={workflowName}
                  onChange={(e) => setWorkflowName(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                  placeholder="My Custom Workflow"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Description (optional)</label>
                <textarea
                  value={workflowDescription}
                  onChange={(e) => setWorkflowDescription(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                  rows={3}
                  placeholder="Describe what this workflow does..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Category</label>
                <select
                  value={workflowCategory}
                  onChange={(e) => setWorkflowCategory(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                >
                  <option value="text-to-video">Text to Video</option>
                  <option value="image-to-video">Image to Video</option>
                  <option value="video-to-video">Video to Video</option>
                  <option value="custom">Custom</option>
                </select>
              </div>

              <div className="flex space-x-3 pt-2">
                <button
                  onClick={handleSaveWorkflow}
                  disabled={!workflowName.trim() || saveWorkflowMutation.isPending}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded disabled:opacity-50 transition"
                >
                  {saveWorkflowMutation.isPending ? 'Saving...' : 'Save Workflow'}
                </button>
                <button
                  onClick={() => {
                    setShowSaveWorkflow(false)
                    setWorkflowName('')
                    setWorkflowDescription('')
                  }}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
