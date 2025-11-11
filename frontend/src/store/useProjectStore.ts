import { create } from 'zustand'
import { Project, Segment } from '../api/projects'

interface ProjectState {
  currentProject: Project | null
  setCurrentProject: (project: Project | null) => void
  updateSegment: (segmentId: string, updates: Partial<Segment>) => void
  addSegment: (segment: Segment) => void
  removeSegment: (segmentId: string) => void
  reorderSegments: (segments: Segment[]) => void
}

export const useProjectStore = create<ProjectState>((set) => ({
  currentProject: null,

  setCurrentProject: (project) => set({ currentProject: project }),

  updateSegment: (segmentId, updates) => set((state) => {
    if (!state.currentProject) return state

    return {
      currentProject: {
        ...state.currentProject,
        segments: state.currentProject.segments.map((seg) =>
          seg.id === segmentId ? { ...seg, ...updates } : seg
        ),
      },
    }
  }),

  addSegment: (segment) => set((state) => {
    if (!state.currentProject) return state

    return {
      currentProject: {
        ...state.currentProject,
        segments: [...state.currentProject.segments, segment],
      },
    }
  }),

  removeSegment: (segmentId) => set((state) => {
    if (!state.currentProject) return state

    return {
      currentProject: {
        ...state.currentProject,
        segments: state.currentProject.segments.filter((seg) => seg.id !== segmentId),
      },
    }
  }),

  reorderSegments: (segments) => set((state) => {
    if (!state.currentProject) return state

    return {
      currentProject: {
        ...state.currentProject,
        segments,
      },
    }
  }),
}))
