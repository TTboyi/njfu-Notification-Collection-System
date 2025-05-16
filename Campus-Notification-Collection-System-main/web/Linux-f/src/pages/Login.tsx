import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Tabs, message, Divider } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { User } from '../types/database';

const Login: React.FC = () => {
  const [activeTab, setActiveTab] = useState('login');
  const navigate = useNavigate();

  // 登录
  const onFinish = (values: { username: string; password: string }) => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const user = users.find((u: User) => u.username === values.username && u.password === values.password && u.username !== 'admin');
      if (user) {
        localStorage.setItem('currentUser', JSON.stringify(user));
        message.success('登录成功！');
        navigate('/');
      } else {
        message.error('用户名或密码错误！');
      }
  };

  // 注册
  const onRegister = (values: { username: string; password: string; confirm: string }) => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
      if (users.some((u: User) => u.username === values.username)) {
        message.error('用户名已存在！');
        return;
      }
      const newUser: User = {
        id: Date.now(),
        username: values.username,
        account: values.username,
        password: values.password,
        favorites: []
      };
      users.push(newUser);
      localStorage.setItem('users', JSON.stringify(users));
      localStorage.setItem('currentUser', JSON.stringify(newUser));
      message.success('注册成功！');
      navigate('/');
  };

  const handleGuestLogin = () => {
    const guestUser: User = {
      id: -1,
      username: '游客',
      account: 'guest',
      password: '',
      favorites: []
    };
    localStorage.setItem('currentUser', JSON.stringify(guestUser));
    message.success('游客登录成功！');
    navigate('/');
  };

  const items = [
    {
      key: 'login',
      label: '登录',
      children: (
        <>
          <Form
            name="login"
            onFinish={onFinish}
            autoComplete="off"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: '请输入用户名！' }]}
            >
              <Input prefix={<UserOutlined />} placeholder="用户名" />
            </Form.Item>
            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码！' }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="密码" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" block>
                登录
              </Button>
            </Form.Item>
          </Form>
          <Divider>或</Divider>
          <Button type="default" block onClick={handleGuestLogin}>
            游客登录
          </Button>
        </>
      )
    },
    {
      key: 'register',
      label: '注册',
      children: (
        <Form
          name="register"
          onFinish={onRegister}
          autoComplete="off"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名！' },
              { min: 3, message: '用户名至少3个字符！' }
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码！' },
              { min: 6, message: '密码至少6个字符！' }
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item
            name="confirm"
            dependencies={['password']}
            rules={[
              { required: true, message: '请确认密码！' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致！'));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="确认密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              注册
            </Button>
          </Form.Item>
        </Form>
      )
    }
  ];

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: 'calc(100vh - 64px)',
      background: '#f0f2f5'
    }}>
      <Card style={{ width: 400 }}>
        <Tabs activeKey={activeTab} onChange={setActiveTab} items={items} />
      </Card>
    </div>
  );
};

export default Login; 