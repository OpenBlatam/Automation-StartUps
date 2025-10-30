import { render } from '@testing-library/react';
import React from 'react';

describe('smoke', () => {
  it('renders', () => {
    render(<div>Hello</div>);
    expect(true).toBe(true);
  });
});


