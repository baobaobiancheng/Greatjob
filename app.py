import pymysql
from pymysql.cursors import DictCursor
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, ResumeForm, ChangePasswordForm
import requests
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '861012',
    'db': 'job_platform',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

def get_db():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        return None

# 创建数据库连接的装饰器
def with_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': '数据库连接失败'})
        try:
            kwargs['db'] = db
            result = func(*args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            print(f"数据库操作失败: {str(e)}")
            return jsonify({'success': False, 'message': '数据库操作失败'})
        finally:
            db.close()
    return wrapper

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于session和flash消息

# 模拟用户数据库
users = {}

# 模拟职位数据
jobs = [
    {
        'id': 1,
        'title': '算法工程师',
        'category': '算法',
        'salary': '25k-35k',
        'company_name': '字节跳动',
        'company_logo': 'static/企业.png',
        'tags': ['人工智能', '机器学习', 'Python'],
        'location': '北京',
        'experience': '1-3年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 2,
        'title': '前端开发工程师',
        'category': '开发',
        'salary': '20k-30k',
        'company_name': '腾讯',
        'company_logo': 'static/企业.png',
        'tags': ['Vue', 'React', 'TypeScript'],
        'location': '深圳',
        'experience': '1-3年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 3,
        'title': '后端开发工程师',
        'category': '开发',
        'salary': '25k-40k',
        'company_name': '阿里巴巴',
        'company_logo': 'static/企业.png',
        'tags': ['Java', 'Spring Boot', 'MySQL'],
        'location': '杭州',
        'experience': '3-5年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 4,
        'title': '数据分析师',
        'category': '数据',
        'salary': '18k-25k',
        'company_name': '网易',
        'company_logo': 'static/企业.png',
        'tags': ['SQL', 'Python', '数据分析'],
        'location': '广州',
        'experience': '1-3年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 5,
        'title': '产品经理',
        'category': '产品',
        'salary': '20k-35k',
        'company_name': '美团',
        'company_logo': 'static/企业.png',
        'tags': ['产品设计', '需求分析', '项目管理'],
        'location': '北京',
        'experience': '3-5年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 6,
        'title': 'UI设计师',
        'category': '设计',
        'salary': '15k-25k',
        'company_name': '小米',
        'company_logo': 'static/企业.png',
        'tags': ['UI设计', 'Figma', 'Sketch'],
        'location': '武汉',
        'experience': '1-3年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 7,
        'title': '运维工程师',
        'category': '运维',
        'salary': '18k-28k',
        'company_name': '华为',
        'company_logo': 'static/企业.png',
        'tags': ['Linux', 'Docker', 'Kubernetes'],
        'location': '深圳',
        'experience': '3-5年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 8,
        'title': '测试工程师',
        'category': '测试',
        'salary': '15k-25k',
        'company_name': '百度',
        'company_logo': 'static/企业.png',
        'tags': ['自动化测试', 'Python', 'Selenium'],
        'location': '上海',
        'experience': '1-3年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 9,
        'title': '安全工程师',
        'category': '安全',
        'salary': '25k-40k',
        'company_name': '京东',
        'company_logo': 'static/企业.png',
        'tags': ['网络安全', '渗透测试', '安全架构'],
        'location': '北京',
        'experience': '3-5年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 10,
        'title': '大数据开发工程师',
        'category': '开发',
        'salary': '25k-40k',
        'company_name': '滴滴',
        'company_logo': 'static/企业.png',
        'tags': ['Hadoop', 'Spark', 'Hive'],
        'location': '杭州',
        'experience': '3-5年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 11,
        'title': '游戏开发工程师',
        'category': '开发',
        'salary': '20k-35k',
        'company_name': '网易游戏',
        'company_logo': 'static/企业.png',
        'tags': ['Unity3D', 'C++', 'Unreal'],
        'location': '广州',
        'experience': '1-3年',
        'education': '本科及以上',
        'job_type': '全职'
    },
    {
        'id': 12,
        'title': '区块链开发工程师',
        'category': '开发',
        'salary': '30k-50k',
        'company_name': '币安',
        'company_logo': 'static/企业.png',
        'tags': ['区块链', 'Solidity', '智能合约'],
        'location': '上海',
        'experience': '3-5年',
        'education': '本科及以上',
        'job_type': '全职'
    }
]

# 添加全局城市列表配置
CITIES = [
    '全国', '北京', '上海', '广州', '深圳', '杭州', '天津', '西安', 
    '苏州', '武汉', '厦门', '长沙', '成都', '郑州', '重庆', '其他城市'
]

@app.route('/')
@app.route('/index')
def index():
    try:
        # 获取筛选参数
        selected_city = request.args.get('city', '全国')
        selected_type = request.args.get('job_type', '不限')
        search_title = request.args.get('title', '')
        
        db = get_db()
        with db.cursor() as cursor:
            # 构建基础查询
            query = """
                SELECT j.*, GROUP_CONCAT(t.tag) as tags
                FROM jobs j
                LEFT JOIN job_tags t ON j.id = t.job_id
                WHERE 1=1
            """
            params = []
            
            # 组合查询条件
            conditions = []
            
            # 添加职位名称搜索条件
            if search_title:
                conditions.append("j.title LIKE %s")
                params.append(f"%{search_title}%")
            
            # 添加城市筛选条件
            if selected_city != '全国':
                conditions.append("j.location = %s")
                params.append(selected_city)
            
            # 添加工作类型筛选条件
            if selected_type != '不限':
                conditions.append("j.job_type = %s")
                params.append(selected_type)
            
            # 将所有条件组合到查询语句中
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            # 分组并排序，限制30条记录（10行3列）
            query += " GROUP BY j.id ORDER BY j.created_at DESC LIMIT 30"
            
            # 执行查询
            cursor.execute(query, params)
            jobs = cursor.fetchall()
            
            # 处理标签字符串为列表
            for job in jobs:
                job['tags'] = job['tags'].split(',') if job['tags'] else []
            
            return render_template('index.html',
                                jobs=jobs,
                                selected_city=selected_city,
                                selected_type=selected_type,
                                search_title=search_title,
                                user=session.get('user_id'))
                                
    except Exception as e:
        print(f"首页加载错误: {str(e)}")
        return render_template('index.html', 
                            jobs=[],
                            selected_city='全国',
                            selected_type='不限',
                            search_title='',
                            user=session.get('user_id'))
    finally:
        if 'db' in locals():
            db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data
            
            db = get_db()
            with db.cursor() as cursor:
                # 查询用户
                cursor.execute(
                    "SELECT id, username, password FROM users WHERE username = %s",
                    (username,)
                )
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password'], password):
                    # 登录成功，存储用户信息到session
                    session['user_id'] = username
                    session['logged_in'] = True  # 添加登录状态标记
                    
                    # 检查是否有next参数，有则跳转到对应页面
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect(url_for('personal_center'))  # 默认跳转到个人中心
                else:
                    flash('用户名或密码错误')
                    return redirect(url_for('login'))
                    
        except Exception as e:
            print(f"登录错误: {str(e)}")
            flash('登录失败，请重试')
            return redirect(url_for('login'))
        finally:
            if 'db' in locals():
                db.close()
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已退出登录')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data
            phone = form.phone.data
            
            # 生成密码哈希
            hashed_password = generate_password_hash(password)
            
            db = get_db()
            with db.cursor() as cursor:
                # 检查用户名是否已存在
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('用户名已存在')
                    return redirect(url_for('register'))
                
                # 检查手机号是否已存在
                cursor.execute("SELECT id FROM users WHERE telephone = %s", (phone,))
                if cursor.fetchone():
                    flash('手机号已被注册')
                    return redirect(url_for('register'))
                
                # 创建新用户
                try:
                    cursor.execute(
                        "INSERT INTO users (username, password, telephone) VALUES (%s, %s, %s)",
                        (username, hashed_password, phone)
                    )
                    db.commit()
                    flash('注册成功，请登录')
                    return redirect(url_for('login'))
                except Exception as e:
                    db.rollback()
                    print(f"数据库插入错误: {str(e)}")
                    flash('注册失败，请重试')
                    return redirect(url_for('register'))
                
        except Exception as e:
            print(f"注册过程错误: {str(e)}")
            flash('注册失败，请重试')
            return redirect(url_for('register'))
        finally:
            if 'db' in locals():
                db.close()
    
    return render_template('register.html', form=form)

@app.route('/competitive-analysis')
@login_required
def competitive_analysis():
    return render_template('competitive_analysis.html', user=session.get('user_id'))

@app.route('/job-analysis')
@login_required
def job_analysis():
    return render_template('job_analysis.html', user=session.get('user_id'))

@app.route('/api/job-analysis/salary-distribution', methods=['GET'])
def get_salary_distribution():
    try:
        category = request.args.get('category', 'all')
        time_range = request.args.get('time_range', '30')
        
        db = get_db()
        with db.cursor() as cursor:
            # 基础查询
            query = """
                SELECT 
                    CASE 
                        WHEN CAST(
                            REGEXP_REPLACE(
                                SUBSTRING_INDEX(
                                    REGEXP_REPLACE(LOWER(salary), '[^0-9-]', ''),
                                    '-',
                                    1
                                ),
                                '[^0-9]', ''
                            ) AS DECIMAL
                        ) < 10 THEN '10k以下'
                        WHEN CAST(
                            REGEXP_REPLACE(
                                SUBSTRING_INDEX(
                                    REGEXP_REPLACE(LOWER(salary), '[^0-9-]', ''),
                                    '-',
                                    1
                                ),
                                '[^0-9]', ''
                            ) AS DECIMAL
                        ) < 15 THEN '10-15k'
                        WHEN CAST(
                            REGEXP_REPLACE(
                                SUBSTRING_INDEX(
                                    REGEXP_REPLACE(LOWER(salary), '[^0-9-]', ''),
                                    '-',
                                    1
                                ),
                                '[^0-9]', ''
                            ) AS DECIMAL
                        ) < 20 THEN '15-20k'
                        WHEN CAST(
                            REGEXP_REPLACE(
                                SUBSTRING_INDEX(
                                    REGEXP_REPLACE(LOWER(salary), '[^0-9-]', ''),
                                    '-',
                                    1
                                ),
                                '[^0-9]', ''
                            ) AS DECIMAL
                        ) < 25 THEN '20-25k'
                        WHEN CAST(
                            REGEXP_REPLACE(
                                SUBSTRING_INDEX(
                                    REGEXP_REPLACE(LOWER(salary), '[^0-9-]', ''),
                                    '-',
                                    1
                                ),
                                '[^0-9]', ''
                            ) AS DECIMAL
                        ) < 30 THEN '25-30k'
                        WHEN CAST(
                            REGEXP_REPLACE(
                                SUBSTRING_INDEX(
                                    REGEXP_REPLACE(LOWER(salary), '[^0-9-]', ''),
                                    '-',
                                    1
                                ),
                                '[^0-9]', ''
                            ) AS DECIMAL
                        ) < 35 THEN '30-35k'
                        ELSE '35k以上'
                    END as salary_range,
                    COUNT(*) as count
                FROM jobs
            """
            
            # 添加分类筛选
            if category != 'all':
                query += " WHERE category = %s"
                params = [category]
            else:
                params = []
                
            # 添加时间范围
            if query.find('WHERE') > 0:
                query += " AND"
            else:
                query += " WHERE"
            query += " created_at >= DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)"
            params.append(time_range)
            
            # 分组和排序
            query += " GROUP BY salary_range ORDER BY salary_range"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # 格式化结果
            salary_ranges = ['10k以下', '10-15k', '15-20k', '20-25k', '25-30k', '30-35k', '35k以上']
            data = {range: 0 for range in salary_ranges}
            for row in results:
                data[row['salary_range']] = row['count']
            
            return jsonify({
                'success': True,
                'data': {
                    'ranges': list(data.keys()),
                    'counts': list(data.values())
                }
            })
            
    except Exception as e:
        print(f"获取薪资分布数据错误: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'db' in locals():
            db.close()

@app.route('/api/job-analysis/skill-requirements', methods=['GET'])
def get_skill_requirements():
    try:
        category = request.args.get('category', 'all')
        time_range = request.args.get('time_range', '30')
        
        db = get_db()
        with db.cursor() as cursor:
            # 基础查询
            query = """
                SELECT job_type as tag, COUNT(*) as count
                FROM jobs
                WHERE 1=1
            """
            
            # 添加分类筛选
            if category != 'all':
                query += " AND category = %s"
                params = [category]
            else:
                params = []
                
            # 添加时间范围
            query += " AND created_at >= DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)"
            params.append(time_range)
            
            # 分组和排序，限制返回前10个结果
            query += " GROUP BY job_type ORDER BY count DESC LIMIT 10"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'data': [{
                    'name': row['tag'],
                    'value': row['count']
                } for row in results]
            })
            
    except Exception as e:
        print(f"获取技能需求数据错误: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'db' in locals():
            db.close()

@app.route('/api/job-analysis/education-distribution', methods=['GET'])
def get_education_distribution():
    try:
        category = request.args.get('category', 'all')
        time_range = request.args.get('time_range', '30')
        
        db = get_db()
        with db.cursor() as cursor:
            # 基础查询
            query = """
                SELECT 
                    CASE 
                        WHEN education REGEXP '本科' THEN '本科'
                        WHEN education REGEXP '大专' THEN '大专'
                        WHEN education REGEXP '硕士' THEN '硕士'
                        WHEN education REGEXP '博士' THEN '博士'
                        WHEN education REGEXP '不限|不要求' THEN '学历不限'
                        ELSE '其他'
                    END as education_level,
                    COUNT(*) as count
                FROM jobs
                WHERE 1=1
            """
            
            # 添加分类筛选
            if category != 'all':
                query += " AND category = %s"
                params = [category]
            else:
                params = []
                
            # 添加时间范围
            query += " AND created_at >= DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)"
            params.append(time_range)
            
            # 分组和排序
            query += " GROUP BY education_level ORDER BY count DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # 过滤掉"其他"类别
            filtered_results = [row for row in results if row['education_level'] != '其他']
            
            return jsonify({
                'success': True,
                'data': [{
                    'name': row['education_level'],
                    'value': row['count']
                } for row in filtered_results]
            })
            
    except Exception as e:
        print(f"获取学历分布数据错误: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'db' in locals():
            db.close()

@app.route('/api/job-analysis/experience-distribution', methods=['GET'])
def get_experience_distribution():
    try:
        category = request.args.get('category', 'all')
        time_range = request.args.get('time_range', '30')
        
        db = get_db()
        with db.cursor() as cursor:
            # 基础查询
            query = """
                SELECT 
                    CASE 
                        WHEN experience REGEXP '3-5年|3到5年|三到五年' THEN '3-5年'
                        WHEN experience REGEXP '1-3年|1到3年|一到三年' THEN '1-3年'
                        WHEN experience REGEXP '不限|不要求|经验不限' THEN '经验不限'
                        WHEN experience REGEXP '5-10年|5到10年|五到十年' THEN '5-10年'
                        WHEN experience REGEXP '1年以内|一年以内|应届|实习|在校' THEN '一年以内'
                        WHEN experience REGEXP '应届|在校|实习生' THEN '在校/应届'
                        WHEN experience REGEXP '10年以上|十年以上' THEN '10年以上'
                        ELSE '其他'
                    END as experience_level,
                    COUNT(*) as count
                FROM jobs
                WHERE 1=1
            """
            
            # 添加分类筛选
            if category != 'all':
                query += " AND category = %s"
                params = [category]
            else:
                params = []
                
            # 添加时间范围
            query += " AND created_at >= DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)"
            params.append(time_range)
            
            # 分组和排序
            query += " GROUP BY experience_level ORDER BY count DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # 过滤掉"其他"类别
            filtered_results = [row for row in results if row['experience_level'] != '其他']
            
            return jsonify({
                'success': True,
                'data': [{
                    'name': row['experience_level'],
                    'value': row['count']
                } for row in filtered_results]
            })
            
    except Exception as e:
        print(f"获取工作经验分布数据错误: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'db' in locals():
            db.close()

@app.route('/resume', methods=['GET'])
@login_required
def resume():
    form = ResumeForm()
    # 从数据库获取已保存的简历数据
    user_resume = users.get(session['user_id'], {}).get('resume', {})
    
    # 填充表单数据
    if user_resume:
        form.name.data = user_resume.get('name')
        form.age.data = user_resume.get('age')
        form.education.data = user_resume.get('education')
    
    return render_template('resume.html', 
                         form=form,
                         education_list=user_resume.get('education_list', []),
                         experience_list=user_resume.get('experience_list', []),
                         project_list=user_resume.get('project_list', []),
                         user=session.get('user_id'))

@app.route('/save_resume', methods=['POST'])
@login_required
def save_resume():
    form = ResumeForm()
    if form.validate_on_submit():
        # 获取表单数据
        resume_data = {
            'name': form.name.data,
            'age': form.age.data,
            'education': form.education.data,
            'education_list': [],
            'experience_list': [],
            'project_list': []
        }
        
        # 获取教育经历
        schools = request.form.getlist('school[]')
        majors = request.form.getlist('major[]')
        degrees = request.form.getlist('degree[]')
        edu_times = request.form.getlist('edu_time[]')
        
        for i in range(len(schools)):
            if schools[i]:  # 只保存非空条目
                resume_data['education_list'].append({
                    'school': schools[i],
                    'major': majors[i],
                    'degree': degrees[i],
                    'time': edu_times[i]
                })
        
        # 获取工作经历
        companies = request.form.getlist('company[]')
        positions = request.form.getlist('position[]')
        exp_times = request.form.getlist('exp_time[]')
        descriptions = request.form.getlist('description[]')
        
        for i in range(len(companies)):
            if companies[i]:
                resume_data['experience_list'].append({
                    'company': companies[i],
                    'position': positions[i],
                    'time': exp_times[i],
                    'description': descriptions[i]
                })
        
        # 获取项目经历
        project_names = request.form.getlist('project_name[]')
        project_roles = request.form.getlist('project_role[]')
        project_times = request.form.getlist('project_time[]')
        project_descriptions = request.form.getlist('project_description[]')
        
        for i in range(len(project_names)):
            if project_names[i]:
                resume_data['project_list'].append({
                    'name': project_names[i],
                    'role': project_roles[i],
                    'time': project_times[i],
                    'description': project_descriptions[i]
                })
        
        # 保存到用户数据中
        if session['user_id'] not in users:
            users[session['user_id']] = {}
        users[session['user_id']]['resume'] = resume_data
        
        flash('简历保存成功')
        return redirect(url_for('resume'))
    
    flash('表单验证失败，请检查输入')
    return redirect(url_for('resume'))

@app.route('/mock-interview')
@login_required
def mock_interview():
    return render_template('mock_interview.html', user=session.get('user_id'))

# 配置上传文件存储路径
UPLOAD_FOLDER = os.path.join('static', 'avatars')  # 修改为正确的相对路径
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制文件大小为16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    try:
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if file and allowed_file(file.filename):
            # 确保上传目录存在
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            # 生成安全的文件名
            filename = secure_filename(f"{session['user_id']}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 保存文件
            file.save(file_path)
            
            # 确保用户数据结构存在
            user_id = session['user_id']
            if user_id not in users:
                users[user_id] = {}
            
            # 更新用户头像信息
            users[user_id]['avatar'] = filename
            
            # 返回新的头像URL
            avatar_url = url_for('static', filename=f'avatars/{filename}')
            print(f"Avatar saved to: {file_path}")  # 添加调试日志
            return jsonify({
                'success': True,
                'avatar_url': avatar_url
            })
        
        return jsonify({'success': False, 'message': '不支持的文件类型'})
    
    except Exception as e:
        print(f"Upload error: {str(e)}")  # 添加错误日志
        return jsonify({'success': False, 'message': f'上传失败：{str(e)}'})

@app.route('/personal-center')
@login_required
def personal_center():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('请先登录')
            return redirect(url_for('login', next=request.url))
            
        db = get_db()
        with db.cursor() as cursor:
            # 获取用户基本信息
            cursor.execute("""
                SELECT username, telephone 
                FROM users 
                WHERE username = %s
            """, (user_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                session.clear()
                flash('用户不存在')
                return redirect(url_for('login'))
                
            # 获取用户的求职意向
            cursor.execute("""
                SELECT * FROM job_intentions 
                WHERE user_id = (SELECT id FROM users WHERE username = %s)
            """, (user_id,))
            job_intention = cursor.fetchone() or {}
            
            # 获取收藏的职位
            cursor.execute("""
                SELECT j.* 
                FROM jobs j 
                JOIN saved_jobs s ON j.id = s.job_id 
                WHERE s.user_id = (SELECT id FROM users WHERE username = %s)
            """, (user_id,))
            saved_jobs = cursor.fetchall() or []
            
            # 获取投递记录
            cursor.execute("""
                SELECT j.*, a.status, a.created_at as apply_time 
                FROM jobs j 
                JOIN job_applications a ON j.id = a.job_id 
                WHERE a.user_id = (SELECT id FROM users WHERE username = %s)
                ORDER BY a.created_at DESC
            """, (user_id,))
            applied_jobs = cursor.fetchall() or []
            
            return render_template('personal_center.html',
                                user=user_id,
                                telephone=user_data['telephone'],
                                saved_jobs=saved_jobs,
                                applied_jobs=applied_jobs,
                                job_intention=job_intention,
                                password_form=ChangePasswordForm(),
                                cities=CITIES)
                                
    except Exception as e:
        print(f"个人中心错误: {str(e)}")
        flash('加载个人中心失败，请重试')
        return redirect(url_for('index'))
    finally:
        if 'db' in locals():
            db.close()

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user_id = session.get('user_id')
        current_password = form.current_password.data
        new_password = form.new_password.data
        
        # 验证当前密码是否正确
        if check_password_hash(users[user_id]['password'], current_password):
            # 更新密码
            users[user_id]['password'] = generate_password_hash(new_password)
            flash('密码修改成功')
        else:
            flash('当前密码不正确')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}")
    
    return redirect(url_for('personal_center'))

@app.route('/apply-job/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    # 这里添加申请职位的逻辑
    return jsonify({'success': True, 'message': '申请成功'})

@app.route('/save-job/<int:job_id>', methods=['POST'])
@login_required
def save_job(job_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'})
            
        db = get_db()
        with db.cursor() as cursor:
            # 获取用户ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (user_id,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify({'success': False, 'message': '用户不存在'})
            
            user_db_id = user_result['id']
            
            # 检查职位是否存在
            cursor.execute("SELECT id FROM jobs WHERE id = %s", (job_id,))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': '职位不存在'})
            
            # 检查是否已经收藏
            cursor.execute("""
                SELECT id FROM saved_jobs 
                WHERE user_id = %s AND job_id = %s
            """, (user_db_id, job_id))
            
            if cursor.fetchone():
                return jsonify({'success': False, 'message': '已收藏该职位'})
            
            # 添加收藏
            cursor.execute("""
                INSERT INTO saved_jobs (user_id, job_id) 
                VALUES (%s, %s)
            """, (user_db_id, job_id))
            
            db.commit()
            return jsonify({'success': True, 'message': '收藏成功'})
            
    except Exception as e:
        print(f"收藏职位错误: {str(e)}")
        return jsonify({'success': False, 'message': f'收藏失败：{str(e)}'})
    finally:
        if 'db' in locals():
            db.close()

@app.route('/unsave-job/<int:job_id>', methods=['POST'])
@login_required
def unsave_job(job_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'})
            
        db = get_db()
        with db.cursor() as cursor:
            # 获取用户ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (user_id,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify({'success': False, 'message': '用户不存在'})
            
            user_db_id = user_result['id']
            
            # 检查是否存在该收藏
            cursor.execute("""
                SELECT id FROM saved_jobs 
                WHERE user_id = %s AND job_id = %s
            """, (user_db_id, job_id))
            
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': '未找到该收藏记录'})
            
            # 删除收藏
            cursor.execute("""
                DELETE FROM saved_jobs 
                WHERE user_id = %s AND job_id = %s
            """, (user_db_id, job_id))
            
            db.commit()
            return jsonify({'success': True, 'message': '取消收藏成功'})
            
    except Exception as e:
        print(f"取消收藏错误: {str(e)}")
        return jsonify({'success': False, 'message': f'取消收藏失败：{str(e)}'})
    finally:
        if 'db' in locals():
            db.close()

@app.route('/save-job-intention', methods=['POST'])
@login_required
def save_job_intention():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'})
        
        # 获取表单数据
        data = request.get_json()
        desired_position = data.get('desired_position')
        desired_city = data.get('desired_city')
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        job_type = data.get('job_type')
        available_time = data.get('available_time')
        
        db = get_db()
        with db.cursor() as cursor:
            # 获取用户ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (user_id,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify({'success': False, 'message': '用户不存在'})
            
            user_db_id = user_result['id']
            
            # 检查是否已存在求职意向
            cursor.execute("SELECT id FROM job_intentions WHERE user_id = %s", (user_db_id,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute("""
                    UPDATE job_intentions 
                    SET desired_position = %s,
                        desired_city = %s,
                        salary_min = %s,
                        salary_max = %s,
                        job_type = %s,
                        available_time = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (desired_position, desired_city, salary_min, salary_max, 
                      job_type, available_time, user_db_id))
            else:
                # 创建新记录
                cursor.execute("""
                    INSERT INTO job_intentions 
                    (user_id, desired_position, desired_city, salary_min, salary_max, 
                     job_type, available_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_db_id, desired_position, desired_city, salary_min, 
                      salary_max, job_type, available_time))
            
            db.commit()
            return jsonify({'success': True, 'message': '求职意向保存成功'})
            
    except Exception as e:
        print(f"保存求职意向错误: {str(e)}")
        return jsonify({'success': False, 'message': f'保存失败：{str(e)}'})
    finally:
        if 'db' in locals():
            db.close()

# 更新API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-322ad34d33b543e28c9df737595c5638')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # 完整的API端点

# 面试相关的系统提示词
TECH_INTERVIEW_PROMPT = """你是一位专业的技术面试官，根据应聘者选择的岗位和难度级别进行技术面试。
请遵循以下规则：
1. 根据岗位和难度提供相应水平的技术问题
2. 对应聘者的回答进行专业点评
3. 循序渐进地深入提问
4. 在面试结束时提供完整的评估报告
"""

HR_INTERVIEW_PROMPT = """你是一位经验丰富的HR面试官，负责考察候选人的综合素质。
请遵循以下规则：
1. 提供针对性的HR问题，包括个人经历、职业规划等
2. 考察候选人的沟通能力和职业素养
3. 根据回答进行追问
4. 在面试结束时提供完整的评估报告
"""

@app.route('/start-interview', methods=['POST'])
@login_required
def start_interview():
    try:
        data = request.json
        interview_type = data.get('type')
        position = data.get('position')
        difficulty = data.get('difficulty')
        
        try:
            response = get_ai_response(
                TECH_INTERVIEW_PROMPT if interview_type == 'tech' else HR_INTERVIEW_PROMPT,
                f"开始{position}岗位的面试，难度级别：{difficulty}。请提出第一个问题。"
            )
        except Exception as e:
            print(f"API调用失败，使用备用响应: {str(e)}")
            response = get_fallback_response(interview_type, position, difficulty)
        
        return jsonify({
            'success': True,
            'message': response
        })
        
    except Exception as e:
        print(f"Interview start error: {str(e)}")
        return jsonify({
            'success': False,
            'message': '开始面试失败，请稍后重试'
        })

@app.route('/interview-next', methods=['POST'])
@login_required
def interview_next():
    try:
        data = request.json
        interview_type = data.get('type')
        answer = data.get('answer')
        history = data.get('history', [])
        
        # 构建提示词
        prompt = f"""
        你是一位{'技术' if interview_type == 'tech' else 'HR'}面试官。
        面试历史记录：
        {format_history(history)}
        
        应聘者刚刚的回答是：{answer}
        
        请：
        1. 简要点评这个回答（1-2句话）
        2. 根据回答情况，提出下一个相关的问题
        3. 确保问题难度循序渐进
        4. 直接给出点评和问题，不要有多余的话
        """
        
        try:
            response = get_ai_response(
                TECH_INTERVIEW_PROMPT if interview_type == 'tech' else HR_INTERVIEW_PROMPT,
                prompt
            )
        except Exception as e:
            # 如果API调用失败，使用备用响应
            response = get_fallback_next_question(interview_type, answer)
        
        return jsonify({
            'success': True,
            'message': response
        })
        
    except Exception as e:
        print(f"Interview next error: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取下一个问题失败，请重试'
        })

def format_history(history):
    """格式化面试历史记录"""
    formatted = []
    for item in history:
        role = "面试官" if item['role'] == 'assistant' else "应聘者"
        formatted.append(f"{role}：{item['content']}")
    return "\n".join(formatted)

def get_fallback_next_question(interview_type, answer):
    """当API调用失败时的备用问题"""
    if interview_type == 'tech':
        return """
        感谢您的回答。接下来请问：
        您在实际项目中遇到过哪些技术难题？是如何解决的？
        """
    else:
        return """
        明白了。下一个问题：
        您对未来的职业规划是怎样的？3-5年内有什么具体目标？
        """

@app.route('/end-interview', methods=['POST'])
@login_required
def end_interview():
    data = request.json
    interview_type = data.get('type')
    history = data.get('history', [])
    
    system_prompt = TECH_INTERVIEW_PROMPT if interview_type == 'tech' else HR_INTERVIEW_PROMPT
    
    try:
        # 调用Deepseek API生成评估报告
        response = get_ai_response(system_prompt, f"""
        面试历史：{json.dumps(history, ensure_ascii=False)}
        请提供详细的面试评估报告，包括以下方面：
        1. 整体表现评分（满分100分）
        2. 优势分析
        3. 不足之处
        4. 改进建议
        """)
        
        return jsonify({
            'success': True,
            'evaluation': response
        })
    except Exception as e:
        print(f"Interview end error: {str(e)}")
        return jsonify({
            'success': False,
            'evaluation': '生成评估报告失败，请重试'
        })

def get_ai_response(system_prompt, user_message):
    """调用Deepseek API获取回复"""
    try:
        # 准备请求数据
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 发送请求
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # 打印调试信息
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.text}")
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            # 如果API调用失败，使用备用响应
            raise Exception(f"API返回错误: {response.status_code}")
            
    except Exception as e:
        print(f"Error in get_ai_response: {str(e)}")
        raise

# 添加备用响应
def get_fallback_response(interview_type, position, difficulty=None):
    """当API调用失败时返回预设的面试问题"""
    if interview_type == 'tech':
        questions = {
            'frontend': '请详细介绍一下你在前端开发中使用过的框架和技术栈。',
            'backend': '请解释一下什么是RESTful API，以及它的主要设计原则。',
            'algorithm': '请讲解一下常见的排序算法及其时间复杂度。',
            'data': '请介绍一下你使用过的数据分析工具和方法。',
            'product': '请分享一个你参与过的产品设计案例。'
        }
        return questions.get(position, '请介绍一下你的技术背景和项目经验。')
    else:
        return '请简单介绍一下你自己，以及为什么选择应聘这个职位？'

# 可选：添加对话历史记录功能
chat_histories = {}

def save_chat_history(user_id, message, response):
    """保存聊天历史"""
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    
    chat_histories[user_id].append({
        'timestamp': datetime.now().isoformat(),
        'user_message': message,
        'ai_response': response
    })

def get_chat_history(user_id, limit=10):
    """获取用户的聊天历史"""
    return chat_histories.get(user_id, [])[-limit:]

@app.route('/test-db')
def test_db():
    try:
        db = get_db()
        if not db:
            return jsonify({
                'success': False,
                'message': '数据库连接失败'
            })
            
        with db.cursor() as cursor:
            # 测试查询users表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            # 测试插入数据
            try:
                cursor.execute("""
                    INSERT INTO users (username, password, telephone) 
                    VALUES (%s, %s, %s)
                """, ('test_user', '123456', '13800138000'))
                db.commit()
                
                # 查询刚插入的数据
                cursor.execute("SELECT * FROM users WHERE username = 'test_user'")
                user = cursor.fetchone()
                
                
            except Exception as e:
                db.rollback()
                return jsonify({
                    'success': False,
                    'message': f'数据操作失败: {str(e)}',
                    'tables': [table['Tables_in_job_platform'] for table in tables]
                })
            
        db.close()
        return jsonify({
            'success': True,
            'message': '数据库连接测试成功',
            'tables': [table['Tables_in_job_platform'] for table in tables],
            'test_user': user
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'测试过程中出错: {str(e)}'
        })

def calculate_job_similarity(job_intention, job):
    """计算职位相似度的辅助函数"""
    similarity_score = 0
    
    # 职位名称匹配
    if job_intention['desired_position']:
        # 将职位名称转换为小写进行比较
        desired_position = job_intention['desired_position'].lower()
        job_title = job['title'].lower()
        
        # 检查职位名称是否匹配
        if (desired_position in job_title or 
            job_title in desired_position):
            similarity_score += 0.4
        # 检查标签是否匹配
        elif job['tags']:
            for tag in job['tags']:
                if desired_position in tag.lower():
                    similarity_score += 0.4
                    break
    
    # 城市匹配
    if job_intention['desired_city'] == job['location'] or job_intention['desired_city'] == '全国':
        similarity_score += 0.2
    
    # 工作类型匹配
    if job_intention['job_type'] == job['job_type']:
        similarity_score += 0.2
    
    # 薪资匹配
    if job_intention['salary_min'] and job_intention['salary_max']:
        try:
            # 处理职位薪资
            job_salary = job['salary'].lower()
            # 移除所有非数字和'-'的字符
            job_salary = ''.join(c for c in job_salary if c.isdigit() or c == '-')
            
            # 如果包含'-'，说明是范围格式
            if '-' in job_salary:
                job_min, job_max = map(int, job_salary.split('-'))
                # 检查薪资范围是否有重叠
                if (job_min <= job_intention['salary_max'] and 
                    job_max >= job_intention['salary_min']):
                    similarity_score += 0.2
            # 如果是单个数字，就用它作为最小值和最大值
            elif job_salary.isdigit():
                job_value = int(job_salary)
                if (job_value >= job_intention['salary_min'] and 
                    job_value <= job_intention['salary_max']):
                    similarity_score += 0.2
        except (ValueError, AttributeError):
            # 如果薪资解析失败，不增加相似度分数
            pass
    
    return similarity_score

@app.route('/recommend-jobs', methods=['GET'])
@login_required
def recommend_jobs():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'})
        
        db = get_db()
        with db.cursor() as cursor:
            # 获取用户ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (user_id,))
            user_result = cursor.fetchone()
            if not user_result:
                return jsonify({'success': False, 'message': '用户不存在'})
            
            user_db_id = user_result['id']
            
            # 获取用户的求职意向
            cursor.execute("""
                SELECT * FROM job_intentions 
                WHERE user_id = %s
            """, (user_db_id,))
            job_intention = cursor.fetchone()
            
            if not job_intention:
                return jsonify({
                    'success': False, 
                    'message': '请先设置求职意向'
                })
            
            # 获取所有职位
            cursor.execute("""
                SELECT j.*, GROUP_CONCAT(t.tag) as tags
                FROM jobs j
                LEFT JOIN job_tags t ON j.id = t.job_id
                GROUP BY j.id
            """)
            all_jobs = cursor.fetchall()
            
            # 计算每个职位的相似度得分
            job_scores = []
            for job in all_jobs:
                # 转换tags字符串为列表
                job['tags'] = job['tags'].split(',') if job['tags'] else []
                
                # 计算相似度得分
                similarity = calculate_job_similarity(job_intention, job)
                job_scores.append((job, similarity))
            
            # 按相似度得分排序
            job_scores.sort(key=lambda x: x[1], reverse=True)
            
            # 获取前10个最相似的职位
            recommended_jobs = [job for job, score in job_scores[:10]]
            
            return jsonify({
                'success': True,
                'jobs': recommended_jobs
            })
            
    except Exception as e:
        print(f"推荐职位错误: {str(e)}")
        return jsonify({'success': False, 'message': f'获取推荐失败：{str(e)}'})
    finally:
        if 'db' in locals():
            db.close()

@app.route('/api/job-analysis/city-distribution', methods=['GET'])
def get_city_distribution():
    try:
        time_range = request.args.get('time_range', '30')
        
        db = get_db()
        with db.cursor() as cursor:
            # 基础查询
            query = """
                SELECT 
                    CASE 
                        WHEN location IN ('北京', '上海', '广州', '深圳', '杭州', '天津', '西安', 
                                        '苏州', '武汉', '厦门', '长沙', '成都', '郑州', '重庆') 
                        THEN location 
                        ELSE '其他城市'
                    END as city,
                    COUNT(*) as count
                FROM jobs
                WHERE created_at >= DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)
                GROUP BY 
                    CASE 
                        WHEN location IN ('北京', '上海', '广州', '深圳', '杭州', '天津', '西安', 
                                        '苏州', '武汉', '厦门', '长沙', '成都', '郑州', '重庆') 
                        THEN location 
                        ELSE '其他城市'
                    END
                ORDER BY count DESC
            """
            
            cursor.execute(query, [time_range])
            results = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'data': [{
                    'name': row['city'],
                    'value': row['count']
                } for row in results]
            })
            
    except Exception as e:
        print(f"获取城市分布数据错误: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if 'db' in locals():
            db.close()

@app.route('/api/job-analysis/benefits-wordcloud', methods=['GET'])
def get_benefits_wordcloud():
    try:
        time_range = request.args.get('time_range', '30')
        category = request.args.get('category', 'all')
        
        db = get_db()
        with db.cursor() as cursor:
            query = """
                SELECT description
                FROM jobs
                WHERE created_at >= DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)
            """
            params = [time_range]
            
            if category != 'all':
                query += " AND category = %s"
                params.append(category)
                
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # 提取福利相关词汇
            benefits_keywords = ['五险一金', '补充医疗', '年终奖', '带薪年假', '加班补助', '餐补', '交通补助', 
                               '住房补贴', '通讯补贴', '节日福利', '团建', '下午茶', '免费班车', '股票期权',
                               '弹性工作', '免费工作餐', '定期体检', '零食下午茶', '补充公积金', '子女教育']
            
            benefit_counts = {}
            for row in results:
                description = row['description'].lower() if row['description'] else ''
                for keyword in benefits_keywords:
                    if keyword in description:
                        benefit_counts[keyword] = benefit_counts.get(keyword, 0) + 1
            
            # 转换为词云数据格式
            wordcloud_data = [{'name': k, 'value': v} for k, v in benefit_counts.items()]
            
            return jsonify({
                'success': True,
                'data': wordcloud_data
            })
            
    except Exception as e:
        print('Error:', str(e))
        return jsonify({
            'success': False,
            'message': '获取福利数据失败'
        })

if __name__ == '__main__':
    app.run(debug=True) 