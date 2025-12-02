// 待辦清單邏輯
let todos = [];
let groupId = '';
let currentFilter = 'all'; // all, pending, in_progress, completed
let currentCategory = null;

/**
 * 初始化待辦清單頁面
 */
async function initTodoListPage(liffId) {
  const initialized = await initializeLIFF(liffId);

  if (initialized) {
    if (!liff.isLoggedIn()) {
      liff.login({ redirectUri: window.location.href });
    } else {
      loadGroupContext();
      await loadTodos();
      setupEventListeners();
    }
  }
}

/**
 * 載入群組資訊
 */
function loadGroupContext() {
  // 使用後端傳入的 group_id
  groupId = window.GROUP_ID;

  if (!groupId) {
    showAlert('此功能只能在群組中使用', 'error');
  }
}

/**
 * 載入待辦清單
 */
async function loadTodos() {
  try {
    showLoading('載入待辦清單...');

    const params = new URLSearchParams({ group_id: groupId });
    if (currentFilter !== 'all') {
      params.append('status', currentFilter);
    }
    if (currentCategory) {
      params.append('category', currentCategory);
    }

    const data = await apiRequest(`/api/todos?${params.toString()}`);

    if (data.success) {
      todos = data.todos || [];
      renderTodos();
    } else {
      showAlert('載入失敗: ' + (data.error || '未知錯誤'), 'error');
    }

    hideLoading();
  } catch (err) {
    hideLoading();
    showAlert('載入待辦清單失敗: ' + err.message, 'error');
  }
}

/**
 * 渲染待辦清單
 */
function renderTodos() {
  const $container = $('#todoList');

  if ($container.length === 0) return;

  if (todos.length === 0) {
    $container.html(`
      <div class="empty-state">
        <div class="empty-state-icon">📝</div>
        <p>目前沒有待辦事項</p>
        <p class="text-secondary">點擊右下角的 + 按鈕新增</p>
      </div>
    `);
    return;
  }

  const statusIcons = {
    'pending': '⏳',
    'in_progress': '🔄',
    'completed': '✅',
    'cancelled': '❌'
  };

  const priorityMap = {
    'low': '低',
    'medium': '中',
    'high': '高'
  };

  const todosHtml = todos.map(todo => {
    const statusIcon = statusIcons[todo.status] || '📝';
    const isOverdue = todo.due_date && new Date(todo.due_date) < new Date() && todo.status !== 'completed';

    return `
      <div class="todo-item ${todo.status === 'completed' ? 'completed' : ''}" data-id="${todo.id}">
        <div class="todo-header">
          <span class="todo-status-icon">${statusIcon}</span>
          <span class="todo-title">${escapeHtml(todo.title)}</span>
          <span class="todo-priority ${todo.priority}">${priorityMap[todo.priority]}</span>
        </div>

        ${todo.description ? `<div class="todo-description">${escapeHtml(todo.description)}</div>` : ''}

        <div class="todo-meta">
          <span class="todo-meta-item">
            <span>📁</span>
            <span class="category-badge">${escapeHtml(todo.category)}</span>
          </span>
          ${todo.assignee_name ? `
            <span class="todo-meta-item">
              <span>👤</span>
              <span>${escapeHtml(todo.assignee_name)}</span>
            </span>
          ` : ''}
          ${todo.due_date ? `
            <span class="todo-meta-item">
              <span>⏰</span>
              <span class="due-date ${isOverdue ? 'overdue' : ''}">${todo.due_date}</span>
            </span>
          ` : ''}
        </div>

        <div class="todo-actions">
          ${todo.status !== 'completed' ? `
            <button class="todo-action-btn edit" data-id="${todo.id}">編輯</button>
            <button class="todo-action-btn complete" data-id="${todo.id}">完成</button>
          ` : ''}
          <button class="todo-action-btn delete" data-id="${todo.id}">刪除</button>
        </div>
      </div>
    `;
  }).join('');

  $container.html(todosHtml);

  // 綁定動作按鈕事件
  $('.todo-action-btn.edit').on('click', function () {
    editTodo($(this).data('id'));
  });

  $('.todo-action-btn.complete').on('click', function () {
    completeTodo($(this).data('id'));
  });

  $('.todo-action-btn.delete').on('click', function () {
    deleteTodo($(this).data('id'));
  });
}

/**
 * 設置事件監聽
 */
function setupEventListeners() {
  // 篩選按鈕
  $('.filter-btn').on('click', function () {
    $('.filter-btn').removeClass('active');
    $(this).addClass('active');
    currentFilter = $(this).data('filter');
    loadTodos();
  });

  // 新增按鈕
  $('#addTodoBtn').on('click', function () {
    window.location.href = `/liff/tall/todo/form?group_id=${groupId}`;
  });
}

/**
 * 編輯待辦
 */
function editTodo(todoId) {
  window.location.href = `/liff/tall/todo/form?id=${todoId}&group_id=${groupId}`;
}

/**
 * 完成待辦
 */
async function completeTodo(todoId) {
  try {
    showLoading('標記為已完成...');

    const data = await apiRequest(`/api/todos/${todoId}/complete`, {
      method: 'POST'
    });

    if (data.success) {
      showAlert('已標記為完成！', 'success');
      await loadTodos();
    } else {
      showAlert('標記失敗: ' + (data.error || '未知錯誤'), 'error');
    }

    hideLoading();
  } catch (err) {
    hideLoading();
    showAlert('操作失敗: ' + err.message, 'error');
  }
}

/**
 * 刪除待辦
 */
async function deleteTodo(todoId) {
  if (!confirm('確定要刪除這個待辦事項嗎？')) {
    return;
  }

  try {
    showLoading('刪除中...');

    const data = await apiRequest(`/api/todos/${todoId}`, {
      method: 'DELETE'
    });

    if (data.success) {
      showAlert('刪除成功！', 'success');
      await loadTodos();
    } else {
      showAlert('刪除失敗: ' + (data.error || '未知錯誤'), 'error');
    }

    hideLoading();
  } catch (err) {
    hideLoading();
    showAlert('刪除失敗: ' + err.message, 'error');
  }
}

/**
 * 防止 XSS 攻擊
 */
function escapeHtml(text) {
  return $('<div>').text(text).html();
}
