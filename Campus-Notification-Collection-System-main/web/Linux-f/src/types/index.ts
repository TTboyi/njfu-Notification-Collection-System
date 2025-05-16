export interface Notice {
  id: number;
  title: string;
  content: string;
  publish_date: string;
  category: string;
  source: string;
  link: string;
  views: number;
  favorites: number;
}

export type NoticeSource = '官网' | 'QQ群' | '管理员';
export type NoticeType = '通知' | '比赛' | '实习';
export type SortType = 'time' | 'views' | 'favorites'; 