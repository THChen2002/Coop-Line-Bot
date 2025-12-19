# -*- coding: utf-8 -*-
"""API Blueprint - RESTful API endpoints"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from services.firebase_service import firebase_service
from services.todo_service import TodoService
from services.settlement_service import SettlementService
from utils.flex_message import FlexMessageHelper

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 初始化服務
todo_service = TodoService()
settlement_service = SettlementService()


# ===== 群組 API =====

@api_bp.route("/groups", methods=['GET', 'POST'])
def groups():
    """群組列表與建立 API"""
    if request.method == 'GET':
        try:
            user_id = request.args.get('user_id')

            if not user_id:
                return jsonify({
                    'success': False,
                    'error': '缺少 user_id 參數'
                }), 400

            # 取得使用者加入的所有群組
            groups_list = firebase_service.get_user_groups(user_id)

            return jsonify({
                'success': True,
                'groups': groups_list
            })

        except Exception as e:
            logger.error(f"取得群組列表失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.json

            # 驗證必要欄位
            required_fields = ['group_name', 'created_by']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'缺少必要欄位: {field}'
                    }), 400

            # 建立群組
            group = firebase_service.create_group(
                group_name=data['group_name'],
                created_by=data['created_by']
            )

            # 將創建者資料記錄到 users 集合
            display_name = data.get('display_name', '')
            picture_url = data.get('picture_url', '')
            if display_name:
                firebase_service.create_or_update_user(
                    line_user_id=data['created_by'],
                    display_name=display_name,
                    picture_url=picture_url
                )

            return jsonify({
                'success': True,
                'group': group
            })

        except Exception as e:
            logger.error(f"建立群組失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@api_bp.route("/groups/join", methods=['POST'])
def join_group():
    """加入群組 API"""
    try:
        data = request.json

        # 驗證必要欄位
        required_fields = ['group_code', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要欄位: {field}'
                }), 400

        # 查詢群組
        group = firebase_service.get_group_by_code(data['group_code'])

        if not group:
            return jsonify({
                'success': False,
                'error': '群組代碼不存在'
            }), 404

        # 檢查是否已經是成員
        if data['user_id'] in group.get('members', []):
            return jsonify({
                'success': True,
                'group': group,
                'already_member': True
            })

        # 加入群組
        success = firebase_service.join_group(group['id'], data['user_id'])

        if success:
            # 將使用者資料記錄到 users 集合
            display_name = data.get('display_name', '')
            picture_url = data.get('picture_url', '')
            if display_name:
                firebase_service.create_or_update_user(
                    line_user_id=data['user_id'],
                    display_name=display_name,
                    picture_url=picture_url
                )

            return jsonify({
                'success': True,
                'group': group
            })
        else:
            return jsonify({
                'success': False,
                'error': '加入群組失敗'
            }), 500

    except Exception as e:
        logger.error(f"加入群組失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route("/groups/<group_id>", methods=['GET', 'DELETE'])
def group_detail(group_id):
    """群組詳細資訊 API"""
    if request.method == 'GET':
        """取得群組資訊

        支援兩種查詢方式：
        - 透過 group_id: /api/groups/<group_id>
        - 透過 group_code: /api/groups/<group_code>?by=code
        """
        try:
            by = request.args.get('by')
            user_id = request.args.get('user_id')

            if by == 'code':
                # 透過 group_code 查詢
                group = firebase_service.get_group_by_code(group_id)
            else:
                # 透過 group_id 查詢
                group = firebase_service.get(collection='groups', doc_id=group_id)

            if not group:
                return jsonify({
                    'success': False,
                    'error': '群組不存在'
                }), 404

            # 檢查是否已經是成員
            is_member = user_id and user_id in group.get('members', [])

            return jsonify({
                'success': True,
                'group': group,
                'is_member': is_member
            })

        except Exception as e:
            logger.error(f"取得群組失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        """刪除群組及其所有相關資料"""
        try:
            # 先檢查群組是否存在
            group = firebase_service.get(collection='groups', doc_id=group_id)

            if not group:
                return jsonify({
                    'success': False,
                    'error': '群組不存在'
                }), 404

            # 刪除群組及其所有相關資料
            success = firebase_service.delete_group(group_id)

            if success:
                return jsonify({
                    'success': True,
                    'message': '群組已刪除'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '刪除群組失敗'
                }), 500

        except Exception as e:
            logger.error(f"刪除群組失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@api_bp.route("/groups/<group_id>/members", methods=['GET'])
def get_group_members(group_id):
    """取得群組成員 API"""
    try:
        # 取得群組資料
        group = firebase_service.get(collection='groups', doc_id=group_id)

        if not group:
            return jsonify({
                'success': False,
                'error': '群組不存在'
            }), 404

        member_ids = group.get('members', [])
        members = []

        # 從 users 集合取得每個成員的詳細資料
        for user_id in member_ids:
            user = firebase_service.get_user(user_id)
            if user:
                members.append({
                    'id': user_id,
                    'name': user.get('display_name', '未知用戶'),
                    'picture_url': user.get('picture_url', '')
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

@api_bp.route("/groups/<group_id>/expenses", methods=['GET', 'POST'])
def expenses(group_id):
    """支出記錄列表與建立 API"""
    if request.method == 'GET':
        try:
            # 支援三種模式：
            # - 不傳 is_settled 參數：回傳所有帳目（None）
            # - is_settled=true：只回傳已結算
            # - is_settled=false：只回傳未結算
            is_settled_param = request.args.get('is_settled')
            if is_settled_param is not None:
                is_settled = is_settled_param.lower() == 'true'
            else:
                is_settled = None  # 不過濾，取得所有帳目

            if not group_id:
                return jsonify({
                    'success': False,
                    'error': '缺少 group_id 參數'
                }), 400

            # 取得群組的支出記錄
            expenses_list = firebase_service.get_group_expenses(group_id, is_settled)

            return jsonify({
                'success': True,
                'expenses': expenses_list
            })

        except Exception as e:
            logger.error(f"取得支出記錄失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'POST':
        try:
            data = request.json
            # 確保 group_id 一致
            data['group_id'] = group_id

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

            # 建立 Flex Message bubble 供前端使用
            flex_bubble = FlexMessageHelper.create_expense_success(
                expense=expense,
                splits=expense.get('splits', []),
                is_edit=False
            )

            return jsonify({
                'success': True,
                'expense_id': expense_id,
                'expense': expense,
                'flexBubble': flex_bubble
            })

        except Exception as e:
            logger.error(f"建立支出記錄失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@api_bp.route("/expenses/<expense_id>", methods=['GET', 'PUT', 'DELETE'])
def expense_detail(expense_id):
    """單一支出記錄的取得、更新、刪除 API"""
    if request.method == 'GET':
        try:
            expense = firebase_service.get_expense(expense_id)

            if not expense:
                return jsonify({
                    'success': False,
                    'error': '支出記錄不存在'
                }), 404

            return jsonify({
                'success': True,
                'expense': expense
            })

        except Exception as e:
            logger.error(f"取得支出記錄失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'PUT':
        try:
            updates = request.json

            # 更新支出記錄
            success = firebase_service.update(
                collection='expenses',
                doc_id=expense_id,
                data=updates
            )

            if success:
                # 取得更新後的記錄
                expense = firebase_service.get_expense(expense_id)

                # 建立 Flex Message bubble 供前端使用
                flex_bubble = FlexMessageHelper.create_expense_success(
                    expense=expense,
                    splits=expense.get('splits', []),
                    is_edit=True
                )

                return jsonify({
                    'success': True,
                    'expense': expense,
                    'flexBubble': flex_bubble
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '更新支出記錄失敗'
                }), 500

        except Exception as e:
            logger.error(f"更新支出記錄失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            # 先取得要刪除的記錄（刪除後就取不到了）
            expense = firebase_service.get_expense(expense_id)

            if not expense:
                return jsonify({
                    'success': False,
                    'error': '支出記錄不存在'
                }), 404

            # 刪除記錄
            success = firebase_service.delete_expense(expense_id)
            import json
            if success:
                # 建立刪除通知的 Flex Message bubble
                flex_bubble = FlexMessageHelper.create_expense_deleted_message(expense)
                logger.info(f"flex_bubble: {json.dumps(flex_bubble, ensure_ascii=False)}")

                return jsonify({
                    'success': True,
                    'message': '支出記錄已刪除',
                    'expense': expense,
                    'flexBubble': flex_bubble
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '刪除支出記錄失敗'
                }), 500

        except Exception as e:
            logger.error(f"刪除支出記錄失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


# ===== 待辦事項 API =====

@api_bp.route("/groups/<group_id>/todos", methods=['GET', 'POST'])
def todos(group_id):
    """待辦事項列表與建立 API"""
    if request.method == 'GET':
        try:
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
            # 確保 group_id 一致
            data['group_id'] = group_id

            # 驗證必要欄位
            required_fields = ['group_id', 'title']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'缺少必要欄位: {field}'
                    }), 400

            # 建立待辦事項(時間戳由 Service 層設置)
            result = todo_service.create_todo(data)

            if not result.get('success'):
                return jsonify(result), 500

            todo_id = result.get('todo_id')
            todo_obj = todo_service.get_todo(todo_id) if todo_id else None
            todo_dict = todo_obj.to_dict() if todo_obj else None

            flex_bubble = None
            if todo_dict:
                flex_bubble = FlexMessageHelper.create_todo_action_bubble(todo_dict, action='created')

            return jsonify({
                'success': True,
                'todo_id': todo_id,
                'todo': todo_dict,
                'flexBubble': flex_bubble
            })

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

            if not result.get('success'):
                return jsonify(result), 500

            todo_obj = todo_service.get_todo(todo_id)
            todo_dict = todo_obj.to_dict() if todo_obj else None
            flex_bubble = None
            if todo_dict:
                flex_bubble = FlexMessageHelper.create_todo_action_bubble(todo_dict, action='updated')

            return jsonify({
                'success': True,
                'todo': todo_dict,
                'flexBubble': flex_bubble
            })

        except Exception as e:
            logger.error(f"更新待辦事項失敗: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    elif request.method == 'DELETE':
        try:
            # 先取得待辦內容，用於建立 Flex
            todo_obj = todo_service.get_todo(todo_id)
            if not todo_obj:
                return jsonify({
                    'success': False,
                    'error': '待辦事項不存在'
                }), 404

            todo_dict = todo_obj.to_dict()

            result = todo_service.delete_todo(todo_id)

            if not result.get('success'):
                return jsonify(result), 500

            flex_bubble = FlexMessageHelper.create_todo_action_bubble(todo_dict, action='deleted')

            return jsonify({
                'success': True,
                'message': '待辦事項已刪除',
                'todo': todo_dict,
                'flexBubble': flex_bubble
            })

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


@api_bp.route("/groups/<group_id>/todos/categories", methods=['GET'])
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


# ===== 結算 API =====

@api_bp.route("/groups/<group_id>/settlement", methods=['GET'])
def get_settlement(group_id):
    """取得結算資訊 API"""
    try:
        if not group_id:
            return jsonify({
                'success': False,
                'error': '缺少 group_id 參數'
            }), 400

        # 取得未結算的支出
        expenses = firebase_service.get_group_expenses(group_id, is_settled=False)

        if not expenses:
            return jsonify({
                'success': True,
                'has_expenses': False,
                'balances': {},
                'payment_plans': [],
                'message': '目前沒有未結算的帳目'
            })

        # 計算淨收支
        balances = settlement_service.calculate_balances(expenses)

        # 計算最優化還款方案
        payment_plans = settlement_service.calculate_optimal_payments(balances)

        return jsonify({
            'success': True,
            'has_expenses': True,
            'balances': balances,
            'payment_plans': payment_plans,
            'expense_count': len(expenses)
        })

    except Exception as e:
        logger.error(f"取得結算資訊失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route("/groups/<group_id>/settlement/clear", methods=['POST'])
def clear_settlement(group_id):
    """清帳 API - 將所有帳目標記為已結算"""
    try:
        data = request.json

        # 驗證必要欄位
        required_fields = ['user_id', 'user_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要欄位: {field}'
                }), 400

        user_id = data['user_id']
        user_name = data['user_name']

        # 取得未結算的支出
        expenses = firebase_service.get_group_expenses(group_id, is_settled=False)

        if not expenses:
            return jsonify({
                'success': False,
                'error': '目前沒有未結算的帳目'
            }), 400

        count = len(expenses)

        # 計算結算資料
        balances = settlement_service.calculate_balances(expenses)
        payment_plans = settlement_service.calculate_optimal_payments(balances)

        # 建立結算記錄
        settlement_data = settlement_service.create_settlement_data(
            group_id=group_id,
            balances=balances,
            payment_plans=payment_plans,
            settled_by=user_id,
            settled_by_name=user_name
        )

        # 儲存結算記錄
        firebase_service.create_settlement(settlement_data)

        # 將所有支出標記為已結算
        firebase_service.settle_expenses(group_id)

        # 使用 FlexMessageHelper 建立結算結果的 Flex bubble，供前端 LIFF 發送
        flex_bubble = FlexMessageHelper.create_settlement_bubble(balances, payment_plans)

        return jsonify({
            'success': True,
            'message': f'已清帳 {count} 筆帳目',
            'expense_count': count,
            'flexBubble': flex_bubble
        })

    except Exception as e:
        logger.error(f"清帳失敗: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== Flex Message API =====

@api_bp.route("/flex-messages/group-invite", methods=['POST'])
def get_group_invite_flex_message():
    """取得群組邀請的 Flex Message bubble"""
    try:
        data = request.json

        # 驗證必要欄位
        required_fields = ['group_name', 'group_code', 'invite_url']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必要欄位: {field}'
                }), 400

        # 使用 FlexMessageHelper 建立 Flex Message bubble
        bubble = FlexMessageHelper.create_group_invite(
            group_name=data['group_name'],
            group_code=data['group_code'],
            invite_url=data['invite_url']
        )

        return jsonify({
            'success': True,
            'bubble': bubble
        })

    except Exception as e:
        logger.error(f"建立群組邀請 Flex Message 失敗: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
