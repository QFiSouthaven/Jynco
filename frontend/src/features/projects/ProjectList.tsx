import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { projectsApi } from '../../api/projects'
import { FaPlus, FaVideo, FaTrash } from 'react-icons/fa'

export default function ProjectList() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [projectName, setProjectName] = useState('')
  const [projectDescription, setProjectDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.listProjects,
  })

  const createMutation = useMutation({
    mutationFn: projectsApi.createProject,
    onSuccess: (newProject) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setShowCreateModal(false)
      setProjectName('')
      setProjectDescription('')
      setError(null)
      navigate(`/projects/${newProject.id}`)
    },
    onError: (error: any) => {
      console.error('Failed to create project:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error occurred'
      setError(errorMessage)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: projectsApi.deleteProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })

  const handleCreate = () => {
    console.log('handleCreate called with:', { name: projectName, description: projectDescription })
    setError(null)
    if (projectName.trim()) {
      createMutation.mutate({ name: projectName, description: projectDescription })
    } else {
      console.warn('Project name is empty, not creating')
      setError('Please enter a project name')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleCreate()
    }
  }

  if (isLoading) {
    return <div className="text-center py-12">Loading projects...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">My Projects</h1>
        <button
          onClick={() => {
            setShowCreateModal(true)
            setError(null)
            setProjectName('')
            setProjectDescription('')
          }}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg transition"
        >
          <FaPlus />
          <span>New Project</span>
        </button>
      </div>

      {projects && projects.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <FaVideo className="text-6xl mx-auto mb-4 opacity-50" />
          <p className="text-xl">No projects yet. Create your first video project!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects?.map((project) => (
            <div
              key={project.id}
              className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition cursor-pointer"
              onClick={() => navigate(`/projects/${project.id}`)}
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold">{project.name}</h3>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    if (confirm('Delete this project?')) {
                      deleteMutation.mutate(project.id)
                    }
                  }}
                  className="text-red-500 hover:text-red-400"
                >
                  <FaTrash />
                </button>
              </div>
              {project.description && (
                <p className="text-gray-400 text-sm mb-4">{project.description}</p>
              )}
              <div className="text-sm text-gray-500">
                {project.segments.length} segments
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4">Create New Project</h2>
            <div className="space-y-4">
              {error && (
                <div className="bg-red-900 bg-opacity-30 border border-red-500 text-red-300 px-4 py-3 rounded">
                  {error}
                </div>
              )}
              <div>
                <label className="block text-sm font-medium mb-2">Project Name</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
                  placeholder="My Awesome Video"
                  autoFocus
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Description (optional)</label>
                <textarea
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
                  rows={3}
                  placeholder="Describe your project..."
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={handleCreate}
                  disabled={!projectName.trim() || createMutation.isPending}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createMutation.isPending ? 'Creating...' : 'Create'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
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
