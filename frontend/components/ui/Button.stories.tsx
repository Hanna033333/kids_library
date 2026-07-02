import type { Meta, StoryObj } from '@storybook/react';
import { expect } from 'storybook/test';
import { Button } from './Button';

const meta = {
  title: 'UI/Button',
  component: Button,
  tags: ['ai-generated'],
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

// 1. Primary Button with basic smoke play function
export const Primary: Story = {
  args: {
    children: '주요 액션',
    variant: 'primary',
  },
  play: async ({ canvas }) => {
    const button = canvas.getByRole('button', { name: /주요 액션/i });
    await expect(button).toBeVisible();
  },
};

// 2. Project-wide single CssCheck story to verify global Tailwind CSS loads
export const CssCheck: Story = {
  args: {
    children: 'CSS 검증',
    variant: 'primary',
  },
  play: async ({ canvas }) => {
    const button = canvas.getByRole('button', { name: /css 검증/i });
    // #F59E0B (brand-primary) is rgb(245, 158, 11) in computed style.
    // If Tailwind CSS didn't load, this computed value will default or fail.
    await expect(getComputedStyle(button).backgroundColor).toBe('rgb(245, 158, 11)');
  },
};

// 3. Variant-only stories (no play functions as per step 6 guidelines)
export const Secondary: Story = {
  args: {
    children: '보조 액션',
    variant: 'secondary',
  },
};

export const Outline: Story = {
  args: {
    children: '테두리 액션',
    variant: 'outline',
  },
};

export const Kakao: Story = {
  args: {
    children: '카카오 로그인',
    variant: 'kakao',
  },
};

export const Destructive: Story = {
  args: {
    children: '삭제',
    variant: 'destructive',
  },
};

export const Loading: Story = {
  args: {
    children: '로딩 중',
    isLoading: true,
  },
};
