import { render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

vi.mock('./api', () => ({
  clearToken: vi.fn(),
  hasToken: vi.fn(() => false),
  listBrands: vi.fn(() => Promise.resolve([])),
  listModels: vi.fn(() => Promise.resolve([])),
  login: vi.fn(),
  removeBrand: vi.fn(),
  removeModel: vi.fn(),
  saveBrand: vi.fn(),
  saveModel: vi.fn()
}))

import { hasToken, listBrands, listModels } from './api'
import App from './App'

test('renders the admin sign-in screen', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: '管理员后台' })).toBeInTheDocument()
})

test('redirects unauthenticated protected routes to login', () => {
  window.history.pushState({}, '', '/brands')
  render(<App />)
  expect(window.location.pathname).toBe('/login')
})

test('accepts the configured five-character admin password', () => {
  vi.mocked(hasToken).mockReturnValue(false)
  render(<App />)
  expect(screen.getByLabelText('密码')).toHaveAttribute('minLength', '5')
})

test('loads only the resource for the current route and reloads after navigation', async () => {
  vi.mocked(hasToken).mockReturnValue(true)
  window.history.pushState({}, '', '/brands')
  const { rerender } = render(<App />)
  await waitFor(() => expect(listBrands).toHaveBeenCalledTimes(1))
  expect(listModels).not.toHaveBeenCalled()
  window.history.pushState({}, '', '/car-models')
  window.dispatchEvent(new PopStateEvent('popstate'))
  rerender(<App />)
  await waitFor(() => expect(listModels).toHaveBeenCalledTimes(1))
})
