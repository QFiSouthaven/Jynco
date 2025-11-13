import { useState, useEffect } from 'react'
import { projectsApi, ComfyUIHealthStatus } from '../api/projects'
import { FaCircle, FaSync, FaChevronDown, FaChevronUp } from 'react-icons/fa'
import clsx from 'clsx'

interface ComfyUIStatusProps {
  variant?: 'compact' | 'full' | 'inline'
  showRefresh?: boolean
  autoExpand?: boolean
}

export default function ComfyUIStatus({
  variant = 'compact',
  showRefresh = true,
  autoExpand = false
}: ComfyUIStatusProps) {
  const [status, setStatus] = useState<ComfyUIHealthStatus>({ status: 'offline' })
  const [isChecking, setIsChecking] = useState(false)
  const [isExpanded, setIsExpanded] = useState(autoExpand)
  const [lastChecked, setLastChecked] = useState<Date | null>(null)

  const checkHealth = async () => {
    setIsChecking(true)
    try {
      const result = await projectsApi.checkComfyUIHealth()
      setStatus(result)
      setLastChecked(new Date())
    } catch (error) {
      setStatus({ status: 'error', error: 'Failed to check status' })
    } finally {
      setIsChecking(false)
    }
  }

  useEffect(() => {
    // Initial check
    checkHealth()

    // Poll every 10 seconds
    const interval = setInterval(checkHealth, 10000)

    // Cleanup
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = () => {
    if (isChecking) return 'text-yellow-500'
    switch (status.status) {
      case 'online':
        return 'text-green-500'
      case 'offline':
        return 'text-red-500'
      case 'error':
        return 'text-orange-500'
      default:
        return 'text-gray-500'
    }
  }

  const getStatusText = () => {
    if (isChecking) return 'Checking...'
    switch (status.status) {
      case 'online':
        return 'Online'
      case 'offline':
        return 'Offline'
      case 'error':
        return 'Error'
      default:
        return 'Unknown'
    }
  }

  const getStatusBgColor = () => {
    if (isChecking) return 'bg-yellow-900 bg-opacity-30 border-yellow-500'
    switch (status.status) {
      case 'online':
        return 'bg-green-900 bg-opacity-30 border-green-500'
      case 'offline':
        return 'bg-red-900 bg-opacity-30 border-red-500'
      case 'error':
        return 'bg-orange-900 bg-opacity-30 border-orange-500'
      default:
        return 'bg-gray-900 bg-opacity-30 border-gray-500'
    }
  }

  // Inline variant (for TimelineEditor)
  if (variant === 'inline') {
    return (
      <div className="flex items-center space-x-2 text-sm">
        <FaCircle className={clsx('text-xs animate-pulse', getStatusColor())} />
        <span className="text-gray-300">ComfyUI: {getStatusText()}</span>
        {showRefresh && (
          <button
            onClick={checkHealth}
            disabled={isChecking}
            className="text-gray-400 hover:text-white transition"
            title="Refresh status"
          >
            <FaSync className={clsx('text-xs', isChecking && 'animate-spin')} />
          </button>
        )}
      </div>
    )
  }

  // Compact variant (for Header)
  if (variant === 'compact') {
    return (
      <div className="relative group">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition"
        >
          <FaCircle className={clsx('text-xs', getStatusColor(), isChecking && 'animate-pulse')} />
          <span className="text-sm text-gray-200">ComfyUI</span>
          {isExpanded ? <FaChevronUp className="text-xs" /> : <FaChevronDown className="text-xs" />}
        </button>

        {/* Tooltip on hover */}
        {!isExpanded && (
          <div className="absolute right-0 top-full mt-2 w-64 bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-3 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">ComfyUI Status</span>
              <span className={clsx('text-xs font-semibold', getStatusColor())}>
                {getStatusText()}
              </span>
            </div>
            {status.url && (
              <div className="text-xs text-gray-400 mb-1">
                <span className="font-medium">URL:</span> {status.url}
              </div>
            )}
            {status.version && (
              <div className="text-xs text-gray-400 mb-1">
                <span className="font-medium">Version:</span> {status.version}
              </div>
            )}
            {status.error && (
              <div className="text-xs text-red-400 mb-1">
                <span className="font-medium">Error:</span> {status.error}
              </div>
            )}
            {lastChecked && (
              <div className="text-xs text-gray-500 mt-2">
                Last checked: {lastChecked.toLocaleTimeString()}
              </div>
            )}
          </div>
        )}

        {/* Expanded details */}
        {isExpanded && (
          <div className="absolute right-0 top-full mt-2 w-72 bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-4 z-50">
            <div className="flex items-center justify-between mb-3">
              <span className="font-medium">ComfyUI Status</span>
              {showRefresh && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    checkHealth()
                  }}
                  disabled={isChecking}
                  className="text-gray-400 hover:text-white transition"
                  title="Refresh status"
                >
                  <FaSync className={clsx('text-sm', isChecking && 'animate-spin')} />
                </button>
              )}
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <FaCircle className={clsx('text-xs', getStatusColor(), isChecking && 'animate-pulse')} />
                <span className={clsx('font-semibold', getStatusColor())}>
                  {getStatusText()}
                </span>
              </div>

              {status.url && (
                <div className="text-sm">
                  <span className="text-gray-400">URL:</span>
                  <a
                    href={status.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 ml-2"
                  >
                    {status.url}
                  </a>
                </div>
              )}

              {status.version && (
                <div className="text-sm">
                  <span className="text-gray-400">Version:</span>
                  <span className="text-gray-200 ml-2">{status.version}</span>
                </div>
              )}

              {status.error && (
                <div className="text-sm bg-red-900 bg-opacity-20 border border-red-800 rounded p-2">
                  <span className="text-red-400">{status.error}</span>
                </div>
              )}

              {lastChecked && (
                <div className="text-xs text-gray-500 pt-2 border-t border-gray-700">
                  Last checked: {lastChecked.toLocaleTimeString()}
                </div>
              )}

              {status.status === 'offline' && (
                <div className="text-xs text-gray-400 pt-2 border-t border-gray-700">
                  ComfyUI service is not available. Make sure it's running on port 8188.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    )
  }

  // Full variant (for Dashboard)
  return (
    <div className={clsx('border rounded-lg p-6', getStatusBgColor())}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <FaCircle className={clsx('text-lg', getStatusColor(), isChecking && 'animate-pulse')} />
          <div>
            <p className="text-sm font-medium text-gray-300">ComfyUI Service</p>
            <p className={clsx('text-2xl font-bold', getStatusColor())}>
              {getStatusText()}
            </p>
          </div>
        </div>
        {showRefresh && (
          <button
            onClick={checkHealth}
            disabled={isChecking}
            className="text-gray-400 hover:text-white transition p-2"
            title="Refresh status"
          >
            <FaSync className={clsx('text-xl', isChecking && 'animate-spin')} />
          </button>
        )}
      </div>

      <div className="space-y-2 text-sm">
        {status.url && (
          <div>
            <span className="text-gray-400">URL:</span>
            <a
              href={status.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 ml-2"
            >
              {status.url}
            </a>
          </div>
        )}

        {status.version && (
          <div>
            <span className="text-gray-400">Version:</span>
            <span className="text-gray-200 ml-2">{status.version}</span>
          </div>
        )}

        {status.error && (
          <div className="bg-red-900 bg-opacity-20 border border-red-800 rounded p-2 mt-2">
            <span className="text-red-400">{status.error}</span>
          </div>
        )}

        {lastChecked && (
          <div className="text-xs text-gray-500 pt-2 mt-2 border-t border-gray-700">
            Last checked: {lastChecked.toLocaleTimeString()}
          </div>
        )}

        {status.status === 'offline' && (
          <div className="text-xs text-gray-400 pt-2 mt-2 border-t border-gray-700">
            ComfyUI service is not available. Make sure it's running on port 8188.
          </div>
        )}

        {status.status === 'online' && (
          <div className="text-xs text-green-400 pt-2 mt-2 border-t border-gray-700">
            Service is ready to process video generation requests.
          </div>
        )}
      </div>
    </div>
  )
}
