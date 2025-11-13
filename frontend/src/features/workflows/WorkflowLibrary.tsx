import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { workflowsApi, Workflow } from '../../api/workflows'
import { FaBook, FaTrash, FaDownload, FaCopy, FaFilter } from 'react-icons/fa'

export default function WorkflowLibrary() {
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(undefined)
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null)

  // Fetch workflows
  const { data: workflows = [], isLoading } = useQuery({
    queryKey: ['workflows', selectedCategory],
    queryFn: () => workflowsApi.listWorkflows({
      category: selectedCategory,
      include_defaults: true
    }),
  })

  // Fetch categories
  const { data: categories = [] } = useQuery({
    queryKey: ['workflow-categories'],
    queryFn: workflowsApi.listCategories,
  })

  // Delete workflow mutation
  const deleteWorkflowMutation = useMutation({
    mutationFn: workflowsApi.deleteWorkflow,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
      setSelectedWorkflow(null)
      alert('Workflow deleted successfully!')
    },
    onError: (error: any) => {
      console.error('Failed to delete workflow:', error)
      alert(error.response?.data?.detail || 'Failed to delete workflow. You can only delete your own workflows.')
    },
  })

  const handleDelete = (workflow: Workflow) => {
    if (workflow.is_default) {
      alert('Cannot delete default workflows')
      return
    }

    if (confirm(`Delete workflow "${workflow.name}"?`)) {
      deleteWorkflowMutation.mutate(workflow.id)
    }
  }

  const handleCopyJson = (workflow: Workflow) => {
    const json = JSON.stringify(workflow.workflow_json, null, 2)
    navigator.clipboard.writeText(json)
    alert('Workflow JSON copied to clipboard!')
  }

  const handleDownloadJson = (workflow: Workflow) => {
    const json = JSON.stringify(workflow.workflow_json, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${workflow.name.replace(/\s+/g, '-').toLowerCase()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (isLoading) {
    return <div className="text-center py-12">Loading workflows...</div>
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 flex items-center space-x-2">
          <FaBook />
          <span>Workflow Library</span>
        </h1>
        <p className="text-gray-400">Browse and manage your ComfyUI workflow templates</p>
      </div>

      {/* Category Filter */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <div className="flex items-center space-x-3">
          <FaFilter className="text-gray-400" />
          <label className="text-sm font-medium text-gray-300">Filter by Category:</label>
          <select
            value={selectedCategory || ''}
            onChange={(e) => setSelectedCategory(e.target.value || undefined)}
            className="bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
          <span className="text-sm text-gray-400">
            ({workflows.length} workflow{workflows.length !== 1 ? 's' : ''})
          </span>
        </div>
      </div>

      {/* Workflows Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workflows.map((workflow) => (
          <div
            key={workflow.id}
            className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition cursor-pointer border border-gray-700"
            onClick={() => setSelectedWorkflow(workflow)}
          >
            <div className="flex justify-between items-start mb-3">
              <h3 className="text-lg font-semibold">{workflow.name}</h3>
              {workflow.is_default && (
                <span className="text-xs bg-blue-600 px-2 py-1 rounded">Default</span>
              )}
            </div>

            <p className="text-sm text-gray-400 mb-3 line-clamp-2">
              {workflow.description || 'No description provided'}
            </p>

            <div className="flex justify-between items-center text-xs text-gray-500">
              <span className="bg-gray-700 px-2 py-1 rounded">{workflow.category}</span>
              <span>{new Date(workflow.created_at).toLocaleDateString()}</span>
            </div>

            <div className="flex space-x-2 mt-4">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleCopyJson(workflow)
                }}
                className="flex-1 flex items-center justify-center space-x-1 bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded text-sm transition"
              >
                <FaCopy />
                <span>Copy</span>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleDownloadJson(workflow)
                }}
                className="flex-1 flex items-center justify-center space-x-1 bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded text-sm transition"
              >
                <FaDownload />
                <span>Download</span>
              </button>
              {!workflow.is_default && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDelete(workflow)
                  }}
                  className="flex items-center justify-center bg-red-600 hover:bg-red-700 px-3 py-2 rounded text-sm transition"
                >
                  <FaTrash />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {workflows.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <FaBook className="mx-auto text-6xl mb-4 opacity-20" />
          <p className="text-lg">No workflows found</p>
          <p className="text-sm mt-2">
            {selectedCategory
              ? 'Try selecting a different category or create a new workflow'
              : 'Create your first workflow from the Timeline Editor'}
          </p>
        </div>
      )}

      {/* Workflow Detail Modal */}
      {selectedWorkflow && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedWorkflow(null)}
        >
          <div
            className="bg-gray-800 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold mb-2">{selectedWorkflow.name}</h2>
                <div className="flex items-center space-x-3 text-sm text-gray-400">
                  <span className="bg-gray-700 px-2 py-1 rounded">{selectedWorkflow.category}</span>
                  {selectedWorkflow.is_default && (
                    <span className="bg-blue-600 px-2 py-1 rounded">Default Workflow</span>
                  )}
                  <span>Created: {new Date(selectedWorkflow.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedWorkflow(null)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                &times;
              </button>
            </div>

            {selectedWorkflow.description && (
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-300 mb-2">Description</h3>
                <p className="text-gray-400">{selectedWorkflow.description}</p>
              </div>
            )}

            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-300 mb-2">Workflow JSON</h3>
              <pre className="bg-gray-900 border border-gray-700 rounded p-4 overflow-x-auto text-sm">
                <code>{JSON.stringify(selectedWorkflow.workflow_json, null, 2)}</code>
              </pre>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => handleCopyJson(selectedWorkflow)}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition"
              >
                <FaCopy />
                <span>Copy JSON</span>
              </button>
              <button
                onClick={() => handleDownloadJson(selectedWorkflow)}
                className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 px-4 py-2 rounded transition"
              >
                <FaDownload />
                <span>Download JSON</span>
              </button>
              {!selectedWorkflow.is_default && (
                <button
                  onClick={() => handleDelete(selectedWorkflow)}
                  className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 px-4 py-2 rounded transition ml-auto"
                >
                  <FaTrash />
                  <span>Delete</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
