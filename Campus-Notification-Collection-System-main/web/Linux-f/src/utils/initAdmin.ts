import type { User } from '../types/database';

export const initializeAdmin = () => {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    
    // 检查是否已存在管理员账号
    const adminExists = users.some((u: User) => u.username === 'admin');
    
    if (!adminExists) {
        // 创建管理员账号
        const adminUser: User = {
            id: 1,
            username: 'admin',
            account: 'admin',
            password: 'admin123',  // 默认密码
            favorites: []
        };
        
        users.push(adminUser);
        localStorage.setItem('users', JSON.stringify(users));
        console.log('管理员账号已初始化');
    }
}; 