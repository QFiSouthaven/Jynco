import { Link } from 'react-router-dom'
import { FaVideo, FaProjectDiagram, FaTachometerAlt } from 'react-icons/fa'

export default function Header() {
  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <FaVideo className="text-3xl text-blue-500" />
            <h1 className="text-2xl font-bold text-white">Video Foundry</h1>
          </Link>

          <nav className="flex space-x-6">
            <Link
              to="/"
              className="flex items-center space-x-2 text-gray-300 hover:text-white transition"
            >
              <FaProjectDiagram />
              <span>Projects</span>
            </Link>
            <Link
              to="/dashboard"
              className="flex items-center space-x-2 text-gray-300 hover:text-white transition"
            >
              <FaTachometerAlt />
              <span>Dashboard</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}
