from utils.query import queries
import json
import math
from collections import Counter, defaultdict


# 获取所有游戏数据
def get_all_games_data():
    try:
        # 查询所有游戏数据
        games_sql = """
        SELECT id, title, icon, time, compatible, evaluate, discount, 
               original_price, current_price, types, summary, 
               recentComment, allComments, firm, publisher, 
               imglist, video, detaillink
        FROM games
        ORDER BY id
        """

        games_result = queries(games_sql, [], 'select')

        if games_result and len(games_result) > 0:
            games_data = []

            for row in games_result:
                # 处理types字段，可能是JSON字符串
                types = row[9]
                if types and isinstance(types, str):
                    if types.startswith('[') and types.endswith(']'):
                        try:
                            # 替换单引号为双引号以确保有效的JSON
                            types = types.replace("'", '"')
                            types = json.loads(types)
                        except:
                            # 如果解析失败，保持原样
                            pass

                # 构建游戏数据字典
                game = {
                    'id': row[0],
                    'title': row[1],
                    'icon': row[2],
                    'time': row[3],
                    'compatible': row[4],
                    'evaluate': row[5],
                    'discount': row[6],
                    'original_price': row[7],
                    'current_price': row[8],
                    'types': types,
                    'summary': row[10],
                    'recentComment': row[11],
                    'allComments': row[12],
                    'firm': row[13],
                    'publisher': row[14],
                    'imglist': row[15],
                    'video': row[16],
                    'detaillink': row[17]
                }

                games_data.append(game)

            return games_data

        return []
    except Exception as e:
        print(f"获取游戏数据列表时出错: {e}")
        return []

# 从MySQL数据库加载游戏数据
def load_data_from_db(search_query=None, page=1, per_page=10):
    try:
        # 构建SQL查询 - 获取总记录数
        count_sql = "SELECT COUNT(*) as total FROM games"
        if search_query:
            count_sql += " WHERE title LIKE %s"
            total_records = queries(count_sql, [f'%{search_query}%'], 'select')[0][0]
        else:
            total_records = queries(count_sql, [], 'select')[0][0]

        total_pages = math.ceil(total_records / per_page)

        # 构建SQL查询 - 获取分页数据
        offset = (page - 1) * per_page
        sql = """
        SELECT id, title, icon, time, compatible, evaluate, discount, 
               original_price, current_price, types, detaillink, 
               recentComment, allComments, firm, publisher
        FROM games
        """

        # 如果有搜索查询，添加WHERE子句
        if search_query:
            sql += " WHERE title LIKE %s"
            sql += f" LIMIT {per_page} OFFSET {offset}"
            games = queries(sql, [f'%{search_query}%'], 'select')
        else:
            sql += f" LIMIT {per_page} OFFSET {offset}"
            games = queries(sql, [], 'select')

        # 将元组列表转换为字典列表
        game_list = []
        for game in games:
            game_dict = {
                'id': game[0],
                'title': game[1],
                'icon': game[2],
                'time': game[3],
                'compatible': game[4],
                'evaluate': game[5],
                'discount': game[6],
                'original_price': game[7],
                'current_price': game[8],
                'types': game[9],
                'detaillink': game[10],
                'recentComment': game[11],
                'allComments': game[12],
                'firm': game[13],
                'publisher': game[14]
            }

            # 处理游戏类型字段 - 解析JSON或处理Unicode
            if game_dict['types'] and isinstance(game_dict['types'], str):
                try:
                    # 尝试解析JSON
                    types_list = json.loads(game_dict['types'].replace("'", '"'))
                    # 确保解码Unicode
                    if isinstance(types_list, list):
                        game_dict['types'] = ', '.join(types_list)
                    else:
                        game_dict['types'] = str(types_list)
                except:
                    # 如果不是有效的JSON，尝试直接解码Unicode
                    game_dict['types'] = game_dict['types'].encode().decode('unicode_escape')

            game_list.append(game_dict)

        print(f"从数据库加载了 {len(game_list)} 条游戏数据")
        return game_list, total_pages, page
    except Exception as e:
        print(f"从数据库加载数据时出错: {e}")
        return [], 1, 1


