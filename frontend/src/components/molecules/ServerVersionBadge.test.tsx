import { describe, expect, it, vi } from 'vitest';

import { renderWithProviders } from '../../test-utils/renderWithProviders';
import { ServerVersionBadge } from './ServerVersionBadge';

describe('ServerVersionBadge', () => {
  it('announces the server version for assistive technology', () => {
    const { getByRole } = renderWithProviders(
      <ServerVersionBadge
        label="v1.2.3"
        retrievedAt="2025-11-10T12:34:56.000Z"
        source="api"
      />,
    );

    const status = getByRole('status');
    expect(status).toHaveAttribute(
      'aria-label',
      expect.stringContaining('Server version: v1.2.3'),
    );
  });

  it('renders formatted retrieval timestamps when provided', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2025-11-11T00:00:00.000Z'));

    const { getByRole, getAllByText } = renderWithProviders(
      <ServerVersionBadge
        label="v1.2.3"
        retrievedAt="2025-11-10T12:34:56.000Z"
      />,
    );

    const status = getByRole('status');
    expect(status).toHaveAccessibleName(/retrieved/i);
    expect(getAllByText(/v1\.2\.3/).length).toBeGreaterThan(0);

    vi.useRealTimers();
  });
});

