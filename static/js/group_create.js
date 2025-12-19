// 建立群組頁面 JavaScript

let userId = null;
let userProfile = null;
let createdGroupData = null;

/**
 * 初始化建立群組頁面
 */
async function initGroupCreatePage(liffId) {
  try {
    showLoading('初始化中...');

    const initialized = await initializeLIFF(liffId);
    if (!initialized) {
      return;
    }

    const profile = await liff.getProfile();
    userId = profile.userId;
    userProfile = profile;

    bindEvents();
    hideLoading();
  } catch (error) {
    console.error('初始化失敗:', error);
    showAlert('初始化失敗: ' + error.message, 'error');
    hideLoading();
  }
}

/**
 * 綁定事件
 */
function bindEvents() {
  $('#createGroupForm').on('submit', handleSubmit);

  $('#cancelBtn').on('click', function () {
    window.location.href = '/liff/full/groups';
  });

  $('#copyLinkBtn').on('click', copyInviteLink);
  $('#shareLineBtn').on('click', shareToLine);

  $('#closeModalBtn').on('click', function () {
    window.location.href = '/liff/full/groups';
  });
}

/**
 * 處理表單提交
 */
async function handleSubmit(e) {
  e.preventDefault();

  const groupName = $('#groupName').val().trim();

  if (!groupName) {
    showAlert('請輸入群組名稱', 'warning');
    return;
  }

  try {
    showLoading('建立群組中...');

    const response = await apiRequest('/api/groups', {
      method: 'POST',
      body: JSON.stringify({
        group_name: groupName,
        created_by: userId,
        display_name: userProfile.displayName,
        picture_url: userProfile.pictureUrl || ''
      })
    });

    hideLoading();

    if (response.success) {
      createdGroupData = response.group;
      showSuccessModal(response.group);
    } else {
      throw new Error(response.error || '建立群組失敗');
    }
  } catch (error) {
    hideLoading();
    console.error('建立群組失敗:', error);
    showAlert('建立群組失敗: ' + error.message, 'error');
  }
}

/**
 * 顯示成功對話框
 */
function showSuccessModal(group) {
  $('#displayGroupCode').text(group.group_code);

  // 生成 LIFF 邀請連結
  const liffId = liff.id;
  const joinUrl = `https://liff.line.me/${liffId}/group/join?code=${group.group_code}`;
  $('#inviteLink').val(joinUrl);

  $('#successModal').removeClass('hidden');
}

/**
 * 複製邀請連結
 */
async function copyInviteLink() {
  const $inviteLinkInput = $('#inviteLink');
  const $copyBtn = $('#copyLinkBtn');

  try {
    await navigator.clipboard.writeText($inviteLinkInput.val());

    // 更新按鈕狀態
    const originalText = $copyBtn.text();
    $copyBtn.text('已複製！').addClass('copied');

    // 2 秒後恢復
    setTimeout(() => {
      $copyBtn.text(originalText).removeClass('copied');
    }, 2000);

    showAlert('連結已複製到剪貼簿', 'success', 1500);
  } catch (error) {
    console.error('複製失敗:', error);
  }
}

/**
 * 分享到 LINE
 */
async function shareToLine() {
  if (!createdGroupData) {
    showAlert('找不到群組資料', 'error');
    return;
  }

  await shareGroupInvite(
    createdGroupData.id,
    createdGroupData.group_code,
    createdGroupData.group_name,
    {
      onSuccess: () => {
        setTimeout(() => {
          window.location.href = '/liff/full/groups';
        }, 1500);
      }
    }
  );
}
