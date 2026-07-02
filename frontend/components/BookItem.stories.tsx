import type { Meta, StoryObj } from '@storybook/react';
import { expect } from 'storybook/test';
import BookItem from './BookItem';
import { Book } from '@/lib/types';

// Mock Book Data
const mockBook: Book = {
  id: 101,
  title: '잠자리 꿀잠 그림책',
  author: '홍길동',
  publisher: '꿈나라 출판사',
  isbn: '9788912345678',
  image_url: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=400',
  age: '3세부터',
  category: '잠자리',
  description: '아이들의 꿀잠을 도와주는 유익한 그림책입니다.',
  pangyo_callno: '유 813.8-꿈56잠',
  vol: '1',
  national_loan_count: 1250,
  library_info: [
    {
      library_name: '판교도서관',
      callno: '유 813.8-꿈56잠',
    },
    {
      library_name: '송파어린이도서관',
      callno: '유 813.8-꿈56잠-1',
    }
  ]
};

const meta = {
  title: 'Components/BookItem',
  component: BookItem,
  tags: ['ai-generated'],
  parameters: {
    nextjs: {
      appDirectory: true,
    },
  },
} satisfies Meta<typeof BookItem>;

export default meta;
type Story = StoryObj<typeof meta>;

// 1. Logged Out View - Should NOT show call number and loan badge
export const LoggedOut: Story = {
  args: {
    book: mockBook,
  },
  parameters: {
    auth: {
      user: null,
      session: null,
      isLoading: false,
      signOut: async () => {},
    },
    library: {
      selectedLibrary: '판교도서관',
      setSelectedLibrary: () => {},
      availableLibraries: ['판교도서관', '송파어린이도서관'],
    },
  },
  play: async ({ canvas }) => {
    // Should display title and publisher
    await expect(canvas.getByText('잠자리 꿀잠 그림책')).toBeVisible();
    await expect(canvas.getByText('꿈나라 출판사')).toBeVisible();
    
    // Call number should not be visible when logged out
    const callNoText = canvas.queryByText(/유 813\.8/);
    await expect(callNoText).toBeNull();
  },
};

// 2. Logged In, Available State - Should show call number and "대출가능" badge
export const LoggedInAvailable: Story = {
  args: {
    book: mockBook,
    loanStatus: {
      status: '대출가능',
      available: true,
    },
  },
  parameters: {
    auth: {
      user: { id: 'test-user-uuid', email: 'user@test.com' } as any,
      session: { user: {} } as any,
      isLoading: false,
      signOut: async () => {},
    },
    library: {
      selectedLibrary: '판교도서관',
      setSelectedLibrary: () => {},
      availableLibraries: ['판교도서관', '송파어린이도서관'],
    },
  },
  play: async ({ canvas }) => {
    // Should display call number and badge
    await expect(canvas.getByText('유 813.8-꿈56잠-1')).toBeVisible(); // 'vol' is 1, so displays as '-1'
    await expect(canvas.getByText('대출가능')).toBeVisible();
  },
};

// 3. Logged In, Borrowed State - Should show "대출중" badge
export const LoggedInBorrowed: Story = {
  args: {
    book: mockBook,
    loanStatus: {
      status: '대출중',
      available: false,
    },
  },
  parameters: {
    auth: {
      user: { id: 'test-user-uuid', email: 'user@test.com' } as any,
      session: { user: {} } as any,
      isLoading: false,
      signOut: async () => {},
    },
    library: {
      selectedLibrary: '판교도서관',
      setSelectedLibrary: () => {},
      availableLibraries: ['판교도서관', '송파어린이도서관'],
    },
  },
};

// 4. Logged In, Checking State - Should show "확인중" badge
export const LoggedInChecking: Story = {
  args: {
    book: mockBook,
    loanStatus: {
      status: '확인중',
      available: null,
    },
  },
  parameters: {
    auth: {
      user: { id: 'test-user-uuid', email: 'user@test.com' } as any,
      session: { user: {} } as any,
      isLoading: false,
      signOut: async () => {},
    },
    library: {
      selectedLibrary: '판교도서관',
      setSelectedLibrary: () => {},
      availableLibraries: ['판교도서관', '송파어린이도서관'],
    },
  },
};
