import type { Meta, StoryObj } from '@storybook/react';

import { ErrorView } from './ErrorView';

const meta: Meta<typeof ErrorView> = {
  title: 'Pages/ErrorView',
  component: ErrorView,
  args: {
    description:
      'We could not connect to the server within one second. Please retry or contact support.',
    details: (
      <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
        <li>Request ID: req-789</li>
        <li>Client Request ID: client-789</li>
      </ul>
    ),
    supportHref: 'mailto:support@airlock.example',
  },
};

export default meta;

type Story = StoryObj<typeof ErrorView>;

export const Default: Story = {};

export const CustomTitle: Story = {
  args: {
    documentTitle: 'Airlock | Version unavailable',
    title: 'Version temporarily unavailable',
  },
};

