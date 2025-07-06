const form = document.getElementById("shorten-form");
const urlInput = document.getElementById("url");
const result = document.getElementById("result");
const resetBtn = document.getElementById("reset-btn");

// URL短縮APIを呼ぶ関数
async function shortenUrl(url) {
    // API実行
  const response = await fetch("http://localhost:8000/shorten", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      url: url,
      expire_minutes: 60 * 24 * 7, // 1週間を有効期限にする
    }),
  });
  if (!response.ok) {
    throw new Error("短縮失敗");
  }
  return response.json();
}

// 結果表示更新
function showResult(shortUrl) {
  result.innerHTML = `<a href="${shortUrl}" target="_blank">${shortUrl}</a>`;
}

// エラー表示更新
function showError(message) {
  result.textContent = "エラー: " + message;
}

// 入力欄と結果のクリア
function resetContents() {
  urlInput.value = "";
  result.innerHTML = "";
}

form.onsubmit = async (event) => {
  event.preventDefault();
  const url = urlInput.value.trim();

  if (!url) {
    showError("URLを入力してください");
    return;
  }

  try {
    // ローディング表示（任意）
    result.textContent = "短縮中…";

    const data = await shortenUrl(url);
    showResult(data.short_url);
  } catch (err) {
    showError(err.message);
  }
};


// リセットボタン
resetBtn.addEventListener("click", resetContents)