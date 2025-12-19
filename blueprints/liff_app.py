# -*- coding: utf-8 -*-
"""LIFF Blueprint - LIFF page routes"""

from flask import Blueprint, render_template, abort, request
from utils.liff_enum import LIFF
from services.firebase_service import firebase_service
import logging

logger = logging.getLogger(__name__)

# Create blueprint
liff_bp = Blueprint('liff', __name__, url_prefix='/liff')


@liff_bp.route("/<size>")
def liff_redirect(size):
    """LIFF 動態尺寸跳轉頁面"""
    liff_id = LIFF.get_liff_id(size, default_to_tall=False)
    if not liff_id:
        abort(404)
    return render_template('liff/liff.html', liff_id=liff_id)

@liff_bp.route("/<size>/groups")
def liff_groups_list(size):
    """LIFF 群組列表頁面"""
    liff_id = LIFF.get_liff_id(size)
    return render_template('liff/groups_list.html', liff_id=liff_id)

@liff_bp.route("/<size>/groups/<group_id>")
def liff_group_detail(size, group_id):
    """LIFF 群組詳情頁面（帳目管理）"""
    liff_id = LIFF.get_liff_id(size)
    return render_template('liff/group_detail.html', liff_id=liff_id, group_id=group_id or '')

@liff_bp.route("/<size>/group/create")
def liff_group_create(size):
    """LIFF 建立群組頁面"""
    liff_id = LIFF.get_liff_id(size)
    return render_template('liff/group_create.html', liff_id=liff_id)

@liff_bp.route("/<size>/group/join")
def liff_group_join(size):
    """LIFF 加入群組頁面"""
    liff_id = LIFF.get_liff_id(size)
    group_code = request.args.get('code', '')
    return render_template('liff/group_join.html', liff_id=liff_id, group_code=group_code)

@liff_bp.route("/<size>/groups/<group_id>/settlement")
def liff_settlement(size, group_id):
    """LIFF 結算頁面"""
    liff_id = LIFF.get_liff_id(size)
    return render_template('liff/settlement.html', liff_id=liff_id, group_id=group_id or '')

@liff_bp.route("/<size>/groups/<group_id>/expense")
def liff_expense_form(size, group_id):
    """LIFF 記帳表單頁面（新增模式）"""
    liff_id = LIFF.get_liff_id(size)
    expense = None
    is_edit_mode = False

    logger.info(f"載入記帳表單 - group_id: {group_id}")

    # 取得群組成員資料
    members = []
    if group_id:
        try:
            # 取得群組資料
            group = firebase_service.get(collection='groups', doc_id=group_id)

            if group:
                member_ids = group.get('members', [])

                # 從 users 集合取得每個成員的詳細資料
                for user_id in member_ids:
                    user = firebase_service.get_user(user_id)
                    if user:
                        members.append({
                            'id': user_id,
                            'name': user.get('display_name', '未知用戶'),
                            'picture_url': user.get('picture_url', '')
                        })

                logger.info(f"載入 {len(members)} 位群組成員")
            else:
                logger.warning(f"找不到群組 {group_id}")
        except Exception as e:
            logger.error(f"取得群組成員失敗: {e}", exc_info=True)
    else:
        logger.warning("group_id 為空，無法載入成員")

    return render_template(
        'liff/expense_form.html',
        liff_id=liff_id,
        group_id=group_id or '',
        members=members,
        expense=expense,
        is_edit_mode=is_edit_mode,
        expense_id=''
    )


@liff_bp.route("/<size>/expenses/<expense_id>")
def liff_expense_edit(size, expense_id):
    """LIFF 記帳表單頁面（編輯模式）"""
    liff_id = LIFF.get_liff_id(size)
    expense = None
    is_edit_mode = True
    group_id = None

    logger.info(f"載入編輯表單 - expense_id: {expense_id}")

    # 載入支出資料
    try:
        expense = firebase_service.get_expense(expense_id)
        if expense:
            group_id = expense.get('group_id')
            logger.info(f"載入支出資料 - expense_id: {expense_id}, group_id: {group_id}")
        else:
            logger.warning(f"找不到支出記錄 - expense_id: {expense_id}")
    except Exception as e:
        logger.error(f"取得支出記錄失敗: {e}", exc_info=True)

    # 取得群組成員資料
    members = []
    if group_id:
        try:
            group = firebase_service.get(collection='groups', doc_id=group_id)
            if group:
                member_ids = group.get('members', [])
                for user_id in member_ids:
                    user = firebase_service.get_user(user_id)
                    if user:
                        members.append({
                            'id': user_id,
                            'name': user.get('display_name', '未知用戶'),
                            'picture_url': user.get('picture_url', '')
                        })
                logger.info(f"載入 {len(members)} 位群組成員")
        except Exception as e:
            logger.error(f"取得群組成員失敗: {e}", exc_info=True)

    return render_template(
        'liff/expense_form.html',
        liff_id=liff_id,
        group_id=group_id or '',
        members=members,
        expense=expense,
        is_edit_mode=is_edit_mode,
        expense_id=expense_id
    )


@liff_bp.route("/<size>/groups/<group_id>/todo")
def liff_todo_form(size, group_id):
    """LIFF 待辦事項表單頁面 (新增/編輯)"""
    liff_id = LIFF.get_liff_id(size)

    # 取得群組成員資料
    members = []
    if group_id:
        try:
            # 取得群組資料
            group = firebase_service.get(collection='groups', doc_id=group_id)

            if group:
                member_ids = group.get('members', [])

                # 從 users 集合取得每個成員的詳細資料
                for user_id in member_ids:
                    user = firebase_service.get_user(user_id)
                    if user:
                        members.append({
                            'id': user_id,
                            'name': user.get('display_name', '未知用戶'),
                            'picture_url': user.get('picture_url', '')
                        })

                logger.info(f"載入 {len(members)} 位群組成員")
            else:
                logger.warning(f"找不到群組 {group_id}")
        except Exception as e:
            logger.error(f"取得群組成員失敗: {e}")

    return render_template('liff/todo_form.html', liff_id=liff_id, group_id=group_id or '', members=members)
