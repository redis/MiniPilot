import html
import urllib
import uuid
from functools import wraps
from urllib.parse import urljoin
import requests
from flask import Blueprint, render_template, Response, request, session, stream_with_context
from langchain.memory import RedisChatMessageHistory
from src.common.config import MINIPILOT_HISTORY_TIMEOUT, REDIS_CFG
from src.common.utils import history_to_json, get_db, generate_redis_connection_string

minipilot_bp = Blueprint('minipilot_bp', __name__,
                      template_folder='./templates',
                      static_folder='./static',
                      static_url_path='/')

def minipilot_session_required(req):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # there is no session id, create one
            if session.get('minipilot_session_id') is None:
                session['minipilot_session_id'] = str(uuid.uuid4())
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@minipilot_bp.route('/')
@minipilot_session_required(request)
def landing():
    redis_history = RedisChatMessageHistory(url=generate_redis_connection_string(REDIS_CFG["host"], REDIS_CFG["port"], REDIS_CFG["password"]),
                                            session_id=session.get('minipilot_session_id'),
                                            key_prefix='minipilot:history:',
                                            ttl=MINIPILOT_HISTORY_TIMEOUT)
    return render_template('chat.html', history=history_to_json(redis_history.messages))


@minipilot_bp.route('/api')
def api():
    pass


@minipilot_bp.route('/reset', methods=['POST'])
@minipilot_session_required(request)
def reset():
    references_url = urljoin("http://localhost:5005", "api/reset")
    headers = {
        'session-id': session.get('minipilot_session_id')
    }

    response = requests.post(references_url, headers=headers, verify=False)
    return response.json(), 200


@minipilot_bp.route('/ask', methods=['GET','POST'])
@minipilot_session_required(request)
def ask():
    chat_url = urljoin("http://localhost:5005", "api/chat")
    headers = {
        'session-id': session.get('minipilot_session_id')
    }

    data = {
        'q': urllib.parse.unquote(request.form['q'])
    }

    if (len(urllib.parse.unquote(request.form['q'])) < 3):
        return Response("Please, refine your question"), 400

    if (len(urllib.parse.unquote(request.form['q'])) > 500):
        return Response("Your question is too long, please refine it"), 400

    def generate():
        answer = ""
        response = requests.post(chat_url, headers=headers, params=data, stream=True, verify=False)
        for chunk in response.iter_content(chunk_size=1024):
            answer += chunk.decode('utf-8')
            yield html.escape(chunk.decode('utf-8'))
        response.close()

    return Response(stream_with_context(generate()), content_type="text/event-stream", headers={'X-Accel-Buffering': 'no'})


@minipilot_bp.route('/logger', methods=['GET','POST'])
@minipilot_session_required(request)
def logger():
    logs = get_db(decode_responses=True).xrange("minipilot:log", "-", "+")
    return render_template('logger.html', logs=logs)


@minipilot_bp.route('/error-page')
@minipilot_session_required(request)
def custom_error():
    return render_template('500.html')
