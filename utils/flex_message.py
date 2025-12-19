# -*- coding: utf-8 -*-
from linebot.v3.messaging import FlexMessage, FlexContainer
from typing import Dict, List
import json
from utils.liff_enum import LIFF


class FlexMessageHelper:
    """Flex Message 格式化工具 - 專業質感版"""

    # 配色方案
    COLOR_PRIMARY = "#2c3e50"    # 深藍灰 (標題)
    COLOR_ACCENT = "#3498db"     # 亮藍 (重點)
    COLOR_SUCCESS = "#27ae60"    # 綠 (成功/收入)
    COLOR_DANGER = "#c0392b"     # 紅 (危險/支出)
    COLOR_WARNING = "#f39c12"    # 橘 (警告/進行中)
    COLOR_TEXT_MAIN = "#2c3e50"  # 主要文字
    COLOR_TEXT_SUB = "#7f8c8d"   # 次要文字
    COLOR_BG_LIGHT = "#f8f9fa"   # 淺灰背景

    @staticmethod
    def _format_date(created_at, default='剛剛'):
        """格式化日期為 YYYY-MM-DD 格式
        
        支援多種日期格式：
        - datetime 物件（有 strftime 方法）
        - Firestore Timestamp 字典（有 seconds 鍵）
        - RFC 2822 字串格式（如 'Mon, 22 Dec 2025 03:52:24 GMT'）
        - ISO 格式字串
        """
        if not created_at:
            return default
        
        from datetime import datetime
        from email.utils import parsedate_to_datetime
        
        # 如果是 datetime 物件
        if hasattr(created_at, 'strftime'):
            return created_at.strftime('%Y-%m-%d')
        
        # 如果是 Firestore Timestamp 字典
        if isinstance(created_at, dict) and 'seconds' in created_at:
            return datetime.fromtimestamp(created_at['seconds']).strftime('%Y-%m-%d')
        
        # 如果是字串
        if isinstance(created_at, str):
            try:
                # 嘗試解析 RFC 2822 格式（如 'Mon, 22 Dec 2025 03:52:24 GMT'）
                dt = parsedate_to_datetime(created_at)
                return dt.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                try:
                    # 嘗試解析 ISO 格式
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    # 如果都解析失敗，返回預設值
                    return default
        
        return default

    @staticmethod
    def _create_row(label: str, value: str) -> Dict:
        """建立詳細資訊的一行"""
        return {
            "type": "box",
            "layout": "baseline",
            "contents": [
                {
                    "type": "text",
                    "text": label,
                    "color": FlexMessageHelper.COLOR_TEXT_SUB,
                    "size": "sm",
                    "flex": 1
                },
                {
                    "type": "text",
                    "text": str(value),
                    "wrap": True,
                    "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                    "size": "sm",
                    "flex": 3
                }
            ],
            "margin": "md"
        }

    @staticmethod
    def create_expense_success(expense: Dict, splits: List[Dict], is_edit: bool = False) -> Dict:
        """建立記帳成功／更新成功的 Flex Message bubble

        回傳純 bubble 字典，前端需自行包裝成 {type: 'flex', altText: '...', contents: bubble}
        後端若要使用 FlexMessage，需自行用 FlexMessage(contents=FlexContainer.from_dict(bubble))
        """
        split_type_names = {
            'equal': '平均分帳',
            'selected': '指定成員',
            'custom': '自訂金額',
            'ratio': '比例分帳'
        }

        # 建立分帳明細
        split_contents = []
        for split in splits:
            split_contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": split['user_name'],
                        "size": "sm",
                        "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": f"NT$ {int(split['amount']):,}",
                        "size": "sm",
                        "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                        "align": "end"
                    }
                ],
                "margin": "sm"
            })

        # 格式化日期
        date_str = FlexMessageHelper._format_date(expense.get('created_at'), default='剛剛')

        # 依據模式決定標題與顏色
        header_title = "帳目已更新" if is_edit else "記帳成功"
        header_color = FlexMessageHelper.COLOR_WARNING if is_edit else FlexMessageHelper.COLOR_SUCCESS

        bubble = {
            "type": "bubble",
            "size": "giga",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "RECEIPT",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "xxs",
                        "align": "center",
                        "lineSpacing": "2px"
                    },
                    {
                        "type": "text",
                        "text": header_title,
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "lg",
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": header_color,
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    # 金額顯示
                    {
                        "type": "text",
                        "text": "NT$",
                        "size": "sm",
                        "color": FlexMessageHelper.COLOR_TEXT_SUB,
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": f"{int(expense['amount']):,}",
                        "size": "4xl",
                        "weight": "bold",
                        "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "xl"
                    },
                    # 詳細資訊
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xl",
                        "spacing": "md",
                        "contents": [
                            FlexMessageHelper._create_row("項目", expense['description']),
                            FlexMessageHelper._create_row("付款人", expense['payer_name']),
                            FlexMessageHelper._create_row("分帳方式", split_type_names.get(expense['split_type'], '平均分帳')),
                            FlexMessageHelper._create_row("日期", date_str),
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "xl"
                    },
                    # 分帳明細標題
                    {
                        "type": "text",
                        "text": "分帳明細",
                        "size": "xs",
                        "color": FlexMessageHelper.COLOR_TEXT_SUB,
                        "margin": "xl",
                        "weight": "bold"
                    },
                    # 分帳明細列表
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "contents": split_contents
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"Expense ID: #{expense.get('expense_number', 0):03d}",
                        "size": "xxs",
                        "color": "#bbbbbb",
                        "align": "center"
                    }
                ],
                "paddingAll": "15px"
            },
            "action": {
                "type": "uri",
                "label": "action",
                "uri": f"https://liff.line.me/{LIFF.get_liff_id('FULL')}/expenses/{expense.get('expense_number', 0)}"
            }
        }

        return bubble

    @staticmethod
    def create_expense_deleted_message(expense: Dict) -> Dict:
        """建立帳目刪除的 Flex Message bubble"""
        
        # 格式化日期
        date_str = FlexMessageHelper._format_date(expense.get('created_at'), default='未知日期')

        bubble = {
            "type": "bubble",
            "size": "giga",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "RECEIPT",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "xxs",
                        "align": "center",
                        "lineSpacing": "2px"
                    },
                    {
                        "type": "text",
                        "text": "帳目已刪除",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "lg",
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": FlexMessageHelper.COLOR_DANGER,
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    # 刪除提示
                    {
                        "type": "text",
                        "text": "以下帳目已被移除",
                        "size": "sm",
                        "color": FlexMessageHelper.COLOR_TEXT_SUB,
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "xl"
                    },
                    # 詳細資訊
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xl",
                        "spacing": "md",
                        "contents": [
                            FlexMessageHelper._create_row("項目", expense.get('description', '未命名')),
                            FlexMessageHelper._create_row("金額", f"NT$ {int(expense.get('amount', 0)):,}"),
                            FlexMessageHelper._create_row("付款人", expense.get('payer_name', '未知')),
                            FlexMessageHelper._create_row("建立日期", date_str),
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"Expense ID: #{expense.get('expense_number', 0):03d}",
                        "size": "xxs",
                        "color": "#bbbbbb",
                        "align": "center"
                    }
                ],
                "paddingAll": "15px"
            },
            "action": {
                "type": "uri",
                "label": "action",
                "uri": f"https://liff.line.me/{LIFF.get_liff_id('FULL')}/groups/{expense.get('group_id', '')}"
            }
        }

        return bubble

    @staticmethod
    def create_todo_action_bubble(todo: Dict, action: str) -> Dict:
        """建立待辦事項操作的 Flex bubble

        action: 'created' | 'updated' | 'deleted'
        """
        action_titles = {
            'created': '新增待辦',
            'updated': '待辦已更新',
            'deleted': '待辦已刪除',
        }
        action_colors = {
            'created': FlexMessageHelper.COLOR_SUCCESS,
            'updated': FlexMessageHelper.COLOR_WARNING,
            'deleted': FlexMessageHelper.COLOR_DANGER,
        }

        priority_names = {
            'low': '低',
            'medium': '中',
            'high': '高',
        }

        status_names = {
            'pending': '待處理',
            'in_progress': '進行中',
            'completed': '已完成',
            'cancelled': '已取消',
        }

        title = todo.get('title', '未命名待辦')
        assignee_name = todo.get('assignee_name') or '未指派'
        category = todo.get('category') or '一般'
        priority = priority_names.get(todo.get('priority', 'medium'), '中')
        status = status_names.get(todo.get('status', 'pending'), '待處理')
        due_date = todo.get('due_date') or '未設定'

        header_title = action_titles.get(action, '待辦更新')
        header_color = action_colors.get(action, FlexMessageHelper.COLOR_PRIMARY)

        bubble = {
            "type": "bubble",
            "size": "giga",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "TODO",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "xxs",
                        "align": "center",
                        "lineSpacing": "2px"
                    },
                    {
                        "type": "text",
                        "text": header_title,
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "lg",
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": header_color,
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "size": "lg",
                        "weight": "bold",
                        "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                        "wrap": True
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "xl",
                        "spacing": "md",
                        "contents": [
                            FlexMessageHelper._create_row("負責人", assignee_name),
                            FlexMessageHelper._create_row("類別", category),
                            FlexMessageHelper._create_row("優先度", priority),
                            FlexMessageHelper._create_row("狀態", status),
                            FlexMessageHelper._create_row("到期日", due_date),
                        ]
                    },
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "前往待辦清單",
                        "size": "xxs",
                        "color": "#bbbbbb",
                        "align": "center"
                    }
                ],
                "paddingAll": "12px"
            },
            "action": {
                "type": "uri",
                "label": "action",
                "uri": f"https://liff.line.me/{LIFF.get_liff_id('FULL')}/groups/{todo.get('group_id', '')}?feature=todo"
            }
        }

        return bubble
    @staticmethod
    def create_settlement_bubble(balance_summary: Dict, payment_plans: List[Dict]) -> Dict:
        """建立結算結果的 Flex Message bubble（供前端或後端重用）"""
        # 分類應收和應付
        creditors = []
        debtors = []

        for user_id, data in balance_summary.items():
            net_amount = data.get('net_amount', 0)
            user_name = data.get('user_name', '未知')
            if net_amount > 0:
                creditors.append((user_name, net_amount))
            elif net_amount < 0:
                debtors.append((user_name, abs(net_amount)))

        # 建立還款計畫內容
        payment_contents = []
        for i, plan in enumerate(payment_plans, 1):
            payment_contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": plan['from_user_name'],
                                        "size": "sm",
                                        "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                                        "align": "center",
                                        "weight": "bold"
                                    }
                                ],
                                "flex": 3
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "➤",
                                        "size": "xs",
                                        "color": "#aaaaaa",
                                        "align": "center"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"NT$ {int(plan['amount']):,}",
                                        "size": "xs",
                                        "color": FlexMessageHelper.COLOR_SUCCESS,
                                        "align": "center",
                                        "weight": "bold"
                                    }
                                ],
                                "flex": 2
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": plan['to_user_name'],
                                        "size": "sm",
                                        "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                                        "align": "center",
                                        "weight": "bold"
                                    }
                                ],
                                "flex": 3
                            }
                        ],
                        "alignItems": "center"
                    }
                ],
                "backgroundColor": FlexMessageHelper.COLOR_BG_LIGHT,
                "cornerRadius": "md",
                "paddingAll": "md",
                "margin": "sm"
            })

        # 應收列表
        creditor_rows = []
        for name, amount in sorted(creditors, key=lambda x: x[1], reverse=True):
            creditor_rows.append(FlexMessageHelper._create_mini_row(name, f"+{int(amount):,}", FlexMessageHelper.COLOR_SUCCESS))

        # 應付列表
        debtor_rows = []
        for name, amount in sorted(debtors, key=lambda x: x[1], reverse=True):
            debtor_rows.append(FlexMessageHelper._create_mini_row(name, f"-{int(amount):,}", FlexMessageHelper.COLOR_DANGER))

        body_contents = []
        
        # 概況區塊
        if creditor_rows or debtor_rows:
            overview_contents = []
            if creditor_rows:
                overview_contents.append({
                    "type": "text",
                    "text": "誰該收錢",
                    "size": "xs",
                    "color": FlexMessageHelper.COLOR_TEXT_SUB,
                    "weight": "bold",
                    "margin": "md"
                })
                overview_contents.extend(creditor_rows)
            
            if debtor_rows:
                overview_contents.append({
                    "type": "text",
                    "text": "誰該付錢",
                    "size": "xs",
                    "color": FlexMessageHelper.COLOR_TEXT_SUB,
                    "weight": "bold",
                    "margin": "lg"
                })
                overview_contents.extend(debtor_rows)

            body_contents.append({
                "type": "box",
                "layout": "vertical",
                "contents": overview_contents,
                "backgroundColor": "#ffffff",
                "cornerRadius": "lg",
                "paddingAll": "md"
            })

        # 建議轉帳區塊
        if payment_contents:
            body_contents.append({
                "type": "text",
                "text": "建議轉帳路徑",
                "size": "sm",
                "weight": "bold",
                "color": FlexMessageHelper.COLOR_PRIMARY,
                "margin": "xl"
            })
            body_contents.extend(payment_contents)
            body_contents.append({
                "type": "text",
                "text": f"共需 {len(payment_plans)} 筆轉帳以結清所有帳目",
                "size": "xxs",
                "color": "#aaaaaa",
                "margin": "md",
                "align": "center"
            })
        else:
             body_contents.append({
                "type": "text",
                "text": "🎉 所有帳目都已經結清囉！",
                "size": "md",
                "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                "align": "center",
                "margin": "xl"
            })

        bubble = {
            "type": "bubble",
            "size": "giga",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "SETTLEMENT",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "xxs",
                        "align": "center",
                        "lineSpacing": "2px"
                    },
                    {
                        "type": "text",
                        "text": "結算報告",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "lg",
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": FlexMessageHelper.COLOR_PRIMARY,
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": body_contents
            }
        }

        return bubble
