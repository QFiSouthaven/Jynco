import { useQuery } from '@tanstack/react-query'
import { projectsApi } from '../../api/projects'
import { FaSpinner, FaCheckCircle, FaExclamationCircle, FaPlay, FaDownload } from 'react-icons/fa'
import { useState } from 'react'
import clsx from 'clsx'
import VideoModal from '../../components/VideoModal'
import ComfyUIStatus from '../../components/ComfyUIStatus'

export default function Dashboard() {
  const [selectedVideo, setSelectedVideo] = useState<{
    url: string
    title: string
    description: string
  } | null>(null)

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.listProjects,
    refetchInterval: 5000, // Poll every 5 seconds
  })

  // Get all render jobs from all projects
  const allRenderJobs = projects
    ?.flatMap((project) =>
      project.segments.map((segment) => ({
        projectName: project.name,
        projectId: project.id,
        segment,
      }))
    )
    .filter((item) => item.segment.status !== 'pending')

  const activeJobs = allRenderJobs?.filter(
    (item) => item.segment.status === 'generating'
  )

  const completedJobs = allRenderJobs?.filter(
    (item) => item.segment.status === 'completed'
  )

  const failedJobs = allRenderJobs?.filter(
    (item) => item.segment.status === 'failed'
  )

  if (isLoading) {
    return <div className="text-center py-12">Loading dashboard...</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Render Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-blue-900 bg-opacity-30 border border-blue-500 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-300 text-sm font-medium">Active Renders</p>
              <p className="text-3xl font-bold mt-2">{activeJobs?.length || 0}</p>
            </div>
            <FaSpinner className="text-4xl text-blue-500 animate-spin" />
          </div>
        </div>

        <div className="bg-green-900 bg-opacity-30 border border-green-500 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-300 text-sm font-medium">Completed</p>
              <p className="text-3xl font-bold mt-2">{completedJobs?.length || 0}</p>
            </div>
            <FaCheckCircle className="text-4xl text-green-500" />
          </div>
        </div>

        <div className="bg-red-900 bg-opacity-30 border border-red-500 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-300 text-sm font-medium">Failed</p>
              <p className="text-3xl font-bold mt-2">{failedJobs?.length || 0}</p>
            </div>
            <FaExclamationCircle className="text-4xl text-red-500" />
          </div>
        </div>

        <ComfyUIStatus variant="full" />
      </div>

      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>

        {!allRenderJobs || allRenderJobs.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <p>No render activity yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {allRenderJobs
              .sort((a, b) => new Date(b.segment.updated_at).getTime() - new Date(a.segment.updated_at).getTime())
              .slice(0, 20)
              .map((item) => (
                <div
                  key={item.segment.id}
                  className="bg-gray-750 rounded p-4 flex items-center justify-between"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-1">
                      {item.segment.status === 'generating' && (
                        <FaSpinner className="text-blue-500 animate-spin" />
                      )}
                      {item.segment.status === 'completed' && (
                        <FaCheckCircle className="text-green-500" />
                      )}
                      {item.segment.status === 'failed' && (
                        <FaExclamationCircle className="text-red-500" />
                      )}
                      <span className="font-medium">{item.projectName}</span>
                      <span className={clsx(
                        'text-xs px-2 py-1 rounded',
                        item.segment.status === 'completed' && 'bg-green-900 text-green-300',
                        item.segment.status === 'generating' && 'bg-blue-900 text-blue-300',
                        item.segment.status === 'failed' && 'bg-red-900 text-red-300'
                      )}>
                        {item.segment.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 truncate">
                      {item.segment.prompt}
                    </p>
                    {item.segment.s3_asset_url && (
                      <div className="flex items-center space-x-2 mt-2">
                        <button
                          onClick={() => setSelectedVideo({
                            url: item.segment.s3_asset_url!,
                            title: `${item.projectName} - Segment #${item.segment.order_index + 1}`,
                            description: item.segment.prompt,
                          })}
                          className="flex items-center space-x-1 text-xs text-blue-400 hover:text-blue-300 transition"
                        >
                          <FaPlay />
                          <span>Preview</span>
                        </button>
                        <a
                          href={item.segment.s3_asset_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-400 transition"
                        >
                          <FaDownload />
                          <span>Download</span>
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>

      {/* Video Modal */}
      {selectedVideo && (
        <VideoModal
          isOpen={!!selectedVideo}
          onClose={() => setSelectedVideo(null)}
          videoUrl={selectedVideo.url}
          title={selectedVideo.title}
          description={selectedVideo.description}
        />
      )}
    </div>
  )
}
