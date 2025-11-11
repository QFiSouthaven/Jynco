import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi } from '../../api/projects'
import { useProjectStore } from '../../store/useProjectStore'
import { FaPlus, FaPlay, FaTrash, FaEdit } from 'react-icons/fa'
import SegmentCard from './SegmentCard'

export default function TimelineEditor() {
  const { projectId } = useParams<{ projectId: string }>()
  const queryClient = useQueryClient()
  const { currentProject, setCurrentProject, addSegment, removeSegment } = useProjectStore()
  const [showAddSegment, setShowAddSegment] = useState(false)
  const [segmentPrompt, setSegmentPrompt] = useState('')

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.getProject(projectId!),
    enabled: !!projectId,
  })

  useEffect(() => {
    if (project) {
      setCurrentProject(project)
    }
  }, [project, setCurrentProject])

  const createSegmentMutation = useMutation({
    mutationFn: (data: { prompt: string; order_index: number }) =>
      projectsApi.createSegment(projectId!, {
        ...data,
        model_params: {
          model: 'mock-ai',
          duration: 5,
          aspect_ratio: '16:9',
        },
      }),
    onSuccess: (newSegment) => {
      addSegment(newSegment)
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      setShowAddSegment(false)
      setSegmentPrompt('')
    },
  })

  const deleteSegmentMutation = useMutation({
    mutationFn: projectsApi.deleteSegment,
    onSuccess: (_, segmentId) => {
      removeSegment(segmentId)
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const startRenderMutation = useMutation({
    mutationFn: () => projectsApi.startRender(projectId!),
    onSuccess: () => {
      alert('Render started! Check the dashboard for progress.')
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })

  const handleAddSegment = () => {
    if (segmentPrompt.trim()) {
      const orderIndex = currentProject?.segments.length || 0
      createSegmentMutation.mutate({
        prompt: segmentPrompt,
        order_index: orderIndex,
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
                />
              ))}
          </div>
        )}
      </div>

      {showAddSegment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full">
            <h2 className="text-2xl font-bold mb-4">Add New Segment</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Video Prompt</label>
                <textarea
                  value={segmentPrompt}
                  onChange={(e) => setSegmentPrompt(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
                  rows={4}
                  placeholder="Describe the video clip you want to generate..."
                />
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={handleAddSegment}
                  disabled={!segmentPrompt.trim() || createSegmentMutation.isPending}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded disabled:opacity-50"
                >
                  {createSegmentMutation.isPending ? 'Adding...' : 'Add Segment'}
                </button>
                <button
                  onClick={() => setShowAddSegment(false)}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded"
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
