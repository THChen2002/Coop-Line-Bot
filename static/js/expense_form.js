// 記帳表單邏輯
let splitType = 'equal';
let groupId = '';

/**
 * 初始化記帳表單
 */
async function initExpenseForm(liffId) {
  const initialized = await initializeLIFF(liffId);

  if (initialized) {
    if (!liff.isLoggedIn()) {
      liff.login({ redirectUri: window.location.href });
    } else {
      initializeForm();
    }
  }
}

/**
 * 初始化表單（綁定事件）
 */
function initializeForm() {
  try {
    showLoading('載入群組成員...');

    // 使用後端傳入的 group_id
    groupId = window.GROUP_ID;

    console.log('Group ID:', groupId);

    if (!groupId) {
      hideLoading();
      showAlert('此功能只能在群組中使用', 'error');
      return;
    }

    // 檢查是否有成員資料（由模板渲染）
    const $memberItems = $('#membersList .member-item');
    if ($memberItems.length === 0) {
      hideLoading();
      showAlert('群組中沒有成員資料，請確保群組成員有在 LINE 中發言過', 'warning');
      return;
    }

    // 綁定成員列表的事件
    bindMemberEvents();

    hideLoading();
  } catch (err) {
    console.error('Initialize form error:', err);
    hideLoading();
    showAlert('初始化表單失敗: ' + err.message, 'error');
  }
}

/**
 * 綁定成員列表的事件
 */
function bindMemberEvents() {
  // 綁定 checkbox 變更事件
  $('#membersList input[type="checkbox"]').on('change', updateAllocation);

  // 綁定金額輸入事件
  $('#membersList .member-amount').on('input', updateAllocation);
}

/**
 * 切換分帳方式
 */
function setupSplitTypeButtons() {
  $('.split-type-btn').on('click', function () {
    $('.split-type-btn').removeClass('active');
    $(this).addClass('active');
    splitType = $(this).data('type');

    // 切換金額輸入框的啟用狀態
    const isEqual = splitType === 'equal';

    if (isEqual) {
      // 平均分帳：所有金額欄位 disabled
      $('.member-amount').prop('disabled', true).val('');
    } else {
      // 自訂金額：根據勾選狀態設定 disabled
      $('#membersList input[type="checkbox"]').each(function () {
        const $amountInput = $(`#amount_${$(this).val()}`);
        if ($(this).is(':checked')) {
          $amountInput.prop('disabled', false);
        } else {
          $amountInput.prop('disabled', true).val(0);
        }
      });
    }

    updateAllocation();
  });
}

/**
 * 更新分配金額
 */
function updateAllocation() {
  const totalAmount = parseFloat($('#amount').val()) || 0;
  const $checkedMembers = $('#membersList input[type="checkbox"]:checked');

  if (splitType === 'equal' && $checkedMembers.length > 0) {
    const count = $checkedMembers.length;

    // 四捨五入到整數元，避免小數點
    const totalInt = Math.round(totalAmount);
    const baseAmount = Math.floor(totalInt / count);
    const remainder = totalInt % count;

    // 分配：最後 remainder 個人多分 1 元
    let allocated = 0;
    $checkedMembers.each(function (index) {
      const amount = (index >= count - remainder) ? baseAmount + 1 : baseAmount;
      $(`#amount_${$(this).val()}`).val(amount);
      allocated += amount;
    });

    // 未勾選的成員金額歸零
    $('#membersList input[type="checkbox"]:not(:checked)').each(function () {
      $(`#amount_${$(this).val()}`).val(0);
    });

    // 檢查分配金額是否與總金額相符
    const $totalCheck = $('#totalCheck');
    const $allocatedAmount = $('#allocatedAmount');

    if (allocated !== totalAmount) {
      $totalCheck.show();
      $allocatedAmount.text(`NT$ ${formatAmount(allocated)}`);
      $allocatedAmount.addClass('over-budget');
    } else {
      $totalCheck.hide();
    }
  } else if (splitType === 'custom') {
    // 已勾選的成員：啟用金額欄位
    $checkedMembers.each(function () {
      $(`#amount_${$(this).val()}`).prop('disabled', false);
    });

    // 未勾選的成員：disabled 並歸零
    $('#membersList input[type="checkbox"]:not(:checked)').each(function () {
      $(`#amount_${$(this).val()}`).prop('disabled', true).val(0);
    });

    // 計算已分配金額
    let allocated = 0;
    $checkedMembers.each(function () {
      const amount = parseFloat($(`#amount_${$(this).val()}`).val()) || 0;
      allocated += amount;
    });

    const $totalCheck = $('#totalCheck');
    const $allocatedAmount = $('#allocatedAmount');

    $totalCheck.show();
    $allocatedAmount.text(`NT$ ${formatAmount(allocated)}`);

    // 檢查分配金額是否與總金額相符（不相等就顯示紅色）
    if (allocated !== totalAmount) {
      $allocatedAmount.addClass('over-budget');
    } else {
      $allocatedAmount.removeClass('over-budget');
    }
  }
}

