import fs from 'fs';
import path from 'path';

export const updateMockNoticesFile = (content: string) => {
  const filePath = path.join(__dirname, '../data/mockNotices.ts');
  try {
    fs.writeFileSync(filePath, content, 'utf8');
    return true;
  } catch (error) {
    console.error('更新 mockNotices.ts 文件失败:', error);
    return false;
  }
}; 