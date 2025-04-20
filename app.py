from flask import Flask, request, render_template, session, redirect, url_for, flash
import time
from utils.query import queries
from utils.get_public_data import *
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
app = Flask(__name__)
app.secret_key = "This is secret key"


@app.route('/')
def hello_world():  # put application's code here
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        request.form = dict(request.form)
        print(request.form)

        def filter_fns(item):
            return request.form['username'] in item and request.form['password'] in item

        users = queries('select * from user', [], 'select')
        login_success = list(filter(filter_fns, users))
        if not len(login_success):
            return 'Invalid username or password'

        session['username'] = request.form['username']
        return redirect('/home')

        # return render_template('./pages-login.html')
    else:
        return render_template('./pages-login.html/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        request.form = dict(request.form)
        if request.form['username'] and request.form['password'] and request.form['password_check']:
            if request.form['password'] != request.form['password_check']:
                return 'Passwords do not match'
            else:
                def filter_fns(item):
                    return request.form['username'] in item
            users = queries('select * from user', [], 'select')
            filter_list = list(filter(filter_fns, users))
            if not len(filter_list):
                queries("insert into user(username, password) values(%s,%s)",
                        [request.form['username'], request.form['password']])
            else:
                return "Username already taken"
        else:
            return "Please enter both username and password"
        return redirect('/login')
    else:
        return render_template('./pages-register.html/')


@app.route('/home', methods=['GET', 'POST'])
def home():
    username = session['username']
    # return render_template('index.html')
    # 获取搜索查询和分页参数
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))

    # 从数据库加载游戏列表
    game_list, total_pages, current_page = load_data_from_db(search_query, page)

    # 获取用户数量
    numbers_of_users = len(get_users())

    # 获取总游戏数量
    numbers_of_games = calculate_total_numbers_of_games()
    print(numbers_of_games)

    # 获取最高折扣游戏
    stats = get_game_stats()
    most_discount_game = stats['most_discounted_title']

    # 获取最常见游戏类型
    most_common_type = stats['most_common_type']

    # 获取近期上市的游戏
    recent_games = get_recent_games()

    return render_template('index.html',
                           username=username,
                           game_list=game_list,
                           recent_games=recent_games,
                           search_query=search_query,
                           total_pages=total_pages,
                           current_page=current_page,
                           numbers_of_users=numbers_of_users,
                           numbers_of_games=numbers_of_games,
                           most_discount_game=most_discount_game,
                           most_common_type=most_common_type
                           )


if __name__ == '__main__':
    app.run()
