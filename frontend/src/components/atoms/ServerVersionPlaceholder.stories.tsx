import type { Meta, StoryObj } from '@storybook/react';

import { ServerVersionPlaceholder } from './ServerVersionPlaceholder';

const meta: Meta<typeof ServerVersionPlaceholder> = {
  title: 'Atoms/ServerVersionPlaceholder',
  component: ServerVersionPlaceholder,
  args: {
    label: 'Loading server version...',
  },
  parameters: {
    docs: {
      description: {
        component:
          'Accessible loading indicator announced via aria-live polite to convey in-progress version requests.',
      },
    },
  },
};

export default meta;

type Story = StoryObj<typeof ServerVersionPlaceholder>;

export const Default: Story = {};

export const CustomLabel: Story = {
  args: {
    label: 'Refreshing build metadata...',
  },
};

