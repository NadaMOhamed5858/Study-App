import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from google import genai
import markdown
app = Flask(__name__)
app.secret_key = 'malak_engineer_2026_ai_key'

# --- إعداد الذكاء الاصطناعي الحقيقي بمفتاحك ---
client = genai.Client(api_key="AIzaSyCfuCdoNDFOW8ZXkNf0MDch8jc6OAjfr4Y")
for m in client.models.list():
    print(m.name)

@app.route('/')
def index():
    if 'user_data' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['user_data'] = request.form.to_dict()
        return redirect(url_for('schedule_info'))
    return render_template('register.html')

@app.route('/schedule-info', methods=['GET', 'POST'])
def schedule_info():
    if request.method == 'POST':
        session['routine'] = request.form.to_dict()
        return redirect(url_for('exam'))
    return render_template('schedule_info.html')

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    if request.method == 'POST':
        session['bad'] = request.form.get('bad_grade_subject', 'الفيزياء')
        return redirect(url_for('dashboard'))
   
    user = session.get('user_data', {})
    return render_template('exam.html', stage=user.get('stage', 'ثانوية عامة'))

@app.route('/dashboard')
def dashboard():
    if 'user_data' not in session:
        return redirect(url_for('index'))
   
    user = session['user_data']
    bad_subject = session.get('bad', 'الفيزياء')
    today_name = datetime.now().strftime('%A')
   
    # تحويل اسم اليوم للعربية
    days_ar = {'Saturday': 'السبت', 'Sunday': 'الأحد', 'Monday': 'الاثنين', 'Tuesday': 'الثلاثاء',
               'Wednesday': 'الأربعاء', 'Thursday': 'الخميس', 'Friday': 'الجمعة'}
    today_ar = days_ar.get(today_name, today_name)
   
    # استرجاع مواعيد الدروس من السجل
    busy_time = session.get('routine', {}).get(today_ar, "لا توجد مواعيد مسجلة")

    # --- طلب المنهج والجدول من الـ AI حقيقي ---
    prompt = f"""
    بصفتك مساعد تعليمي ذكي، قم بتحليل البيانات التالية للطالبة ملاك:
    - المرحلة: {user['stage']} (منهج 2026 الجديد).
    - الحلم: {user['dream']}.
    - المادة التي تعاني فيها: {bad_subject}.
    - اليوم هو: {today_ar}.
    - هي مشغولة في دروسها في وقت: {busy_time}.
   
    المطلوب منك:
    1. حدد لها "أهم درس" تذاكره اليوم في مادة {bad_subject} من المنهج الحقيقي لعام 2026.
    2. صمم جدولاً زمنياً (من الساعة كذا للساعة كذا) للمذاكرة، مع استبعاد 8 ساعات للنوم و2 للراحة ووقت الدروس المذكور.
    3. اشرح لها "كيفية مذاكرة هذا الجزء" بأسلوب تعليمي حديث (مثل تقنية فاينمان أو الخرائط الذهنية).
    4. اكتب أهم 20 سؤالاً (Top 20) متوقعاً وشاملاً لهذا الدرس بنظام الامتحانات الجديد.
   
    اجعل الرد منظمًا جدًا، بأسلوب مشجع (ناديها يا هندسة)، واستخدم لغة عربية سليمة.
    """

    try:
        response = client.models.generate_content(model="models/gemini-2.5-flash",contents=prompt)
        ai_plan = response.text
        ai_plan_html = markdown.markdown(ai_plan,extensions=['extra', 'tables'])
    except Exception as e:
        ai_plan = f"حدث خطأ في الاتصال بالـ AI: {str(e)}"

    return render_template('dashboard.html', user=user, today=today_ar, ai_plan=ai_plan_html)

@app.route('/ask-bot', methods=['POST'])
def ask_bot():
    data = request.json
    user_msg = data.get('message', '')
    user_info = session.get('user_data', {})
   
    # المساعد الذكي يرد بذكاء كامل
    chat_prompt = f"أنت المساعد الذكي الخاص بملاك، طالبة {user_info.get('stage')} وتحلم بأن تكون {user_info.get('dream')}. رد بذكاء وعلمية على سؤالها: {user_msg}"
   
    try:
        response = client.models.generate_content(model="models/gemini-2.5-flash",contents=chat_prompt)
        reply = response.text
        
    except:
        reply = "أنا معكِ يا هندسة، لكن يبدو أن هناك ضغطاً على الشبكة. حاولي مجدداً."
       
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)