import type { Meta, StoryObj } from '@storybook/react';

import { ErrorLayout } from './ErrorLayout';

const meta: Meta<typeof ErrorLayout> = {
  title: 'Organisms/ErrorLayout',
  component: ErrorLayout,
  args: {
    title: 'We cannot load the server version.',
    description:
      'The request took longer than expected. Please try again or reach out to support if the issue persists.',
    details: (
      <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
        <li>Request ID: req-123</li>
        <li>Client Request ID: client-123</li>
      </ul>
    ),
    supportHref: 'mailto:support@airlock.example',
  },
  parameters: {
    docs: {
      description: {
        component:
          'Accessible full-screen error state with focus management, retry affordances, and support guidance.',
      },
    },
  },
};

export default meta;

type Story = StoryObj<typeof ErrorLayout>;

export const Default: Story = {};

export const WithoutDetails: Story = {
  args: {
    details: undefined,
  },
};

