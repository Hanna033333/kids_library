import type { Meta, StoryObj } from '@storybook/react';
import { expect } from 'storybook/test';
import BackButton from './BackButton';

const meta = {
  title: 'Components/BackButton',
  component: BackButton,
  tags: ['ai-generated'],
  parameters: {
    nextjs: {
      appDirectory: true,
    },
  },
} satisfies Meta<typeof BackButton>;

export default meta;
type Story = StoryObj<typeof meta>;

// Basic BackButton story
export const Default: Story = {
  args: {
    href: '/',
  },
  play: async ({ canvas }) => {
    const button = canvas.getByRole('button', { name: /뒤로가기/i });
    await expect(button).toBeVisible();
  },
};

// Custom onClick handler variant
export const CustomClick: Story = {
  args: {
    href: '/',
    onClick: () => alert('Custom back clicked'),
  },
};