# 获取近期上市的游戏
def get_recent_games():
    try:
        # 查询近期上市的游戏
        sql = """
        SELECT id, title, icon, time, current_price
        FROM games
        ORDER BY time DESC
        LIMIT 8
        """

        games = queries(sql, [], 'select')

        # 将元组列表转换为字典列表
        recent_games = []
        for game in games:
            game_dict = {
                'id': game[0],
                'title': game[1],
                'icon': game[2],
                'time': game[3],
                'current_price': game[4]
            }
            recent_games.append(game_dict)

        return recent_games
    except Exception as e:
        print(f"获取近期游戏时出错: {e}")
        return []


def get_users():
    user_list = queries('select * from user', [], 'select')
    return user_list


def calculate_total_numbers_of_games():
    total_number_of_games = queries('select count(*) from games', [], 'select')
    return total_number_of_games[0][0]


def get_game_stats():
    """
    获取游戏统计信息：
    1. 折扣最高的游戏标题
    2. 出现频率最高的游戏类型

    返回: 包含两个统计结果的字典
    """
    result = {
        'most_discounted_title': '',
        'most_common_type': ''
    }

    try:
        # 1. 获取折扣最高的游戏标题
        discount_sql = """
        SELECT title
        FROM games
        WHERE discount IS NOT NULL AND discount > 0
        ORDER BY discount ASC
        LIMIT 1
        """

        discount_result = queries(discount_sql, [], 'select')
        print(discount_result)
        if discount_result and len(discount_result) > 0:
            result['most_discounted_title'] = discount_result[0][0]
        else:
            result['most_discounted_title'] = "没有找到折扣游戏"

        # 2. 获取出现频率最高的游戏类型
        # 由于types是JSON数组，需要特殊处理

        # 首先获取所有非空的types数据
        types_sql = """
        SELECT types
        FROM games
        WHERE types IS NOT NULL AND types != ''
        """

        types_result = queries(types_sql, [], 'select')

        if types_result and len(types_result) > 0:
            # 创建一个字典来统计每种类型的出现次数
            type_counts = {}

            for row in types_result:
                types_str = row[0]

                try:
                    # 尝试解析JSON数组
                    # 处理可能的格式问题，有些可能是字符串形式的数组
                    if types_str.startswith('[') and types_str.endswith(']'):
                        # 替换单引号为双引号以确保有效的JSON
                        types_str = types_str.replace("'", '"')
                        types_list = json.loads(types_str)
                    else:
                        # 如果不是数组格式，将其视为单个类型
                        types_list = [types_str]

                    # 统计每种类型的出现次数
                    for game_type in types_list:
                        if game_type in type_counts:
                            type_counts[game_type] += 1
                        else:
                            type_counts[game_type] = 1

                except Exception as e:
                    print(f"解析游戏类型时出错: {e}, 数据: {types_str}")
                    continue

            # 找出出现次数最多的类型
            if type_counts:
                most_common_type = max(type_counts.items(), key=lambda x: x[1])
                result['most_common_type'] = most_common_type[0]
            else:
                result['most_common_type'] = "无法确定最常见类型"
        else:
            result['most_common_type'] = "没有找到游戏类型数据"

    except Exception as e:
        print(f"获取游戏统计信息时出错: {e}")
        result['error'] = str(e)
    return result


