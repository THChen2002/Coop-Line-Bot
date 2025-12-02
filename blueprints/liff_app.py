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


@liff_bp.route("/<size>/expense")
def liff_expense_form(size):
    """LIFF 記帳表單頁面"""
    liff_id = LIFF.get_liff_id(size)
    group_id = request.args.get('group_id')

    logger.info(f"載入記帳表單 - group_id: {group_id}")

    # 取得群組成員資料
    members = []
    if group_id:
        try:
            members = firebase_service.get_group_members(group_id)
            logger.info(f"從 Firebase 取得成員列表: {members}")
            logger.info(f"載入 {len(members)} 位群組成員")
        except Exception as e:
            logger.error(f"取得群組成員失敗: {e}", exc_info=True)
    else:
        logger.warning("group_id 為空，無法載入成員")

    return render_template('liff/expense_form.html', liff_id=liff_id, group_id=group_id or '', members=members)


@liff_bp.route("/<size>/todo")
def liff_todo_list(size):
    """LIFF 待辦清單頁面"""
    liff_id = LIFF.get_liff_id(size)
    group_id = request.args.get('group_id')
    return render_template('liff/todo_list.html', liff_id=liff_id, group_id=group_id or '')

@liff_bp.route("/<size>/todo/form")
def liff_todo_form(size):
    """LIFF 待辦事項表單頁面"""
    liff_id = LIFF.get_liff_id(size)
    group_id = request.args.get('group_id')

    # 取得群組成員資料
    members = []
    if group_id:
        try:
            members = firebase_service.get_group_members(group_id)
            logger.info(f"載入 {len(members)} 位群組成員")
        except Exception as e:
            logger.error(f"取得群組成員失敗: {e}")

    return render_template('liff/todo_form.html', liff_id=liff_id, group_id=group_id or '', members=members)
