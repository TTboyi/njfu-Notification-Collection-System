export interface User {
  id: number;
  username: string;
  account: string;
  password: string;
  favorites: number[];
}

export interface Notification {
  id: number;
  title: string;
  content: string;
  createdAt: string;
}

export interface Notice {
  id: number;
  title: string;
  content: string;
  source: string;
  type: string;
  publishTime: string;
  views: number;
  favorites: number;
}

export interface Database {
  users: User[];
  notices: Notice[];
} 