# 获取游戏类型分布数据
def get_game_types_distribution():
    try:
        # 获取所有非空的types数据
        types_sql = """
        SELECT types, current_price
        FROM games
        WHERE types IS NOT NULL AND types != ''
        """

        types_result = queries(types_sql, [], 'select')

        if types_result and len(types_result) > 0:
            # 创建字典来统计每种类型的出现次数和价格总和
            type_counts = {}
            type_prices = {}

            for row in types_result:
                types_str = row[0]
                price = float(row[1]) if row[1] is not None else 0

                try:
                    # 尝试解析JSON数组
                    if types_str.startswith('[') and types_str.endswith(']'):
                        # 替换单引号为双引号以确保有效的JSON
                        types_str = types_str.replace("'", '"')
                        types_list = json.loads(types_str)
                    else:
                        # 如果不是数组格式，将其视为单个类型
                        types_list = [types_str]

                    # 统计每种类型的出现次数和价格总和
                    for game_type in types_list:
                        if game_type in type_counts:
                            type_counts[game_type] += 1
                            type_prices[game_type] += price
                        else:
                            type_counts[game_type] = 1
                            type_prices[game_type] = price

                except Exception as e:
                    print(f"解析游戏类型时出错: {e}, 数据: {types_str}")
                    continue

            # 计算总游戏数量
            total_games = sum(type_counts.values())

            # 准备数据
            game_types_data = []
            for game_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                if count > 0:  # 避免除以零错误
                    avg_price = round(type_prices[game_type] / count, 2)
                    percentage = round((count / total_games) * 100, 1)

                    game_types_data.append({
                        'type': game_type,
                        'count': count,
                        'percentage': percentage,
                        'avg_price': avg_price
                    })

            # 限制为前15种类型，其余归为"其他"
            if len(game_types_data) > 15:
                top_types = game_types_data[:14]
                other_types = game_types_data[14:]

                other_count = sum(item['count'] for item in other_types)
                other_price_sum = sum(item['count'] * item['avg_price'] for item in other_types)
                other_avg_price = round(other_price_sum / other_count, 2) if other_count > 0 else 0
                other_percentage = round((other_count / total_games) * 100, 1)

                top_types.append({
                    'type': '其他',
                    'count': other_count,
                    'percentage': other_percentage,
                    'avg_price': other_avg_price
                })

                game_types_data = top_types

            # 准备饼图数据
            game_types_labels = [item['type'] for item in game_types_data]
            game_types_counts = [item['count'] for item in game_types_data]

            return game_types_data, game_types_labels, game_types_counts

        return [], [], []
    except Exception as e:
        print(f"获取游戏类型分布时出错: {e}")
        return [], [], []


# 获取游戏类型趋势数据
def get_game_types_trend():
    try:
        # 获取游戏类型和发行时间数据
        trend_sql = """
        SELECT types, time
        FROM games
        WHERE types IS NOT NULL AND types != '' AND time IS NOT NULL
        """

        trend_result = queries(trend_sql, [], 'select')

        if trend_result and len(trend_result) > 0:
            # 按年份和类型统计游戏数量
            year_type_counts = defaultdict(lambda: defaultdict(int))

            for row in trend_result:
                types_str = row[0]
                time_str = row[1]

                try:
                    # 提取年份
                    year = int(time_str.split('-')[0]) if '-' in time_str else int(time_str[:4])

                    # 解析类型
                    if types_str.startswith('[') and types_str.endswith(']'):
                        types_str = types_str.replace("'", '"')
                        types_list = json.loads(types_str)
                    else:
                        types_list = [types_str]

                    # 统计每年每种类型的游戏数量
                    for game_type in types_list:
                        year_type_counts[year][game_type] += 1

                except Exception as e:
                    print(f"处理游戏类型趋势数据时出错: {e}, 数据: {types_str}, {time_str}")
                    continue

            # 获取所有年份和类型
            all_years = sorted(year_type_counts.keys())

            # 获取出现频率最高的10种类型
            all_types = defaultdict(int)
            for year_data in year_type_counts.values():
                for game_type, count in year_data.items():
                    all_types[game_type] += count

            top_types = [t[0] for t in sorted(all_types.items(), key=lambda x: x[1], reverse=True)[:10]]

            # 准备趋势图数据
            trend_labels = [str(year) for year in all_years]
            trend_datasets = []

            # 颜色列表
            colors = [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                '#FF9F40', '#8AC249', '#EA5545', '#F46A9B', '#EF9B20'
            ]

            # 为每种类型创建数据集
            for i, game_type in enumerate(top_types):
                dataset = {
                    'label': game_type,
                    'data': [year_type_counts[year].get(game_type, 0) for year in all_years],
                    'borderColor': colors[i % len(colors)],
                    'backgroundColor': colors[i % len(colors)],
                    'fill': False,
                    'tension': 0.1
                }
                trend_datasets.append(dataset)

            return trend_labels, trend_datasets

        return [], []
    except Exception as e:
        print(f"获取游戏类型趋势时出错: {e}")
        return [], []


