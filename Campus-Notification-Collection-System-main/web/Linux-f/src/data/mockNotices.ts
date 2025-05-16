import { Notice } from '../types';

export const mockNotices: Notice[] = [
  {
    id: 1,
    title: '系统维护通知',
    content: '系统将于本周六凌晨2点进行例行维护，预计持续2小时。',
    source: '系统管理员',
    category: '通知',
    publish_date: '2024-03-20',
    views: 156,
    favorites: 15,
    link: 'https://example.com/maintenance'
  },
  {
    id: 2,
    title: '新功能上线公告',
    content: '我们很高兴地通知您，新版本的功能已经上线，包括日历视图等新特性。',
    source: '产品团队',
    category: '通知',
    publish_date: '2024-03-21',
    views: 289,
    favorites: 23,
    link: 'https://example.com/new-features'
  },
  {
    id: 3,
    title: '用户反馈调查',
    content: '为了更好地改进产品，我们正在收集用户反馈，欢迎参与调查。',
    source: '用户运营',
    category: '活动通知',
    publish_date: '2024-03-22',
    views: 178,
    favorites: 8,
    link: 'https://example.com/survey'
  },
  {
    id: 4,
    title: '安全提醒',
    content: '请及时更新您的密码，确保账号安全。',
    source: '安全团队',
    category: '安全通知',
    publish_date: '2024-03-23',
    views: 342,
    favorites: 12,
    link: 'https://example.com/security'
  },
  {
    id: 5,
    title: '技术分享会',
    content: '本周末将举办线上技术分享会，欢迎参加。',
    source: '活动策划',
    category: '活动通知',
    publish_date: '2024-03-24',
    views: 267,
    favorites: 18,
    link: 'https://example.com/tech-share'
  }
]; 