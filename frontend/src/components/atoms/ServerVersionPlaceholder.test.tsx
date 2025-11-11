import { describe, expect, it } from 'vitest';

import { renderWithProviders } from '../../test-utils/renderWithProviders';
import { ServerVersionPlaceholder } from './ServerVersionPlaceholder';

describe('ServerVersionPlaceholder', () => {
  it('renders an accessible loading status message', () => {
    const { getByRole } = renderWithProviders(
      <ServerVersionPlaceholder />,
    );

    const status = getByRole('status');
    expect(status).toHaveAccessibleName(/loading server version/i);
    expect(status).toHaveAttribute('aria-busy', 'true');
  });

  it('supports custom labels', () => {
    const { getByRole } = renderWithProviders(
      <ServerVersionPlaceholder label="Fetching build..." />,
    );

    expect(getByRole('status')).toHaveAccessibleName(/fetching build/i);
  });
});

