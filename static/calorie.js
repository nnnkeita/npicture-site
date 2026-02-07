(function() {
    'use strict';

    // カロリープロパティキャッシュ
    const caloriePropsCache = {};

    // カロリー結果をレンダリング
    function renderCalorieResult(blockId, data) {
        if (!data) return;
        const r = data.result || data;
        if (!r) return;

        const totalEl = document.getElementById(`cal-total-${blockId}`);
        if (totalEl && r.total_kcal !== undefined) {
            totalEl.textContent = `${r.total_kcal} kcal`;
        }

        const itemsEl = document.getElementById(`cal-items-${blockId}`);
        if (itemsEl && Array.isArray(r.items)) {
            itemsEl.innerHTML = r.items.length
                ? r.items.map(item => {
                    const mark = item.is_estimated ? '（推定）' : '';
                    return `<div>${item.input} → ${item.kcal} kcal ${mark}</div>`;
                }).join('')
                : '';
        }

        const legacyDiv = document.querySelector(`[data-block-id="${blockId}"] .calorie-result`);
        if (legacyDiv) {
            legacyDiv.innerHTML = `合計: ${r.total_kcal ?? '-'} kcal`;
        }
    }

    // カロリー入力処理
    function handleCalorieInput(blockId, value) {
        const lines = String(value || '').split('\n').map(line => line.trim()).filter(Boolean);
        fetch('/api/calc-calories', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({lines})
        })
        .then(res => res.json())
        .then(data => {
            renderCalorieResult(blockId, data);
            if (data && data.total_kcal !== undefined) {
                caloriePropsCache[blockId] = caloriePropsCache[blockId] || {};
                caloriePropsCache[blockId].total_kcal = data.total_kcal;
                caloriePropsCache[blockId].items = data.items || [];
                if (data.note) caloriePropsCache[blockId].note = data.note;

                fetch(`/api/blocks/${blockId}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ props: JSON.stringify(caloriePropsCache[blockId]) })
                }).catch(err => console.warn('Failed to save calorie props:', err));
            }
        })
        .catch(err => {
            console.error('Calorie calculation error:', err);
            const itemsEl = document.getElementById(`cal-items-${blockId}`);
            if (itemsEl) {
                itemsEl.innerHTML = '<div style="color:red">カロリー計算エラー</div>';
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
