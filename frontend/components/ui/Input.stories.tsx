import type { Meta, StoryObj } from '@storybook/react';
import { expect } from 'storybook/test';
import { Input } from './Input';

const meta = {
  title: 'UI/Input',
  component: Input,
  tags: ['ai-generated'],
} satisfies Meta<typeof Input>;

export default meta;
type Story = StoryObj<typeof meta>;

// 1. Default Input with an interactive typing verification
export const Default: Story = {
  args: {
    placeholder: '이름을 입력하세요',
    type: 'text',
  },
  play: async ({ canvas, userEvent }) => {
    const input = canvas.getByPlaceholderText('이름을 입력하세요') as HTMLInputElement;
    await expect(input).toBeVisible();
    
    // Type into the input
    await userEvent.type(input, '홍길동');
    
    // Assert the value changed
    await expect(input.value).toBe('홍길동');
  },
};

// 2. Disabled Input (no play function since it's a simple variant)
export const Disabled: Story = {
  args: {
    placeholder: '입력할 수 없습니다',
    disabled: true,
  },
};

// 3. Password Input
export const Password: Story = {
  args: {
    placeholder: '비밀번호를 입력하세요',
    type: 'password',
  },
};
