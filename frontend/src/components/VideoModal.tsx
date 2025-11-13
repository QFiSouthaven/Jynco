import { useEffect, useRef } from 'react'
import { FaTimes, FaDownload, FaExpand } from 'react-icons/fa'
import VideoPlayer from './VideoPlayer'
import clsx from 'clsx'

interface VideoModalProps {
  isOpen: boolean
  onClose: () => void
  videoUrl: string
  title?: string
  description?: string
  downloadable?: boolean
}

export default function VideoModal({
  isOpen,
  onClose,
  videoUrl,
  title,
  description,
  downloadable = true,
}: VideoModalProps) {
  const modalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === modalRef.current) {
      onClose()
    }
  }

  const handleDownload = () => {
    window.open(videoUrl, '_blank')
  }

  if (!isOpen) return null

  return (
    <div
      ref={modalRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90 p-4 animate-fadeIn"
      onClick={handleBackdropClick}
    >
      <div className="relative w-full max-w-6xl mx-auto animate-slideUp">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex-1">
            {title && (
              <h2 className="text-xl font-semibold text-white mb-1">{title}</h2>
            )}
            {description && (
              <p className="text-sm text-gray-400">{description}</p>
            )}
          </div>

          <div className="flex items-center space-x-2 ml-4">
            {downloadable && (
              <button
                onClick={handleDownload}
                className="p-3 rounded-lg bg-gray-800 hover:bg-gray-700 text-white transition"
                title="Download video"
              >
                <FaDownload />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-3 rounded-lg bg-gray-800 hover:bg-gray-700 text-white transition"
              title="Close (Esc)"
            >
              <FaTimes />
            </button>
          </div>
        </div>

        {/* Video Player */}
        <div className="rounded-lg overflow-hidden shadow-2xl bg-gray-900">
          <VideoPlayer
            videoUrl={videoUrl}
            controls
            autoplay
            className="max-h-[80vh]"
          />
        </div>

        {/* Footer Info */}
        <div className="mt-4 text-center text-sm text-gray-500">
          Press <kbd className="px-2 py-1 bg-gray-800 rounded text-gray-300">Esc</kbd> to close
        </div>
      </div>
    </div>
  )
}
