import { Request, Response } from 'express';
import fs from 'fs-extra';
import path from 'path';

export const updateMockNotices = async (req: Request, res: Response) => {
  try {
    const { content } = req.body;
    console.log('收到更新请求，内容长度:', content?.length);

    if (!content) {
      console.error('请求缺少文件内容');
      return res.status(400).json({ error: '缺少文件内容' });
    }

    // 获取前端项目的根目录
    const frontendRoot = path.resolve(__dirname, '../../..');
    const filePath = path.join(frontendRoot, 'src/data/mockNotices.ts');
    console.log('目标文件路径:', filePath);

    // 检查目录是否存在
    const dirExists = await fs.pathExists(path.dirname(filePath));
    console.log('目录是否存在:', dirExists);

    // 确保目录存在
    await fs.ensureDir(path.dirname(filePath));
    console.log('目录已创建/确认');

    // 写入文件
    await fs.writeFile(filePath, content, 'utf8');
    console.log('文件写入成功');

    // 验证文件是否写入成功
    const fileExists = await fs.pathExists(filePath);
    console.log('文件是否存在:', fileExists);
    if (fileExists) {
      const fileContent = await fs.readFile(filePath, 'utf8');
      console.log('文件内容长度:', fileContent.length);
    }

    res.json({ success: true, message: '文件更新成功' });
  } catch (error: any) {
    console.error('更新文件失败:', error);
    res.status(500).json({ error: '更新文件失败', details: error.message });
  }
}; 