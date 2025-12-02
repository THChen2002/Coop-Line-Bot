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
    def create_expense_success(expense: Dict, splits: List[Dict]) -> FlexMessage:
        """建立記帳成功的 Flex Message"""
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
                        "letterSpacing": "2px"
                    },
                    {
                        "type": "text",
                        "text": "記帳成功",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "lg",
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": FlexMessageHelper.COLOR_SUCCESS,
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
                            FlexMessageHelper._create_row("日期", expense.get('created_at', '').strftime('%Y-%m-%d') if hasattr(expense.get('created_at'), 'strftime') else '剛剛'),
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
            }
        }

        return FlexMessage(
            alt_text=f"記帳成功：{expense['description']} NT$ {int(expense['amount']):,}",
            contents=FlexContainer.from_dict(bubble)
        )

    @staticmethod
    def create_settlement_result(balance_summary: Dict, payment_plans: List[Dict]) -> FlexMessage:
        """建立結算結果的 Flex Message"""
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
                        "letterSpacing": "2px"
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

        return FlexMessage(
            alt_text="結算報告",
            contents=FlexContainer.from_dict(bubble)
        )

    @staticmethod
    def create_expense_list(expenses: List[Dict]) -> FlexMessage:
        """建立帳目清單的 Flex Message"""
        if not expenses:
            return FlexMessageHelper.create_info_message("無未結帳目", "目前沒有未結算的帳目，太棒了！")

        total_amount = sum(e.get('amount', 0) for e in expenses)
        
        # 帳目列表內容
        expense_rows = []
        for expense in expenses[:10]:  # 顯示前 10 筆
            expense_rows.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": expense.get('description', '未命名'),
                                "size": "sm",
                                "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                                "weight": "bold",
                                "maxLines": 1,
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": f"#{expense.get('expense_number', 0):03d} • {expense.get('payer_name', '未知')}",
                                "size": "xxs",
                                "color": FlexMessageHelper.COLOR_TEXT_SUB
                            }
                        ],
                        "flex": 7
                    },
                    {
                        "type": "text",
                        "text": f"NT$ {int(expense.get('amount', 0)):,}",
                        "size": "sm",
                        "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                        "weight": "bold",
                        "align": "end",
                        "flex": 3
                    }
                ],
                "paddingAll": "sm",
                "action": {
                    "type": "message",
                    "label": "詳細",
                    "text": f"查詢帳目 #{expense.get('expense_number')}"
                }
            })
            expense_rows.append({"type": "separator"})

        # 移除最後一個分隔線
        if expense_rows:
            expense_rows.pop()

        bubble = {
            "type": "bubble",
            "size": "giga",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "EXPENSES",
                        "weight": "bold",
                        "color": FlexMessageHelper.COLOR_PRIMARY,
                        "size": "xxs",
                        "letterSpacing": "2px"
                    },
                    {
                        "type": "text",
                        "text": "未結帳目",
                        "weight": "bold",
                        "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                        "size": "xl",
                        "margin": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"總計 NT$ {int(total_amount):,}",
                        "size": "md",
                        "color": FlexMessageHelper.COLOR_DANGER,
                        "weight": "bold",
                        "margin": "xs"
                    }
                ],
                "paddingAll": "20px",
                "paddingBottom": "10px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": expense_rows,
                        "backgroundColor": FlexMessageHelper.COLOR_BG_LIGHT,
                        "cornerRadius": "md"
                    },
                    {
                        "type": "text",
                        "text": f"共 {len(expenses)} 筆記錄",
                        "size": "xs",
                        "color": "#aaaaaa",
                        "align": "center",
                        "margin": "md"
                    }
                ],
                "paddingAll": "20px",
                "paddingTop": "0px"
            }
        }

        return FlexMessage(
            alt_text="未結帳目清單",
            contents=FlexContainer.from_dict(bubble)
        )

    @staticmethod
    def create_todo_list(todos: List) -> FlexMessage:
        """建立待辦清單的 Flex Message"""
        from models.todo import Todo

        if not todos:
            return FlexMessageHelper.create_info_message("無待辦事項", "目前沒有待辦事項，放鬆一下吧！")

        # 統計
        pending_count = 0
        completed_count = 0
        
        todo_rows = []
        for todo in todos[:10]:
            if isinstance(todo, Todo):
                todo_dict = todo.to_dict()
            else:
                todo_dict = todo
            
            status = todo_dict.get('status', 'pending')
            is_done = status == 'completed'
            if is_done:
                completed_count += 1
            else:
                pending_count += 1

            icon = "✅" if is_done else "⬜"
            if status == 'in_progress':
                icon = "🔄"
            
            title_color = "#aaaaaa" if is_done else FlexMessageHelper.COLOR_TEXT_MAIN
            decoration = "line-through" if is_done else "none"
            
            todo_rows.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": icon,
                        "flex": 0,
                        "size": "sm",
                        "gravity": "center"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": todo_dict.get('title', '未命名'),
                                "size": "sm",
                                "color": title_color,
                                "decoration": decoration,
                                "weight": "bold" if not is_done else "regular",
                                "wrap": True
                            },
                            {
                                "type": "text",
                                "text": f"{todo_dict.get('assignee_name', '未分配')} • {todo_dict.get('category', '一般')}",
                                "size": "xxs",
                                "color": "#aaaaaa"
                            }
                        ],
                        "flex": 1,
                        "margin": "sm"
                    }
                ],
                "margin": "md"
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
                        "text": "TODO LIST",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "xxs",
                        "letterSpacing": "2px"
                    },
                    {
                        "type": "text",
                        "text": "待辦事項",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "lg",
                        "margin": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"待處理: {pending_count}",
                                "size": "xs",
                                "color": "#ffffff",
                                "flex": 0,
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": "|",
                                "size": "xs",
                                "color": "#ffffff",
                                "margin": "sm",
                                "flex": 0,
                                "alpha": 0.5
                            },
                            {
                                "type": "text",
                                "text": f"已完成: {completed_count}",
                                "size": "xs",
                                "color": "#ffffff",
                                "margin": "sm",
                                "flex": 0,
                                "alpha": 0.8
                            }
                        ],
                        "margin": "xs"
                    }
                ],
                "backgroundColor": FlexMessageHelper.COLOR_ACCENT,
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": todo_rows,
                "paddingAll": "20px"
            },
            "footer": {
                 "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "＋ 新增待辦事項",
                            "uri": f"https://liff.line.me/{LIFF.get_liff_id('TALL')}/todo/form"
                        },
                        "style": "primary",
                        "color": FlexMessageHelper.COLOR_ACCENT,
                        "height": "sm"
                    }
                ],
                "paddingAll": "20px",
                "paddingTop": "0px"
            }
        }

        return FlexMessage(
            alt_text="待辦清單",
            contents=FlexContainer.from_dict(bubble)
        )

    @staticmethod
    def create_simple_message(title: str, message: str, color: str = "#2c3e50") -> FlexMessage:
        """建立簡單訊息的 Flex Message"""
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "color": color,
                        "size": "md"
                    },
                    {
                        "type": "text",
                        "text": message,
                        "wrap": True,
                        "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                        "size": "sm",
                        "margin": "md"
                    }
                ],
                "paddingAll": "20px"
            }
        }
        return FlexMessage(
            alt_text=title,
            contents=FlexContainer.from_dict(bubble)
        )

    @staticmethod
    def create_success_message(message: str) -> FlexMessage:
        return FlexMessageHelper.create_simple_message("✅ 成功", message, FlexMessageHelper.COLOR_SUCCESS)

    @staticmethod
    def create_error_message(message: str) -> FlexMessage:
        return FlexMessageHelper.create_simple_message("❌ 錯誤", message, FlexMessageHelper.COLOR_DANGER)

    @staticmethod
    def create_info_message(title: str, message: str) -> FlexMessage:
        return FlexMessageHelper.create_simple_message(title, message, FlexMessageHelper.COLOR_ACCENT)

    @staticmethod
    def create_statistics_message(title: str, stats: Dict) -> FlexMessage:
        """建立統計資訊的 Flex Message"""
        stat_contents = []

        for key, value in stats.items():
            # 檢查是否為分隔線（空字串或只有空白）
            if not key.strip():
                stat_contents.append({"type": "separator", "margin": "md"})
                continue

            # 判斷是否為縮排項目 (以空白開頭)
            is_indented = key.startswith("  ")
            display_key = key.strip()
            
            if is_indented:
                row = {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "↳",
                            "size": "xs",
                            "color": "#aaaaaa",
                            "flex": 0,
                            "margin": "lg"
                        },
                        {
                            "type": "text",
                            "text": display_key,
                            "size": "xs",
                            "color": FlexMessageHelper.COLOR_TEXT_SUB,
                            "flex": 0,
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": str(value),
                            "size": "xs",
                            "color": FlexMessageHelper.COLOR_TEXT_SUB,
                            "align": "end",
                            "flex": 1
                        }
                    ],
                    "margin": "xs"
                }
            else:
                # 一般項目
                color = FlexMessageHelper.COLOR_TEXT_MAIN
                weight = "regular"
                
                # 特殊關鍵字加強顯示
                if "總" in key or "淨" in key:
                    weight = "bold"
                if "淨收入" in key:
                    color = FlexMessageHelper.COLOR_SUCCESS
                elif "淨支出" in key:
                    color = FlexMessageHelper.COLOR_DANGER
                
                row = {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": display_key,
                            "size": "sm",
                            "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": str(value),
                            "size": "sm",
                            "color": color,
                            "align": "end",
                            "weight": weight
                        }
                    ],
                    "margin": "sm"
                }
            
            stat_contents.append(row)

        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "STATISTICS",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "xxs",
                        "letterSpacing": "2px"
                    },
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "lg",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": FlexMessageHelper.COLOR_PRIMARY,
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": stat_contents,
                "paddingAll": "20px"
            }
        }

        return FlexMessage(
            alt_text=title,
            contents=FlexContainer.from_dict(bubble)
        )

    @staticmethod
    def create_help_message() -> FlexMessage:
        """建立說明訊息的 Flex Message"""
        bubble = {
            "type": "bubble",
            "size": "giga",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "USER GUIDE",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "xxs",
                        "align": "center",
                        "letterSpacing": "2px"
                    },
                    {
                        "type": "text",
                        "text": "使用說明",
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
                "contents": [
                    # 記帳功能
                    {
                        "type": "text",
                        "text": "💰 記帳功能",
                        "weight": "bold",
                        "color": FlexMessageHelper.COLOR_PRIMARY,
                        "size": "sm",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "sm",
                        "spacing": "sm",
                        "contents": [
                            FlexMessageHelper._create_help_item("開啟記帳表單", "使用 LIFF 表單記帳（推薦）"),
                            FlexMessageHelper._create_help_item("記帳 500 午餐", "平均分帳：記帳 [金額] [項目]"),
                            FlexMessageHelper._create_help_item("記帳 500 午餐 小明", "指定付款人：記帳 [金額] [項目] [付款人]"),
                            FlexMessageHelper._create_help_item("帳目", "顯示所有未結算帳目"),
                            FlexMessageHelper._create_help_item("我的帳目", "顯示個人收支統計"),
                            FlexMessageHelper._create_help_item("統計", "顯示總支出統計")
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    # 待辦功能
                    {
                        "type": "text",
                        "text": "📝 待辦功能",
                        "weight": "bold",
                        "color": FlexMessageHelper.COLOR_PRIMARY,
                        "size": "sm",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "sm",
                        "spacing": "sm",
                        "contents": [
                             FlexMessageHelper._create_help_item("新增待辦", "開啟表單新增待辦"),
                             FlexMessageHelper._create_help_item("待辦清單", "查看所有待辦事項"),
                             FlexMessageHelper._create_help_item("待處理", "查看待處理事項"),
                             FlexMessageHelper._create_help_item("已完成", "查看已完成事項")
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    # 結算與其他
                    {
                        "type": "text",
                        "text": "⚙️ 結算與其他",
                        "weight": "bold",
                        "color": FlexMessageHelper.COLOR_PRIMARY,
                        "size": "sm",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "sm",
                        "spacing": "sm",
                        "contents": [
                             FlexMessageHelper._create_help_item("結算", "計算應收應付金額"),
                             FlexMessageHelper._create_help_item("清帳", "標記所有帳目為已結算"),
                             FlexMessageHelper._create_help_item("刪除 [編號]", "刪除指定帳目")
                        ]
                    },
                     {
                        "type": "text",
                        "text": "💡 支援群組共享與個人紀錄",
                        "size": "xxs",
                        "color": "#aaaaaa",
                        "align": "center",
                        "margin": "xl"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "開啟記帳表單",
                            "uri": f"https://liff.line.me/{LIFF.get_liff_id('TALL')}/expense"
                        },
                        "style": "primary",
                        "color": FlexMessageHelper.COLOR_PRIMARY,
                        "height": "sm"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "新增待辦事項",
                            "uri": f"https://liff.line.me/{LIFF.get_liff_id('TALL')}/todo/form"
                        },
                        "style": "secondary",
                        "margin": "sm",
                        "height": "sm"
                    }
                ],
                "paddingAll": "20px",
                "paddingTop": "0px"
            }
        }

        return FlexMessage(
            alt_text="使用說明",
            contents=FlexContainer.from_dict(bubble)
        )

    @staticmethod
    def _create_help_item(command: str, desc: str) -> Dict:
        """建立說明項目的 Row"""
        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": command,
                    "size": "sm",
                    "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": desc,
                    "size": "xs",
                    "color": FlexMessageHelper.COLOR_TEXT_SUB,
                    "wrap": True
                }
            ],
            "paddingStart": "md"
        }

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
            "spacing": "sm"
        }

    @staticmethod
    def _create_mini_row(label: str, value: str, color: str) -> Dict:
        """建立小型的 key-value row"""
        return {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": label,
                    "size": "sm",
                    "color": FlexMessageHelper.COLOR_TEXT_MAIN,
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": value,
                    "size": "sm",
                    "color": color,
                    "align": "end",
                    "weight": "bold"
                }
            ],
            "margin": "sm"
        }
