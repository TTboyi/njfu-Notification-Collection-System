import React from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { User } from '../types/database';

const AdminLogin: React.FC = () => {
  const navigate = useNavigate();

  const onFinish = (values: { password: string }) => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const admin = users.find((u: User) => u.username === 'admin' && u.password === values.password);
    if (admin) {
      localStorage.setItem('currentUser', JSON.stringify(admin));
      message.success('管理员登录成功！');
      navigate('/admin');
    } else {
      message.error('管理员账号或密码错误！');
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: 'calc(100vh - 64px)',
      background: '#f0f2f5'
    }}>
      <Card style={{ width: 400 }}>
        <Form name="admin-login" onFinish={onFinish} autoComplete="off">
          <Form.Item
            name="username"
            initialValue="admin"
            rules={[{ required: true, message: '请输入管理员账号！' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="管理员账号" disabled />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码！' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              管理员登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default AdminLogin; 