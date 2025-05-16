import React, { useState, useEffect } from 'react';
import { Card, Tabs, List, Button, message, Space, Popconfirm, Typography } from 'antd';
import { LogoutOutlined, DeleteOutlined, StarFilled } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { User } from '../types/database';
import type { Notice } from '../types';

const { Title, Text } = Typography;

const UserProfile: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [favoriteNotices, setFavoriteNotices] = useState<Notice[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('currentUser') || 'null');
    if (!user) {
      message.error('请先登录！');
      navigate('/login');
      return;
    }
    setCurrentUser(user);

    // 从 localStorage 获取通知数据
    const notices = JSON.parse(localStorage.getItem('notices') || '[]');
    const favorites = notices.filter((notice: Notice) => 
      user.favorites.includes(notice.id)
    );
    setFavoriteNotices(favorites);
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    message.success('退出登录成功！');
    navigate('/login');
  };

  // 取消收藏
  const handleUnfavorite = (noticeId: number) => {
    if (!currentUser) return;

    // 更新用户的收藏列表
    const updatedFavorites = currentUser.favorites.filter(id => id !== noticeId);
    const updatedUser = { ...currentUser, favorites: updatedFavorites };
    
    // 更新本地存储
    localStorage.setItem('currentUser', JSON.stringify(updatedUser));
    setCurrentUser(updatedUser);

    // 更新用户列表中的用户信息
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const updatedUsers = users.map((u: User) => 
      u.id === currentUser.id ? updatedUser : u
    );
    localStorage.setItem('users', JSON.stringify(updatedUsers));

    // 更新通知的收藏量
    const notices = JSON.parse(localStorage.getItem('notices') || '[]');
    const updatedNotices = notices.map((notice: Notice) => {
      if (notice.id === noticeId) {
        return { ...notice, favorites: notice.favorites - 1 };
      }
      return notice;
    });
    localStorage.setItem('notices', JSON.stringify(updatedNotices));

    // 更新收藏列表显示
    setFavoriteNotices(favorites => favorites.filter(notice => notice.id !== noticeId));
    message.success('已取消收藏！');
  };

  const items = [
    {
      key: 'favorites',
      label: '我的收藏',
      children: (
        <List
          dataSource={favoriteNotices}
          renderItem={notice => (
            <List.Item
              actions={[
                <Popconfirm
                  title="确定要取消收藏这条通知吗？"
                  onConfirm={() => handleUnfavorite(notice.id)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button 
                    type="text" 
                    danger 
                    icon={<DeleteOutlined />}
                  >
                    取消收藏
                  </Button>
                </Popconfirm>
              ]}
            >
              <List.Item.Meta
                title={notice.title}
                description={
                  <Space direction="vertical">
                    <div>{notice.content}</div>
                    <Space>
                      <span>来源：{notice.source}</span>
                      <span>类型：{notice.category}</span>
                      <span>发布日期：{notice.publish_date}</span>
                    </Space>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      ),
    },
  ];

  if (!currentUser) {
    return null;
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card title="个人中心" style={{ marginBottom: 16 }}>
        <p>用户名：{currentUser.username}</p>
        <p>账号：{currentUser.account}</p>
      </Card>
      <Tabs items={items} />
      <Button 
        type="primary" 
        danger 
        icon={<LogoutOutlined />}
        onClick={handleLogout}
      >
        退出登录
      </Button>
    </div>
  );
};

export default UserProfile; 