// 待辦事項表單邏輯
let groupId = '';
let todoId = null;

/**
 * 初始化表單
 */
async function initTodoForm(liffId) {
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
 * 初始化表單
 */
function initializeForm() {
  // 優先使用後端傳入的 group_id，否則從 URL 參數讀取
  groupId = window.GROUP_ID;

  if (!groupId) {
    const urlParams = new URLSearchParams(window.location.search);
    groupId = urlParams.get('group_id');
  }

  if (!groupId) {
    showAlert('此功能只能在群組中使用', 'error');
    return;
  }

  checkEditMode();
  setupEventListeners();
}

/**
 * 檢查是否為編輯模式
 */
function checkEditMode() {
  const urlParams = new URLSearchParams(window.location.search);
  todoId = urlParams.get('id');

  if (todoId) {
    $('#formSubtitle').text('編輯待辦事項');
    $('#submitBtn').text('更新');
    loadTodoData();
  }
}

/**
 * 載入待辦事項資料
 */
async function loadTodoData() {
  try {
    showLoading('載入資料...');

    const data = await apiRequest(`/api/todos/${todoId}`);

    if (data.success && data.todo) {
      const todo = data.todo;

      $('#title').val(todo.title || '');
      $('#description').val(todo.description || '');
      $('#category').val(todo.category || '一般');

      // 設定優先度
      $(`#priority-${todo.priority || 'medium'}`).prop('checked', true);

      // 設定負責人
      $('#assignee').val(todo.assignee_id || '');

      // 設定到期日
      if (todo.due_date) {
        $('#dueDate').val(todo.due_date);
      }

      // 設定狀態
      $(`#status-${todo.status || 'pending'}`).prop('checked', true);

      // 更新 radio button 樣式
      $('input[type="radio"]:checked').each(function () {
        $(this).closest('.radio-btn').addClass('active');
      });
    }

    hideLoading();
  } catch (err) {
    hideLoading();
    showAlert('載入資料失敗: ' + err.message, 'error');
  }
}

/**
 * 設置事件監聽
 */
function setupEventListeners() {
  // 表單提交
  $('#todoForm').on('submit', handleFormSubmit);

  // 設置 radio button 樣式
  $('.radio-btn').on('click', function () {
    const $radio = $(this).find('input[type="radio"]');
    if ($radio.length) {
      $radio.prop('checked', true);

      // 移除同組其他按鈕的選中樣式
      const name = $radio.attr('name');
      $(`input[name="${name}"]`).each(function () {
        $(this).closest('.radio-btn').removeClass('active');
      });

      $(this).addClass('active');
    }
  });

  // 初始化選中的 radio button 樣式
  $('input[type="radio"]:checked').each(function () {
    $(this).closest('.radio-btn').addClass('active');
  });
}

/**
 * 重置表單
 */
function resetForm() {
  $('#title').val('');
  $('#description').val('');
  $('#category').val('一般');
  $('#priority-medium').prop('checked', true);
  $('#assignee').val('');
  $('#dueDate').val('');
  $('#status-pending').prop('checked', true);

  // 更新 radio button 樣式
  $('.radio-btn').removeClass('active');
  $('input[type="radio"]:checked').each(function () {
    $(this).closest('.radio-btn').addClass('active');
  });

  // 捲動到頂部
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * 處理表單提交
 */
async function handleFormSubmit(e) {
  e.preventDefault();

  const $form = $(this);
  if (!validateForm($form[0])) {
    return;
  }

  const title = $('#title').val();
  const description = $('#description').val();
  const category = $('#category').val();
  const priority = $('input[name="priority"]:checked').val();
  const assigneeId = $('#assignee').val();
  const dueDate = $('#dueDate').val();
  const status = $('input[name="status"]:checked').val();

  // 取得負責人名稱
  let assigneeName = '';
  if (assigneeId) {
    assigneeName = $(`#assignee option[value="${assigneeId}"]`).text();
  }

  // 取得當前使用者
  const profile = await getLIFFProfile();
  const createdBy = profile ? profile.userId : '';

  const todoData = {
    group_id: groupId,
    title: title,
    description: description,
    category: category,
    priority: priority,
    assignee_id: assigneeId,
    assignee_name: assigneeName,
    due_date: dueDate || null,
    status: status,
    created_by: createdBy
  };

  try {
    showLoading('處理中...');

    let data;
    if (todoId) {
      // 更新
      data = await apiRequest(`/api/todos/${todoId}`, {
        method: 'PUT',
        body: JSON.stringify(todoData)
      });
    } else {
      // 新增
      data = await apiRequest('/api/todos', {
        method: 'POST',
        body: JSON.stringify(todoData)
      });
    }

    if (data.success) {
      hideLoading();
      showAlert(todoId ? '更新成功！' : '新增成功！', 'success', 1000);

      if (todoId) {
        // 編輯模式：關閉視窗
        setTimeout(() => {
          closeLIFF();
        }, 1000);
      } else {
        // 新增模式：清空表單，讓用戶可以繼續新增
        setTimeout(() => {
          resetForm();
        }, 1000);
      }
    } else {
      hideLoading();
      showAlert(data.error || '操作失敗', 'error');
    }
  } catch (err) {
    hideLoading();
    showAlert('操作失敗: ' + err.message, 'error');
  }
}
