import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import Navbar from './components/Navbar';
import NoticeList from './pages/NoticeList';
import CalendarView from './pages/CalendarView';
import Login from './pages/Login';
import AdminLogin from './pages/AdminLogin';
import Admin from './pages/Admin';
import UserProfile from './pages/UserProfile';
import { initializeAdmin } from './utils/initAdmin';
import './App.css';

const { Header, Content } = Layout;

const App: React.FC = () => {
  useEffect(() => {
    // 初始化管理员账号
    initializeAdmin();
  }, []);

  return (
    <Router>
      <Layout className="layout">
        <Header>
          <Navbar />
        </Header>
        <Content className="site-content">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/admin-login" element={<AdminLogin />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/" element={<NoticeList />} />
            <Route path="/calendar" element={<CalendarView />} />
            <Route path="/profile" element={<UserProfile />} />
          </Routes>
        </Content>
      </Layout>
    </Router>
  );
};

export default App; 