(function() {
    'use strict';

    // カロリープロパティキャッシュ
    const caloriePropsCache = {};

    // カロリー結果をレンダリング
    function renderCalorieResult(blockId, data) {
        if (!data || !data.result) return;
        
        const r = data.result;
        const html = `
            <div style="margin-top:8px;padding:10px;background:#f9f9f9;border-radius:4px">
                <div><strong>合計カロリー:</strong> ${r.total_calories} kcal</div>
                ${r.details && r.details.length > 0 ? `
                    <div style="margin-top:6px;font-size:0.9em">
                        ${r.details.map(d => `<div>${d.item}: ${d.calories} kcal (${d.amount})</div>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        const resultDiv = document.querySelector(`[data-block-id="${blockId}"] .calorie-result`);
        if (resultDiv) {
            resultDiv.innerHTML = html;
        }
    }

    // カロリー入力処理
    function handleCalorieInput(blockId, value) {
        fetch('/api/calc-calories', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: value})
        })
        .then(res => res.json())
        .then(data => {
            renderCalorieResult(blockId, data);
        })
        .catch(err => {
            console.error('Calorie calculation error:', err);
            const resultDiv = document.querySelector(`[data-block-id="${blockId}"] .calorie-result`);
            if (resultDiv) {
                resultDiv.innerHTML = '<div style="color:red">カロリー計算エラー</div>';
            }
        });
    }

    // カロリータイトル更新
    function updateCalorieTitle(blockId, title) {
        caloriePropsCache[blockId] = caloriePropsCache[blockId] || {};
        caloriePropsCache[blockId].title = title;
    }

    // カロリーボックス追加
    function addCalorieBox(blockId) {
        if (typeof addBlockAfter === 'function') {
            addBlockAfter(blockId, 'calorie');
        } else {
            console.error('addBlockAfter function not found');
        }
    }

    // グローバル公開
    window.renderCalorieResult = renderCalorieResult;
    window.handleCalorieInput = handleCalorieInput;
    window.updateCalorieTitle = updateCalorieTitle;
    window.addCalorieBox = addCalorieBox;
    window.caloriePropsCache = caloriePropsCache;

})();
