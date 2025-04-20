from utils.query import queries
import json
import math


# def get_game_data():
#     gamelist = queries('select * from games', [], 'select')
#
#     def map_fn(item):
#         item = list(item)
#         item[4] = json.loads(item[4])
#         item[9] = json.loads(item[9])
#         item[15] = json.loads(item[15])
#         item[8] = round(float(item[8]), 1)
#         return item
#
#     gamelist = list(map(map_fn, gamelist))
#     print(gamelist)


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


import json


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

