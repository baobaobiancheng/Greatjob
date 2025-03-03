from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from forms import LoginForm, RegisterForm, ResumeForm

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于session和flash消息

# 模拟用户数据库
users = {}

# 模拟职位数据
jobs = [
    {
        'id': 1,
        'title': '算法工程师',
        'salary': '25k-35k',
        'company_name': '字节跳动',
        'company_logo': 'https://example.com/bytedance-logo.png',
        'tags': ['人工智能', '机器学习', 'Python'],
        'location': '武汉',
        'experience': '1-3年',
        'education': '本科及以上'
    },
    {
        'id': 2,
        'title': '前端开发工程师',
        'salary': '20k-30k',
        'company_name': '腾讯',
        'company_logo': 'https://example.com/tencent-logo.png',
        'tags': ['Vue', 'React', 'TypeScript'],
        'location': '武汉',
        'experience': '1-3年',
        'education': '本科及以上'
    },
    # 可以添加更多职位...
]

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html', user=session.get('user_id'), jobs=jobs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        if username in users and check_password_hash(users[username]['password'], password):
            session['user_id'] = username
            flash('登录成功')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    
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
        username = form.username.data
        password = form.password.data
        phone = form.phone.data
        
        if username in users:
            flash('用户名已存在')
        else:
            users[username] = {
                'password': generate_password_hash(password),
                'phone': phone
            }
            flash('注册成功，请登录')
            return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/competitive-analysis')
@login_required
def competitive_analysis():
    return render_template('competitive_analysis.html', user=session.get('user_id'))

@app.route('/job-analysis')
@login_required
def job_analysis():
    return render_template('job_analysis.html', user=session.get('user_id'))

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

@app.route('/personal-center')
@login_required
def personal_center():
    return render_template('personal_center.html', user=session.get('user_id'))

@app.route('/apply-job/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    # 这里添加申请职位的逻辑
    return jsonify({'success': True, 'message': '申请成功'})

@app.route('/save-job/<int:job_id>', methods=['POST'])
@login_required
def save_job(job_id):
    # 这里添加收藏职位的逻辑
    return jsonify({'success': True, 'message': '收藏成功'})

if __name__ == '__main__':
    app.run(debug=True) 