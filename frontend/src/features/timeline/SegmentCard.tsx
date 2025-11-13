import { Segment } from '../../api/projects'
import { FaTrash, FaSpinner, FaCheckCircle, FaExclamationCircle, FaChevronDown, FaChevronUp, FaExpand, FaDownload, FaRedo } from 'react-icons/fa'
import clsx from 'clsx'
import { useState } from 'react'
import VideoPlayer from '../../components/VideoPlayer'
import VideoModal from '../../components/VideoModal'
import { getErrorInfo, isRetryableError } from '../../utils/errorMessages'

interface SegmentCardProps {
  segment: Segment
  onDelete: () => void
  onRetry?: (segmentId: string) => void
}

const MODEL_LABELS: Record<string, string> = {
  'comfyui': 'ComfyUI',
  'mock-ai': 'Mock AI',
  'runway-gen3': 'Runway Gen-3',
  'stability-ai': 'Stability AI',
}

export default function SegmentCard({ segment, onDelete, onRetry }: SegmentCardProps) {
  const [showPreview, setShowPreview] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [isRetrying, setIsRetrying] = useState(false)

  const handleRetry = async () => {
    if (!onRetry) return
    setIsRetrying(true)
    try {
      await onRetry(segment.id)
    } finally {
      setIsRetrying(false)
    }
  }

  const getStatusIcon = () => {
    switch (segment.status) {
      case 'completed':
        return <FaCheckCircle className="text-green-500" />
      case 'generating':
        return <FaSpinner className="text-blue-500 animate-spin" />
      case 'failed':
        return <FaExclamationCircle className="text-red-500" />
      default:
        return <div className="w-4 h-4 bg-gray-600 rounded-full" />
    }
  }

  const getStatusColor = () => {
    switch (segment.status) {
      case 'completed':
        return 'border-green-500'
      case 'generating':
        return 'border-blue-500'
      case 'failed':
        return 'border-red-500'
      default:
        return 'border-gray-600'
    }
  }

  return (
    <div className={clsx('bg-gray-750 rounded-lg p-4 border-l-4 transition', getStatusColor())}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            {getStatusIcon()}
            <span className="font-medium text-sm text-gray-400">
              Segment #{segment.order_index + 1}
            </span>
            <span className={clsx(
              'text-xs px-2 py-1 rounded',
              segment.status === 'completed' && 'bg-green-900 text-green-300',
              segment.status === 'generating' && 'bg-blue-900 text-blue-300',
              segment.status === 'failed' && 'bg-red-900 text-red-300',
              segment.status === 'pending' && 'bg-gray-700 text-gray-300'
            )}>
              {segment.status}
            </span>
          </div>
          <p className="text-white mb-2">{segment.prompt}</p>
          <div className="flex items-center gap-3 text-sm text-gray-400">
            <span className="px-2 py-1 bg-purple-900 text-purple-300 rounded text-xs font-medium">
              {MODEL_LABELS[segment.model_params.model] || segment.model_params.model || 'Unknown'}
            </span>
            <span>
              {segment.model_params.width || 1024}x{segment.model_params.height || 576}
            </span>
            <span>{segment.model_params.duration || 5}s</span>
          </div>
          {segment.error_message && segment.status === 'failed' && (
            <div className="mt-3 p-3 bg-red-900 bg-opacity-20 border border-red-800 rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <FaExclamationCircle className="text-red-500 flex-shrink-0" />
                    <span className="text-red-400 font-medium text-sm">
                      {getErrorInfo(segment.error_code).userMessage}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">
                    {getErrorInfo(segment.error_code).troubleshooting}
                  </p>
                  {segment.error_code && (
                    <p className="text-xs text-gray-500 font-mono">
                      Error code: {segment.error_code}
                    </p>
                  )}
                </div>
                {onRetry && isRetryableError(segment.error_code) && (
                  <button
                    onClick={handleRetry}
                    disabled={isRetrying}
                    className="ml-3 flex items-center space-x-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-sm rounded transition"
                    title="Retry generation"
                  >
                    <FaRedo className={clsx(isRetrying && 'animate-spin')} />
                    <span>{isRetrying ? 'Retrying...' : 'Retry'}</span>
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Video Preview Section */}
          {segment.s3_asset_url && segment.status === 'completed' && (
            <div className="mt-3 space-y-2">
              {/* Video Actions */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowPreview(!showPreview)}
                  className="flex items-center space-x-2 text-sm text-blue-400 hover:text-blue-300 transition"
                >
                  {showPreview ? <FaChevronUp /> : <FaChevronDown />}
                  <span>{showPreview ? 'Hide' : 'Show'} Preview</span>
                </button>
                <button
                  onClick={() => setShowModal(true)}
                  className="flex items-center space-x-1 text-sm text-gray-400 hover:text-white transition"
                  title="View fullscreen"
                >
                  <FaExpand />
                  <span>Fullscreen</span>
                </button>
                <a
                  href={segment.s3_asset_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 text-sm text-gray-400 hover:text-white transition"
                  title="Download video"
                >
                  <FaDownload />
                  <span>Download</span>
                </a>
              </div>

              {/* Collapsible Video Preview */}
              {showPreview && (
                <div className="mt-3 rounded-lg overflow-hidden border border-gray-600">
                  <VideoPlayer
                    videoUrl={segment.s3_asset_url}
                    controls
                    className="max-h-64"
                  />
                </div>
              )}
            </div>
          )}
        </div>
        <button
          onClick={onDelete}
          className="ml-4 text-red-500 hover:text-red-400"
          title="Delete segment"
        >
          <FaTrash />
        </button>
      </div>

      {/* Video Modal */}
      {segment.s3_asset_url && (
        <VideoModal
          isOpen={showModal}
          onClose={() => setShowModal(false)}
          videoUrl={segment.s3_asset_url}
          title={`Segment #${segment.order_index + 1}`}
          description={segment.prompt}
        />
      )}
    </div>
  )
}
