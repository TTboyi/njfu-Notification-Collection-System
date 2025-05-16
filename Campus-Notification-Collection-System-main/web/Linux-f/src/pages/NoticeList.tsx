import React, { useState, useEffect } from 'react';
import { Card, Input, Select, Space, Tag, Row, Col, Button, message, Popconfirm } from 'antd';
import { SearchOutlined, StarOutlined, StarFilled, DeleteOutlined, LinkOutlined } from '@ant-design/icons';
import type { Notice, NoticeSource, NoticeType, SortType } from '../types';
import type { User } from '../types/database';
import { getCompetitions, getNotices, getExams, getInternships } from '../services/api';

const { Search } = Input;
const { Option } = Select;

const NoticeList: React.FC = () => {
  const [searchText, setSearchText] = useState('');
  const [sourceFilter, setSourceFilter] = useState<NoticeSource | 'all'>('all');
  const [typeFilter, setTypeFilter] = useState<NoticeType | 'all'>('all');
  const [sortBy, setSortBy] = useState<SortType>('time');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState(false);
  const isAdmin = currentUser?.username === 'admin';

  useEffect(() => {
    // 获取当前用户信息
    const user = JSON.parse(localStorage.getItem('currentUser') || 'null');
    setCurrentUser(user);

    // 获取所有类型的通知
    fetchAllNotices();
  }, []);

  const fetchAllNotices = async () => {
    setLoading(true);
    try {
      const [competitions, notices, exams, internships] = await Promise.all([
        getCompetitions(),
        getNotices(),
        getExams(),
        getInternships()
      ]);

      const allNotices = [
        ...(competitions.data || []),
        ...(notices.data || []),
        ...(exams.data || []),
        ...(internships.data || [])
      ];

      setNotices(allNotices);
    } catch (error) {
      console.error('获取通知失败:', error);
      message.error('获取通知失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleFavorite = (noticeId: number) => {
    if (!currentUser) {
      message.warning('请先登录后再收藏！');
      return;
    }

    const updatedFavorites = currentUser.favorites.includes(noticeId)
      ? currentUser.favorites.filter(id => id !== noticeId)
      : [...currentUser.favorites, noticeId];

    const updatedUser = { ...currentUser, favorites: updatedFavorites };
    localStorage.setItem('currentUser', JSON.stringify(updatedUser));
    setCurrentUser(updatedUser);

    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const updatedUsers = users.map((u: User) => 
      u.id === currentUser.id ? updatedUser : u
    );
    localStorage.setItem('users', JSON.stringify(updatedUsers));

    // 更新通知的收藏量
    const updatedNotices = notices.map(notice => {
      if (notice.id === noticeId) {
        return {
          ...notice,
          favorites: updatedFavorites.includes(noticeId) ? notice.favorites + 1 : notice.favorites - 1
        };
      }
      return notice;
    });
    localStorage.setItem('notices', JSON.stringify(updatedNotices));
    setNotices(updatedNotices);

    message.success(updatedFavorites.includes(noticeId) ? '收藏成功！' : '已取消收藏！');
  };

  const handleDeleteNotice = (noticeId: number) => {
    const updatedNotices = notices.filter(notice => notice.id !== noticeId);
    localStorage.setItem('notices', JSON.stringify(updatedNotices));
    setNotices(updatedNotices);
    message.success('删除通知成功！');
  };

  const handleViewNotice = (notice: Notice) => {
    // 更新浏览量
    const updatedNotices = notices.map(n => {
      if (n.id === notice.id) {
        return { ...n, views: n.views + 1 };
      }
      return n;
    });
    localStorage.setItem('notices', JSON.stringify(updatedNotices));
    setNotices(updatedNotices);

    // 打开链接
    window.open(notice.link, '_blank');
  };

  const filteredNotices = notices
    .filter(notice => {
      const matchesSearch = notice.title.toLowerCase().includes(searchText.toLowerCase()) ||
                          notice.content.toLowerCase().includes(searchText.toLowerCase());
      const matchesSource = sourceFilter === 'all' || notice.source === sourceFilter;
      const matchesType = typeFilter === 'all' || notice.category === typeFilter;
      return matchesSearch && matchesSource && matchesType;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'time':
          return new Date(b.publish_date).getTime() - new Date(a.publish_date).getTime();
        case 'views':
          return b.views - a.views;
        case 'favorites':
          return b.favorites - a.favorites;
        default:
          return 0;
      }
    });

  return (
    <div>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Row gutter={16}>
          <Col span={8}>
            <Search
              placeholder="搜索通知..."
              allowClear
              enterButton={<SearchOutlined />}
              onChange={e => setSearchText(e.target.value)}
            />
          </Col>
          <Col span={4}>
            <Select
              style={{ width: '100%' }}
              value={sourceFilter}
              onChange={value => setSourceFilter(value as NoticeSource | 'all')}
            >
              <Option value="all">所有来源</Option>
              <Option value="官网">官网</Option>
              <Option value="QQ群">QQ群</Option>
              <Option value="管理员">管理员</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Select
              style={{ width: '100%' }}
              value={typeFilter}
              onChange={value => setTypeFilter(value as NoticeType | 'all')}
            >
              <Option value="all">所有类型</Option>
              <Option value="通知">通知</Option>
              <Option value="比赛">比赛</Option>
              <Option value="实习">实习</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Select
              style={{ width: '100%' }}
              value={sortBy}
              onChange={value => setSortBy(value as SortType)}
            >
              <Option value="time">按时间排序</Option>
              <Option value="views">按浏览量排序</Option>
              <Option value="favorites">按收藏量排序</Option>
            </Select>
          </Col>
        </Row>

        {filteredNotices.map(notice => (
          <Card
            key={notice.id}
            className="notice-card"
            hoverable
            onClick={() => handleViewNotice(notice)}
          >
            <Card.Meta
              title={notice.title}
              description={
                <Space direction="vertical">
                  <div>{notice.content}</div>
                  <Space>
                    <Tag color="blue">{notice.source}</Tag>
                    <Tag color="green">{notice.category}</Tag>
                    <span>{notice.publish_date}</span>
                    <Space>
                      <SearchOutlined /> {notice.views}
                      <Button
                        type="text"
                        icon={currentUser?.favorites.includes(notice.id) ? 
                          <StarFilled style={{ color: '#1890ff' }} /> : 
                          <StarOutlined />
                        }
                        onClick={(e) => {
                          e.stopPropagation();
                          handleFavorite(notice.id);
                        }}
                        style={{ padding: '0 4px' }}
                      >
                        {notice.favorites}
                      </Button>
                      <Button
                        type="text"
                        icon={<LinkOutlined />}
                        onClick={(e) => {
                          e.stopPropagation();
                          window.open(notice.link, '_blank');
                        }}
                        style={{ padding: '0 4px' }}
                      />
                      {isAdmin && (
                        <Popconfirm
                          title="确定要删除这条通知吗？"
                          onConfirm={(e) => {
                            e?.stopPropagation();
                            handleDeleteNotice(notice.id);
                          }}
                          okText="确定"
                          cancelText="取消"
                        >
                          <Button
                            type="text"
                            danger
                            icon={<DeleteOutlined />}
                            style={{ padding: '0 4px' }}
                            onClick={(e) => e.stopPropagation()}
                          />
                        </Popconfirm>
                      )}
                    </Space>
                  </Space>
                </Space>
              }
            />
          </Card>
        ))}
      </Space>
    </div>
  );
};

export default NoticeList; 