/**
 * 構建記帳成功的 Flex Message
 */
function createExpenseFlexMessage(expense) {
  const splitTypeNames = {
    'equal': '平均分帳',
    'selected': '指定成員',
    'custom': '自訂金額',
    'ratio': '比例分帳'
  };

  // 建立分帳明細
  const splitContents = expense.splits.map(split => ({
    type: "box",
    layout: "horizontal",
    contents: [
      {
        type: "text",
        text: split.user_name,
        size: "sm",
        color: "#555555",
        flex: 0
      },
      {
        type: "text",
        text: `NT$ ${Math.round(split.amount).toLocaleString()}`,
        size: "sm",
        color: "#555555",
        align: "end"
      }
    ],
    margin: "sm"
  }));

  // 格式化日期
  const date = new Date();
  const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;

  return {
    type: "flex",
    altText: `記帳成功：${expense.description} NT$ ${Math.round(expense.amount).toLocaleString()}`,
    contents: {
      type: "bubble",
      size: "giga",
      header: {
        type: "box",
        layout: "vertical",
        contents: [
          {
            type: "text",
            text: "RECEIPT",
            weight: "bold",
            color: "#ffffff",
            size: "xxs",
            align: "center",
            letterSpacing: "2px"
          },
          {
            type: "text",
            text: "記帳成功",
            weight: "bold",
            color: "#ffffff",
            size: "lg",
            align: "center",
            margin: "sm"
          }
        ],
        backgroundColor: "#06C755",
        paddingAll: "20px"
      },
      body: {
        type: "box",
        layout: "vertical",
        contents: [
          {
            type: "text",
            text: "NT$",
            size: "sm",
            color: "#aaaaaa",
            align: "center"
          },
          {
            type: "text",
            text: Math.round(expense.amount).toLocaleString(),
            size: "4xl",
            weight: "bold",
            color: "#1DB446",
            align: "center"
          },
          {
            type: "separator",
            margin: "xl"
          },
          {
            type: "box",
            layout: "vertical",
            margin: "xl",
            spacing: "md",
            contents: [
              {
                type: "box",
                layout: "horizontal",
                contents: [
                  { type: "text", text: "項目", size: "sm", color: "#aaaaaa", flex: 0 },
                  { type: "text", text: expense.description, size: "sm", color: "#555555", align: "end" }
                ]
              },
              {
                type: "box",
                layout: "horizontal",
                contents: [
                  { type: "text", text: "付款人", size: "sm", color: "#aaaaaa", flex: 0 },
                  { type: "text", text: expense.payer_name, size: "sm", color: "#555555", align: "end" }
                ]
              },
              {
                type: "box",
                layout: "horizontal",
                contents: [
                  { type: "text", text: "分帳方式", size: "sm", color: "#aaaaaa", flex: 0 },
                  { type: "text", text: splitTypeNames[expense.split_type] || '平均分帳', size: "sm", color: "#555555", align: "end" }
                ]
              },
              {
                type: "box",
                layout: "horizontal",
                contents: [
                  { type: "text", text: "日期", size: "sm", color: "#aaaaaa", flex: 0 },
                  { type: "text", text: dateStr, size: "sm", color: "#555555", align: "end" }
                ]
              }
            ]
          },
          {
            type: "separator",
            margin: "xl"
          },
          {
            type: "text",
            text: "分帳明細",
            size: "xs",
            color: "#aaaaaa",
            margin: "xl",
            weight: "bold"
          },
          {
            type: "box",
            layout: "vertical",
            margin: "md",
            contents: splitContents
          }
        ]
      },
      footer: {
        type: "box",
        layout: "vertical",
        contents: [
          {
            type: "text",
            text: `Expense ID: #${String(expense.expense_number || 0).padStart(3, '0')}`,
            size: "xxs",
            color: "#bbbbbb",
            align: "center"
          }
        ],
        paddingAll: "15px"
      }
    }
  };
}

