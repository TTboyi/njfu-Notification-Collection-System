import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, message, Space, Card, Tabs, Select } from 'antd';
import { DeleteOutlined, PlusOutlined, LogoutOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { User, Notification } from '../types/database';
import type { Notice, NoticeType } from '../types';
import { mockNotices } from '../data/mockNotices';
import { updateMockNotices } from '../services/api';

const { Option } = Select;

const Admin: React.FC = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState<User[]>([]);
  const [notices, setNotices] = useState<Notice[]>([]);
  const [isNotificationModalVisible, setIsNotificationModalVisible] = useState(false);
  const [notificationForm] = Form.useForm();

  // 加载用户和通知数据
  useEffect(() => {
    fetchUsers();
    fetchNotices();
  }, []);

  // 获取用户
  const fetchUsers = () => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    setUsers(users);
  };

  // 获取通知
  const fetchNotices = () => {
    const notices = JSON.parse(localStorage.getItem('notices') || '[]');
    setNotices(notices);
  };

  // 删除用户
  const handleDeleteUser = (userId: number) => {
    let users = JSON.parse(localStorage.getItem('users') || '[]');
    users = users.filter((u: User) => u.id !== userId);
    localStorage.setItem('users', JSON.stringify(users));
    message.success('删除用户成功');
    fetchUsers();
  };

  // 删除通知
  const handleDeleteNotice = async (noticeId: number) => {
    try {
      let notices = JSON.parse(localStorage.getItem('notices') || '[]');
      notices = notices.filter((n: Notice) => n.id !== noticeId);
      localStorage.setItem('notices', JSON.stringify(notices));
      setNotices(notices);

      // 更新 mockNotices.ts 文件
      const updatedMockNotices = mockNotices.filter(n => n.id !== noticeId);
      const fileContent = `import { Notice } from '../types';\n\nexport const mockNotices: Notice[] = ${JSON.stringify(updatedMockNotices, null, 2)};`;
      
      try {
        await updateMockNotices(fileContent);
        message.success('删除通知成功');
      } catch (error) {
        message.warning('通知已从列表中删除，但文件更新失败，请稍后重试');
        console.error('文件更新失败:', error);
      }
      
      fetchNotices();
    } catch (error) {
      message.error('删除通知失败，请重试');
      console.error('删除通知失败:', error);
    }
  };

  // 添加通知
  const handleAddNotice = async (values: any) => {
    try {
      let notices = JSON.parse(localStorage.getItem('notices') || '[]');
      const newNotice: Notice = {
        id: Date.now(),
        title: values.title,
        content: values.content,
        category: values.type,
        source: '管理员',
        link: values.link,
        publish_date: new Date().toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        }).replace(/\//g, '-'),
        views: 0,
        favorites: 0
      };
      notices.unshift(newNotice);
      localStorage.setItem('notices', JSON.stringify(notices));
      setNotices(notices);

      // 更新 mockNotices.ts 文件
      const updatedMockNotices = [newNotice, ...mockNotices];
      const fileContent = `import { Notice } from '../types';\n\nexport const mockNotices: Notice[] = ${JSON.stringify(updatedMockNotices, null, 2)};`;
      
      try {
        await updateMockNotices(fileContent);
        message.success('添加通知成功');
      } catch (error) {
        message.warning('通知已添加到列表，但文件更新失败，请稍后重试');
        console.error('文件更新失败:', error);
      }

      setIsNotificationModalVisible(false);
      notificationForm.resetFields();
      fetchNotices();
    } catch (error) {
      message.error('添加通知失败，请重试');
      console.error('添加通知失败:', error);
    }
  };

  // 退出管理
  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    message.success('退出管理成功！');
    navigate('/admin-login');
  };

  const userColumns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '账号',
      dataIndex: 'account',
      key: 'account',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: User) => (
        <Space>
          <Button 
            type="primary" 
            danger 
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteUser(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const noticeColumns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
    },
    {
      title: '链接',
      dataIndex: 'link',
      key: 'link',
      ellipsis: true,
    },
    {
      title: '发布日期',
      dataIndex: 'publishTime',
      key: 'publishTime',
    },
    {
      title: '浏览量',
      dataIndex: 'views',
      key: 'views',
    },
    {
      title: '收藏量',
      dataIndex: 'favorites',
      key: 'favorites',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Notice) => (
        <Space>
          <Button 
            type="primary" 
            danger 
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteNotice(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const items = [
    {
      key: 'users',
      label: '用户管理',
      children: (
        <Card>
          <Table columns={userColumns} dataSource={users} rowKey="id" />
        </Card>
      ),
    },
    {
      key: 'notices',
      label: '通知管理',
      children: (
        <Card>
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={() => setIsNotificationModalVisible(true)}
            style={{ marginBottom: 16 }}
          >
            添加通知
          </Button>
          <Table columns={noticeColumns} dataSource={notices} rowKey="id" />
        </Card>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: 16, textAlign: 'right' }}>
        <Button 
          type="primary" 
          danger 
          icon={<LogoutOutlined />}
          onClick={handleLogout}
        >
          退出管理
        </Button>
      </div>
      <Tabs items={items} />
      <Modal
        title="添加通知"
        open={isNotificationModalVisible}
        onCancel={() => setIsNotificationModalVisible(false)}
        footer={null}
      >
        <Form form={notificationForm} onFinish={handleAddNotice}>
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入通知标题' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="content"
            label="内容"
            rules={[{ required: true, message: '请输入通知内容' }]}
          >
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item
            name="type"
            label="类型"
            rules={[{ required: true, message: '请选择通知类型' }]}
          >
            <Select>
              <Option value="通知">通知</Option>
              <Option value="比赛">比赛</Option>
              <Option value="实习">实习</Option>
              <Option value="活动通知">活动通知</Option>
              <Option value="安全通知">安全通知</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="link"
            label="链接"
            rules={[{ required: true, message: '请输入通知链接' }]}
          >
            <Input placeholder="请输入完整的URL地址" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              提交
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Admin; 