import React from 'react';
import { Menu } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import { HomeOutlined, CalendarOutlined, UserOutlined, LockOutlined, SettingOutlined } from '@ant-design/icons';

const Navbar: React.FC = () => {
  const location = useLocation();
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
  const isAdmin = currentUser?.username === 'admin';

  return (
    <Menu
      mode="horizontal"
      selectedKeys={[location.pathname]}
      style={{ borderBottom: 'none' }}
    >
      <Menu.Item key="/" icon={<HomeOutlined />}>
        <Link to="/">通知列表</Link>
      </Menu.Item>
      <Menu.Item key="/calendar" icon={<CalendarOutlined />}>
        <Link to="/calendar">日历视图</Link>
      </Menu.Item>
      {currentUser ? (
        <>
          {isAdmin ? (
            <Menu.Item key="/admin" icon={<SettingOutlined />}>
              <Link to="/admin">管理中心</Link>
            </Menu.Item>
          ) : (
            <Menu.Item key="/profile" icon={<UserOutlined />}>
              <Link to="/profile">个人中心</Link>
            </Menu.Item>
          )}
        </>
      ) : (
        <>
          <Menu.Item key="/login" icon={<UserOutlined />}>
            <Link to="/login">登录/注册</Link>
          </Menu.Item>
          <Menu.Item key="/admin-login" icon={<LockOutlined />}>
            <Link to="/admin-login">管理员登录</Link>
          </Menu.Item>
        </>
      )}
    </Menu>
  );
};

export default Navbar; 