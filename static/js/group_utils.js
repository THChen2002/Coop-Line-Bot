// 群組相關共用工具函數

/**
 * 分享群組邀請連結
 * @param {string} groupId - 群組 ID
 * @param {string} groupCode - 群組代碼
 * @param {string} groupName - 群組名稱
 * @param {Object} options - 選項
 * @param {Function} options.onSuccess - 分享成功後的回調函數
 * @param {boolean} options.enableFallback - 是否啟用降級方案（複製連結）
 * @returns {Promise<boolean>} 是否分享成功
 */
export async function shareGroupInvite(groupId, groupCode, groupName, options = {}) {
  const {
    onSuccess = null,
    enableFallback = false
  } = options;

  const liffId = liff.id;
  const baseUrl = window.location.origin;

  // Flex Message 使用 ?code= 連結（邀請連結）
  const inviteUrl = `${baseUrl}/liff/full/group/join?code=${groupCode}`;

  // 純文字訊息使用 /groups/<id> 連結（群組詳情）
  const groupDetailUrl = `https://liff.line.me/${liffId}/groups/${groupId}`;

  try {
    // 從後端 API 取得 Flex Message
    const flexResponse = await apiRequest('/api/flex-messages/group-invite', {
      method: 'POST',
      body: JSON.stringify({
        group_name: groupName,
        group_code: groupCode,
        invite_url: inviteUrl
      })
    });

    if (!flexResponse.success) {
      throw new Error(flexResponse.error || '無法取得 Flex Message');
    }

    // 包裝 bubble 成完整的 Flex Message
    const flexMessage = {
      type: 'flex',
      altText: `邀請您加入分帳群組「${groupName}」`,
      contents: flexResponse.bubble
    };

    // 純文字訊息（群組詳情連結）
    const textMessage = {
      type: 'text',
      text: groupDetailUrl
    };

    const result = await liff.shareTargetPicker([flexMessage, textMessage]);

    if (result) {
      showAlert('分享成功！', 'success');
      if (onSuccess) {
        onSuccess();
      }
      return true;
    }
    return false;
  } catch (error) {
    console.error('分享失敗:', error);

    if (error.code === 'CANCEL') {
      return false;
    }

    // 如果啟用降級方案，提供複製連結選項
    if (enableFallback) {
      const confirmed = await showConfirm('無法開啟分享功能，是否複製連結？', {
        confirmText: '複製連結',
        cancelText: '取消',
        type: 'info'
      });

      if (confirmed) {
        try {
          await navigator.clipboard.writeText(groupDetailUrl);
          showAlert('連結已複製到剪貼簿', 'success');
          return true;
        } catch (copyError) {
          showAlert('複製失敗，請手動複製連結：\n' + groupDetailUrl, 'error');
          return false;
        }
      }
    } else {
      showAlert('分享失敗: ' + error.message, 'error');
    }

    return false;
  }
}

// 將匯出的函數掛到 window 上，供非 module 的檔案使用
window.shareGroupInvite = shareGroupInvite;