# 获取游戏类型组合数据
def get_game_types_combinations():
    try:
        # 获取游戏类型数据
        types_sql = """
        SELECT types
        FROM games
        WHERE types IS NOT NULL AND types != ''
        """

        types_result = queries(types_sql, [], 'select')

        if types_result and len(types_result) > 0:
            # 统计类型组合
            combinations = []

            for row in types_result:
                types_str = row[0]

                try:
                    # 解析类型
                    if types_str.startswith('[') and types_str.endswith(']'):
                        types_str = types_str.replace("'", '"')
                        types_list = json.loads(types_str)

                        # 只考虑有多个类型的游戏
                        if len(types_list) > 1:
                            # 对类型列表排序以确保一致性
                            types_list.sort()
                            # 生成所有可能的两两组合
                            for i in range(len(types_list)):
                                for j in range(i + 1, len(types_list)):
                                    combinations.append(f"{types_list[i]} + {types_list[j]}")

                except Exception as e:
                    print(f"处理游戏类型组合时出错: {e}, 数据: {types_str}")
                    continue

            # 统计组合出现次数
            combination_counter = Counter(combinations)

            # 获取前10个最常见的组合
            top_combinations = combination_counter.most_common(10)

            combination_labels = [combo[0] for combo in top_combinations]
            combination_counts = [combo[1] for combo in top_combinations]

            return combination_labels, combination_counts

        return [], []
    except Exception as e:
        print(f"获取游戏类型组合时出错: {e}")
        return [], []


# 获取游戏类型与价格、评价关系数据
def get_game_types_price_rating_relation():
    try:
        # 获取游戏类型、价格和评价数据
        relation_sql = """
        SELECT types, current_price, evaluate
        FROM games
        WHERE types IS NOT NULL AND types != '' 
          AND current_price IS NOT NULL 
          AND evaluate IS NOT NULL
        """

        relation_result = queries(relation_sql, [], 'select')

        if relation_result and len(relation_result) > 0:
            # 按类型统计价格和评价
            type_data = defaultdict(lambda: {'prices': [], 'ratings': []})

            for row in relation_result:
                types_str = row[0]
                price = float(row[1]) if row[1] is not None else 0
                rating_str = row[2]

                # 尝试解析评分
                try:
                    rating = float(rating_str) if rating_str else 0
                except:
                    rating = 0

                try:
                    # 解析类型
                    if types_str.startswith('[') and types_str.endswith(']'):
                        types_str = types_str.replace("'", '"')
                        types_list = json.loads(types_str)
                    else:
                        types_list = [types_str]

                    # 为每种类型添加价格和评分数据
                    for game_type in types_list:
                        type_data[game_type]['prices'].append(price)
                        type_data[game_type]['ratings'].append(rating)

                except Exception as e:
                    print(f"处理游戏类型关系数据时出错: {e}, 数据: {types_str}")
                    continue

            # 计算每种类型的平均价格和评分
            relation_data = {}
            for game_type, data in type_data.items():
                if data['prices'] and data['ratings']:
                    avg_price = sum(data['prices']) / len(data['prices'])
                    avg_rating = sum(data['ratings']) / len(data['ratings'])
                    relation_data[game_type] = {
                        'avg_price': avg_price,
                        'avg_rating': avg_rating,
                        'count': len(data['prices'])
                    }

            # 获取出现频率最高的15种类型
            top_types = sorted(relation_data.items(), key=lambda x: x[1]['count'], reverse=True)[:15]

            # 准备散点图数据
            colors = [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                '#FF9F40', '#8AC249', '#EA5545', '#F46A9B', '#EF9B20',
                '#EDBF33', '#87BC45', '#27AEEF', '#B33DC6', '#5D69B1'
            ]

            relation_datasets = []
            for i, (game_type, data) in enumerate(top_types):
                dataset = {
                    'label': game_type,
                    'data': [{
                        'x': data['avg_price'],
                        'y': data['avg_rating'],
                        'r': min(20, max(5, data['count'] / 10))  # 气泡大小基于游戏数量
                    }],
                    'backgroundColor': colors[i % len(colors)]
                }
                relation_datasets.append(dataset)

            return relation_datasets

        return []
    except Exception as e:
        print(f"获取游戏类型关系数据时出错: {e}")
        return []
