import { render, screen } from '@testing-library/react'
import App from './App'

test('renders the admin sign-in screen', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: '管理员后台' })).toBeInTheDocument()
})
