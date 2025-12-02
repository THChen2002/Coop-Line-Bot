# -*- coding: utf-8 -*-
"""API Blueprint - RESTful API endpoints"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from services.firebase_service import firebase_service
from services.todo_service import TodoService

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 初始化服務
todo_service = TodoService()


# ===== 群組 API =====

@api_bp.route("/groups/<group_id>/members", methods=['GET'])
def get_group_members(group_id):
    """取得群組成員 API"""
    try:
        members_dict = firebase_service.get_group_members(group_id)

        # 轉換為列表格式
        members = []
        for user_id, member_data in members_dict.items():
            members.append({
                'id': user_id,
                'name': member_data.get('display_name', '未知')
            })

        return jsonify({
            'success': True,
            'members': members
        })
    except Exception as e:
        logger.error(f"取得群組成員失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== 支出 API =====

@api_bp.route("/expenses", methods=['POST'])
def create_expense():
    """建立支出記錄 API"""
    try:
        data = request.json

        # 驗證必要欄位
        required_fields = ['group_id', 'payer_id', 'payer_name', 'amount', 'description', 'splits']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要欄位: {field}'
                }), 400

        # 建立支出記錄
        expense_id = firebase_service.create_expense(data)

        # 取得完整記錄
        expense = firebase_service.get_expense(expense_id)

        return jsonify({
            'success': True,
            'expense_id': expense_id,
            'expense': expense
        })

    except Exception as e:
        logger.error(f"建立支出記錄失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== 待辦事項 API =====

@api_bp.route("/todos", methods=['GET', 'POST'])
def todos():
    """待辦事項列表與建立 API"""
    if request.method == 'GET':
        try:
            group_id = request.args.get('group_id')
            status = request.args.get('status')
            category = request.args.get('category')
            user_id = request.args.get('user_id')

            if not group_id:
                return jsonify({
                    'success': False,
                    'error': '缺少 group_id 參數'
                }), 400

            if user_id:
                todos_list = todo_service.get_user_todos(group_id, user_id, status)
            else:
                todos_list = todo_service.get_group_todos(group_id, status, category)

            # 轉換為字典
            todos_data = [todo.to_dict() for todo in todos_list]

            return jsonify({
                'success': True,
                'todos': todos_data
            })

        except Exception as e:
            logger.error(f"取得待辦清單失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.json

            # 驗證必要欄位
            required_fields = ['group_id', 'title']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'缺少必要欄位: {field}'
                    }), 400

            # 加入時間戳
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()

            # 建立待辦事項
            result = todo_service.create_todo(data)

            return jsonify(result)

        except Exception as e:
            logger.error(f"建立待辦事項失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@api_bp.route("/todos/<todo_id>", methods=['GET', 'PUT', 'DELETE'])
def todo_detail(todo_id):
    """單一待辦事項的取得、更新、刪除 API"""
    if request.method == 'GET':
        try:
            todo = todo_service.get_todo(todo_id)

            if not todo:
                return jsonify({
                    'success': False,
                    'error': '待辦事項不存在'
                }), 404

            return jsonify({
                'success': True,
                'todo': todo.to_dict()
            })

        except Exception as e:
            logger.error(f"取得待辦事項失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'PUT':
        try:
            updates = request.json
            updates['updated_at'] = datetime.now()

            result = todo_service.update_todo(todo_id, updates)

            return jsonify(result)

        except Exception as e:
            logger.error(f"更新待辦事項失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            result = todo_service.delete_todo(todo_id)

            return jsonify(result)

        except Exception as e:
            logger.error(f"刪除待辦事項失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@api_bp.route("/todos/<todo_id>/complete", methods=['POST'])
def complete_todo(todo_id):
    """標記待辦事項為已完成 API"""
    try:
        result = todo_service.mark_completed(todo_id)

        return jsonify(result)

    except Exception as e:
        logger.error(f"標記完成失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route("/todos/categories/<group_id>", methods=['GET'])
def get_todo_categories(group_id):
    """取得待辦事項類別列表 API"""
    try:
        categories = todo_service.get_categories(group_id)

        return jsonify({
            'success': True,
            'categories': categories
        })

    except Exception as e:
        logger.error(f"取得類別失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
