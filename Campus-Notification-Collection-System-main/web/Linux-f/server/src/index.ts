import express from 'express';
import cors from 'cors';
import { updateMockNotices } from './controllers/noticeController';
import path from 'path';

const app = express();
const port = process.env.PORT || 3001;

// 中间件
app.use(cors());
app.use(express.json());

// 路由
app.post('/api/update-mock-notices', updateMockNotices);

// 启动服务器
app.listen(port, () => {
  console.log(`服务器运行在 http://localhost:${port}`);
}); 