from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_v2.db'
db = SQLAlchemy(app)

# 1. 이벤트(방) 모델
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False) # 이벤트 이름 (예: 엠티)
    schedules = db.relationship('Schedule', backref='event', lazy=True, cascade="all, delete-orphan")

# 2. 개별 일정 모델 (이벤트에 종속)
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 이 부분이 에러 메시지에서 찾지 못했다고 한 컬럼입니다.
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    dates = db.Column(db.String(500), nullable=False)

with app.app_context():
    db.create_all()

ALL_NAMES = ["지완", "상철", "호준", "우진", "정호", "본정", "유민"]
COLOR_MAP = {"지완": "#FF7675", "상철": "#74B9FF", "호준": "#55E6C1", "우진": "#FAD390", "정호": "#A29BFE", "본정": "#FAB1A0", "유민": "#E17055"}

# --- 경로 설정 ---

# [NEW] 첫 화면: 이벤트 목록 및 생성
@app.route('/')
def home():
    events = Event.query.all()
    return render_template('home.html', events=events)

# [NEW] 이벤트 생성 API
@app.route('/create_event', methods=['POST'])
def create_event():
    title = request.form.get('title')
    if title:
        new_event = Event(title=title)
        db.session.add(new_event)
        db.session.commit()
    return redirect(url_for('home'))

# 기존 메인 페이지: 특정 이벤트 내의 일정 현황
@app.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    schedules = Schedule.query.filter_by(event_id=event_id).all()
    
    unique_data = {s.name: set(d for d in s.dates.split(',') if d) for s in schedules}
    events_list = []
    text_list = []

    for name in ALL_NAMES:
        if name in unique_data:
            dates_set = unique_data[name]
            for d in dates_set:
                events_list.append({
                    'title': name, 'start': d,
                    'backgroundColor': COLOR_MAP.get(name, "#636e72"), 'borderColor': 'transparent'
                })
            pretty_dates = [d.split('-', 1)[1].replace('-', '/') for d in sorted(list(dates_set))]
            text_list.append({'name': name, 'dates': ", ".join(pretty_dates), 'color': COLOR_MAP.get(name)})
        
    serializable_data = {name: list(dates) for name, dates in unique_data.items()}
    return render_template('index.html', event=event, events=events_list, text_list=text_list, all_data=serializable_data, all_names=ALL_NAMES)

@app.route('/event/<int:event_id>/calendar/<name>')
def calendar(event_id, name):
    return render_template('calendar.html', event_id=event_id, name=name)

@app.route('/save_schedule', methods=['POST'])
def save_schedule():
    data = request.json
    event_id = data['event_id']
    name = data['name']
    new_dates = set(data['dates'])

    existing = Schedule.query.filter_by(event_id=event_id, name=name).first()
    if existing:
        existing.dates = ",".join(new_dates)
    else:
        db.session.add(Schedule(event_id=event_id, name=name, dates=",".join(new_dates)))
    
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/debug/reset_db')
def reset_db():
    with app.app_context():
        db.drop_all()   # 기존 테이블 강제 삭제
        db.create_all() # 새 구조로 재생성
    return "DB 초기화 완료! 이제 다시 시도해보세요."

if __name__ == '__main__':
    app.run(debug=True)