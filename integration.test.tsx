// Integration tests for the frontend
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('Integration Tests for the App', () => {
  test('renders learn react link', () => {
    render(<App />);
    const linkElement = screen.getByText(/learn react/i);
    expect(linkElement).toBeInTheDocument();
  });
});
