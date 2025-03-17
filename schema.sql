-- 创建数据库
CREATE DATABASE IF NOT EXISTS job_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE job_platform;

-- 用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    telephone VARCHAR(11) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_telephone (telephone)
);

-- 求职意向表
CREATE TABLE job_intentions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    desired_position VARCHAR(100),
    desired_city VARCHAR(50),
    salary_min INT,
    salary_max INT,
    job_type ENUM('全职', '兼职', '实习'),
    available_time VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 职位表
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    company_name VARCHAR(100) NOT NULL,
    company_logo VARCHAR(255),
    category VARCHAR(50),
    salary VARCHAR(50),
    location VARCHAR(50),
    street VARCHAR(255),
    experience VARCHAR(50),
    education VARCHAR(50),
    job_type VARCHAR(20),
    description TEXT,
    requirements TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 职位标签表
CREATE TABLE job_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    tag VARCHAR(50) NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- 收藏职位表
CREATE TABLE saved_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_save (user_id, job_id)
);

-- 投递记录表
CREATE TABLE job_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    status ENUM('待处理', '已查看', '面试中', '已通过', '未通过') DEFAULT '待处理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- 面试记录表
CREATE TABLE interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    interview_type ENUM('tech', 'hr') NOT NULL,
    status ENUM('待面试', '进行中', '已完成') DEFAULT '待面试',
    score INT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- 用户浏览记录表
CREATE TABLE user_views (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    view_count INT DEFAULT 1,
    last_viewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_view (user_id, job_id)
);

-- 插入示例职位数据
INSERT INTO jobs (title, company_name, company_logo, category, salary, location, street, experience, education, job_type, description) 
VALUES 
('算法工程师', '字节跳动', 'static/企业.png', '算法', '25k-35k', '北京', '北京市海淀区中关村软件园二期西区8号楼', '1-3年', '本科及以上', '全职', '负责算法研发和优化'),
('前端开发工程师', '腾讯', 'static/企业.png', '开发', '20k-30k', '深圳', '深圳市南山区科技园腾讯大厦', '1-3年', '本科及以上', '全职', '负责前端开发工作'),
('后端开发工程师', '阿里巴巴', 'static/企业.png', '开发', '25k-40k', '杭州', '杭州市余杭区文一西路969号阿里巴巴西溪园区', '3-5年', '本科及以上', '全职', '负责后端系统开发'),
('数据分析师', '网易', 'static/企业.png', '数据', '18k-25k', '广州', '广州市天河区科韵路16号网易大厦', '1-3年', '本科及以上', '全职', '负责数据分析工作');

-- 插入职位标签
INSERT INTO job_tags (job_id, tag) VALUES 
(1, '人工智能'), (1, '机器学习'), (1, 'Python'),
(2, 'Vue'), (2, 'React'), (2, 'TypeScript'),
(3, 'Java'), (3, 'Spring Boot'), (3, 'MySQL'),
(4, 'SQL'), (4, 'Python'), (4, '数据分析'); 