import type { Meta, StoryObj } from '@storybook/react';

import { InitialSite } from './InitialSite';
import {
  createServerVersionErrorHandler,
  createServerVersionPendingHandler,
  createServerVersionSuccessHandler,
} from '../services/versionService.mock';

const meta: Meta<typeof InitialSite> = {
  title: 'Pages/InitialSite',
  component: InitialSite,
  parameters: {
    layout: 'fullscreen',
  },
};

export default meta;

type Story = StoryObj<typeof InitialSite>;

export const Loading: Story = {
  parameters: {
    msw: {
      handlers: [createServerVersionPendingHandler()],
    },
  },
};

export const Success: Story = {
  parameters: {
    msw: {
      handlers: [createServerVersionSuccessHandler()],
    },
  },
};

export const TimeoutError: Story = {
  parameters: {
    msw: {
      handlers: [
        createServerVersionErrorHandler({
          status: 503,
          error: 'timeout',
          message: 'Version lookup timed out.',
        }),
      ],
    },
  },
};

