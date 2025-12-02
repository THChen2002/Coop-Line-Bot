# -*- coding: utf-8 -*-
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction, URIAction
from utils.liff_enum import LIFF

class QuickReplyHelper:
    """Quick Reply 快速回覆工具"""

    @staticmethod
    def get_main_menu():
        """主選單 Quick Reply"""
        return QuickReply(items=[
            QuickReplyItem(
                action=MessageAction(label="📝 記帳", text="記帳選單")
            ),
            QuickReplyItem(
                action=MessageAction(label="✅ 待辦", text="待辦清單")
            ),
            QuickReplyItem(
                action=MessageAction(label="❓ 說明", text="說明")
            )
        ])

    @staticmethod
    def get_expense_menu(group_id=None):
        """記帳子選單 Quick Reply"""
        expense_url = f"https://liff.line.me/{LIFF.get_liff_id('tall')}/expense"
        if group_id:
            expense_url += f"?group_id={group_id}"
        return QuickReply(items=[
            QuickReplyItem(
                action=URIAction(label="📝 開啟表單", uri=expense_url)
            ),
            QuickReplyItem(
                action=MessageAction(label="📋 查帳目", text="帳目")
            ),
            QuickReplyItem(
                action=MessageAction(label="💰 我的帳目", text="我的帳目")
            ),
            QuickReplyItem(
                action=MessageAction(label="📊 統計", text="統計")
            ),
            QuickReplyItem(
                action=MessageAction(label="💸 結算", text="結算")
            ),
            QuickReplyItem(
                action=MessageAction(label="↩️ 返回主選單", text="主選單")
            )
        ])

    @staticmethod
    def get_settlement_menu():
        """結算選單 Quick Reply"""
        return QuickReply(items=[
            QuickReplyItem(
                action=MessageAction(label="✅ 確認清帳", text="清帳")
            ),
            QuickReplyItem(
                action=MessageAction(label="📋 查看帳目", text="帳目")
            ),
            QuickReplyItem(
                action=MessageAction(label="↩️ 返回主選單", text="主選單")
            )
        ])

    @staticmethod
    def get_query_menu():
        """查詢選單 Quick Reply"""
        return QuickReply(items=[
            QuickReplyItem(
                action=MessageAction(label="📋 所有帳目", text="帳目")
            ),
            QuickReplyItem(
                action=MessageAction(label="💰 我的帳目", text="我的帳目")
            ),
            QuickReplyItem(
                action=MessageAction(label="📊 群組統計", text="統計")
            ),
            QuickReplyItem(
                action=MessageAction(label="💸 結算", text="結算")
            ),
            QuickReplyItem(
                action=MessageAction(label="↩️ 返回主選單", text="主選單")
            )
        ])

    @staticmethod
    def get_todo_menu(group_id=None):
        """待辦清單選單 Quick Reply"""
        todo_list_url = f"https://liff.line.me/{LIFF.get_liff_id('tall')}/todo"
        todo_form_url = f"https://liff.line.me/{LIFF.get_liff_id('tall')}/todo/form"
        if group_id:
            todo_list_url += f"?group_id={group_id}"
            todo_form_url += f"?group_id={group_id}"
        return QuickReply(items=[
            QuickReplyItem(
                action=URIAction(label="➕ 新增待辦", uri=todo_form_url)
            ),
            QuickReplyItem(
                action=URIAction(label="📝 查看全部", uri=todo_list_url)
            ),
            QuickReplyItem(
                action=MessageAction(label="⏳ 待處理", text="待處理")
            ),
            QuickReplyItem(
                action=MessageAction(label="✅ 已完成", text="已完成")
            ),
            QuickReplyItem(
                action=MessageAction(label="📊 待辦統計", text="待辦統計")
            ),
            QuickReplyItem(
                action=MessageAction(label="↩️ 返回主選單", text="主選單")
            )
        ])
