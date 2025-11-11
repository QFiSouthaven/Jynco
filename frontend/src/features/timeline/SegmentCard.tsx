import { Segment } from '../../api/projects'
import { FaTrash, FaSpinner, FaCheckCircle, FaExclamationCircle } from 'react-icons/fa'
import clsx from 'clsx'

interface SegmentCardProps {
  segment: Segment
  onDelete: () => void
}

export default function SegmentCard({ segment, onDelete }: SegmentCardProps) {
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
          <div className="text-sm text-gray-500">
            Model: {segment.model_params.model || 'default'} | Duration: {segment.model_params.duration || 5}s
          </div>
          {segment.error_message && (
            <div className="mt-2 text-sm text-red-400">
              Error: {segment.error_message}
            </div>
          )}
          {segment.s3_asset_url && (
            <div className="mt-2">
              <a
                href={segment.s3_asset_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-400 hover:text-blue-300"
              >
                View Video
              </a>
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
    </div>
  )
}
