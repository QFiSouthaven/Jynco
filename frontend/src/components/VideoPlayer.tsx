import { useState, useRef, useEffect } from 'react'
import { FaPlay, FaExclamationTriangle, FaSpinner } from 'react-icons/fa'
import clsx from 'clsx'

interface VideoPlayerProps {
  videoUrl: string
  autoplay?: boolean
  controls?: boolean
  className?: string
  onError?: (error: Error) => void
  onLoad?: () => void
  poster?: string
}

export default function VideoPlayer({
  videoUrl,
  autoplay = false,
  controls = true,
  className,
  onError,
  onLoad,
  poster,
}: VideoPlayerProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showPlayButton, setShowPlayButton] = useState(!autoplay)
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    setShowPlayButton(!autoplay)
  }, [videoUrl, autoplay])

  const handleLoadedData = () => {
    setLoading(false)
    onLoad?.()
  }

  const handleError = (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
    setLoading(false)
    const errorMessage = 'Failed to load video. The video may not be available or there may be a network issue.'
    setError(errorMessage)
    onError?.(new Error(errorMessage))
  }

  const handlePlay = () => {
    setShowPlayButton(false)
    if (videoRef.current) {
      videoRef.current.play()
    }
  }

  const handlePause = () => {
    setShowPlayButton(true)
  }

  return (
    <div className={clsx('relative rounded-lg overflow-hidden bg-gray-900', className)}>
      {/* Video Element */}
      <video
        ref={videoRef}
        src={videoUrl}
        controls={controls && !showPlayButton}
        autoPlay={autoplay}
        onLoadedData={handleLoadedData}
        onError={handleError}
        onPlay={handlePlay}
        onPause={handlePause}
        className="w-full h-full object-contain"
        crossOrigin="anonymous"
        poster={poster}
        playsInline
      >
        Your browser does not support the video tag.
      </video>

      {/* Loading State */}
      {loading && !error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75">
          <div className="flex flex-col items-center space-y-3">
            <FaSpinner className="text-4xl text-blue-500 animate-spin" />
            <span className="text-sm text-gray-300">Loading video...</span>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-90">
          <div className="flex flex-col items-center space-y-3 text-center px-4">
            <FaExclamationTriangle className="text-4xl text-red-500" />
            <div>
              <p className="text-sm text-red-400 font-medium mb-1">Unable to Load Video</p>
              <p className="text-xs text-gray-400">{error}</p>
            </div>
            <a
              href={videoUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-400 hover:text-blue-300 underline"
            >
              Try opening in new tab
            </a>
          </div>
        </div>
      )}

      {/* Play Button Overlay */}
      {showPlayButton && !loading && !error && (
        <button
          onClick={handlePlay}
          className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40 hover:bg-opacity-50 transition group"
          aria-label="Play video"
        >
          <div className="w-16 h-16 rounded-full bg-blue-600 flex items-center justify-center group-hover:bg-blue-500 transition transform group-hover:scale-110">
            <FaPlay className="text-white text-2xl ml-1" />
          </div>
        </button>
      )}
    </div>
  )
}