/**
 * 處理表單提交
 */
async function handleExpenseSubmit(e) {
  e.preventDefault();

  const $form = $(e.target);
  if (!validateForm($form[0])) {
    return;
  }

  const description = $('#description').val();
  const amount = parseFloat($('#amount').val());
  const payerId = $('#payer').val();

  if (!payerId) {
    showAlert('請選擇付款人', 'warning');
    return;
  }

  const $checkedMembers = $('#membersList input[type="checkbox"]:checked');

  if ($checkedMembers.length === 0) {
    showAlert('請至少選擇一位分帳成員', 'warning');
    return;
  }

  // 收集分帳資料
  const splits = [];
  let totalAllocated = 0;

  $checkedMembers.each(function () {
    const memberId = $(this).val();
    const memberName = $(this).data('name');
    const splitAmount = parseFloat($(`#amount_${memberId}`).val()) || 0;

    splits.push({
      user_id: memberId,
      user_name: memberName,
      amount: splitAmount,
      is_paid: false
    });

    totalAllocated += splitAmount;
  });

  // 驗證總金額
  if (Math.abs(totalAllocated - amount) > 0.01) {
    showAlert(`分配金額 (${formatAmount(totalAllocated)}) 與總金額 (${formatAmount(amount)}) 不符`, 'error');
    return;
  }

  // 送出資料
  try {
    showLoading('處理中...');

    const payerName = $(`#payer option[value="${payerId}"]`).text();

    const result = await apiRequest('/api/expenses', {
      method: 'POST',
      body: JSON.stringify({
        group_id: groupId,
        payer_id: payerId,
        payer_name: payerName,
        amount: amount,
        description: description,
        split_type: splitType,
        splits: splits,
        created_by: payerId
      })
    });

    if (result.success) {
      // 構建 Flex Message
      const expense = result.expense;
      const flexMessage = createExpenseFlexMessage(expense);

      // 使用 liff.sendMessages 發送訊息
      liff.sendMessages([flexMessage])
        .then(() => {
          showAlert('記帳成功！', 'success', 800);
          setTimeout(() => {
            closeLIFF();
          }, 800);
        })
        .catch((err) => {
          console.error('發送訊息失敗:', err);
          // 即使發送失敗，也顯示成功並關閉
          showAlert('記帳成功！', 'success', 800);
          setTimeout(() => {
            closeLIFF();
          }, 800);
        });
    } else {
      hideLoading();
      showAlert(result.error || '記帳失敗', 'error');
    }
  } catch (err) {
    hideLoading();
    showAlert('送出失敗: ' + err.message, 'error');
  }
}

// 初始化
$(document).ready(function () {
  // 設置分帳方式按鈕
  setupSplitTypeButtons();

  // 監聽總金額變化
  $('#amount').on('input', debounce(updateAllocation, 300));

  // 監聽表單提交
  $('#expenseForm').on('submit', handleExpenseSubmit);
});
