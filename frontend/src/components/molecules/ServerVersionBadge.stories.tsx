import type { Meta, StoryObj } from '@storybook/react';

import { ServerVersionBadge } from './ServerVersionBadge';

const meta: Meta<typeof ServerVersionBadge> = {
  title: 'Molecules/ServerVersionBadge',
  component: ServerVersionBadge,
  args: {
    label: 'v1.4.2',
    retrievedAt: new Date().toISOString(),
    source: 'api',
  },
  parameters: {
    docs: {
      description: {
        component:
          'Displays the live server version with accessible announcements and contextual metadata.',
      },
    },
  },
};

export default meta;

type Story = StoryObj<typeof ServerVersionBadge>;

export const Default: Story = {};

export const WithoutMetadata: Story = {
  args: {
    source: undefined,
    retrievedAt: undefined,
  },
};

