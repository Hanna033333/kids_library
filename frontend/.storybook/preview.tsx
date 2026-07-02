import React from 'react'
import type { Preview } from '@storybook/nextjs-vite'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import '../app/globals.css'
import { AuthContext } from '../context/AuthContext'
import { LibraryContext } from '../context/LibraryContext'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    a11y: {
      test: 'todo'
    }
  },
  decorators: [
    (Story, storyContext) => {
      const mockAuth = storyContext.parameters.auth || {
        user: null,
        session: null,
        isLoading: false,
        signOut: async () => {}
      }

      const mockLibrary = storyContext.parameters.library || {
        selectedLibrary: '판교도서관' as const,
        setSelectedLibrary: () => {},
        availableLibraries: ['판교도서관', '송파어린이도서관'] as const
      }

      return (
        <QueryClientProvider client={queryClient}>
          <AuthContext.Provider value={mockAuth}>
            <LibraryContext.Provider value={mockLibrary}>
              <Story />
            </LibraryContext.Provider>
          </AuthContext.Provider>
        </QueryClientProvider>
      )
    }
  ]
}

export default preview