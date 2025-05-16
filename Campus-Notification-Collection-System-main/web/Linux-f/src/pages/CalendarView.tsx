import React, { useState, useEffect } from 'react';
import { Calendar, Badge, Card, List, Button, Spin, message, Tag } from 'antd';
import { LinkOutlined } from '@ant-design/icons';
import type { Dayjs } from 'dayjs';
import type { BadgeProps } from 'antd';
import type { Notice } from '../types';
import axios from 'axios';

const CalendarView: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<Dayjs | null>(null);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchNotices();
  }, []);

  const fetchNotices = async () => {
    try {
      setLoading(true);
      // 获取QQ群数据
      const qqResponse = await axios.get('http://localhost:5000/api/notices?source=QQ群');
      // 获取官网数据
      const webResponse = await axios.get('http://localhost:5000/api/notices?source=官网');
      
      const allNotices = [
        ...(qqResponse.data?.data || []),
        ...(webResponse.data?.data || [])
      ];
      
      setNotices(allNotices);
    } catch (error) {
      console.error('获取通知失败:', error);
      message.error('获取通知失败');
    } finally {
      setLoading(false);
    }
  };

  const getListData = (value: Dayjs) => {
    return notices.filter(notice => 
      notice.publish_date === value.format('YYYY-MM-DD')
    );
  };

  const getBadgeStatus = (type: string, source: string): BadgeProps['status'] => {
    // 根据来源和类型设置不同的徽章状态
    if (source === 'QQ群') {
      switch (type) {
        case '通知':
          return 'processing';
        case '活动通知':
          return 'warning';
        case '安全通知':
          return 'error';
        default:
          return 'default';
      }
    } else {
      switch (type) {
        case '通知':
          return 'success';
        case '活动通知':
          return 'processing';
        case '安全通知':
          return 'error';
        default:
          return 'default';
      }
    }
  };

  const dateCellRender = (value: Dayjs) => {
    const listData = getListData(value);
    return (
      <ul className="events">
        {listData.map(item => (
          <li key={item.id}>
            <Badge 
              status={getBadgeStatus(item.category, item.source)} 
              text={
                <span>
                  {item.title}
                  <Tag color={item.source === 'QQ群' ? 'blue' : 'green'} style={{ marginLeft: 8 }}>
                    {item.source}
                  </Tag>
                </span>
              } 
            />
          </li>
        ))}
      </ul>
    );
  };

  return (
    <Spin spinning={loading}>
      <div className="calendar-view">
        <Calendar
          onSelect={setSelectedDate}
          dateCellRender={dateCellRender}
        />
        {selectedDate && (
          <Card
            title={`${selectedDate.format('YYYY-MM-DD')} 的通知`}
            style={{ marginTop: 16 }}
          >
            <List
              dataSource={getListData(selectedDate)}
              renderItem={item => (
                <List.Item
                  actions={[
                    <Button
                      key="link"
                      type="text"
                      icon={<LinkOutlined />}
                      onClick={() => window.open(item.link, '_blank')}
                    />
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <span>
                        {item.title}
                        <Tag color={item.source === 'QQ群' ? 'blue' : 'green'} style={{ marginLeft: 8 }}>
                          {item.source}
                        </Tag>
                      </span>
                    }
                    description={
                      <div>
                        <div>{item.content}</div>
                        <div style={{ marginTop: 8 }}>
                          <Badge status={getBadgeStatus(item.category, item.source)} text={item.category} />
                          <span style={{ marginLeft: 16 }}>浏览量：{item.views}</span>
                          <span style={{ marginLeft: 16 }}>收藏量：{item.favorites}</span>
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        )}
      </div>
    </Spin>
  );
};

export default CalendarView; 